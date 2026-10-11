"""The two "v1" generators must never be confused, and must be wired correctly.

Two unrelated functions in `scripts/skills_compiler.py` produce output whose
names both contain "v1":

* `checklist_v1()` -- the A5 ablation variant, `*_a5_v1_bullets.md`
* `compile_ieee_v1()` -- the `checklist` delivery arm, `checklists_ieee/*.txt`

Swapping them is silent: each returns plausible-looking text, just not the bytes
the recorded artifact holds. These tests resolve both through the
`ARM_GENERATORS` registry so no call site can pick the wrong one, and they pin
the specific defect that the registry exists to prevent.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
import skills_compiler as sc  # noqa: E402

SOURCE = """---
name: demo
description: demo
---

## Rules

- Always validate input

```typescript
function f(x: string): number {
  return x.length;
}
```

| Task | Jump to |
|------|---------|
| Deploy | [Runbook](#runbook) |
"""


def test_registry_separates_the_two_arms():
    """The two generators are distinct, and neither is reachable as the other."""
    assert sc.ARM_GENERATORS["checklist"] is sc.compile_ieee_v1
    assert sc.ARM_GENERATORS["a5_v1_bullets"] is not sc.compile_ieee_v1
    # A5 output starts with the v1 directive header; the checklist arm has no
    # header at all. If these ever produced the same bytes, the mapping is wrong.
    a5 = sc.generate("a5_v1_bullets", SOURCE)
    checklist = sc.generate("checklist", SOURCE)
    assert a5.startswith(sc.V1_HEADER), a5[:80]
    assert not checklist.startswith("["), checklist[:80]
    assert a5 != checklist


def test_unknown_arm_is_rejected():
    """An unregistered arm is an error, not a silent default."""
    try:
        sc.generate("checklist_v1", SOURCE)
    except KeyError as exc:
        assert "checklist" in str(exc)
    else:
        raise AssertionError(
            "generate() accepted 'checklist_v1' -- that name must not resolve, "
            "it is the A5 ablation variant's historical function name"
        )


def test_table_row_keeps_its_head_column():
    """Regression guard for the porting bug that scored 10/18.

    While moving the recovered extractor from a scratch script into this module,
    the table flattener was transcribed as joining *every* cell instead of
    dropping the head column, so `| Deploy | [Runbook](#runbook) |` became
    `Deploy: Deploy | [Runbook](#runbook)`. The scratch version scored 18/18;
    only rerunning the full matrix against the shipped module caught it.
    """
    out = sc.generate("checklist", SOURCE)
    assert "- Deploy: [Runbook](#runbook)" in out, out
    assert "Deploy: Deploy" not in out, out


def test_cli_refuses_to_overwrite_tracked_evidence():
    """A bare regeneration must not be able to destroy what CI verifies."""
    assert sc._is_tracked_evidence_dir(sc.REPO / "benchmarks" / "checklists_ieee")
    assert sc._is_tracked_evidence_dir(sc.REPO / "benchmarks" / "checklists_v2")
    assert sc._is_tracked_evidence_dir(sc.REPO / "benchmarks" / "ablations")
    assert not sc._is_tracked_evidence_dir(sc.REPO / "benchmarks" / "tasks_ieee.json")