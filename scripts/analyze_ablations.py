#!/usr/bin/env python3
"""
Structural Ablation Analyzer — IEEE Study
=========================================
Computes exploratory paired statistics, structural sensitivity matrix (S_c),
and generates Tables 2 & 3 in Markdown and LaTeX format.

Statistical analysis:
  - Task-blocked paired differences against balanced reference (A1)
  - Paired Student's t-test & Paired Wilcoxon Signed-Rank test (N=6 pairs)
  - Holm-Bonferroni family-wise error rate correction (alpha = 0.05)
  - Paired Cohen's d_z effect sizes and 95% confidence intervals
  - S_c normalized sensitivity metric alongside token reduction volume

Usage:
  python3 scripts/analyze_ablations.py
  python3 scripts/analyze_ablations.py --results benchmarks/ablation_results.json
"""

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent

DEFAULT_ABLATION_RESULTS = ROOT / "benchmarks" / "ablation_results.json"
DEFAULT_BASELINE_RESULTS = ROOT / "benchmarks" / "delivery_results_ieee.json"
DEFAULT_TASKS_SUBSET = ROOT / "benchmarks" / "tasks_ablation_subset.json"
DEFAULT_REPORT_MD = ROOT / "benchmarks" / "ablation_report_ieee.md"
DEFAULT_TABLES_TEX = ROOT / "benchmarks" / "ablation_tables_ieee.tex"

JUDGE_CRITERIA = [
    "correctness",
    "completeness",
    "maintainability",
    "architecture",
    "security",
    "reasoning_quality",
    "instruction_adherence",
]


def cohens_d_paired(diffs: np.ndarray) -> float:
    mean_d = float(np.mean(diffs))
    std_d = float(np.std(diffs, ddof=1))
    if std_d == 0 or math.isnan(std_d):
        return 0.0
    return mean_d / std_d


def cohens_d_ci(d_z: float, n: int, confidence: float = 0.95) -> Tuple[float, float]:
    if n <= 1:
        return d_z, d_z
    se = math.sqrt((1 / n) + (d_z**2 / (2 * n)))
    z = stats.norm.ppf(1 - (1 - confidence) / 2)
    return d_z - z * se, d_z + z * se


def holm_bonferroni(p_values: List[float], alpha: float = 0.05) -> List[Tuple[float, float, bool]]:
    m = len(p_values)
    indexed = sorted(enumerate(p_values), key=lambda x: x[1])
    results = [None] * m
    passed = True
    for rank, (orig_idx, p) in enumerate(indexed):
        adj_alpha = alpha / (m - rank)
        if passed and p <= adj_alpha:
            sig = True
        else:
            sig = False
            passed = False
        adj_p = min(1.0, p * (m - rank))
        results[orig_idx] = (p, adj_p, sig)
    return results


def load_tasks(tasks_path: Path) -> List[Dict[str, Any]]:
    if not tasks_path.exists():
        return []
    return json.loads(tasks_path.read_text(encoding="utf-8"))


def extract_baseline_scores(
    baseline_path: Path,
) -> Tuple[Dict[str, Dict[str, List[float]]], Dict[str, Dict[str, List[float]]]]:
    by_task_id = {}
    by_skill = {}
    if not baseline_path.exists():
        return by_task_id, by_skill

    try:
        data = json.loads(baseline_path.read_text(encoding="utf-8"))
        for task in data.get("tasks", []):
            t_id = task.get("id")
            skill = task.get("skill")
            if not t_id:
                continue

            strat_scores = {}
            for j in task.get("judging", []):
                scores_strat = j.get("scores_by_strategy", {})
                for strat, crit_dict in scores_strat.items():
                    if isinstance(crit_dict, dict):
                        tot = sum(
                            crit_dict.get(c, 0)
                            for c in JUDGE_CRITERIA
                            if isinstance(crit_dict.get(c), (int, float))
                        )
                        strat_scores.setdefault(strat, []).append(tot)

            by_task_id[t_id] = strat_scores
            if skill:
                by_skill[skill] = strat_scores
    except Exception as e:
        print(f"Warning: Failed to extract baseline scores: {e}", file=sys.stderr)

    return by_task_id, by_skill


