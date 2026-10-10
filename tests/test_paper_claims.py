"""Claim-integrity tests: the manuscript's numbers must match the archived data.

Scope and intent
----------------
This file exists for one reason: to stop `paper/MANUSCRIPT.md` from silently
driving apart from the evidence behind it. Every test here loads an archived
artefact and asserts a number the manuscript quotes. If a re-run, a compiler
change, or an accidental edit moves a result, the suite fails instead of the
paper quietly going stale.

These are not unit tests of the codebase. Arithmetic on hard-coded constants is
deliberately *not* asserted here — such tests pass whether or not the underlying
data agrees, and two of them were removed for exactly that reason. Anything that
can be recomputed from an artefact is recomputed; anything that cannot is not
claimed at all.

Deliberately excluded:

* `tests/test_rate_limiter.py` and `tests/test_project.py` cover build tooling
  unrelated to this research artefact.
* Claims that are *derived* from other pinned claims (e.g. the K=20 token
  projection) are not asserted separately; the inputs are pinned instead, and
  the manuscript's arithmetic is checked by eye.
* Tests that merely assert a caveat string exists in the data were removed —
  they guard the existence of a note, not an invariant.

Count is intentionally small. Each test below guards a distinct claim.
"""

from __future__ import annotations

import json
import pathlib
import statistics as st
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
BENCH = REPO / "benchmarks"

CRITERIA = [
    "correctness", "completeness", "maintainability", "architecture",
    "security", "reasoning_quality", "instruction_adherence",
]


def _load(name: str):
    path = BENCH / name
    if not path.exists():
        pytest.skip(f"archived artefact absent: {name}")
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def _scripts_on_path() -> None:
    scripts = str(REPO / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)


# ---------------------------------------------------------------------------
# §5, §8.1, §8.2 — the macro benchmark
# ---------------------------------------------------------------------------
class TestMacroBenchmark:
    """Table 1 and Table 3 of the manuscript."""

    MEANS = {
        "control": 24.49, "full": 25.17, "retrieved": 24.73,
        "checklist": 24.54, "checklist_v2": 24.96,
    }
    PROMPT_TOKENS = {
        "control": 144, "full": 2270, "retrieved": 430,
        "checklist": 663, "checklist_v2": 1590,
    }

    @staticmethod
    def _runs(data, field=None):
        for task in data["tasks"]:
            for arm, runs in task.get("strategy_runs", {}).items():
                for r in runs:
                    yield task, arm, (r if field is None else r.get(field))

    def test_counts_and_attrition(self):
        """§5: 18 tasks defined, 17 completed, 396 evaluations, 5 arms each."""
        data = _load("delivery_results_ieee.json")
        runs = list(self._runs(data))
        assert len(runs) == 396, "manuscript states N=396"

        contributing = [t for t in data["tasks"]
                        if any(t.get("strategy_runs", {}).values())]
        assert len(contributing) == 17, "manuscript states 17 of 18 tasks completed"

        # §5 names the dropout explicitly; assert the identity, not just a count.
        empty = [t["id"] for t in data["tasks"]
                 if not any(t.get("strategy_runs", {}).values())]
        assert empty == ["db-ratelimit-redis-ieee"]

        for task in data["tasks"]:
            assert set(task.get("strategy_runs", {})) == set(TestMacroBenchmark.MEANS), (
                f"{task['id']} does not carry all five delivery arms"
            )

    def test_arm_means_match_table_1(self):
        """§8.1: the five per-arm mean judge scores."""
        data = _load("delivery_results_ieee.json")
        by_arm: dict[str, list[int]] = {}
        for _, arm, score in self._runs(data, "judge_total"):
            by_arm.setdefault(arm, []).append(score)

        for arm, expected in TestMacroBenchmark.MEANS.items():
            scores = by_arm.get(arm, [])
            assert scores, f"arm {arm} absent from archive"
            mean = st.mean(scores)
            assert mean == pytest.approx(expected, abs=0.01), (
                f"{arm}: manuscript says {expected}, archive gives {mean:.2f}"
            )

        # Ordering claims the manuscript makes about these arms.
        assert by_arm["full"] and st.mean(by_arm["full"]) == max(
            st.mean(v) for v in by_arm.values()
        ), "manuscript treats `full` as the highest-scoring arm"

        def sd(xs):
            m = st.mean(xs)
            return (sum((x - m) ** 2 for x in xs) / (len(xs) - 1)) ** 0.5

        assert max(by_arm, key=lambda a: sd(by_arm[a])) == "checklist", (
            "manuscript attributes the highest variance to checklist_v1"
        )

    def test_prompt_token_means_match_table_3(self):
        """§8.2: the five per-arm prompt token means, and the 30% headline."""
        data = _load("delivery_results_ieee.json")
        by_arm: dict[str, list[int]] = {}
        for _, arm, n in self._runs(data, "input_tokens"):
            by_arm.setdefault(arm, []).append(n)

        for arm, expected in TestMacroBenchmark.PROMPT_TOKENS.items():
            mean = st.mean(by_arm[arm])
            assert mean == pytest.approx(expected, abs=1.0), (
                f"{arm}: manuscript says {expected}, archive gives {mean:.0f}"
            )

        # The 30% / 680-token headline, derived from the archive rather than
        # restated as arithmetic on constants.
        full = st.mean(by_arm["full"])
        v2 = st.mean(by_arm["checklist_v2"])
        assert 100 * (full - v2) / full == pytest.approx(30.0, abs=0.5)
        assert full - v2 == pytest.approx(680, abs=5)


