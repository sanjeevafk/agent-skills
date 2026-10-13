"""Pin the manuscript's headline power analysis to the archived runs.

Why this file exists
--------------------
The three numbers the central argument rests on -- the test-retest floor
($\\sigma$), the paired-difference SD ($\\sigma_d$), and the minimum detectable
effect (MDE) -- were previously quoted in the manuscript with no code that
produced them and no test that asserted them. An earlier draft gave
$\\sigma = 6.09$ from "42 runs on byte-identical prompts", $\\sigma_d = 7.87$
over "78 pairs", and an MDE of 2.53. No run subset of size 42 exists in the
archive; those figures could not be reproduced by any estimator, and the
nearest one (the raw SD of all 396 scores, 6.03) is *total* variance, which
includes between-task difficulty and is the wrong quantity for a test-retest
floor.

That is the same defect this paper criticises in other work: a number that no
code produces cannot be checked. These tests close that gap. They assert the
values now printed in `paper/MANUSCRIPT_SKILL.md` against
`scripts/verify_noise_floor.py`, so if a re-run moves them, the suite fails
instead of the paper quietly going stale.

The assertions are deliberately tight ($\\pm 0.01$) because every one of these
figures is a deterministic function of a frozen JSON artefact. There is no
legitimate source of drift other than a change to that artefact, which should
fail here loudly.
"""

from __future__ import annotations

import pathlib
import re
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
BENCH = REPO / "benchmarks"


def _scripts_on_path() -> None:
    scripts = str(REPO / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)


@pytest.fixture(scope="module")
def report():
    _scripts_on_path()
    from verify_noise_floor import _load, paired_difference, test_retest_floor

    data = _load()
    return {
        "floor": test_retest_floor(data),
        "contrast": paired_difference(data, "full", "checklist_v2"),
    }

MANUSCRIPT_CANDIDATES = ("MANUSCRIPT_SKILL_ANON.md", "MANUSCRIPT_SKILL.md")


def manuscript_text() -> str:
    """Return the manuscript source available in this checkout.

    The anonymised source is tracked in the public repository precisely so these
    checks execute rather than skip; a reviewer checking the artifact should
    not have to wonder whether a check ran. The camera-ready is git-ignored
    (it names the author) and is used only when a local checkout has it.
    """
    for name in MANUSCRIPT_CANDIDATES:
        path = REPO / "paper" / name
        if path.exists():
            return path.read_text(encoding="utf-8")
    pytest.skip("no manuscript source present in this checkout")


def assert_no_identity_leak(text: str) -> None:
    for token in ("Sanjeev", "Saveetha", "Department of Computer", "sanjeevafk"):
        assert token not in text, f"anonymised source leaks {token!r}"


class TestNoiseFloor:
    """§5.1: sigma, and the machinery that produces it."""

    def test_sigma_matches_manuscript(self, report):
        """Manuscript: sigma = 5.37."""
        assert report["floor"]["sigma"] == pytest.approx(5.37, abs=0.01), (
            f"manuscript says 5.37, archive gives "
            f"{report['floor']['sigma']:.3f}"
        )

    def test_floor_is_computed_from_the_whole_archive(self, report):
        """The estimator must consume all 396 runs, not a hand-picked subset."""
        floor = report["floor"]
        assert floor["n_runs"] == 396
        assert floor["n_cells"] == 85
        assert floor["df"] == 311

    def test_floor_is_not_total_variance(self, report):
        """Guard the specific error: total SD overstates a test-retest floor.

        The raw SD of all 396 scores is 6.03. Using it as the floor would fold
        genuine between-task difficulty into 'judge noise' and inflate the MDE
        for the wrong reason. The within-cell estimator must be strictly lower.
        """
        import json
        import statistics as st

        data = json.loads((BENCH / "delivery_results_ieee.json").read_text())
        scores = [
            run["judge_total"]
            for task in data["tasks"]
            for runs in task.get("strategy_runs", {}).values()
            for run in runs
        ]
        total_sd = st.stdev(scores)
        assert total_sd == pytest.approx(6.03, abs=0.01)
        assert report["floor"]["sigma"] < total_sd, (
            "within-cell floor must be below total variance"
        )