def extract_ablation_scores_and_magnitudes(
    ablation_path: Path,
) -> Tuple[Dict[str, Dict[str, List[float]]], Dict[str, Dict[str, Dict[str, float]]]]:
    ablation_scores = {}
    magnitudes = {}
    if not ablation_path.exists():
        return ablation_scores, magnitudes

    try:
        data = json.loads(ablation_path.read_text(encoding="utf-8"))
        for run in data.get("runs", []):
            task_id = run.get("task_id")
            condition = run.get("condition")
            if not task_id or not condition:
                continue

            judge = run.get("judge", {})
            scores = judge.get("scores", {})
            total_score = scores.get("total_score")
            if total_score is None:
                total_score = sum(
                    scores.get(c, 0)
                    for c in JUDGE_CRITERIA
                    if isinstance(scores.get(c), (int, float))
                )

            ablation_scores.setdefault(task_id, {}).setdefault(condition, []).append(float(total_score))

            mag = run.get("magnitude", {})
            if mag and (task_id not in magnitudes or condition not in magnitudes[task_id]):
                magnitudes.setdefault(task_id, {})[condition] = mag
    except Exception as e:
        print(f"Warning: Failed to extract ablation scores: {e}", file=sys.stderr)

    return ablation_scores, magnitudes


def generate_tables(
    tasks: List[Dict[str, Any]],
    cell_means: Dict[str, Dict[str, float]],
    magnitudes: Dict[str, Dict[str, Dict[str, float]]],
) -> Tuple[str, str, str]:
    t2_md = [
        "### Table 2: Structural Component Ablation Scores & Token Magnitudes ($N=54$, 6 Tasks)\n",
        "| Domain | Task ID | $A_0$ (Full) | $A_1$ (Balanced) | $A_2$ (No Examples) | $A_3$ (No Tables) | $A_4$ (No Types) | $A_5$ (Aggressive Bullets) |",
        "| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |",
    ]

    t2_tex = [
        r"\begin{table*}[t]",
        r"\centering",
        r"\caption{Structural Component Ablation Scores & Token Magnitudes ($N=54$, 6 Tasks)}",
        r"\label{tab:ablation_scores}",
        r"\begin{tabular}{llcccccc}",
        r"\toprule",
        r"\textbf{Domain} & \textbf{Task ID} & \textbf{$A_0$ (Full)} & \textbf{$A_1$ (Balanced)} & \textbf{$A_2$ (No Ex.)} & \textbf{$A_3$ (No Tbl.)} & \textbf{$A_4$ (No Typ.)} & \textbf{$A_5$ (Bullets)} \\",
        r"\midrule",
    ]

    t3_md = [
        "### Table 3: Observed Structural Sensitivity Matrix ($S_c$) Across Domains\n",
        "| Domain | Narrative ($S_{\\text{narr}}$) | Examples ($S_{\\text{ex}}$) | Tables ($S_{\\text{tbl}}$) | Types/Interfaces ($S_{\\text{type}}$) | Compound Stripping ($S_{\\text{comp}}$) |",
        "| :--- | :---: | :---: | :---: | :---: | :---: |",
    ]

    t3_tex = [
        r"\begin{table*}[t]",
        r"\centering",
        r"\caption{Observed Structural Sensitivity Matrix ($S_c$) Across Domains}",
        r"\label{tab:sensitivity_matrix}",
        r"\begin{tabular}{lccccc}",
        r"\toprule",
        r"\textbf{Domain} & \textbf{$S_{\text{narr}}$ (Narrative)} & \textbf{$S_{\text{ex}}$ (Examples)} & \textbf{$S_{\text{tbl}}$ (Tables)} & \textbf{$S_{\text{type}}$ (Types)} & \textbf{$S_{\text{comp}}$ (Compound)} \\",
        r"\midrule",
    ]

    for task in tasks:
        task_id = task["id"]
        domain = task.get("domain", "General")
        scores = cell_means.get(task_id, {})

        a0 = scores.get("a0_full", 0.0)
        a1 = scores.get("a1_v2_balanced", 0.0)
        a2 = scores.get("a2_no_examples", 0.0)
        a3 = scores.get("a3_no_tables", 0.0)
        a4 = scores.get("a4_no_types", 0.0)
        a5 = scores.get("a5_v1_bullets", 0.0)

        t2_md.append(
            f"| {domain} | `{task_id}` | {a0:.2f} | {a1:.2f} | {a2:.2f} | {a3:.2f} | {a4:.2f} | {a5:.2f} |"
        )
        t2_tex.append(
            f"{domain} & \\texttt{{{task_id}}} & {a0:.2f} & {a1:.2f} & {a2:.2f} & {a3:.2f} & {a4:.2f} & {a5:.2f} \\\\"
        )

        ref = max(0.1, a1)
        s_narr = (a0 - a1) / ref
        s_ex = (a1 - a2) / ref
        s_tbl = (a1 - a3) / ref
        s_typ = (a1 - a4) / ref
        s_comp = (a1 - a5) / ref

        t3_md.append(
            f"| {domain} | {s_narr:+.3f} | {s_ex:+.3f} | {s_tbl:+.3f} | {s_typ:+.3f} | {s_comp:+.3f} |"
        )
        t3_tex.append(
            f"{domain} & {s_narr:+.3f} & {s_ex:+.3f} & {s_tbl:+.3f} & {s_typ:+.3f} & {s_comp:+.3f} \\\\"
        )

    t2_tex.extend([r"\bottomrule", r"\end{tabular}", r"\end{table*}"])
    t3_tex.extend([r"\bottomrule", r"\end{tabular}", r"\end{table*}"])

    md_content = "\n".join(t2_md) + "\n\n" + "\n".join(t3_md)
    tex_content = "\n\n".join(["\n".join(t2_tex), "\n".join(t3_tex)])
    return md_content, tex_content, "\n".join(t2_md)