# ---------------------------------------------------------------------------
# §7.1 — compiler provenance
# ---------------------------------------------------------------------------
class TestCompilerProvenance:
    """The compiled artefacts the paper's token figures depend on."""

    def test_artifacts_exist_and_match_their_recorded_hashes(self):
        """Each manifest entry's artefact is present and unmodified."""
        import hashlib

        data = _load("checklists_v2/manifest.json")
        assert data["aggregate_token_reduction_pct"] == pytest.approx(30.0, abs=1.0)

        bad = []
        for entry in data["skills"].values():
            artefact = REPO / entry["compiled_path"]
            if not artefact.exists():
                bad.append((entry["skill_id"], "missing"))
            elif hashlib.sha256(artefact.read_bytes()).hexdigest() != entry["compiled_sha256"]:
                bad.append((entry["skill_id"], "edited"))
        assert not bad, f"compiled artefacts drifted from the manifest: {bad}"

    @pytest.mark.xfail(
        strict=True,
        reason=(
            "skills/tdd/SKILL.md was edited after the 2026-08-29 run (recorded sha "
            "1d0a1439..., on disk 93ea419b...). The benchmark-time source predates "
            "the repository's initial commit and only the compiled artefact survives; "
            "skills/tdd/SKILL.benchmark-time.md reproduces that artefact byte-for-byte "
            "but no file on disk matches the recorded *source* hash. See "
            "skills/RECOVERY.md."
        ),
    )
    def test_source_hashes_still_match_disk(self):
        data = _load("checklists_v2/manifest.json")
        drifted = []
        for entry in data["skills"].values():
            src = REPO / entry["source_path"]
            if not src.exists():
                drifted.append((entry["skill_id"], "missing"))
            elif hashlib_sha(src) != entry["source_sha256"]:
                drifted.append((entry["skill_id"], "edited"))
        assert not drifted, f"SKILL.md sources drifted after compilation: {drifted}"


def hashlib_sha(path: pathlib.Path) -> str:
    import hashlib
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# §8.4 — component ablation and the noise floor
# ---------------------------------------------------------------------------
class TestAblation:
    """§8.4: the TDD exceeder is the manuscript's one robust RQ4 claim."""

    def test_tdd_a2_replication_and_noise_floor_inputs(self):
        data = _load("ablation_results.json")
        runs = data["runs"] if isinstance(data, dict) and "runs" in data else data
        assert len(runs) == 69, "§7.5 / abstract state 69 ablation runs"

        tdd_a2 = [r for r in runs
                  if r.get("task_id", "").startswith("test-tdd")
                  and r.get("condition") == "a2_no_examples"]
        assert len(tdd_a2) == 6, "manuscript states tdd-A2 at n=6"