class TestPowerAnalysis:
    """§2.2 and §5.1: sigma_d, the MDE, and the required sample size."""

    def test_sigma_d_matches_manuscript(self, report):
        """Manuscript: sigma_d = 3.76 over 17 task pairs."""
        contrast = report["contrast"]
        assert contrast["sigma_d"] == pytest.approx(3.76, abs=0.01)
        assert contrast["n_pairs"] == 17

    def test_pairing_unit_is_the_task_not_the_run(self, report):
        """§4.3 blocks on task; sigma_d must therefore be over task pairs.

        An earlier draft asserted '78 pairs', which is neither the number of
        tasks (17) nor the number of runs in one arm (80). Pin the identity.
        """
        assert report["contrast"]["n_pairs"] != 78
        assert report["contrast"]["n_pairs"] == 17

    def test_mde_matches_manuscript(self, report):
        """Manuscript: exact (noncentral-t) MDE = 2.72 points, 7.8% of scale."""
        contrast = report["contrast"]
        assert contrast["mde_exact_nct"] == pytest.approx(2.72, abs=0.01)
        assert contrast["mde"] == pytest.approx(2.72, abs=0.01)
        assert contrast["mde_pct_of_scale"] == pytest.approx(7.8, abs=0.1)

    def test_normal_approximation_is_reported_and_slightly_smaller(self, report):
        """The paper discloses the normal approximation as well.

        At n = 17 the uncertainty in sigma_d is material, so the exact
        noncentral-t threshold must exceed the normal approximation. Reporting
        both is required; silently shipping only the approximation understates
        the threshold.
        """
        contrast = report["contrast"]
        assert contrast["mde_normal_approx"] == pytest.approx(2.55, abs=0.01)
        assert contrast["mde_exact_nct"] > contrast["mde_normal_approx"]
        # known shortfall at n = 17, for both forms of MDE
        assert (contrast["mde_exact_nct"] / contrast["mde_normal_approx"]
                == pytest.approx(1.065, abs=0.01))

    def test_mde_uses_the_paired_form_not_the_two_sample_form(self, report):
        """The formula must be the paired one: MDE = (za+zb) * sd_d / sqrt(n).

        The two-sample form carries a sqrt(2) for the standard error of a
        difference of independent means. A paired design conditions on the
        task, so its standard error is sd_d / sqrt(n) and no sqrt(2) appears.
        Using the two-sample form with a paired sd_d overstates the threshold
        by exactly sqrt(2) -- which is what a first correction of this paper
        did, and what review caught.
        """
        import math

        contrast = report["contrast"]
        z = 2.8016  # z_{0.975} + z_{0.80}
        sd_d, n = contrast["sigma_d"], contrast["n_pairs"]
        assert contrast["mde_normal_approx"] == pytest.approx(
            z * sd_d / math.sqrt(n), abs=0.01)
        two_sample = z * sd_d * math.sqrt(2 / n)
        assert contrast["mde_normal_approx"] < two_sample
        assert two_sample / contrast["mde_normal_approx"] == pytest.approx(
            math.sqrt(2), abs=0.01)

    def test_mde_is_internally_consistent_with_required_n(self, report):
        """MDE at n = required_n must reproduce the observed gap exactly.

        This is the invariant that the mixed formulas violated: the required-n
        expression was paired while the MDE expression was two-sample, so the
        two could never agree. Asserting the agreement catches that class of
        error without depending on either constant.
        """
        import math

        contrast = report["contrast"]
        z = 2.8016
        sd_d = contrast["sigma_d"]
        n_req = contrast["pairs_needed_for_observed_gap"]
        mde_at_nreq = z * sd_d / math.sqrt(n_req)  # normal form, paired SE
        assert mde_at_nreq == pytest.approx(abs(contrast["observed_gap"]), abs=0.002)

    def test_observed_gap_matches_manuscript(self, report):
        """Manuscript: task-blocked mean difference +0.275, t = 0.30, p = 0.7672."""
        contrast = report["contrast"]
        assert contrast["observed_gap"] == pytest.approx(0.275, abs=0.005)
        assert contrast["t_statistic"] == pytest.approx(0.30, abs=0.01)
        assert contrast["p_value"] == pytest.approx(0.7672, abs=0.001)

    def test_gap_is_a_small_fraction_of_the_mde(self, report):
        """The paper's actual claim: the null is detection-limited.

        This is the assertion that carries the argument, so it is stated as a
        property rather than as two independent constants. If a future re-run
        moves the gap above the threshold, this fails and the paper's claim
        must be revisited.
        """
        contrast = report["contrast"]
        assert contrast["gap_pct_of_mde"] < 15.0, (
            f"gap is now {contrast['gap_pct_of_mde']:.1f}% of MDE; the "
            f"detection-limited framing no longer holds"
        )
        assert contrast["p_value"] > 0.05

    def test_required_sample_size_matches_manuscript(self, report):
        """Manuscript: ~1,500 task pairs (earlier draft said ~3,700)."""
        contrast = report["contrast"]
        assert contrast["pairs_needed_for_observed_gap"] == pytest.approx(
            1473, abs=25
        )


