#!/usr/bin/env python3
"""Generate the six-page manuscript's figures from archived artefacts.

This is a read-only companion to ``make_figures.py``: it never overwrites the
existing ``fig_arms.pdf`` / ``fig_correction.pdf`` files. Outputs are written
as ``paper/fig_v2_*.pdf`` and ``paper/fig_v2_*.png`` so the LaTeX and DOCX
builders can consume them independently.

Run:
    uv run python scripts/make_figures_v2.py
"""

from __future__ import annotations

import collections
import json
import pathlib
import statistics as st

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]
PAPER = REPO / "paper"
BENCH = REPO / "benchmarks"

INK = "#12263f"
MUTED = "#8899aa"
GRID = "#e3e9f0"
BAND = "#dce6f2"
GOOD = "#2d6a4f"
WARN = "#7d1d3f"
PALE = "#b9c6d4"

plt.rcParams.update({
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "font.family": "DejaVu Sans",
    "axes.edgecolor": MUTED,
    "axes.linewidth": 0.6,
    "xtick.color": INK,
    "ytick.color": INK,
    "text.color": INK,
})


def save(fig: plt.Figure, stem: str) -> None:
    fig.savefig(PAPER / f"{stem}.pdf", bbox_inches="tight")
    fig.savefig(PAPER / f"{stem}.png", dpi=300, bbox_inches="tight")
    print(f"  {stem}.pdf / .png")


def style(ax: plt.Axes, grid_axis: str | None = None) -> None:
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    if grid_axis:
        ax.grid(axis=grid_axis, lw=0.4, color=GRID, zorder=0)
        ax.set_axisbelow(True)
    ax.tick_params(labelsize=5.9, length=2, width=0.5)


def delivery() -> tuple[dict[str, list[int]], dict[str, dict[str, list[int]]]]:
    data = json.loads((BENCH / "delivery_results_ieee.json").read_text())
    tasks = {t["id"]: t for t in json.loads((BENCH / "tasks_ieee.json").read_text())}
    by: dict[str, list[int]] = collections.defaultdict(list)
    by_domain: dict[str, dict[str, list[int]]] = collections.defaultdict(
        lambda: collections.defaultdict(list))
    for task in data["tasks"]:
        domain = tasks.get(task["id"], {}).get("domain", "Unknown")
        for arm, runs in task.get("strategy_runs", {}).items():
            for run in runs:
                by[arm].append(run["judge_total"])
                by_domain[domain][arm].append(run["judge_total"])
    return by, by_domain


