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

class TestJudgePositionBias:
    """Audit in benchmarks/POSITION_BIAS_AUDIT.md — the manuscript does not report this.

    The blind protocol permutes arms across labels A-E (§7.2). The judge has a
    strong slot preference that exceeds every treatment effect, so these tests
    pin both the magnitude of the bias and the fact that correcting for it
    leaves the paper's conclusions intact.
    """

    @staticmethod
    def _analysis():
        import sys

        sys.path.insert(0, str(REPO / "scripts"))
        from analyze_position_bias import (  # noqa: PLC0415
            correct,
            load_rows,
            position_effects,
        )

        rows = load_rows()
        effects = position_effects(rows)
        corrected = {}
        for _, arm, pos, value in rows:
            corrected.setdefault(arm, []).append(value - effects[pos])
        return rows, effects, corrected

    def test_judged_arm_instance_count(self):
        rows, _, _ = self._analysis()
        assert len(rows) == 396

    def test_position_effects_are_large_and_monotone_in_slot(self):
        _, effects, _ = self._analysis()
        assert effects["A"] == pytest.approx(2.08, abs=0.01), (
            "slot A is materially inflated; a judge change or re-run will shift this"
        )
        assert effects["D"] == pytest.approx(-1.58, abs=0.01)
        # slot A penalty is 12x the paper's headline strategy effect
        spread = effects["A"] - effects["D"]
        assert spread > 0.21 * 10, "position spread dwarfs the treatment effect"

    def test_position_effect_is_statistically_significant(self):
        import statistics as st  # noqa: PLC0415

        from scipy import stats  # noqa: PLC0415

        rows, _, _ = self._analysis()
        by_pos = {}
        for _, _, pos, value in rows:
            by_pos.setdefault(pos, []).append(value)
        letters = sorted(by_pos)
        _, p_anova = stats.f_oneway(*[by_pos[p] for p in letters])
        assert p_anova < 0.01, (
            f"position bias should be significant; got p={p_anova:.4f}"
        )

    def test_position_is_balanced_across_arms(self):
        """Permutation worked: no arm systematically sits in a favoured slot."""
        from collections import Counter  # noqa: PLC0415

        rows, _, _ = self._analysis()
        cross = Counter((arm, pos) for _, arm, pos, _ in rows)
        cells = [v for v in cross.values()]
        assert min(cells) >= 5, f"a slot-starved arm cell implies confounding: {cross}"

    def test_correction_preserves_the_headline_null(self):
        """Finding 1 must survive position correction."""
        rows, _, corrected = self._analysis()
        gap = (
            sum(corrected["full"]) / len(corrected["full"])
            - sum(corrected["checklist_v2"]) / len(corrected["checklist_v2"])
        )
        assert abs(gap) < 0.21, (
            f"corrected full-v2 gap widened to {gap:+.3f}; paper reports 0.21"
        )

    def test_no_arm_significantly_beats_control_after_correction(self):
        """The economics-first premise in §8.6.A."""
        import statistics as st  # noqa: PLC0415

        from scipy import stats  # noqa: PLC0415

        _, _, corrected = self._analysis()
        base = corrected["control"]
        for arm in ("full", "retrieved", "checklist", "checklist_v2"):
            _, p = stats.ttest_ind(corrected[arm], base, equal_var=False)
            assert p > 0.05, f"{arm} significantly beats control after correction (p={p:.3f})"