class TestManuscriptAgreement:
    """The manuscript text must quote the values the script computes."""

    @staticmethod
    def _manuscript() -> str:
        return manuscript_text()

    @staticmethod
    def _outside_disclosure_section(text: str) -> list[tuple[int, str]]:
        """Lines outside the section whose purpose is disclosing the correction.

        The manuscript has a dedicated section ("What We Could Not Reproduce")
        whose entire subject is the withdrawn figures. Quoting them there is
        required; quoting them anywhere else as if they were current would be
        the defect this suite exists to catch.
        """
        lines = text.splitlines()
        start = next(
            (i for i, l in enumerate(lines)
             if l.startswith("## 7.") and "Reproduce" in l),
            None,
        )
        if start is None:
            pytest.skip("disclosure section not found; nothing to scope against")
        end = next(
            (i for i in range(start + 1, len(lines))
             if lines[i].startswith("## 8.")),
            len(lines),
        )
        return [
            (i + 1, l) for i, l in enumerate(lines)
            if not (start <= i < end)
        ]

    def test_manuscript_quotes_the_current_sigma(self):
        text = self._manuscript()
        assert "5.37" in text, "manuscript no longer quotes sigma = 5.37"

    def test_manuscript_quotes_the_current_mde(self):
        text = self._manuscript()
        assert "2.72" in text, "manuscript no longer quotes MDE = 2.72"

    def test_withdrawn_sigma_appears_only_as_a_disclosed_correction(self):
        offenders = [
            (n, line) for n, line in self._outside_disclosure_section(
                self._manuscript()
            )
            # \b before the number avoids matching a suffix such as the
            # "2.53" inside "22.53" in the replication table.
            if re.search(r"(?<![\d.])6\.09(?![\d])", line)
            and "earlier draft" not in line.lower()
        ]
        assert not offenders, (
            "withdrawn sigma = 6.09 quoted outside the disclosure section: "
            + "; ".join(f"line {n}: {line[:70]}" for n, line in offenders)
        )

    def test_withdrawn_mde_appears_only_as_a_disclosed_correction(self):
        offenders = [
            (n, line) for n, line in self._outside_disclosure_section(
                self._manuscript()
            )
            if re.search(r"(?<![\d.])2\.53(?![\d])", line)
            and "earlier draft" not in line.lower()
        ]
        assert not offenders, (
            "withdrawn MDE = 2.53 quoted outside the disclosure section: "
            + "; ".join(f"line {n}: {line[:70]}" for n, line in offenders)
        )

