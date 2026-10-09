"""Judge position-bias analysis for the 18-task macro benchmark.

The macro protocol (§7.2) permutes delivery arms across blind labels A-E
before judging. This script asks whether the judge rewards *position*
independently of content, and whether correcting for it changes any
published conclusion.

Usage:  uv run python scripts/analyze_position_bias.py [--json]

Findings (paper §7.2, §8.1; reported in benchmarks/POSITION_BIAS_AUDIT.md):

  * Position effects are large and highly significant:
        A +2.08   B +0.70   C -0.79   D -1.58   E -0.37
        one-way ANOVA F=4.5373, p=0.00136; Kruskal-Wallis H=15.82, p=0.00328
    The A-to-D spread (+3.66 raw) exceeds every strategy effect in Table 1.

  * Position is close to balanced across arms, so it acts as noise rather
    than as a confound: no arm is systematically assigned to a favoured slot.

  * Correcting for position (subtract per-position mean deviation) does not
    change any conclusion:
        - full - checklist_v2 narrows from +0.204 to +0.120 (Finding 1 holds)
        - no arm significantly beats control (the economics-first premise
          in §8.6.A survives intact)
        - the arm ordering is essentially unchanged

  * The design is underpowered for the effect size being claimed. With
    SD(paired diff) = 7.87 over 78 pairs, the minimum detectable effect at
    80% power / alpha = 0.05 is ~2.53 points. The headline 0.21-point gap is
    8.3% of that floor, so "no significant difference" means "not
    detectable", not "equivalent".
"""

import argparse
import json
import pathlib
import statistics as st
from collections import Counter

from scipy import stats

REPO = pathlib.Path(__file__).resolve().parents[1]
RESULTS = REPO / "benchmarks" / "delivery_results_ieee.json"

CRITERIA = [
    "correctness",
    "completeness",
    "maintainability",
    "architecture",
    "security",
    "reasoning_quality",
    "instruction_adherence",
]


