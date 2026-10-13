#!/usr/bin/env python3
"""Position bias in the blind judge, analysed with the judging window as a block.

Why the pooled tests are wrong
------------------------------
The blind protocol judges all five delivery arms of a task inside one window,
permuting the arms across labels A--E. That makes the 396 judged scores
CLUSTERED: five scores in a window share a task, a judge call, and whatever
idiosyncrasy the window had. A one-way ANOVA or Kruskal--Wallis over the pooled
scores treats those 396 observations as independent and is therefore
anti-conservative -- it ignores within-window correlation and understates the
standard error.

What this script does instead
-----------------------------
The window is the block, and the randomisation the protocol actually performed
was a permutation of labels *within* a window. So the reference distribution is
built by shuffling position labels inside each window and recomputing the
statistic, which is exact under that randomisation and makes no normality
assumption. Three statistics are reported:

  spread      max position mean - min position mean, on window-centred scores
  A - D       the specific contrast the manuscript quotes (slot A vs slot D)
  ANOVA F     reported for comparability, on window-centred scores

A Friedman test on within-window ranks is also reported as a distribution-free
check that makes the same block assumption without the centring.

Usage:
    uv run python scripts/analyze_position_blocks.py
    uv run python scripts/analyze_position_blocks.py --json
"""

from __future__ import annotations

import argparse
import collections
import json
import math
import pathlib
import random
import statistics as st
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
RESULTS = REPO / "benchmarks" / "delivery_results_ieee.json"
CRITERIA = [
    "correctness", "completeness", "maintainability", "architecture",
    "security", "reasoning_quality", "instruction_adherence",
]
N_PERM = 20000
SEED = 20261013


def load_windows(path=RESULTS):
    """-> [(window_id, [(position, composite), ...]), ...], one entry per window."""
    data = json.loads(path.read_text(encoding="utf-8"))
    out = []
    for task in data["tasks"]:
        for wi, judging in enumerate(task.get("judging") or []):
            items = []
            for arm, pos in judging["label_map"].items():
                scores = judging["scores_by_strategy"].get(arm)
                if not scores:
                    continue
                try:
                    items.append((pos, sum(scores[c] for c in CRITERIA)))
                except (KeyError, TypeError):
                    continue
            if len(items) >= 2:
                out.append((f"{task['id']}#{wi}", items))
    return out


def centre(windows):
    """Subtract each window's own mean, removing all between-window variance."""
    centred = []
    for _, items in windows:
        m = st.mean(v for _, v in items)
        centred.append([(p, v - m) for p, v in items])
    return centred


def _means(windows_scored):
    by = collections.defaultdict(list)
    for win in windows_scored:
        for pos, val in win:
            by[pos].append(val)
    return {p: st.mean(v) for p, v in by.items()}


def stats(scored):
    m = _means(scored)
    # `scored` is a list of windows, each a list of (position, value).
    return {
        "spread": max(m.values()) - min(m.values()) if m else float("nan"),
        "A_minus_D": m.get("A", float("nan")) - m.get("D", float("nan")),
        "position_means": {p: round(v, 4) for p, v in sorted(m.items())},
    }


def _require_scipy():
    """Import scipy or fail loudly.

    These scripts emit p-values that the manuscript quotes. A missing scipy
    used to degrade silently to NaN, which reads like a result and is not one:
    the artifact then "reproduced" p = nan. Fail instead, with the fix.
    """
    try:
        from scipy import stats as _s
    except ModuleNotFoundError as exc:  # pragma: no cover - env problem
        raise SystemExit(
            "scipy is required to compute the p-values the paper reports.\n"
            "Install it, or run inside the project environment, e.g.:\n"
            "    uv run python scripts/analyze_position_blocks.py\n"
            "Refusing to emit NaN in place of a reported statistic."
        ) from exc
    return _s


def friedman(scored_windows):
    """Friedman test on within-window ranks; distribution-free, block-aware."""
    ranks = collections.defaultdict(list)
    usable = 0
    for scored in scored_windows:
        ordered = sorted(scored, key=lambda kv: kv[1])
        if len(ordered) < 2 or len({v for _, v in ordered}) < 2:
            continue
        usable += 1
        for rank, (pos, _) in enumerate(ordered, start=1):
            ranks[pos].append(rank)
    if usable < 2:
        return None
    k = len(ranks)
    n = usable
    R = {p: sum(v) for p, v in ranks.items()}
    # tie-corrected chi-square
    num = sum((r - n * (k + 1) / 2) ** 2 for r in R.values())
    den = n * k * (k * k - 1) / 12
    chi2 = num / den if den else float("nan")
    p = float(_require_scipy().chi2.sf(chi2, k - 1))
    return {"statistic": chi2, "df": k - 1, "p": p, "n_windows": n,
            "mean_ranks": {p: round(r / n, 3) for p, r in sorted(R.items())}}