def fig_design() -> None:
    """Five delivery arms, attrition, and the tokenizer check."""
    fig = plt.figure(figsize=(7.0, 3.5), dpi=300)
    gs = fig.add_gridspec(2, 2, height_ratios=[1.0, 0.95],
                          hspace=0.62, wspace=0.30)

    # (a) compression ladder ------------------------------------------------
    ax = fig.add_subplot(gs[0, 0])
    arms = ["control", "full", "retrieved", "checklist_v2", "checklist"]
    labels = ["control\n(no skill)", "full\n(verbatim)", "retrieved\n(subset)",
              "checklist_v2\n(compiled)", "checklist\n(bulletised)"]
    reduction = [0.0, 0.0, 0.0, 28.6, 70.8]
    y = np.arange(len(arms))[::-1]
    colors = [PALE, PALE, PALE, GOOD, WARN]
    ax.barh(y, reduction, height=0.58, color=colors, zorder=2)
    for yy, val in zip(y, reduction):
        if val == 0:
            ax.plot(0, yy, marker="o", ms=3.0, color=INK, zorder=3)
            ax.text(1.2, yy, "0%", va="center", fontsize=5.8, color=INK)
        else:
            ax.text(val + 1.2, yy, f"{val:.1f}%", va="center",
                    fontsize=5.8, color=INK)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=5.7)
    ax.set_xlim(0, 82)
    ax.set_xlabel("prompt-token reduction vs. full manual (%)", fontsize=6.2)
    ax.set_title("(a) Delivery arms", fontsize=7.0, loc="left", pad=3,
                 fontweight="bold")
    style(ax, "x")

    # (b) tokenizer check ---------------------------------------------------
    ax = fig.add_subplot(gs[0, 1])
    methods = ["len//4\nheuristic", "cl100k\nbase", "o200k\nbase", "p50k\nbase"]
    vals = [30.41, 28.56, 28.47, 29.05]
    cols = [PALE, GOOD, PALE, PALE]
    bars = ax.bar(np.arange(4), vals, width=0.62, color=cols, zorder=2)
    for bar, val in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 0.18,
                f"{val:.2f}", ha="center", fontsize=5.9, color=INK)
    ax.set_xticks(np.arange(4))
    ax.set_xticklabels(methods, fontsize=5.6)
    ax.set_ylim(0, 32.5)
    ax.set_ylabel("reduction (%)", fontsize=6.2)
    ax.text(0.99, 0.04, "axis truncated at 0", transform=ax.transAxes,
            ha="right", fontsize=4.8, color=MUTED)
    ax.set_title("(b) Estimator sensitivity", fontsize=7.0, loc="left", pad=3,
                 fontweight="bold")
    style(ax, "y")

    # (c) attrition flow ----------------------------------------------------
    ax = fig.add_subplot(gs[1, :])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    def box(x, y, w, h, title, sub, fill="white"):
        patch = FancyBboxPatch((x, y), w, h,
                               boxstyle="round,pad=0.012,rounding_size=0.02",
                               linewidth=0.7, edgecolor=INK, facecolor=fill,
                               zorder=2)
        ax.add_patch(patch)
        ax.text(x + w / 2, y + h * 0.62, title, ha="center", va="center",
                fontsize=6.4, fontweight="bold", zorder=3)
        ax.text(x + w / 2, y + h * 0.27, sub, ha="center", va="center",
                fontsize=5.3, color="#3d5875", zorder=3)

    box(0.02, 0.50, 0.24, 0.36, "450 generated",
        "18 tasks x 5 arms x 5 runs")
    box(0.37, 0.50, 0.24, 0.36, "425 scheduled", "17 judged tasks")
    box(0.72, 0.50, 0.24, 0.36, "396 judged", "85 task-arm cells")

    box(0.18, 0.05, 0.25, 0.25, "25 dropped task",
        "5 arms x 5 runs; executor exit 5", fill="#f5edf0")
    box(0.53, 0.05, 0.30, 0.25, "29 unaccounted",
        "23 executor stubs + 6 full-length", fill="#f5edf0")

    def arrow(x1, y1, x2, y2, dash=False):
        ax.add_patch(FancyArrowPatch(
            (x1, y1), (x2, y2),
            arrowstyle="-|>", mutation_scale=7, linewidth=0.7,
            color=INK, linestyle="--" if dash else "-",
            shrinkA=2, shrinkB=2, zorder=1))

    arrow(0.26, 0.68, 0.37, 0.68)
    arrow(0.61, 0.68, 0.72, 0.68)
    arrow(0.14, 0.50, 0.24, 0.30, dash=True)
    arrow(0.49, 0.50, 0.62, 0.30, dash=True)
    ax.text(0.50, 0.92, "(c) Attrition account (all counts reconcile)",
            fontsize=7.0, fontweight="bold", ha="left", va="center")

    save(fig, "fig_v2_design")
    plt.close(fig)