# ---------------------------------------------------------------------------
# §9 — judge position bias and statistical power
# ---------------------------------------------------------------------------
class TestJudgeInstrument:
    """§9: the disclosed instrument flaws that bound what the paper can claim."""

    @staticmethod
    def _analysis():
        _scripts_on_path()
        from analyze_position_bias import correct, load_rows, position_effects

        rows = load_rows()
        effects = position_effects(rows)
        corrected = {}
        for _, arm, pos, value in rows:
            corrected.setdefault(arm, []).append(value - effects[pos])
        return rows, effects, corrected

    def test_position_bias_is_large_and_significant(self):
        """§9: slot A/D effects exceed every treatment effect, and are real."""
        from scipy import stats

        rows, effects, _ = TestJudgeInstrument._analysis()
        assert effects["A"] == pytest.approx(2.08, abs=0.01)
        assert effects["D"] == pytest.approx(-1.58, abs=0.01)
        # the A-to-D spread must exceed the paper's headline treatment effect
        assert effects["A"] - effects["D"] > 0.21 * 10

        by_pos: dict[str, list[float]] = {}
        for _, _, pos, value in rows:
            by_pos.setdefault(pos, []).append(value)
        _, p_anova = stats.f_oneway(*[by_pos[k] for k in sorted(by_pos)])
        assert p_anova < 0.01, f"position bias should be significant; got p={p_anova:.4f}"

    def test_position_correction_preserves_every_conclusion(self):
        """The null in Finding 1 must survive removing the bias."""
        from scipy import stats

        _, _, corrected = TestJudgeInstrument._analysis()
        gap = st.mean(corrected["full"]) - st.mean(corrected["checklist_v2"])
        assert abs(gap) < 0.21, (
            f"corrected full-v2 gap widened to {gap:+.3f}; manuscript reports 0.21"
        )
        for arm in ("full", "retrieved", "checklist", "checklist_v2"):
            _, p = stats.ttest_ind(corrected[arm], corrected["control"], equal_var=False)
            assert p > 0.05, (
                f"{arm} now significantly beats control after correction (p={p:.3f})"
            )


# ---------------------------------------------------------------------------
# §8.7 — routing
# ---------------------------------------------------------------------------
class TestRouting:
    """The corrected routing study and its catalogue preconditions."""

    @staticmethod
    def _rows():
        return _load("router_level1_results.json")["task_runs"]

    @staticmethod
    def _scored():
        return [r for r in TestRouting._rows() if not r["freebie"]]

    def test_gold_labels_are_canonical_and_routable(self):
        rows = TestRouting._rows()
        gold = {r["task_id"]: r["gold"] for r in rows}
        assert gold["sre-node-leak-ieee"] == "systematic-debugging"
        assert gold["qa-ratelimiter-tdd-ieee"] == "tdd"

        index = json.loads((REPO / "skills_canonical.json").read_text(encoding="utf-8"))["skills"]
        missing = [r["gold"] for r in rows if r["gold"] not in index]
        assert not missing, f"unroutable gold labels: {missing}"

    def test_catalogue_is_de_duplicated_and_de_leaked(self):
        """Two structural invariants the corrected study depends on."""
        import numpy as np

        if not (REPO / "skills_embeddings.npy").exists():
            pytest.skip("embedding cache not built")

        canonical = json.loads((REPO / "skills_canonical.json").read_text(encoding="utf-8"))
        vectors = np.load(REPO / "skills_embeddings.npy")
        manifest = json.loads((REPO / "skills_manifest.json").read_text(encoding="utf-8"))["skills"]

        assert vectors.shape[0] == len(manifest) == len(canonical["skills"])
        # absorbed duplicates must not be routable
        assert not (set(canonical["collapsed"]) & set(canonical["skills"]))
        # and no two routable entries may embed identically
        sims = vectors @ vectors.T
        np.fill_diagonal(sims, -1.0)
        assert float(sims.max()) < 0.99, "identical routable entries remain"
        # documents must not embed the skill name (the original leak)
        leaky = [e["name"] for e in manifest
                 if e.get("rendered_text", "").startswith(e["name"] + ":")]
        assert not leaky, f"name-leaking vectors: {leaky[:5]}"

    def test_reranking_is_a_net_loss(self):
        """§8.7-Finding 6: reranking lowers Top-1 and the lexical baseline wins."""
        scored = TestRouting._scored()
        stage1 = sum(1 for r in scored if r["two_stage_top5"][0] == r["gold"])
        reranked = sum(1 for r in scored if r["two_stage_top1_match"])
        lexical = sum(1 for r in scored if r["tfidf_top1_match"])

        assert reranked < stage1, "reranking should lower Top-1 vs Stage 1 alone"
        assert lexical >= stage1, "lexical retrieval should beat dense retrieval"
        assert lexical > 0, "the real TF-IDF baseline must not regress to zero"

    def test_option_truncation_stays_fixed(self):
        """The 2/17 regression must not silently return."""
        rows = [r for r in TestRouting._rows() if r.get("latency")]
        clips = [r["latency"].get("option_clip_words") for r in rows]
        assert all(c is not None for c in clips)
        assert not [c for c in clips if c <= 10], (
            "options are collapsing to the tight end of the clip ladder again"
        )


