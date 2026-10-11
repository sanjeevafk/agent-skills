"""The checklist_v1 artifacts are irreplaceable and must not drift.

`benchmarks/checklists_ieee/` backs the `checklist` delivery arm -- 80 of the
396 scored evaluations (20%) and 7 of the 10 pairwise comparisons, including
`checklist_vs_checklist_v2`, the balanced-vs-aggressive contrast that the
headline delivery result rests on.

The byte pins below guard the *committed originals*. Regenerating them is a
separate check, in `test_checklist_v1_artefacts_regenerate_from_source`.

Unlike `checklists_v2/`, **no generator in this repository reproduces these
files**. They were produced by a tool that predates the repository's initial
commit. The compiler's `checklist_v1()` path emits a `[CHECKLIST GUIDELINES]`
header these files do not have, so recompiling produces *different* bytes and
would silently invalidate the archived evaluations. See
`benchmarks/COMPILER_PROVENANCE.md` section 4.

So these files cannot be regenerated -- they can only be lost. This module is
the only guard against that, and against an edit that would leave the archived
`checklist` scores unreproducible without anyone noticing.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
V1_DIR = REPO_ROOT / "benchmarks" / "checklists_ieee"
RESULTS = V1_DIR.parent / "delivery_results_ieee.json"

EXPECTED_SHA256 = {
    "architecture-decision-records.txt": "a56f1794f83d7e80adca24725c51fdb7bc883fc67cc558e1ad30add9d0c47c18",
    "browser-qa.txt": "4fbdf664e66a4d5be517279176b9e1765f6e8018a557a91e3182fcbeea0136bc",
    "ci-cd-pipeline-builder.txt": "156e43c92c27c025e317a01f29a2978bfdef87b382a20523a71895f277c30481",
    "code-refactor.txt": "7b2805129e656c55585fff4e85bd6af1ae3cf052ec1a49b04e11ff7cdebd17e3",
    "database-migrations.txt": "6ac71912ad7674fc9f1e84200bb8009fa81d315702821396eaf0b9fed3251176",
    "debugging-code.txt": "b956502023c925c30bba5c7922e57d22c93560865d44acf540a66f25082acae6",
    "defi-amm-security.txt": "ddd565f3ac13644a9b078714f9cefe15b4215c0cf47f9ca0932f073f6e24c978",
    "django-security.txt": "c42669a2abfdbc66a1e7226729e4b65b4f4813a7e80b77ca6c913e0fa5ae8c13",
    "docker-patterns.txt": "3edd90174e637198f0482da9a5aeb3cbd747569dad7bcb50a28ef66a022530c4",
    "e2e-testing.txt": "7b4e29af67f4fe5ff125e85b890bb6072c399c747df9f7c5bccf060b48f7b1d0",
    "kubernetes-patterns.txt": "28842077da9280515dd134909add8498be91e4ce436aac457ebc34522350047f",
    "manifest.json": "55ce1b3d8643c0c8131bb461c7216fc678fd461dd51af84287a1abc5493bfeca",
    "performance-profiler.txt": "ecefdd88ed09b41f4b40e206e347a5eb0bc916a3af2e1b0ef518a24dc0f743a0",
    "postgres-patterns.txt": "61ccae982f0a3ecd1943518c0728cc9e92a82664d812abbf4ef7342b51e712f6",
    "redis-patterns.txt": "136965428fdcfdfde495e80dabdae7b24e97baedd66459ab94c9c0e6bd0a9f16",
    "security-review.txt": "5e589ffef702557ea194e4d64aea8e6d89228efa069c4903d00847faae6f41c0",
    "systematic-debugging.txt": "ceb12ae59164f29ac7e1bae043e0ed4ad2b620282b7463d4cffbc617f0825252",
    "tdd.txt": "bf270372ab4c8fa418f24ad4cb340a85c6d0918dccee4c5022bf1aa3fecf95be",
    "type-architecture-analyzer.txt": "da354a375595f1253cffbbfc761b2ab2b52067bcaf50e940104d777406a9fb9c",
}


def test_checklist_v1_artifacts_are_intact() -> None:
    """All 19 files pinned in one assertion.

    These were previously 19 `@pytest.mark.parametrize` cases. That multiplied
    the collected-test count without adding coverage -- it is one assertion
    applied N times -- and split a single failure into N near-identical ones.
    Checking the whole set at once also reports every drifted file in one run
    instead of forcing 19.
    """
    missing = sorted(n for n in EXPECTED_SHA256 if not (V1_DIR / n).exists())
    assert not missing, (
        f"missing: {missing}. These back the `checklist` delivery arm (80 of 396 "
        f"evaluations) and no tool in this repository regenerates them. Restore "
        f"from git history -- do not recompile."
    )
    drifted = [
        f"{n} ({expected[:12]} -> {hashlib.sha256((V1_DIR / n).read_bytes()).hexdigest()[:12]})"
        for n, expected in sorted(EXPECTED_SHA256.items())
        if hashlib.sha256((V1_DIR / n).read_bytes()).hexdigest() != expected
    ]
    assert not drifted, (
        f"modified: {drifted}. These artifacts have no reproducing generator, so "
        f"an edit silently invalidates the archived `checklist` scores. If the "
        f"change is intended, the affected evaluations must be re-run and the "
        f"arm restated."
    )


def test_no_extra_files_in_checklist_v1_directory() -> None:
    """An added artifact was never the input to any scored run.

    `manifest.json` is part of the recorded set; it is read, never regenerated.
    """
    found = {p.name for p in V1_DIR.iterdir()} - set(EXPECTED_SHA256)
    assert not found, f"unexpected files in checklists_ieee/: {sorted(found)}"


def test_checklist_arm_is_still_part_of_the_archived_results() -> None:
    """Guard the premise of the guard: the arm exists and carries its 80 runs."""
    results = json.loads(RESULTS.read_text(encoding="utf-8"))
    assert "checklist" in results["strategies"]
    assert results["raw_score_counts"]["checklist"] == 80

def test_checklist_v1_artefacts_regenerate_from_source() -> None:
    """The arm is reproducible, not merely archived.

    Guards the claim that the recovered extractor still produces these exact
    bytes. If this fails, either the extractor drifted or a source changed --
    both invalidate the 80 archived `checklist` evaluations.
    """
    import subprocess
    import sys

    proc = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "verify_ieee_v1_artifacts.py")],
        capture_output=True, text=True,
    )
    assert proc.returncode == 0, (
        f"checklist_v1 no longer regenerates from source:\n{proc.stdout}\n{proc.stderr}"
    )