class TestPositionBiasBlocks:
    """§5.6: position bias analysed with the judging window as a block.

    The blind protocol scores all five arms of a task in one window, so the 396
    rows are clustered and a pooled ANOVA is anti-conservative. These tests pin
    the block-aware statistics the manuscript quotes, and assert that the
    withdrawn pooled statistic is not what we report.
    """

    @pytest.fixture(scope="class")
    @classmethod
    def block_report(self):
        _scripts_on_path()
        from analyze_position_blocks import centre, friedman, load_windows, stats
        windows = load_windows()
        centred = centre(windows)
        return {
            "windows": windows, "centred": centred,
            "obs": stats(centred),
            "friedman": friedman(centred),
        }

    def test_windows_are_recoverable_from_the_archive(self, block_report):
        """80 windows, 396 scored rows: the clustering is recoverable."""
        wins = block_report["windows"]
        assert len(wins) == 80, f"expected 80 judging windows, got {len(wins)}"
        assert sum(len(i) for _, i in wins) == 396

    def test_block_aware_spread_matches_manuscript(self, block_report):
        """Manuscript: window-centred spread = 3.63 points."""
        assert block_report["obs"]["spread"] == pytest.approx(3.63, abs=0.01)
        assert block_report["obs"]["A_minus_D"] == pytest.approx(3.63, abs=0.01)

    def test_position_means_match_manuscript(self, block_report):
        pm = block_report["obs"]["position_means"]
        assert pm["A"] == pytest.approx(2.06, abs=0.01)
        assert pm["D"] == pytest.approx(-1.57, abs=0.01)

    def test_centring_does_not_inflate_the_effect(self, block_report):
        """Block-aware centring must not manufacture the effect.

        The uncentred spread (3.66) is the pooled figure; centring can only
        remove between-window variance, so it must be the smaller of the two.
        """
        import sys as _sys
        from analyze_position_blocks import stats as _stats
        raw = _stats([items for _, items in block_report["windows"]])
        assert block_report["obs"]["spread"] < raw["spread"]
        assert raw["spread"] == pytest.approx(3.66, abs=0.01)

    def test_rank_based_test_is_reported_as_not_significant(self, block_report):
        """The paper must report the Friedman result too, not omit it.

        Bias in score magnitude (significant) and in within-window ordering
        (not significant) are different findings; reporting only the first
        would overstate what the bias does.
        """
        assert block_report["friedman"]["p"] > 0.05
        assert block_report["friedman"]["statistic"] == pytest.approx(4.84, abs=0.02)

    def test_manuscript_reports_both_position_tests(self):
        text = manuscript_text()
        assert "0.000014" in text, "block-aware ANOVA p-value not reported"
        assert "0.304" in text, "Friedman p-value not reported"
        assert "7.1794" in text, "block-aware F not reported"
        assert "within** each window" in text or "within**" in text, \
            "within-window permutation not described"