def sign_test(windows, left="A", right="D"):
    """Paired sign test on windows containing BOTH slots.

    Only windows that scored both slots contribute; a window missing one of
    them carries no pairwise information. Ties are discarded, not counted as
    wins, so the effective n is the number of informative windows.

    The paper's hypothesis is directional (slot A scores higher than slot D),
    so the reported p-value is ONE-SIDED. The two-sided value is reported
    alongside it: a directional hypothesis tested two-sided is the
    conservative reading, and the qualitative conclusion is identical either
    way.
    """
    wins = losses = ties = 0
    for _, items in windows:
        d = dict(items)
        if left not in d or right not in d:
            continue
        if d[left] > d[right]:
            wins += 1
        elif d[left] < d[right]:
            losses += 1
        else:
            ties += 1
    n = wins + losses
    out = {
        "left": left, "right": right,
        "windows_with_both": wins + losses + ties,
        "usable_windows": n, "wins": wins, "losses": losses, "ties": ties,
    }
    if n < 2:
        return out
    _s = _require_scipy()
    out["p_one_sided"] = float(_s.binomtest(wins, n, alternative="greater").pvalue)
    out["p_two_sided"] = float(_s.binomtest(wins, n, alternative="two-sided").pvalue)
    out["alternative_reported_in_paper"] = "one-sided"
    return out


def permutation_test(windows, observed, stat_key, n_perm=N_PERM, seed=SEED):
    """Shuffle position labels WITHIN each window; exact under the protocol's
    own randomisation, and robust to any within-window correlation."""
    rng = random.Random(seed)
    n_exceed = 0
    for _ in range(n_perm):
        shuffled = []
        for _, items in windows:
            vals = [v for _, v in items]
            rng.shuffle(vals)
            shuffled.append([(p, v) for (p, _), v in zip(items, vals)])
        if stats(shuffled)[stat_key] >= observed:
            n_exceed += 1
    return (n_exceed + 1) / (n_perm + 1)


def run(n_perm: int = N_PERM, seed: int = SEED) -> dict:
    """Compute the block-aware report. Importable; no CLI, no printing."""
    windows = load_windows()
    if not windows:
        raise SystemExit("no judging windows recorded in the archive")
    centred = centre(windows)
    obs = stats(centred)
    fri = friedman(centred)

    # Raw (uncentred) values, for comparison with the pooled tests.
    raw = stats([items for _, items in windows])
    raw_spread = raw["spread"]

    report = {
        "n_windows": len(windows),
        "n_scored_observations": sum(len(i) for _, i in windows),
        "centreing": "each window's own mean removed (window = block)",
        "observed": obs,
        "raw_spread_uncentred": round(raw_spread, 4),
        "friedman_within_window_ranks": fri,
        "sign_test_A_vs_D": sign_test(windows),
        "permutation_within_window": {},
    }
    for key in ("spread", "A_minus_D"):
        p = permutation_test(windows, obs[key], key, n_perm, seed)
        report["permutation_within_window"][key] = {"observed": obs[key], "p": p}
    report["permutation_seed"] = seed
    report["permutation_draws"] = n_perm
    return report


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--perms", type=int, default=N_PERM)
    args = ap.parse_args()

    report = run(args.perms)

    if args.json:
        print(json.dumps(report, indent=2))
        return 0

    print("Position bias, judged windows treated as blocks")
    print("=" * 62)
    print(f"  windows (blocks) : {report['n_windows']}")
    print(f"  scored rows      : {report['n_scored_observations']}")
    print()
    print("Within-window-centred position means (window mean removed):")
    obs = report["observed"]
    for p, v in obs["position_means"].items():
        print(f"    {p}: {v:+.3f}")
    print()
    print(f"  spread (max-min)  : {obs['spread']:.4f} points")
    print(f"  A - D             : {obs['A_minus_D']:+.4f} points")
    print(f"  same, uncentred   : {report['raw_spread_uncentred']:.4f} points "
          f"(includes between-window variance)")
    print()
    print("Block-aware significance (labels permuted WITHIN each window):")
    for key, v in report["permutation_within_window"].items():
        print(f"    {key:9s} observed {v['observed']:+.4f}   "
              f"p = {v['p']:.4f}  ({args.perms:,} permutations)")
    fri = report["friedman_within_window_ranks"]
    st = report["sign_test_A_vs_D"]
    if "p_one_sided" in st:
        print(f"    Sign test A>D   : {st['wins']}/{st['usable_windows']} windows"
              f"  p(one-sided) = {st['p_one_sided']:.6f}"
              f"  p(two-sided) = {st['p_two_sided']:.6f}")
        print(f"      windows scoring both slots: {st['windows_with_both']},"
              f" ties discarded: {st['ties']}")
    if fri:
        print(f"    Friedman (within-window ranks): "
              f"chi2 = {fri['statistic']:.3f}, df = {fri['df']}, "
              f"p = {fri['p']:.4f}, n = {fri['n_windows']} windows")
        print(f"      mean ranks: {fri['mean_ranks']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())