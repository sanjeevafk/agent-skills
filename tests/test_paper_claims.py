"""Regression tests pinning the manuscript's headline claims to the archived data.

These exist because the paper states numbers in prose. If a strategy arm, a
judge window, or a compiled artifact changes, these tests fail loudly rather
than letting the manuscript silently drift out of agreement with the evidence.

References: paper/MANUSCRIPT.md sections 5, 8.1-8.4.

Archive schema (benchmarks/delivery_results_ieee.json):
    data["tasks"]                       -> list of task objects
    task["id"], task["strategy_runs"]   -> dict of arm -> list of runs
    run["judge_total"]                  -> 35-point composite score
    run["input_tokens"], run["output_tokens"], run["latency"]
"""

import hashlib
import json
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
BENCH = REPO / "benchmarks"


def _load(name):
    path = BENCH / name
    if not path.exists():
        pytest.skip(f"archived artifact missing: {name}")
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def _completed_runs(data):
    """Yield (task_id, arm, run) for every run that completed."""
    for task in data["tasks"]:
        for arm, runs in task.get("strategy_runs", {}).items():
            for run in runs:
                yield task["id"], arm, run


def _arm_means(data, field, arms):
    out = {}
    for _, arm, run in _completed_runs(data):
        if arm in arms and run.get(field) is not None:
            out.setdefault(arm, []).append(run[field])
    return {k: sum(v) / len(v) for k, v in out.items()}


class TestExecutionAndAttrition:
    """§5 — 18 defined tasks, 17 completed, 396 evaluations."""

    def test_completed_evaluation_count(self):
        data = _load("delivery_results_ieee.json")
        runs = [r for _, _, r in _completed_runs(data)]
        assert len(runs) == 396, f"paper states N=396, archive holds {len(runs)}"

    def test_completed_task_count(self):
        data = _load("delivery_results_ieee.json")
        contributing = [
            t["id"] for t in data["tasks"] if any(t.get("strategy_runs", {}).values())
        ]
        assert len(contributing) == 17, "paper states 17 of 18 tasks completed"

    def test_excluded_task_is_the_documented_one(self):
        data = _load("delivery_results_ieee.json")
        empty = [
            t["id"] for t in data["tasks"] if not any(t.get("strategy_runs", {}).values())
        ]
        assert empty == ["db-ratelimit-redis-ieee"], (
            "§5 attributes the single dropout to db-ratelimit-redis-ieee"
        )

    def test_arms_per_task(self):
        data = _load("delivery_results_ieee.json")
        expected = {"control", "full", "retrieved", "checklist", "checklist_v2"}
        for task in data["tasks"]:
            assert set(task.get("strategy_runs", {})) == expected, (
                f"{task['id']} does not carry all five delivery arms"
            )


class TestStrategyMeans:
    """§8.1 Table 1 — mean 35-point judge scores."""

    EXPECTED = {
        "control": 24.49,
        "full": 25.17,
        "retrieved": 24.73,
        "checklist": 24.54,
        "checklist_v2": 24.96,
    }

    def test_means_match_table_1(self):
        means = _arm_means(_load("delivery_results_ieee.json"), "judge_total", self.EXPECTED)
        for arm, expected in self.EXPECTED.items():
            assert arm in means, f"arm {arm} absent from archive"
            assert means[arm] == pytest.approx(expected, abs=0.01), (
                f"{arm}: paper says {expected}, archive gives {means[arm]:.2f}"
            )

    def test_control_is_the_weakest_arm(self):
        """§8.6.A — the economics-first premise: baseline is within noise, not better."""
        means = _arm_means(_load("delivery_results_ieee.json"), "judge_total", self.EXPECTED)
        assert means["control"] < means["full"], (
            "paper positions control as near-best; if it is now weakest the "
            "framing in §8.6.A needs revisiting"
        )

    def test_checklist_v1_has_the_highest_variance(self):
        """§8.1 Table 1 / Finding 3 — sigma 6.94 vs 5.80 for full."""
        data = _load("delivery_results_ieee.json")
        by_arm = {}
        for _, arm, run in _completed_runs(data):
            if run.get("judge_total") is not None:
                by_arm.setdefault(arm, []).append(run["judge_total"])

        def sd(xs):
            m = sum(xs) / len(xs)
            return (sum((x - m) ** 2 for x in xs) / (len(xs) - 1)) ** 0.5

        sds = {a: sd(v) for a, v in by_arm.items() if len(v) > 1}
        assert max(sds, key=sds.get) == "checklist", (
            f"paper attributes highest variance to checklist_v1 (aggressive "
            f"extraction); archive gives {sds}"
        )