class TestAttritionAccounting:
    """§4.3 / §8.4: the retention and truncation counts must reconcile.

    These exist because this account was wrong twice -- once from reading file
    lengths by list position, once from over-correcting and calling all losses
    stub records. The numbers below are the reconciled set.
    """

    @staticmethod
    def _partition(cap: int = 10000):
        import json
        root = REPO / "benchmarks" / "raw_outputs_ieee"
        data = json.loads(
            (REPO / "benchmarks" / "delivery_results_ieee.json").read_text())
        drop = "db-ratelimit-redis-ieee"
        judged_t = judged_s = 0
        dropped, scattered_t, scattered_s = [], [], []
        for task in data["tasks"]:
            d = root / task["id"]
            files = {}
            if d.is_dir():
                for f in d.glob("*.txt"):
                    arm = f.stem.rsplit("_run", 1)[0]
                    if arm == "judge_prompt":
                        continue
                    files[(arm, int(f.stem.rsplit("_run", 1)[1]))] = len(
                        f.read_text(errors="ignore"))
            if task["id"] == drop:
                dropped = sorted(files.values())
                continue
            keys = {(a, r["run"]) for a, rs in task.get("strategy_runs", {}).items()
                    for r in rs}
            for k in keys:
                if k in files:
                    judged_t += files[k] > cap
                    judged_s += files[k] <= cap
            for k, n in files.items():
                if k not in keys:
                    (scattered_t if n > cap else scattered_s).append(n)
        return {"dropped": dropped, "judged_t": judged_t, "judged_s": judged_s,
                "scattered_t": scattered_t, "scattered_s": scattered_s}

    def test_dropped_task_responses_are_all_executor_stubs(self):
        p = self._partition()
        assert len(p["dropped"]) == 25
        assert set(p["dropped"]) == {23}, (
            f"dropped-task responses should all be 23-char stubs, got "
            f"{sorted(set(p['dropped']))}")

    def test_scattered_losses_are_a_mix_not_all_stubs(self):
        """23 stub records AND 6 full-length responses.

        An earlier draft called all 29 ordinary-length; the over-correction
        called all 29 stubs. The truth is both, and §8.4's truncation share
        depends on the 6.
        """
        p = self._partition()
        n_stub = sum(1 for n in p["scattered_s"] if n <= 30)
        assert len(p["scattered_t"]) == 6, "6 scattered losses exceed the cap"
        assert n_stub == 23, f"expected 23 stub records, got {n_stub}"
        assert len(p["scattered_s"]) == 23
        assert len(p["scattered_t"]) + len(p["scattered_s"]) == 29

    def test_truncation_counts_reconcile(self):
        """The chain that must close: 425 = 348 + 77, and 396 = 342 + 54."""
        p = self._partition()
        assert p["judged_t"] == 342 and p["judged_s"] == 54
        assert p["judged_t"] + p["judged_s"] == 396
        total_long = p["judged_t"] + len(p["scattered_t"])
        total_short = p["judged_s"] + len(p["scattered_s"])
        assert total_long == 348 and total_short == 77
        assert total_long + total_short == 425

    def test_judged_truncation_share(self):
        """§8.4: 342 of 396 = 86.4% of judged responses were truncated."""
        p = self._partition()
        share = 100 * p["judged_t"] / (p["judged_t"] + p["judged_s"])
        assert share == pytest.approx(86.4, abs=0.05)

    def test_manuscript_states_the_reconciled_figures(self):
        # Collapse whitespace: the manuscript hard-wraps, so a phrase can
        # straddle a newline in the source.
        text = " ".join(manuscript_text().split())
        assert "342 (86.4%)" in text
        assert "348 (81.9%)" in text
        assert "48 are executor failures" in text, "attrition cause count not stated"
        assert "Six further attempts generated a full-length response" in text


class TestSqrtTwoFactor:
    """§7.2 / abstract: the error factor is sqrt(2), never 2."""

    @staticmethod
    def _manuscript():
        return manuscript_text()

    def test_the_factor_is_sqrt_two(self):
        import math
        import re

        text = self._manuscript()
        assert "overstates the threshold by exactly $\\sqrt{2}$" in text, \
            "sqrt(2) overstatement not stated in 7.2"
        # The mis-statement we must never reintroduce: "by a factor of 2"
        # or "by exactly 2" without the root.
        assert not re.search(r"overstat\w+ the threshold by (a factor of |exactly )2(?![.\d])",
                             text), "threshold overstatement stated as 2, not sqrt(2)"
        assert math.isclose(math.sqrt(2), 1.41421356, rel_tol=1e-6)

    def test_abstract_states_sqrt_two(self):
        text = self._manuscript()
        abstract = text.split("## Abstract")[1].split("**Keywords")[0]
        assert "by a factor of $\\sqrt{2}$" in abstract, \
            "abstract does not state the error factor as sqrt(2)"


