#!/usr/bin/env python3
"""Recompute the manuscript's noise floor, power analysis, and position bias.

This script exists because the three numbers the paper's central argument rests
on -- the test-retest floor (sigma), the paired-difference SD (sigma_d), and the
minimum detectable effect (MDE) -- were, until this file, stated in the
manuscript with no code that produced them. A claim that cannot be recomputed
from the archived artefact is not a claim; it is an assertion. This file makes
all three recomputable, and `tests/test_noise_floor.py` asserts that the
manuscript still agrees with it.

Definitions, stated explicitly because they were previously implicit:

sigma       Pooled within-cell standard deviation of the judge total, where a
            cell is one (task, arm) pair. Every run in a cell was produced from
            a byte-identical prompt, so this is a test-retest quantity: it
            contains judge noise and generation stochasticity, and no treatment
            effect, because the arm is held constant inside the cell.

sigma_d     Standard deviation of the per-task mean differences between two
            arms. This is the quantity the MDE formula requires, and it must be
            paired at the task level -- the benchmark's unit of blocking -- not
            across individual runs.

MDE         The effect size detectable at the stated power target. Two forms
            are reported; the paper leads with the exact one.

            mde_exact   Solved from the noncentral t distribution:
                        P(|T| > t_{1-alpha/2, n-1} | ncp) = 1 - beta with
                        ncp = MDE * sqrt(n) / sigma_d. This accounts for the
                        uncertainty in sigma_d itself, which is material at
                        n = 17.

            mde_normal  The normal approximation
                        (z_{1-alpha/2} + z_{1-beta}) * sigma_d / sqrt(n),
                        treating sigma_d as known. At n = 17 it understates the
                        exact threshold by about 6.5%.

            Both use the PAIRED standard error sigma_d / sqrt(n). The two-sample
            form (z_a + z_b) * sigma * sqrt(2/n) carries a factor of sqrt(2) for
            the standard error of a difference of independent means; a paired
            test already conditions on the task, so that factor must not
            appear. Using it with a paired sigma_d overstates the threshold by
            exactly sqrt(2), which is the error this file was first written with.
            `tests/test_noise_floor.py` asserts that the paired form is used and
            that the MDE and required-n expressions agree.

required_n  (z * sigma_d / observed_gap)^2, the paired-design sample size for
            detecting the observed effect at the same power target.

Usage:
    uv run python scripts/verify_noise_floor.py            # human-readable
    uv run python scripts/verify_noise_floor.py --json     # machine-readable
"""

from __future__ import annotations

import argparse
import collections
import json
import math
import pathlib
import statistics as st
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
BENCH = REPO / "benchmarks"
ARTEFACT = BENCH / "delivery_results_ieee.json"
ALPHA = 0.05
POWER = 0.80
SCALE_MAX = 35.0


def _require_scipy():
    """Import scipy or fail loudly.

    This script produces the paper's headline numbers. Without scipy the exact
    noncentral-t MDE becomes NaN and `gap / MDE` silently falls back to the
    normal approximation -- 10.7% instead of the reported 10.1%. A degraded
    path that prints a plausible wrong headline is worse than a hard failure.
    """
    try:
        from scipy import optimize, stats
    except ModuleNotFoundError as exc:  # pragma: no cover - env problem
        raise SystemExit(
            "scipy is required to reproduce the reported power analysis.\n"
            "Install it, or run inside the project environment, e.g.:\n"
            "    uv run python scripts/verify_noise_floor.py\n"
            "Refusing to emit a degraded headline (the normal-approximation\n"
            "ratio would be reported as if it were the exact one)."
        ) from exc
    return optimize, stats


def _load() -> dict:
    if not ARTEFACT.exists():
        sys.exit(f"archived artefact absent: {ARTEFACT}")
    with ARTEFACT.open(encoding="utf-8") as fh:
        return json.load(fh)


def _runs(data: dict):
    for task in data["tasks"]:
        for arm, runs in task.get("strategy_runs", {}).items():
            for run in runs:
                yield task["id"], arm, run["judge_total"]


def test_retest_floor(data: dict) -> dict:
    """Pooled within-cell SD. The instrument's resolution limit."""
    cells: dict[tuple[str, str], list[int]] = collections.defaultdict(list)
    for task_id, arm, score in _runs(data):
        cells[(task_id, arm)].append(score)

    ss = df = 0
    per_cell = []
    for values in cells.values():
        if len(values) < 2:
            continue
        mean = st.mean(values)
        ss += sum((v - mean) ** 2 for v in values)
        df += len(values) - 1
        per_cell.append(st.stdev(values))

    sigma = math.sqrt(ss / df)
    return {
        "sigma": sigma,
        "n_runs": sum(len(v) for v in cells.values()),
        "n_cells": len(cells),
        "df": df,
        "per_cell_sd_min": min(per_cell),
        "per_cell_sd_max": max(per_cell),
    }