def fig_results() -> None:
    """Arm means, domain deltas, ablations, and the failed replication."""
    by, by_domain = delivery()
    fig, axes = plt.subplots(2, 2, figsize=(7.0, 3.6), dpi=300)
    fig.subplots_adjust(hspace=0.62, wspace=0.32)

    # (a) arm means ---------------------------------------------------------
    ax = axes[0, 0]
    order = ["full", "checklist_v2", "retrieved", "checklist", "control"]
    labels = ["full", "checklist_v2", "retrieved", "checklist", "control"]
    means = np.array([st.mean(by[a]) for a in order])
    ci = 1.96 * np.array([st.stdev(by[a]) / np.sqrt(len(by[a]))
                          for a in order])
    y = np.arange(len(order))[::-1]
    ref = float(np.mean(by["full"]))
    mde = 2.721
    ax.axvspan(ref - mde / 2, ref + mde / 2, color=BAND, alpha=0.85, zorder=0)
    ax.errorbar(means, y, xerr=ci, fmt="o", ms=3.8, color=INK,
                ecolor="#3d5875", elinewidth=0.9, capsize=2, zorder=3)
    ya = y.max() + 0.42
    ax.annotate("", xy=(means.min(), ya), xytext=(means.max(), ya),
                arrowprops=dict(arrowstyle="<|-|>", lw=0.8, color=GOOD))
    ax.text((means.min() + means.max()) / 2, ya + 0.13,
            f"spread {round(means.max(), 2) - round(means.min(), 2):.2f}", ha="center",
            va="bottom", fontsize=5.4, color=GOOD)
    yb = y.min() - 0.70
    ax.annotate("", xy=(ref - mde / 2, yb), xytext=(ref + mde / 2, yb),
                arrowprops=dict(arrowstyle="<|-|>", lw=0.8, color=WARN))
    ax.text(ref, yb - 0.14, f"MDE {mde:.2f}", ha="center", va="top",
            fontsize=5.4, color=WARN)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=5.7)
    ax.set_xlim(23.3, 26.9)
    ax.set_ylim(y.min() - 1.05, y.max() + 1.05)
    ax.set_xlabel("mean rubric score (35-point)", fontsize=6.2)
    ax.set_title("(a) Arm means with 95% CI", fontsize=7.0, loc="left",
                 pad=3, fontweight="bold")
    style(ax, "x")

    # (b) domain deltas -----------------------------------------------------
    ax = axes[0, 1]
    doms = ["Architecture", "DevOps", "SRE", "Databases", "Security",
            "Testing & QA"]
    keys = ["Architecture & Refactoring", "DevOps & Cloud", "SRE & Debugging",
            "Databases & Persistence", "Security & Auditing", "Testing & QA"]
    deltas = []
    for key in keys:
        full = by_domain[key]["full"]
        check = by_domain[key]["checklist"]
        deltas.append(st.mean(check) - st.mean(full))
    deltas = np.array(deltas)
    y = np.arange(len(doms))
    cols = [WARN if abs(d) > 4 else MUTED for d in deltas]
    ax.barh(y, deltas, height=0.58, color=cols, zorder=2)
    ax.axvline(0, color=INK, lw=0.6, zorder=3)
    for yy, d in zip(y, deltas):
        ax.text(d + (0.22 if d >= 0 else -0.22), yy, f"{d:+.2f}",
                va="center", ha="left" if d >= 0 else "right",
                fontsize=5.6, color=INK)
    ax.set_yticks(y)
    ax.set_yticklabels(doms, fontsize=5.7)
    ax.set_xlim(-7.5, 4.8)
    ax.set_xlabel("checklist - full (points)", fontsize=6.2)
    ax.set_title("(b) Domain deltas", fontsize=7.0, loc="left", pad=3,
                 fontweight="bold")
    style(ax, "x")

    # (c) ablations ---------------------------------------------------------
    ax = axes[1, 0]
    conds = ["a1_v2_balanced", "a2_no_examples", "a3_no_tables",
             "a4_no_types"]
    names = ["A1 balanced", "A2 no examples", "A3 no tables", "A4 no types"]
    means = [19.75, 18.58, 16.83, 21.50]
    cols = [PALE, PALE, PALE, GOOD]
    bars = ax.barh(np.arange(4), means, height=0.58, color=cols, zorder=2)
    ax.axvspan(19.75 - 5.37 / 2, 19.75 + 5.37 / 2, color=BAND, alpha=0.55,
               zorder=0)
    for bar, val in zip(bars, means):
        ax.text(val + 0.28, bar.get_y() + bar.get_height() / 2,
                f"{val:.2f}", va="center", fontsize=5.7, color=INK)
    ax.set_yticks(np.arange(4))
    ax.set_yticklabels(names, fontsize=5.7)
    ax.set_xlim(0, 27)
    ax.set_xlabel("mean rubric score", fontsize=6.2)
    ax.set_title("(c) Component ablations", fontsize=7.0, loc="left",
                 pad=3, fontweight="bold")
    style(ax, "x")

    # (d) failed replication ------------------------------------------------
    ax = axes[1, 1]
    rep = json.loads(
        (BENCH / "tdd_replication/tdd_a1_a2_n15_results.json").read_text())
    by_cond = collections.defaultdict(list)
    for run in rep["runs"]:
        by_cond[run["condition"]].append(run["judge"]["scores"]["total_score"])
    names = ["A1 balanced", "A2 no examples"]
    vals = [st.mean(by_cond["a1_v2_balanced"]),
            st.mean(by_cond["a2_no_examples"])]
    sds = [st.stdev(by_cond["a1_v2_balanced"]),
           st.stdev(by_cond["a2_no_examples"])]
    bars = ax.bar([0, 1], vals, yerr=sds, width=0.55, color=[PALE, GOOD],
                  capsize=2.5, error_kw={"elinewidth": 0.8, "ecolor": INK},
                  zorder=2)
    for bar, val, sd in zip(bars, vals, sds):
        ax.text(bar.get_x() + bar.get_width() / 2, val + sd + 0.45,
                f"{val:.2f}", ha="center", fontsize=5.8, color=INK)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(names, fontsize=5.7)
    ax.set_ylim(12, 37)
    ax.set_ylabel("mean rubric score", fontsize=6.2)
    ax.text(0.5, 34.0, "reversal: +3.53\nWelch p = 0.14",
            ha="center", fontsize=5.4, color=WARN)
    ax.set_title("(d) Failed replication (n=15/arm)", fontsize=7.0,
                 loc="left", pad=3, fontweight="bold")
    style(ax, "y")

    save(fig, "fig_v2_results")
    plt.close(fig)


