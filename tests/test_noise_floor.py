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
        path = REPO / "paper" / "MANUSCRIPT_SKILL.md"
        if not path.exists():
            pytest.skip("manuscript not present in this checkout")
        return path.read_text(encoding="utf-8")

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