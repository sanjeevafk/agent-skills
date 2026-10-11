"""Verify that the `checklist_v1` delivery arm reproduces from source.

Answers the second half of the reviewer question answered for the `checklist_v2`
arm by verify_compiled_artifacts.py: the 80 scored evaluations delivered from
`benchmarks/checklists_ieee/` are reproducible, not just archived.

Those artefacts were produced by an extractor that did not survive in the
repository, so for a time the arm was auditable but not reproducible. Its rule
set has since been recovered by fitting it against the committed artefacts
until all 18 reproduced byte-for-byte (`scripts/skills_compiler.py` documents
the recovered rules). This script is what keeps that claim honest: it
regenerates every artefact from its recorded source and compares SHA-256
against both the file on disk and the digest the manifest recorded at run time.

It drives the shipped `skills_compiler.py ieee-v1` **command line** into a
temporary directory rather than importing the extractor directly. That is
deliberate. During the recovery the rules were fitted in a scratch script which
scored 18/18; copying them into the real module dropped the score to 10/18,
because the table flattener joined every column instead of dropping the head.
Only rerunning the full matrix caught it. Verifying through the same entry
point a user would invoke is what keeps that class of porting error visible.

Usage:
    uv run python scripts/verify_ieee_v1_artifacts.py

Exit codes:
    0 = all 18 regenerate byte-for-byte
    1 = any artefact drifted
    2 = a recorded source is missing
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

MANIFEST = REPO / "benchmarks" / "checklists_ieee" / "manifest.json"
ARTIFACTS = REPO / "benchmarks" / "checklists_ieee"


def sha256_file(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    if not MANIFEST.exists():
        print(f"manifest not found: {MANIFEST}", file=sys.stderr)
        return 2

    recorded = json.loads(MANIFEST.read_text(encoding="utf-8"))["checklists"]

    tmp = pathlib.Path(tempfile.mkdtemp(prefix="verify-ieee-v1-"))
    try:
        # Go through the shipped CLI, exactly as a user would.
        proc = subprocess.run(
            [sys.executable, str(COMPILER), "ieee-v1",
             "--manifest", str(MANIFEST), "--out-dir", str(tmp)],
            cwd=REPO, capture_output=True, text=True,
        )
        if proc.returncode != 0:
            print(f"compiler CLI failed:\n{proc.stdout}\n{proc.stderr}",
                  file=sys.stderr)
            return 1
        produced = {
            path.stem: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(tmp.glob("*.txt"))
        }

        matched, drifted, missing_source, absent = [], [], [], []
        for skill, entry in sorted(recorded.items()):
            if skill not in produced:
                missing_source.append(skill)
                continue
            committed = ARTIFACTS / f"{skill}.txt"
            if not committed.exists():
                absent.append(skill)
                continue
            # Both comparisons matter: the file on disk must be unmodified, and
            # it must match what the manifest recorded at experiment time.
            if (produced[skill] == sha256_file(committed)
                    == entry["artifact_sha256"]):
                matched.append(skill)
            else:
                drifted.append(skill)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"compiler: {COMPILER.relative_to(REPO)} ieee-v1")
    print(f"manifest: {MANIFEST.relative_to(REPO)} "
          f"(extractor v{json.loads(MANIFEST.read_text(encoding='utf-8'))['extractor_version']})")
    print()
    print(f"  reproduced byte-for-byte: {len(matched)}/{len(recorded)}")
    print(f"  drifted:                  {len(drifted)}")
    print(f"  source unavailable:       {len(missing_source)}")
    print(f"  artefact missing on disk: {len(absent)}")

    for skill in drifted + absent + missing_source:
        print(f"\n  [FAIL] {skill}\n         the `checklist` arm cannot be reproduced",
              file=sys.stderr)

    if drifted or absent or missing_source:
        print(
            "\nFAIL: the checklist_v1 arm no longer reproduces. It backs 80 of the "
            "396 scored evaluations and 7 of the 10 pairwise comparisons, so a "
            "drift here invalidates those scores.",
            file=sys.stderr,
        )
        return 1

    print(
        f"\nOK: {len(matched)}/{len(recorded)} checklist_v1 artefacts reproduce "
        f"byte-for-byte from their recorded sources."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())