def fig_position() -> None:
    """Slot deviations and the four position-bias analyses."""
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.25), dpi=300)
    fig.subplots_adjust(wspace=0.42)

    # (a) slot deviations ---------------------------------------------------
    ax = axes[0]
    slots = ["A", "B", "C", "D", "E"]
    dev = [2.08, 0.70, -0.79, -1.58, -0.37]
    cols = [WARN, MUTED, MUTED, GOOD, MUTED]
    bars = ax.bar(np.arange(5), dev, width=0.58, color=cols, zorder=2)
    ax.axhline(0, color=INK, lw=0.6, zorder=3)
    for bar, val in zip(bars, dev):
        ax.text(bar.get_x() + bar.get_width() / 2,
                val + (0.12 if val >= 0 else -0.12),
                f"{val:+.2f}", ha="center",
                va="bottom" if val >= 0 else "top",
                fontsize=5.8, color=INK)
    ax.set_xticks(np.arange(5))
    ax.set_xticklabels(slots, fontsize=6.4)
    ax.set_ylim(-2.3, 2.8)
    ax.set_ylabel("deviation (points)", fontsize=6.2)
    ax.set_title("(a) Slot deviation from grand mean", fontsize=7.0,
                 loc="left", pad=3, fontweight="bold")
    style(ax, "y")

    # (b) analysis comparison ----------------------------------------------
    ax = axes[1]
    rows = [
        ("Pooled ANOVA (withdrawn)", 0.00136, "x", MUTED),
        ("Centred ANOVA (descriptive)", 0.000014, "o", "white"),
        ("Permutation, within window", 0.00005, "o", GOOD),
        ("Sign test, A vs D", 0.000186, "o", GOOD),
        ("Friedman ranks (n.s.)", 0.304, "o", MUTED),
    ]
    y = np.arange(len(rows))[::-1]
    for yy, (label, p, marker, color) in zip(y, rows):
        ax.plot(p, yy, marker=marker, ms=5.0 if marker == "o" else 4.2,
                color=color, markeredgecolor=INK if color == "white" else color,
                markeredgewidth=0.7, zorder=3)
        if p > 0.1:
            ax.text(p * 0.65, yy, f"{p:.6f}".rstrip("0").rstrip("."),
                    va="center", ha="right", fontsize=5.4, color=INK)
        else:
            ax.text(p * 1.35, yy, f"{p:.6f}".rstrip("0").rstrip("."),
                    va="center", fontsize=5.4, color=INK)
    ax.axvline(0.05, color=WARN, lw=0.7, linestyle="--", zorder=1)
    ax.text(0.05, len(rows) - 0.35, "0.05", color=WARN, fontsize=5.2,
            ha="center")
    ax.set_xscale("log")
    ax.set_xlim(8e-6, 0.8)
    ax.set_yticks(y)
    ax.set_yticklabels([r[0] for r in rows], fontsize=5.5)
    ax.set_xlabel("p-value (log scale)", fontsize=6.2)
    ax.set_title("(b) Position-bias tests", fontsize=7.0, loc="left",
                 pad=3, fontweight="bold")
    style(ax, "x")

    save(fig, "fig_v2_position")
    plt.close(fig)


