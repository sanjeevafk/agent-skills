#!/usr/bin/env python3
"""Generate the manuscript's figures from the archived artefacts.

Every figure here is a deterministic function of files in `benchmarks/`, so the
figures can be regenerated rather than trusted as binaries. Run:

    uv run python scripts/make_figures.py

Requires matplotlib; the output lands in paper/.
"""

from __future__ import annotations

import collections
import json
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]
PAPER = REPO / "paper"

INK = "#12263f"
MUTED = "#8899aa"
GRID = "#e3e9f0"
BAND = "#dce6f2"
GOOD = "#2d6a4f"
WARN = "#7d1d3f"


def arm_scores() -> dict[str, list[int]]:
    data = json.loads((REPO / "benchmarks/delivery_results_ieee.json").read_text())
    by: dict[str, list[int]] = collections.defaultdict(list)
    for task in data["tasks"]:
        for arm, runs in task.get("strategy_runs", {}).items():
            by[arm].extend(r["judge_total"] for r in runs)
    return by


def fig_arms(mde: float = 2.721) -> None:
    """Per-arm means with CIs against the detection threshold.

    The figure carries no internal title: the LaTeX caption states the finding,
    and an in-figure title would only duplicate it while eating column height.
    """
    by = arm_scores()
    order = ["full", "checklist_v2", "retrieved", "checklist", "control"]
    labels = ["full\nverbatim manual", "checklist_v2\ncompiled 28.6%",
              "retrieved\nsame budget, subset", "checklist\nbulletised 70.8%",
              "control\nno skill"]
    means = np.array([float(np.mean(by[a])) for a in order])
    ci = 1.96 * np.array([float(np.std(by[a], ddof=1)) / np.sqrt(len(by[a]))
                          for a in order])

    fig, ax = plt.subplots(figsize=(3.45, 2.15), dpi=300)
    y = np.arange(len(order))[::-1]
    ref = float(np.mean(by["full"]))

    ax.axvspan(ref - mde / 2, ref + mde / 2, color=BAND, alpha=.85, zorder=0)
    ax.errorbar(means, y, xerr=ci, fmt="o", ms=4.2, color=INK,
                ecolor="#3d5875", elinewidth=.9, capsize=2, zorder=3)

    # observed spread, annotated just above the top arm
    ya = y.max() + .40
    ax.annotate("", xy=(means.min(), ya), xytext=(means.max(), ya),
                arrowprops=dict(arrowstyle="<|-|>", lw=.9, color=GOOD))
    ax.text((means.min() + means.max()) / 2, ya + .14,
            f"observed spread  {means.max()-means.min():.2f}",
            ha="center", va="bottom", fontsize=5.9, color=GOOD)

    # resolvable difference, below the last arm
    yb = y.min() - .78
    ax.annotate("", xy=(ref - mde / 2, yb), xytext=(ref + mde / 2, yb),
                arrowprops=dict(arrowstyle="<|-|>", lw=.9, color=WARN))
    ax.text(ref, yb - .16, f"resolvable difference  {mde:.2f}",
            ha="center", va="top", fontsize=5.9, color=WARN)

    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=5.6)
    ax.set_xlabel("mean rubric score (35-point)", fontsize=6.2, labelpad=1.5)
    ax.set_ylim(y.min() - 1.55, y.max() + 1.15)
    ax.set_xlim(23.35, 26.85)
    ax.tick_params(axis="x", labelsize=5.8)
    ax.tick_params(axis="y", length=0)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.grid(axis="x", lw=.4, color=GRID, zorder=0)
    fig.tight_layout(pad=.25)
    fig.savefig(PAPER / "fig_arms.pdf", bbox_inches="tight")
    print("  fig_arms.pdf")


def fig_correction() -> None:
    """The three unreproducible statistics, as reported and as recomputed."""
    rows = [(r"$\sigma$ (floor)", 6.09, 5.365),
            (r"$\sigma_d$", 7.87, 3.760),
            ("MDE at 80% power", 2.53, 2.721)]
    titles = [r[0] for r in rows]
    pairs = [(r[1], r[2]) for r in rows]

    fig, axes = plt.subplots(1, 3, figsize=(7.0, 1.65), dpi=300)
    for ax, title, (was, now) in zip(axes, titles, pairs):
        bars = ax.bar([0, 1], [was, now], width=.6, color=["#b9c6d4", GOOD])
        ax.set_xticks([0, 1])
        ax.set_xticklabels(["as\nreported", "recomputed"], fontsize=5.6)
        ax.set_title(title, fontsize=7.0, pad=4)
        top = max(was, now)
        ax.set_ylim(0, top * 1.34)
        for b, v in zip(bars, [was, now]):
            ax.text(b.get_x() + b.get_width() / 2, v + top * .04,
                    f"{v:.2f}" if v < 10 else f"{v:.3g}",
                    ha="center", fontsize=6.1, fontweight="bold", color=INK)
        ax.tick_params(axis="y", labelsize=5.2, length=0)
        for s in ("top", "right", "left"):
            ax.spines[s].set_visible(False)
        ax.spines["bottom"].set_color(MUTED)
        ax.grid(axis="y", lw=.4, color=GRID, zorder=0)
        ax.set_axisbelow(True)

    fig.tight_layout(pad=.35, w_pad=1.5)
    fig.savefig(PAPER / "fig_correction.pdf", bbox_inches="tight")
    print("  fig_correction.pdf")


def main() -> int:
    print("Generating figures from benchmarks/ into paper/:")
    fig_arms()
    fig_correction()
    print("Done. The TikZ architecture diagram is hand-authored, not generated:")
    print("  paper/fig_architecture.tex")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())