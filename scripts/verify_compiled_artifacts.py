"""Verify that the committed checklist artifacts are reproducible from source.

Answers the reviewer question the manuscript leaves open: *which tool produced
these numbers?* Instead of asserting it in prose, this recompiles the benchmark
corpus with scripts/skills_compiler.py and compares SHA-256 digests against the
manifest recorded at experiment time.

The compiler is a byte-for-byte Python port of the former Rust crate
(crates/skills-compiler v0.2.0). That port was cross-validated against the Rust
binary on identical input for all six compilation modes across the benchmark
corpus (120/120 byte-identical) before the crate was removed, so switching
implementations did not change any recorded artifact. See
benchmarks/COMPILER_PROVENANCE.md.

Known exceptions are declared explicitly below rather than silently skipped, so
that fixing them flips this check from "known-degraded" to fully clean.

Usage:
    uv run python scripts/verify_compiled_artifacts.py

Exit codes:
    0 = every skill not declared as a known exception reproduces byte-for-byte
    1 = unexpected drift (regression)
    2 = compiler unavailable (skip)
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
COMPILER = REPO / "scripts" / "skills_compiler.py"
TASKS = REPO / "benchmarks" / "tasks_ieee.json"
MANIFEST = REPO / "benchmarks" / "checklists_v2" / "manifest.json"

# Skills whose recorded artifacts are known not to reproduce today. Each entry
# states why, so the exception is auditable rather than a blanket waiver.
KNOWN_EXCEPTIONS: dict[str, str] = {
    "tdd": (
        "The benchmark-time source of skills/tdd/SKILL.md predates the repository's "
        "initial commit and is not recoverable; only its compiled artifact survives. "
        "The reconstructed benchmark-time source is kept at "
        "skills/tdd/SKILL.benchmark-time.md and reproduces the recorded artifact "
        "byte-for-byte, but the recorded source hash (1d0a1439...) no longer matches "
        "any file on disk. The live skills/tdd/SKILL.md is the post-run version "
        "(93ea419b...) that current tooling uses. See skills/RECOVERY.md."
    ),
}


def sha256_file(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    if not COMPILER.exists():
        print(f"compiler not found: {COMPILER}", file=sys.stderr)
        return 2

    manifest_data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    recorded = manifest_data["skills"]

    tmp = pathlib.Path(tempfile.mkdtemp(prefix="verify-artifacts-"))
    try:
        proc = subprocess.run(
            [sys.executable, str(COMPILER), "from-tasks",
             "--tasks", str(TASKS), "--out-dir", str(tmp)],
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

    print(f"compiler: {COMPILER.relative_to(REPO)}")
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