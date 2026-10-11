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

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from skills_compiler import TASK_DOMAIN_TO_DOMAIN  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]
COMPILER = REPO / "scripts" / "skills_compiler.py"
TASKS = REPO / "benchmarks" / "tasks_ieee.json"
MANIFEST = REPO / "benchmarks" / "checklists_v2" / "manifest.json"

# Skills whose recorded artifacts are known not to reproduce today. Each entry
# states why, so the exception is auditable rather than a blanket waiver.
# No skills are exempt today. The last one (`tdd`) was cleared when its
# benchmark-time source was recovered verbatim from the A0 ablation artifact --
# see skills/RECOVERY.md. The table is kept because a future drift should be
# declared explicitly rather than silently skipped.
KNOWN_EXCEPTIONS: dict[str, str] = {}


def sha256_file(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _domain_for(skill_id: str) -> str:
    """The Domain enum name the manifest recorded this skill under."""
    tasks = json.loads(TASKS.read_text(encoding="utf-8"))
    for t in tasks:
        if t.get("skill") == skill_id:
            return TASK_DOMAIN_TO_DOMAIN.get((t.get("domain") or "").lower(), "general")
    return "general"


def resolve_source(entry: dict) -> tuple[pathlib.Path | None, str]:
    """Return the on-disk file whose bytes are the recorded source, and how.

    The live `SKILL.md` is the first candidate. If it was legitimately edited
    after the run, a sibling `SKILL.benchmark-time.md` may hold the recorded
    source verbatim -- recovered from the A0 ablation artifact, which is a raw
    passthrough of the benchmark-time input. Candidates are accepted only when
    their SHA-256 equals the manifest's `source_sha256`, so this can never be
    satisfied by a reconstruction that merely happens to recompile to the same
    artefact.

    Falls back to the live path so genuine drift is still reported rather than
    silently hidden.
    """
    live = REPO / entry["source_path"]
    recorded = entry["source_sha256"]
    candidates = [live, live.parent / "SKILL.benchmark-time.md"]
    fallback = None
    for candidate in candidates:
        if not candidate.exists():
            continue
        if sha256_file(candidate) == recorded:
            return candidate, ("live" if candidate == live else "recovered")
        fallback = fallback or candidate
    return fallback, "unmatched"


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
        recovered: list[str] = []
        drifted: list[str] = []
        absent: list[str] = []

        for skill_id, entry in sorted(recorded.items()):
            want = entry["compiled_sha256"]
            artifact = tmp / f"{skill_id}.txt"
            source, provenance = resolve_source(entry)

            # The bulk `from-tasks` run compiles live sources. When a skill's
            # recorded source is only available as the recovered copy, compile
            # that file directly so the artefact check stays honest.
            if source is None:
                absent.append(skill_id)
                continue
            if provenance != "live":
                proc2 = subprocess.run(
                    [sys.executable, str(COMPILER), "compile",
                     "--input", str(source),
                     "--domain", _domain_for(skill_id),
                     "--output", str(artifact)],
                    cwd=REPO, capture_output=True, text=True,
                )
                if proc2.returncode != 0:
                    drifted.append(skill_id)
                    continue

            if skill_id not in rebuilt and provenance == "live":
                absent.append(skill_id)
                continue
            if not artifact.exists():
                absent.append(skill_id)
                continue

            # Hash the artefact on disk rather than trusting the rebuild manifest.
            if sha256_file(artifact) == want:
                matched.append(skill_id)
                if provenance != "live":
                    recovered.append(skill_id)
            else:
                drifted.append(skill_id)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"compiler: {COMPILER.relative_to(REPO)}")
    print(f"manifest: {MANIFEST.relative_to(REPO)} "
          f"(recorded with compiler v{manifest_data['compiler_version']})")
    print()
    print(f"  reproducible (byte-identical): {len(matched)}/{len(recorded)}")
    print(f"    from the live SKILL.md:      {len(matched) - len(recovered)}")
    print(f"    from a recovered source:     {len(recovered)}"
          + (f"  ({', '.join(sorted(recovered))})" if recovered else ""))
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