def fig_retrieval() -> None:
    """Routing recall, latency, and the corrected statistics."""
    fig, axes = plt.subplots(1, 3, figsize=(7.0, 2.35), dpi=300)
    fig.subplots_adjust(wspace=0.46)

    # (a) recall ------------------------------------------------------------
    ax = axes[0]
    methods = ["TF-IDF", "dense", "dense +\nrerank"]
    top1 = [8, 7, 5]
    top5 = [11, 11, 11]
    x = np.arange(3)
    ax.bar(x - 0.18, top1, width=0.34, color=INK, label="Top-1", zorder=2)
    ax.bar(x + 0.18, top5, width=0.34, color=PALE, label="Top-5", zorder=2)
    for xx, a, b in zip(x, top1, top5):
        ax.text(xx - 0.18, a + 0.35, str(a), ha="center", fontsize=5.7)
        ax.text(xx + 0.18, b + 0.35, str(b), ha="center", fontsize=5.7)
    ax.axhline(17, color=MUTED, lw=0.6, linestyle=":", zorder=1)
    ax.text(2.35, 17.25, "17", fontsize=5.2, color=MUTED, ha="right")
    ax.set_xticks(x)
    ax.set_xticklabels(methods, fontsize=5.7)
    ax.set_ylim(0, 18.8)
    ax.set_ylabel("correct (of 17)", fontsize=6.2)
    ax.legend(fontsize=5.2, frameon=False, loc="upper right",
              handlelength=1.0)
    ax.set_title("(a) Routing recall", fontsize=7.0, loc="left", pad=3,
                 fontweight="bold")
    style(ax, "y")

    # (b) latency -----------------------------------------------------------
    ax = axes[1]
    lat = [1.51, 47.0, 391.0]
    bars = ax.bar(np.arange(3), lat, width=0.58,
                  color=[PALE, PALE, WARN], zorder=2)
    for bar, val in zip(bars, lat):
        ax.text(bar.get_x() + bar.get_width() / 2, val * 1.18,
                f"{val:g} ms", ha="center", fontsize=5.6)
    ax.set_yscale("log")
    ax.set_ylim(0.8, 900)
    ax.set_xticks(np.arange(3))
    ax.set_xticklabels(["TF-IDF", "dense", "dense +\nrerank"], fontsize=5.7)
    ax.set_ylabel("p50 latency (ms, log)", fontsize=6.2)
    ax.set_title("(b) Retrieval cost", fontsize=7.0, loc="left", pad=3,
                 fontweight="bold")
    style(ax, "y")

    # (c) corrections -------------------------------------------------------
    ax = axes[2]
    rows = [
        (r"$\sigma$", 6.09, 5.37),
        (r"$\sigma_d$", 7.87, 3.76),
        ("MDE", 2.53, 2.72),
        ("pairs", 3700, 1473),
    ]
    y = np.arange(len(rows))[::-1]
    for yy, (label, was, now) in zip(y, rows):
        ax.plot([was, now], [yy, yy], color=MUTED, lw=1.0, zorder=1)
        ax.plot(was, yy, "o", ms=4.0, color=PALE, markeredgecolor=INK,
                markeredgewidth=0.5, zorder=3)
        ax.plot(now, yy, "o", ms=4.0, color=GOOD, zorder=3)
        fmt = (lambda v: f"{v:,.0f}") if label == "pairs" else (lambda v: f"{v:g}")
        ax.text(was, yy + 0.21, fmt(was), ha="center", fontsize=5.1,
                color="#3d5875")
        ax.text(now, yy - 0.27, fmt(now), ha="center", fontsize=5.1,
                color=GOOD)
    ax.set_xscale("log")
    ax.set_xlim(1.6, 7000)
    ax.set_yticks(y)
    ax.set_yticklabels([r[0] for r in rows], fontsize=5.8)
    ax.set_ylim(-0.6, len(rows) - 0.3)
    ax.set_xlabel("value (log scale)", fontsize=6.2)
    ax.set_title("(c) Reported to recomputed", fontsize=7.0, loc="left",
                 pad=3, fontweight="bold")
    style(ax, "x")

    save(fig, "fig_v2_retrieval")
    plt.close(fig)


def main() -> int:
    print("Generating V2 figures into paper/:")
    fig_design()
    fig_results()
    fig_position()
    fig_retrieval()
    print("Done. Existing fig_arms.pdf / fig_correction.pdf were not touched.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
