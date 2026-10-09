"""Verify that the committed checklist artifacts are reproducible from source.

Answers the reviewer question the manuscript leaves open: *which tool produced
these numbers?* Instead of asserting it in prose, this recompiles the benchmark
corpus with crates/skills-compiler and compares SHA-256 digests against the
manifest recorded at experiment time.

Known exceptions are declared explicitly below rather than silently skipped, so
that fixing them flips this check from "known-degraded" to fully clean.

Usage:
    cargo build --release --manifest-path crates/skills-compiler/Cargo.toml
    uv run python scripts/verify_compiled_artifacts.py

Exit codes:
    0 = every skill not declared as a known exception reproduces byte-for-byte
    1 = unexpected drift (regression)
    2 = compiler binary unavailable (skip)
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[1]
BINARY = REPO / "crates" / "skills-compiler" / "target" / "release" / "skills-compiler"
TASKS = REPO / "benchmarks" / "tasks_ieee.json"
MANIFEST = REPO / "benchmarks" / "checklists_v2" / "manifest.json"

# Skills whose recorded artifacts are known not to reproduce today. Each entry
# states why, so the exception is auditable rather than a blanket waiver.
KNOWN_EXCEPTIONS: dict[str, str] = {
    "tdd": (
        "skills/tdd/SKILL.md was edited after the 2026-08-29 benchmark run "
        "(recorded source sha 1d0a1439..., on disk 93ea419b...). Its recorded "
        "16.63% token reduction no longer reproduces; the current file yields "
        "46.00%. Restore the recorded source to clear this."
    ),
    "debugging-code": (
        "skills/debugging-code/ is absent from the repository, so the sre-node-leak "
        "task cannot be recompiled at all. Restore the skill directory to clear this."
    ),
}


def sha256_file(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    if not BINARY.exists():
        print(
            "compiler binary not found; build it with:\n"
            "  cargo build --release --manifest-path crates/skills-compiler/Cargo.toml",
            file=sys.stderr,
        )
        return 2

    manifest_data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    recorded = manifest_data["skills"]

    tmp = pathlib.Path(tempfile.mkdtemp(prefix="verify-artifacts-"))
    try:
        proc = subprocess.run(
            [str(BINARY), "from-tasks", "--tasks", str(TASKS), "--out-dir", str(tmp)],
            cwd=REPO,
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            print(f"compiler failed:\n{proc.stdout}\n{proc.stderr}", file=sys.stderr)
            return 1

        rebuilt_manifest = tmp / "manifest.json"
        if not rebuilt_manifest.exists():
            print("compiler produced no manifest.json", file=sys.stderr)
            return 1
        rebuilt = json.loads(rebuilt_manifest.read_text(encoding="utf-8"))["skills"]

        matched: list[str] = []
        drifted: list[str] = []
        absent: list[str] = []

        for skill_id, entry in sorted(recorded.items()):
            want = entry["compiled_sha256"]
            artifact = tmp / f"{skill_id}.txt"
            if skill_id not in rebuilt or not artifact.exists():
                absent.append(skill_id)
                continue
            # Hash the artefact on disk rather than trusting the rebuild manifest.
            if sha256_file(artifact) == want:
                matched.append(skill_id)
            else:
                drifted.append(skill_id)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"compiler: {BINARY.relative_to(REPO)}")
    print(f"manifest: {MANIFEST.relative_to(REPO)} "
          f"(recorded with compiler v{manifest_data['compiler_version']})")
    print()
    print(f"  reproducible (byte-identical): {len(matched)}/{len(recorded)}")
    print(f"  drifted:                       {len(drifted)}")
    print(f"  not recompiled (source absent): {len(absent)}")

    for skill_id in sorted(set(drifted) | set(absent)):
        reason = KNOWN_EXCEPTIONS.get(skill_id, "UNDECLARED - investigate")
        label = "drifted  " if skill_id in drifted else "absent   "
        print(f"\n  [{label}] {skill_id}\n             {reason}")

    # An exception that now reproduces means KNOWN_EXCEPTIONS is stale.
    stale = sorted(set(KNOWN_EXCEPTIONS) & set(matched))
    for skill_id in stale:
        print(
            f"\n  NOTE: '{skill_id}' is declared a known exception but now reproduces. "
            "Remove it from KNOWN_EXCEPTIONS.",
            file=sys.stderr,
        )

    unexpected = [s for s in drifted + absent if s not in KNOWN_EXCEPTIONS]
    if unexpected or stale:
        print(
            "\nFAIL: artifact reproducibility regressed for "
            f"{sorted(set(unexpected) | set(stale))}. Either the compiler changed "
            "behaviour or a benchmark SKILL.md was edited without updating the manifest.",
            file=sys.stderr,
        )
        return 1

    print(
        f"\nOK: {len(matched)}/{len(recorded)} artifacts reproduce byte-for-byte; "
        f"{len(set(drifted) | set(absent))} documented exception(s) remain "
        "(see scripts/verify_compiled_artifacts.py KNOWN_EXCEPTIONS)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())