class TestAnonymisedSourceIsTrackableAndClean:
    """The anonymised manuscript source is what makes these checks runnable.

    The camera-ready names the author and stays git-ignored; this file is
    tracked so a reviewer can execute the manuscript-agreement tests. That is
    only safe while it carries no identity, so it is asserted here.
    """

    def test_anonymised_source_exists(self):
        path = REPO / "paper" / "MANUSCRIPT_SKILL_ANON.md"
        assert path.exists(), (
            "paper/MANUSCRIPT_SKILL_ANON.md must be tracked so the "
            "manuscript-agreement tests run in a public checkout"
        )

    def test_anonymised_source_leaks_no_identity(self):
        assert_no_identity_leak(manuscript_text())

    def test_camera_ready_stays_ignored(self):
        """The identified manuscript must never enter the repository."""
        import subprocess
        r = subprocess.run(
            ["git", "check-ignore", "paper/MANUSCRIPT_SKILL.md"],
            cwd=REPO, capture_output=True, text=True)
        assert r.returncode == 0, (
            "paper/MANUSCRIPT_SKILL.md is no longer git-ignored; the camera-ready "
            "names the author and must not be committed"
        )

    def test_manuscript_agreement_checks_actually_run(self):
        """Guard against the silent-skip failure mode.

        An earlier review found these tests skipping in the public repository,
        so nothing verified the manuscript against the computed values. Assert
        that the resolver returns a non-empty source rather than skipping.
        """
        text = manuscript_text()
        assert len(text) > 1000, "manuscript source resolved but looks empty"
        assert "## Abstract" in text


class TestEveryQuotedStatisticReproduces:
    """Every number the paper quotes must be emitted by the artifact.

    The sign test was asserted in the manuscript while no script computed it,
    and the manuscript drifted ahead of the artifact for exactly this reason.
    This pins the paper's quoted values to the artifact's emitted values, so a
    statistic can no longer be reported without code behind it.
    """

    @staticmethod
    def _report():
        import json
        import subprocess
        r = subprocess.run(
            [sys.executable, str(REPO / "scripts" / "analyze_position_blocks.py"), "--json"],
            cwd=REPO, capture_output=True, text=True, check=True)
        return json.loads(r.stdout)

    def test_every_quoted_position_statistic(self):
        b = self._report()
        st = b["sign_test_A_vs_D"]
        expected = {
            "permutation spread": (b["observed"]["spread"], 3.6265),
            "A minus D": (b["observed"]["A_minus_D"], 3.6265),
            "raw uncentred spread": (b["raw_spread_uncentred"], 3.6590),
            "sign test wins": (st["wins"], 52),
            "sign test usable windows": (st["usable_windows"], 73),
            "sign test windows scoring both": (st["windows_with_both"], 78),
            "sign test ties discarded": (st["ties"], 5),
            "sign test p one-sided": (round(st["p_one_sided"], 6), 0.000186),
            "sign test p two-sided": (round(st["p_two_sided"], 6), 0.000371),
            "friedman p": (round(b["friedman_within_window_ranks"]["p"], 3), 0.304),
            "friedman chi2": (round(b["friedman_within_window_ranks"]["statistic"], 3), 4.843),
            "n windows": (b["n_windows"], 80),
            "n scored observations": (b["n_scored_observations"], 396),
        }
        bad = {k: v for k, v in expected.items() if abs(v[0] - v[1]) > 5e-4}
        assert not bad, f"artifact disagrees with the manuscript: {bad}"

    def test_permutation_is_reproducible_under_its_seed(self):
        """Same seed, same p. A randomisation without a pinned seed is not a result."""
        a = self._report()
        b = self._report()
        assert a["permutation_within_window"] == b["permutation_within_window"]
        assert a["permutation_seed"] == 20261013
        assert a["permutation_draws"] == 20000

    def test_manuscript_quotes_the_one_sided_value_and_labels_it(self):
        text = " ".join(manuscript_text().split())
        assert "one-sided binomial $p = 0.000186$" in text
        assert "two-sided value is $p = 0.000371$" in text, (
            "the two-sided value must be stated so the sidedness is auditable"
        )