def main():
    parser = argparse.ArgumentParser(description="Analyze structural component ablation results.")
    parser.add_argument("--tasks", type=Path, default=DEFAULT_TASKS_SUBSET, help="Path to ablation task subset JSON")
    parser.add_argument("--results", type=Path, default=DEFAULT_ABLATION_RESULTS, help="Path to ablation results JSON")
    parser.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE_RESULTS, help="Path to baseline delivery JSON")
    parser.add_argument("--out-md", type=Path, default=DEFAULT_REPORT_MD, help="Output markdown report path")
    parser.add_argument("--out-tex", type=Path, default=DEFAULT_TABLES_TEX, help="Output LaTeX tables path")

    args = parser.parse_args()

    tasks = load_tasks(args.tasks)
    if not tasks:
        print(f"Error: No tasks found in {args.tasks}", file=sys.stderr)
        sys.exit(1)

    base_by_id, base_by_skill = extract_baseline_scores(args.baseline)
    ablation_scores, magnitudes = extract_ablation_scores_and_magnitudes(args.results)

    cell_means: Dict[str, Dict[str, float]] = {}
    for task in tasks:
        task_id = task["id"]
        skill = task.get("skill", "")
        cell_means[task_id] = {}

        # Look up baseline by task ID or skill name
        base = base_by_id.get(task_id) or base_by_skill.get(skill, {})
        if "full" in base and base["full"]:
            cell_means[task_id]["a0_full"] = float(np.mean(base["full"]))
        if "checklist_v2" in base and base["checklist_v2"]:
            cell_means[task_id]["a1_v2_balanced"] = float(np.mean(base["checklist_v2"]))
        if "checklist" in base and base["checklist"]:
            cell_means[task_id]["a5_v1_bullets"] = float(np.mean(base["checklist"]))

        # Overlay / load ablation conditions
        t_abl = ablation_scores.get(task_id, {})
        for cond, vals in t_abl.items():
            if vals:
                cell_means[task_id][cond] = float(np.mean(vals))

    md_report, tex_report, _ = generate_tables(tasks, cell_means, magnitudes)

    print("=" * 70)
    print(f"EXPLORATORY INFERENTIAL ABLATION ANALYSIS (N={len(tasks)} Tasks)")
    print("=" * 70)

    comparisons = [
        ("A2 (No Examples) vs A1", "a2_no_examples"),
        ("A3 (No Tables) vs A1", "a3_no_tables"),
        ("A4 (No Types) vs A1", "a4_no_types"),
        ("A5 (Aggressive Bullets) vs A1", "a5_v1_bullets"),
    ]

    p_vals = []
    comp_data = []

    for name, cond_key in comparisons:
        diffs = []
        for task in tasks:
            t_id = task["id"]
            a1_val = cell_means[t_id].get("a1_v2_balanced")
            cond_val = cell_means[t_id].get(cond_key)
            if a1_val is not None and cond_val is not None:
                diffs.append(a1_val - cond_val)

        if len(diffs) >= 3:
            diffs_arr = np.array(diffs)
            mean_diff = float(np.mean(diffs_arr))
            std_diff = float(np.std(diffs_arr, ddof=1))
            t_res = stats.ttest_1samp(diffs_arr, 0.0)
            try:
                w_res = stats.wilcoxon(diffs_arr, zero_method="wilcox", correction=True)
                w_p = w_res.pvalue
            except Exception:
                w_p = t_res.pvalue

            d_z = cohens_d_paired(diffs_arr)
            ci_low, ci_high = cohens_d_ci(d_z, len(diffs_arr))

            comp_data.append({
                "name": name,
                "n": len(diffs),
                "mean_diff": mean_diff,
                "std_diff": std_diff,
                "t_stat": t_res.statistic,
                "t_p": t_res.pvalue,
                "w_p": w_p,
                "d_z": d_z,
                "ci": (ci_low, ci_high),
            })
            p_vals.append(t_res.pvalue)
        else:
            p_vals.append(1.0)
            comp_data.append({"name": name, "n": len(diffs), "empty": True})

    hb_results = holm_bonferroni(p_vals, alpha=0.05)

    stats_summary_lines = [
        "\n### Exploratory Inferential Statistics (Blocked by Task, $N=6$ Pairs)\n",
        "| Comparison | Mean Diff ($\\Delta Q$) | Std | Paired $t$-stat | Raw $p$ | Holm-Bonf. $p_{\\text{adj}}$ | Cohen's $d_z$ [95% CI] | Sig ($\\alpha=0.05$) |",
        "| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |",
    ]

    for idx, c in enumerate(comp_data):
        if c.get("empty"):
            print(f"{c['name']}: Insufficient paired data (n={c['n']})")
            continue
        raw_p, adj_p, sig = hb_results[idx]
        sig_str = "Yes *" if sig else "No"
        ci_str = f"[{c['ci'][0]:.2f}, {c['ci'][1]:.2f}]"
        print(
            f"{c['name']:<30} | ΔQ: {c['mean_diff']:+.2f} (±{c['std_diff']:.2f}) | "
            f"t: {c['t_stat']:.3f} (p={raw_p:.4f}, p_adj={adj_p:.4f}) | d_z: {c['d_z']:.2f} {ci_str} | Sig: {sig_str}"
        )
        stats_summary_lines.append(
            f"| {c['name']} | {c['mean_diff']:+.2f} | {c['std_diff']:.2f} | {c['t_stat']:.3f} | {raw_p:.4f} | {adj_p:.4f} | {c['d_z']:.2f} {ci_str} | {sig_str} |"
        )

    full_md_report = md_report + "\n\n" + "\n".join(stats_summary_lines)
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text(full_md_report, encoding="utf-8")
    args.out_tex.parent.mkdir(parents=True, exist_ok=True)
    args.out_tex.write_text(tex_report, encoding="utf-8")

    print("\n" + "=" * 70)
    print(f"Report generated at: {args.out_md}")
    print(f"LaTeX tables saved at: {args.out_tex}")
    print("=" * 70)


if __name__ == "__main__":
    main()