class TestTokenEconomy:
    """§8.2 Table 3 — prompt token overhead and the 30.0% headline."""

    EXPECTED_TOKENS = {
        "control": 144,
        "full": 2270,
        "retrieved": 430,
        "checklist": 663,
        "checklist_v2": 1590,
    }

    def test_prompt_token_means(self):
        means = _arm_means(
            _load("delivery_results_ieee.json"), "input_tokens", self.EXPECTED_TOKENS
        )
        for arm, expected in self.EXPECTED_TOKENS.items():
            assert means[arm] == pytest.approx(expected, abs=1.0), (
                f"{arm}: paper says {expected}, archive gives {means[arm]:.0f}"
            )

    def test_v2_reduction_is_thirty_percent(self):
        full = self.EXPECTED_TOKENS["full"]
        v2 = self.EXPECTED_TOKENS["checklist_v2"]
        assert 100 * (full - v2) / full == pytest.approx(30.0, abs=0.5)
        assert full - v2 == pytest.approx(680, abs=5)

    def test_analytical_projection_arithmetic(self):
        """§7.4 / §8.5 — K=20 -> 13,600 tokens/turn -> 408,000 per 30 turns."""
        full = self.EXPECTED_TOKENS["full"]
        v2 = self.EXPECTED_TOKENS["checklist_v2"]
        per_turn = 20 * (full - v2)
        assert per_turn == pytest.approx(13600, abs=200)
        assert 30 * per_turn == pytest.approx(408000, abs=6000)


class TestCompilerManifest:
    """§7.1 / §8.2 — provenance for the checklist artifacts."""

    def test_manifest_aggregate_reduction(self):
        data = _load("checklists_v2/manifest.json")
        assert data["aggregate_token_reduction_pct"] == pytest.approx(30.0, abs=1.0)

    def test_every_manifest_skill_has_an_artifact(self):
        data = _load("checklists_v2/manifest.json")
        for entry in data["skills"].values():
            artifact = REPO / entry["compiled_path"]
            assert artifact.exists(), f"missing compiled artifact: {entry['compiled_path']}"

    def test_compiled_artifacts_match_recorded_hash(self):
        data = _load("checklists_v2/manifest.json")
        bad = []
        for entry in data["skills"].values():
            artifact = REPO / entry["compiled_path"]
            if not artifact.exists():
                bad.append((entry["skill_id"], "missing"))
                continue
            if hashlib.sha256(artifact.read_bytes()).hexdigest() != entry["compiled_sha256"]:
                bad.append((entry["skill_id"], "edited"))
        assert not bad, f"compiled artifacts drifted from manifest: {bad}"

    @pytest.mark.xfail(
        strict=True,
        reason=(
            "Known source drift found during the 0.2.0 recompile audit: "
            "skills/tdd/SKILL.md was edited after the Aug-2026 benchmark run "
            "(recorded sha 1d0a1439..., on disk 93ea419b..., so its recorded "
            "16.63% reduction no longer reproduces), and skills/debugging-code/ "
            "is absent from the tree entirely. Both must be restored for the "
            "§8.2 per-skill token figures to be reproducible."
        ),
    )
    def test_source_hashes_still_match_disk(self):
        """Guards the drift found during the 0.2.0 recompile audit.

        A skill edited after the benchmark invalidates its recorded token
        reduction, so this asserts provenance instead of trusting the number.
        """
        data = _load("checklists_v2/manifest.json")
        drifted = []
        for entry in data["skills"].values():
            src = REPO / entry["source_path"]
            if not src.exists():
                drifted.append((entry["skill_id"], "missing"))
                continue
            if hashlib.sha256(src.read_bytes()).hexdigest() != entry["source_sha256"]:
                drifted.append((entry["skill_id"], "edited"))
        assert not drifted, (
            "SKILL.md sources drifted after compilation; the §8.2 token figures "
            f"are no longer reproducible for: {drifted}"
        )


class TestAblationNoiseFloor:
    """§8.4 — test-retest noise floor from byte-identical prompts."""

    def test_six_identical_prompt_runs_for_tdd_a2(self):
        """Finding 4 claim 1: 0/6 runs reach 17+, replicated at small n."""
        data = _load("ablation_results.json")
        runs = data["runs"] if isinstance(data, dict) and "runs" in data else data
        tdd = [
            r for r in runs
            if r.get("task_id", "").startswith("test-tdd")
            and r.get("condition") == "a2_no_examples"
        ]
        assert len(tdd) == 6, f"paper states tdd-A2 at n=6, archive holds {len(tdd)}"