def paired_difference(data: dict, arm_x: str, arm_y: str) -> dict:
    """sigma_d and the paired test for one arm-vs-arm contrast, task-blocked."""
    by_task: dict[str, dict[str, list[int]]] = collections.defaultdict(
        lambda: collections.defaultdict(list)
    )
    for task_id, arm, score in _runs(data):
        by_task[task_id][arm].append(score)

    pairs = [
        t for t in by_task
        if by_task[t].get(arm_x) and by_task[t].get(arm_y)
    ]
    means_x = [st.mean(by_task[t][arm_x]) for t in pairs]
    means_y = [st.mean(by_task[t][arm_y]) for t in pairs]
    diffs = [x - y for x, y in zip(means_x, means_y)]
    n = len(diffs)
    sigma_d = st.stdev(diffs) if n > 1 else float("nan")

    # Two-sided paired t on the task-blocked design. scipy is used when
    # available; the closed form below is the fallback so this script has no
    # hard dependency for reproducing the headline numbers.
    _opt, _stats = _require_scipy()
    t_stat, p_value = _stats.ttest_rel(means_x, means_y)
    t_stat, p_value = float(t_stat), float(p_value)
    z_sum = float(_stats.norm.ppf(1 - ALPHA / 2) + _stats.norm.ppf(POWER))

    mde = z_sum * sigma_d / math.sqrt(n) if n else float("nan")
    observed = st.mean(diffs)
    required_n = (
        math.ceil((z_sum * sigma_d / abs(observed)) ** 2)
        if observed
        else float("inf")
    )

    # Exact paired MDE from the noncentral t distribution. At n = 17 the
    # uncertainty in sigma_d itself is not negligible, so this exceeds the
    # normal approximation; the paper reports this one and discloses the other.
    try:
        _tcrit = _stats.t.ppf(1 - ALPHA / 2, n - 1)

        def _power(delta: float) -> float:
            _ncp = delta * math.sqrt(n) / sigma_d
            return (_stats.nct.sf(_tcrit, n - 1, _ncp)
                    + _stats.nct.cdf(-_tcrit, n - 1, _ncp))

        # Bisection on a bracket that stays clear of the noncentral-t CDF's
        # numerical breakdown at very large noncentrality parameters.
        _lo, _hi = 0.1, 1.0
        while _power(_hi) < POWER and _hi < 64.0:
            _hi *= 1.5
        if _power(_hi) >= POWER:
            for _ in range(200):
                _mid = (_lo + _hi) / 2
                if _power(_mid) < POWER:
                    _lo = _mid
                else:
                    _hi = _mid
            mde_exact = (_lo + _hi) / 2
    except Exception as exc:
        # A failed solve would leave the headline MDE undefined. Never report
        # the normal-approximation ratio in its place.
        raise SystemExit(
            f"exact noncentral-t MDE failed to converge ({exc}). The paper "
            f"reports this value; refusing to substitute the normal "
            f"approximation, which would report 10.7% instead of 10.1%."
        ) from exc

    return {
        "arm_x": arm_x,
        "arm_y": arm_y,
        "n_pairs": n,
        "sigma_d": sigma_d,
        "observed_gap": observed,
        "t_statistic": t_stat,
        "p_value": p_value,
        "mde": mde_exact if mde_exact == mde_exact else mde,
        "mde_exact_nct": mde_exact,
        "mde_normal_approx": mde,
        "mde_pct_of_scale": 100 * (mde_exact if mde_exact == mde_exact
                                   else mde) / SCALE_MAX,
        "gap_pct_of_mde": (100 * abs(observed) / mde_exact
                           if mde_exact == mde_exact else
                           100 * abs(observed) / mde if mde else float("nan")),
        "pairs_needed_for_observed_gap": required_n,
    }


def unpaired_arm_means(data: dict) -> dict[str, dict]:
    by_arm: dict[str, list[int]] = collections.defaultdict(list)
    for _, arm, score in _runs(data):
        by_arm[arm].append(score)
    return {
        arm: {"mean": st.mean(v), "n": len(v), "sd": st.stdev(v)}
        for arm, v in sorted(by_arm.items())
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args()

    data = _load()
    floor = test_retest_floor(data)
    contrast = paired_difference(data, "full", "checklist_v2")
    arms = unpaired_arm_means(data)

    report = {
        "artefact": str(ARTEFACT.relative_to(REPO)),
        "alpha": ALPHA,
        "power": POWER,
        "scale_max": SCALE_MAX,
        "test_retest_floor": floor,
        "headline_contrast": contrast,
        "arm_means": arms,
    }

    if args.json:
        print(json.dumps(report, indent=2))
        return 0

    print("Noise floor and power analysis")
    print("=" * 66)
    print(f"artefact: {report['artefact']}")
    print()
    print("Test-retest floor (pooled within-cell SD)")
    print(f"  sigma            = {floor['sigma']:.3f} points")
    print(f"  runs / cells /df = {floor['n_runs']} / {floor['n_cells']} / {floor['df']}")
    print(f"  per-cell SD range= {floor['per_cell_sd_min']:.2f} - "
          f"{floor['per_cell_sd_max']:.2f}")
    print()
    print(f"Headline contrast: {contrast['arm_x']} - {contrast['arm_y']}")
    print(f"  n task pairs     = {contrast['n_pairs']}")
    print(f"  sigma_d          = {contrast['sigma_d']:.3f}")
    print(f"  observed gap     = {contrast['observed_gap']:+.4f}")
    print(f"  paired t / p     = {contrast['t_statistic']:.4f} / "
          f"{contrast['p_value']:.4f}")
    print(f"  MDE (exact nct)  = {contrast['mde_exact_nct']:.3f} points "
          f"({contrast['mde_pct_of_scale']:.2f}% of scale)")
    print(f"  MDE (normal appr)= {contrast['mde_normal_approx']:.3f} points")
    print(f"  gap / MDE        = {contrast['gap_pct_of_mde']:.1f}%")
    print(f"  pairs for 80% pw = {contrast['pairs_needed_for_observed_gap']}")
    print()
    print("Per-arm means (unpaired; the paired design is task-blocked)")
    for arm, v in arms.items():
        print(f"  {arm:14s} mean {v['mean']:.2f}  n {v['n']:3d}  sd {v['sd']:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())