def load_rows(path=RESULTS):
    """Return (task_id, arm, label_position, composite_score) per judged arm."""
    if not path.exists():
        raise SystemExit(f"missing archived results: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = []
    for task in data["tasks"]:
        for judgement in task.get("judging") or []:
            for arm, position in judgement["label_map"].items():
                scores = judgement["scores_by_strategy"].get(arm)
                if not scores:
                    continue
                composite = sum(scores[c] for c in CRITERIA)
                rows.append((task["id"], arm, position, composite))
    return rows


def position_effects(rows):
    """Mean deviation of each label position from the grand mean."""
    grand = st.mean(r[3] for r in rows)
    by_position = {}
    for _, _, pos, value in rows:
        by_position.setdefault(pos, []).append(value)
    return {p: st.mean(v) - grand for p, v in by_position.items()}


def correct(rows, effects):
    corrected = {}
    for _, arm, pos, value in rows:
        corrected.setdefault(arm, []).append(value - effects[pos])
    return corrected


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="emit machine-readable output")
    args = parser.parse_args()

    rows = load_rows()
    effects = position_effects(rows)
    raw = {}
    for _, arm, _, value in rows:
        raw.setdefault(arm, []).append(value)
    corrected = correct(rows, effects)

    by_position = {}
    for _, _, pos, value in rows:
        by_position.setdefault(pos, []).append(value)

    letters = sorted(by_position)
    groups = [by_position[p] for p in letters]
    f_stat, p_anova = stats.f_oneway(*groups)
    h_stat, p_kw = stats.kruskal(*groups)

    raw_means = {a: st.mean(v) for a, v in raw.items()}
    cor_means = {a: st.mean(v) for a, v in corrected.items()}

    # task-blocked paired test on corrected scores
    task_means = {}
    for tid, arm, pos, value in rows:
        task_means.setdefault((tid, arm), []).append(value - effects[pos])
    tasks = sorted({tid for tid, _ in task_means})
    if "full" in raw_means and "checklist_v2" in raw_means:
        t_stat, p_paired = stats.ttest_rel(
            [st.mean(task_means[(t, "full")]) for t in tasks],
            [st.mean(task_means[(t, "checklist_v2")]) for t in tasks],
        )
    else:
        t_stat = p_paired = float("nan")

    # minimum detectable effect for the full-vs-v2 contrast
    sd_paired = st.stdev(
        [a - b for a, b in zip(corrected["full"], corrected["checklist_v2"])]
    ) if {"full", "checklist_v2"} <= set(corrected) else float("nan")
    n_pairs = len(corrected.get("full", []))
    if sd_paired == sd_paired and n_pairs > 2:
        mde = (
            stats.t.ppf(0.975, n_pairs - 1) + stats.t.ppf(0.80, n_pairs - 1)
        ) * sd_paired / (n_pairs ** 0.5)
    else:
        mde = float("nan")

    cross = Counter((arm, pos) for _, arm, pos, _ in rows)
    arms = sorted(raw_means)

    result = {
        "n_judged_arm_instances": len(rows),
        "position_effects": effects,
        "position_means": {p: st.mean(v) for p, v in by_position.items()},
        "anova": {"F": f_stat, "p": p_anova},
        "kruskal_wallis": {"H": h_stat, "p": p_kw},
        "raw_means": raw_means,
        "corrected_means": cor_means,
        "position_x_arm": {a: {p: cross[(a, p)] for p in letters} for a in arms},
        "full_minus_v2": {
            "raw": raw_means.get("full", float("nan")) - raw_means.get("checklist_v2", float("nan")),
            "corrected": cor_means.get("full", float("nan")) - cor_means.get("checklist_v2", float("nan")),
            "paired_t": t_stat,
            "paired_p": p_paired,
            "n_tasks": len(tasks),
        },
        "minimum_detectable_effect": mde,
        "sd_paired_diff": sd_paired,
    }

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
        return

    print(f"judged arm-instances: {len(rows)}")
    print("\n=== position effects (deviation from grand mean) ===")
    for pos in letters:
        print(f"  {pos}: {effects[pos]:+.2f}")
    print(f"\nANOVA           F={f_stat:.4f}  p={p_anova:.6f}")
    print(f"Kruskal-Wallis  H={h_stat:.4f}  p={p_kw:.6f}")
    print(
        f"\nA-D spread = {st.mean(by_position['A']) - st.mean(by_position['D']):+.2f} points "
        f"({(st.mean(by_position['A']) - st.mean(by_position['D'])) / 0.21:.0f}x the 0.21pt headline)"
    )

    print("\n=== strategy means: raw vs position-corrected ===")
    print(f"  {'arm':<16}{'raw':>8}{'corrected':>12}{'delta':>9}")
    for arm in arms:
        print(
            f"  {arm:<16}{raw_means[arm]:>8.2f}{cor_means[arm]:>12.2f}"
            f"{cor_means[arm] - raw_means[arm]:>+9.2f}"
        )

    print("\n=== headline contrast, task-blocked (corrected) ===")
    fv = result["full_minus_v2"]
    print(f"  full - checklist_v2: raw={fv['raw']:+.3f}  corrected={fv['corrected']:+.3f}")
    print(f"  paired t={fv['paired_t']:.4f}  p={fv['paired_p']:.4f}  (n_tasks={fv['n_tasks']})")

    print("\n=== power ===")
    print(f"  SD(paired diff) = {sd_paired:.2f} over {n_pairs} pairs")
    print(f"  minimum detectable effect (80% power) = {mde:.2f} points")
    print(f"  headline 0.21 pt gap = {0.21 / mde * 100:.1f}% of that floor")

    print("\n=== position x arm balance ===")
    print("  arm".ljust(20) + "".join(f"{p:>5}" for p in letters))
    for arm in arms:
        print("  " + arm.ljust(20) + "".join(f"{cross[(arm, p)]:>5}" for p in letters))


if __name__ == "__main__":
    main()