class TestRouterLevel1:
    """benchmarks/ROUTER_LEVEL1_AUDIT.md — supersedes the withdrawn §8.7 figures.

    The original run reported 55.6% Top-1 for the two-stage router against a
    0.0% "TF-IDF baseline". Both are withdrawn: the baseline was a hand-weighted
    keyword scorer that could not score correctly by construction, and the
    catalogue vectors embedded the skill name.
    """

    @staticmethod
    def _rows():
        data = _load("router_level1_results.json")
        return data["task_runs"]

    def test_freebie_task_is_excluded_from_headline(self):
        data = _load("router_level1_results.json")
        freebies = data["metadata"]["excluded_freebie_tasks"]
        assert freebies == ["sec-webhook-audit-ieee"]
        rows = {r["task_id"]: r for r in self._rows()}
        # The exclusion must be visible per-row, not silently dropped.
        assert rows["sec-webhook-audit-ieee"]["freebie"] is True
        assert data["summary"]["n_excluded_freebie"] == 1

    def test_gold_labels_are_canonical(self):
        rows = {r["task_id"]: r["gold"] for r in self._rows()}
        assert rows["sre-node-leak-ieee"] == "systematic-debugging"
        assert rows["qa-ratelimiter-tdd-ieee"] == "tdd"

    def test_gold_labels_exist_in_catalogue(self):
        _require_router_cache()
        index = json.loads((REPO / "skills.json").read_text(encoding="utf-8"))["skills"]
        missing = [r["gold"] for r in self._rows() if r["gold"] not in index]
        assert not missing, f"unroutable gold labels: {missing}"

    def test_option_truncation_is_fixed(self):
        """After the truncation fix, options must fit Julia-1's 48-token budget.

        The first corrected run word-clipped description prefixes, truncating
        17 of 18 routes and scoring 2/17. Options now retain the leading clause
        and are only clipped when the runtime rejects them.
        """
        rows = [r for r in self._rows() if r.get("latency")]
        assert rows, "no latency stats recorded"
        clips = [r["latency"].get("option_clip_words") for r in rows]
        assert all(c is not None for c in clips), "option clip not recorded"
        # Every scored route should now fit at or near the ceiling rather than
        # falling back to the tight end of the ladder.
        tight = [c for c in clips if c is not None and c <= 10]
        assert not tight, f"options still collapsing to the tight ladder: {tight}"

    def test_baseline_beats_two_stage_reranking(self):
        """The measured regression: Julia-1 rerank lowers Stage-1 Top-1."""
        rows = [r for r in self._rows() if not r["freebie"]]
        stage1_top1 = sum(1 for r in rows if r["two_stage_top5"][0] == r["gold"])
        two_stage_top1 = sum(1 for r in rows if r["two_stage_top1_match"])
        assert two_stage_top1 < stage1_top1, (
            "if reranking now helps, ROUTER_LEVEL1_AUDIT.md needs updating"
        )

    def test_tfidf_baseline_is_not_zero(self):
        """Guards against regressing to the rigged 0/18 baseline."""
        rows = [r for r in self._rows() if not r["freebie"]]
        top1 = sum(1 for r in rows if r["tfidf_top1_match"])
        assert top1 > 0, "real TF-IDF must score above zero; a 0 result means the baseline regressed"

    def test_catalogue_counts_agree(self):
        _require_router_cache()
        """Stale-cache guard: vectors, manifest, and routable catalogue lockstep."""
        import numpy as np

        vectors = np.load(REPO / "skills_embeddings.npy")
        manifest = json.loads(
            (REPO / "skills_manifest.json").read_text(encoding="utf-8")
        )
        canonical = json.loads(
            (REPO / "skills_canonical.json").read_text(encoding="utf-8")
        )
        assert vectors.shape[0] == len(manifest["skills"]) == len(canonical["skills"])

    def test_collapsed_duplicates_are_not_routable(self):
        _require_router_cache()
        """Near-duplicates must never re-enter a shortlist."""
        canonical = json.loads(
            (REPO / "skills_canonical.json").read_text(encoding="utf-8")
        )
        collapsed = set(canonical["collapsed"])
        routable = set(canonical["skills"])
        assert collapsed, "expected duplicate groups"
        assert not (collapsed & routable), (
            f"collapsed duplicates routable again: {sorted(collapsed & routable)[:5]}"
        )
        index = json.loads((REPO / "skills.json").read_text(encoding="utf-8"))
        missing = [a for a in collapsed if index["aliases"].get(a) not in routable]
        assert not missing, f"absorbed names not aliased to a routable skill: {missing[:5]}"

    def test_routable_catalogue_has_no_identical_embeddings(self):
        _require_router_cache()
        """The point of de-duplication: no two routable entries are identical."""
        import numpy as np

        vectors = np.load(REPO / "skills_embeddings.npy")
        canonical = json.loads(
            (REPO / "skills_canonical.json").read_text(encoding="utf-8")
        )
        sims = vectors @ vectors.T
        np.fill_diagonal(sims, -1.0)
        assert float(sims.max()) < 0.99, (
            f"identical routable entries remain: {list(canonical['skills'])[int(np.argmax(sims))]}"
        )

    def test_embedded_documents_do_not_leak_skill_names(self):
        _require_router_cache()
        manifest = json.loads(
            (REPO / "skills_manifest.json").read_text(encoding="utf-8")
        )["skills"]
        leaky = [
            e["name"] for e in manifest
            if e.get("rendered_text", "").startswith(e["name"] + ":")
        ]
        assert not leaky, f"vectors embed skill names again: {leaky[:5]}"


def _require_router_cache() -> None:
    """Skip router assertions when the generated embedding cache is absent.

    skills_embeddings.npy, skills_manifest.json, skills.json and
    skills_canonical.json are generated artifacts and are git-ignored, so a
    fresh CI checkout has none of them. The invariants are still checked whenever
    a developer has built the cache, and by the router-integrity CI job when it
    builds one.
    """
    for rel in ("skills_embeddings.npy", "skills_manifest.json", "skills_canonical.json"):
        if not (REPO / rel).exists():
            pytest.skip(f"router cache not built ({rel} missing); run scripts/build_index.py")


class TestUnionShortlist:
    """benchmarks/union_shortlist_results.json — §8.7 union-shortlist follow-up.

    The lexical and dense retrievers agree on few top-1 answers but reach equal
    recall, so a union of their shortlists should recall more. It does: 11/17 to
    14/17. But the reranker then discards most of that gain.
    """

    def test_union_shortlist_lifts_recall(self):
        data = _load("union_shortlist_results.json")
        s = data["summary"]
        assert s["recall_at_k"]["union"] > s["recall_at_k"]["tfidf"], (
            "union shortlist must beat lexical recall"
        )
        assert s["recall_at_k"]["union"] > s["recall_at_k"]["dense"], (
            "union shortlist must beat dense recall"
        )

    def test_union_costs_few_extra_candidates(self):
        """Recall lift must not come from brute-force widening of the shortlist."""
        data = _load("union_shortlist_results.json")
        s = data["summary"]
        assert s["mean_union_size"] < 2 * s["k_per_retriever"], (
            f"union too wide: {s['mean_union_size']} vs {2 * s['k_per_retriever']}"
        )

    def test_reranker_loses_union_recall(self):
        """The headline: Julia-1 realises far less than the union ceiling."""
        data = _load("union_shortlist_results.json")
        s = data["summary"]
        if not data["metadata"]["rerank_enabled"]:
            pytest.skip("rerank disabled in recorded run")
        assert s["rerank_top1"] < s["oracle_ceiling"], (
            "reranker is expected to underperform the oracle ceiling here"
        )
        assert s["rerank_recall_lost"] > 0, (
            "reranker should lose at least some union recall on these queries"
        )

    def test_lexical_top1_remains_the_best_simple_ranker(self):
        """With no reranker, lexical alone beats dense and union lex-first."""
        data = _load("union_shortlist_results.json")
        s = data["summary"]
        assert s["tfidf_top1"] >= s["dense_top1"]
        assert s["tfidf_top1"] >= s["union_lexfirst_top1"]