class TestUnionShortlist:
    """§8.7-D: the union lifts recall; the reranker then loses it."""

    def test_union_lifts_recall_at_low_candidate_cost(self):
        s = _load("union_shortlist_results.json")["summary"]
        assert s["recall_at_k"]["union"] > s["recall_at_k"]["tfidf"]
        assert s["recall_at_k"]["union"] > s["recall_at_k"]["dense"]
        assert s["mean_union_size"] < 2 * s["k_per_retriever"]

    def test_reranker_forfeits_the_union_ceiling(self):
        s = _load("union_shortlist_results.json")["summary"]
        if not _load("union_shortlist_results.json")["metadata"]["rerank_enabled"]:
            pytest.skip("rerank disabled in the recorded run")
        assert s["rerank_top1"] < s["oracle_ceiling"]
        assert s["rerank_recall_lost"] > 0


class TestDirectChoice:
    """§8.7-F: no retrieval at all reaches the union oracle ceiling."""

    def test_direct_choice_matches_the_oracle_ceiling(self):
        runs = _load("direct_choice_results.json")["runs"]
        ceiling = _load("union_shortlist_results.json")["summary"]["oracle_ceiling"]
        solved = len({r["task_id"] for r in runs if r["match"]})
        assert solved == ceiling, (
            f"direct choice solves {solved}, union oracle ceiling {ceiling}"
        )


# ---------------------------------------------------------------------------
# §8.2 — the withdrawn output-volume claim
# ---------------------------------------------------------------------------
class TestConfoundExperiment:
    """The retraction of Finding 2 rests on this paired experiment."""

    @staticmethod
    def _cells():
        pairs: dict[tuple[str, int], dict[str, int]] = {}
        for r in _load("confound_results.json")["runs"]:
            if r["ok"]:
                pairs.setdefault((r["task_id"], r["run"]), {})[r["condition"]] = r["output_tokens_est"]
        return [(v["v2_with_directive"], v["v2_no_directive"])
                for v in pairs.values() if len(v) == 2]

    def test_directive_explains_the_retracted_gap(self):
        """82% of Finding 2's +843 gap, and directionally consistent."""
        cells = TestConfoundExperiment._cells()
        assert cells, "no paired cells"

        deltas = [a - b for a, b in cells]
        assert st.mean(deltas) > 0, "the directive must increase output volume"
        assert sum(1 for d in deltas if d > 0) >= 0.7 * len(deltas), (
            "the directive effect should be mostly positive across paired cells"
        )
        archived_gap = 5431 - 4588  # Finding 2 / Table 3
        assert st.mean(deltas) > 0.5 * archived_gap, (
            "the retraction only stands if the directive explains most of the gap"
        )

    def test_the_two_conditions_differ_only_by_the_directive(self):
        """The confound is only identified if nothing else changed."""
        import json as _json

        _scripts_on_path()
        from run_confound_experiment import DEFAULT_TASKS, build_prompts

        task = {t["id"]: t for t in _json.loads(
            (REPO / "benchmarks" / "tasks_ieee.json").read_text(encoding="utf-8")
        )}[DEFAULT_TASKS[0]]
        compiled = REPO / "benchmarks" / "checklists_v2" / f"{task['skill']}.txt"
        if not compiled.exists():
            pytest.skip("compiled v2 artefact absent")

        p = build_prompts(task, "", compiled.read_text(encoding="utf-8"))
        with_d, without_d = p["v2_with_directive"], p["v2_no_directive"]
        assert with_d.startswith(without_d)
        assert with_d[len(without_d):].startswith("\n\n[INSTRUCTION]:")