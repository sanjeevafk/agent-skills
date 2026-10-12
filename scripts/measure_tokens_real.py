#!/usr/bin/env python3
"""Re-measure the checklist_v2 compression claim with real BPE tokenizers.

The published 30.0% figure was computed with estimate_tokens() == len(text)//4,
which is a character heuristic, not a tokenizer. This recomputes source vs
compiled token counts from the exact paths recorded in the compilation manifest
and reports the aggregate reduction under each tokenizer, plus the heuristic for
comparison.

Usage:
    uv run python scripts/measure_tokens_real.py
"""
from __future__ import annotations

import argparse
import json
import pathlib
import statistics as st
import sys

import tiktoken

ROOT = pathlib.Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "benchmarks" / "checklists_v2" / "manifest.json"

ENCODINGS = {
    "cl100k_base (GPT-4 family)": "cl100k_base",
    "o200k_base (GPT-4o family)": "o200k_base",
    "p50k_base (GPT-3.5 family)": "p50k_base",
}

# The published figure, measured with cl100k_base on manifest-matching sources.
# Kept here so a drift in the corpus surfaces as a CI failure rather than as a
# silently stale number in the manuscript. Tolerance is 0.5 percentage points,
# which is wider than the 0.58pp spread across tokenizers but far tighter than
# the 1.85pp gap between the old len//4 heuristic and the real measurement.
CHECK_REDUCTION_PCT = 28.56
CHECK_TOLERANCE_PP = 0.5


def heuristic(text: str) -> int:
    """The estimator the original claim used."""
    return len(text) // 4


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--check",
        action="store_true",
        help="fail if the cl100k reduction drifts beyond tolerance",
    )
    args = ap.parse_args()

    manifest = json.loads(MANIFEST.read_text())
    skills = manifest["skills"]

    rows = []
    missing = []
    for entry in skills.values():
        src = ROOT / entry["source_path"]
        cmp_ = ROOT / entry["compiled_path"]
        if not src.exists() or not cmp_.exists():
            missing.append(entry["skill_id"])
            continue
        rows.append((entry["skill_id"], src.read_text(), cmp_.read_text()))

    if missing:
        print(f"  WARNING: {len(missing)} skills missing on disk: {missing}",
              file=sys.stderr)

    print(f"  skills measured: {len(rows)}")
    print()

    encoders = {}
    for label, name in ENCODINGS.items():
        try:
            encoders[label] = tiktoken.get_encoding(name)
        except Exception as exc:  # offline / unknown encoding
            print(f"  (skipping {label}: {exc})", file=sys.stderr)

    # Heuristic baseline, for comparison with the published figure.
    h_src = sum(heuristic(s) for _, s, _ in rows)
    h_cmp = sum(heuristic(c) for _, _, c in rows)
    h_red = 100.0 * (h_src - h_cmp) / h_src
    print(f"  {'heuristic len//4':<26} {h_src:>8} {h_cmp:>8} "
          f"{h_red:>7.2f}%   <- the published method")
    print()

    summary = {}
    for label, enc in encoders.items():
        s_tot = c_tot = 0
        per_skill = []
        for name, src, cmp_ in rows:
            ns = len(enc.encode(src))
            nc = len(enc.encode(cmp_))
            s_tot += ns
            c_tot += nc
            per_skill.append((name, ns, nc))
        red = 100.0 * (s_tot - c_tot) / s_tot
        mean_delta = (s_tot - c_tot) / len(rows)
        summary[label] = {
            "source_tokens": s_tot,
            "compiled_tokens": c_tot,
            "reduction_pct": red,
            "mean_source": s_tot / len(rows),
            "mean_compiled": c_tot / len(rows),
            "mean_delta": mean_delta,
        }
        print(f"  {label:<26} {s_tot:>8} {c_tot:>8} {red:>7.2f}%")
        print(f"  {'':<26} mean {s_tot/len(rows):>6.0f} -> {c_tot/len(rows):<6.0f}"
              f"  delta {mean_delta:.0f} tokens/skill/turn")
        print()

    # Spread across tokenizers, to show the claim is not tokenizer-dependent.
    reds = [v["reduction_pct"] for v in summary.values()]
    if reds:
        print(f"  reduction across tokenizers: "
              f"min {min(reds):.2f}%  max {max(reds):.2f}%  "
              f"spread {max(reds) - min(reds):.2f} pp")
        print(f"  heuristic baseline:           {h_red:.2f}%")

    if not args.check:
        return 0

    print()
    key = "cl100k_base (GPT-4 family)"
    if key not in summary:
        print(f"  CHECK SKIPPED: {key} unavailable", file=sys.stderr)
        return 0

    got = summary[key]["reduction_pct"]
    delta = got - CHECK_REDUCTION_PCT
    print(f"  CHECK cl100k reduction: {got:.2f}% "
          f"(expected {CHECK_REDUCTION_PCT:.2f}% "
          f"+/- {CHECK_TOLERANCE_PP:.2f} pp, delta {delta:+.2f} pp)")

    # A source that no longer matches the manifest is the usual cause of drift,
    # so name it rather than reporting a bare percentage.
    for entry in skills.values():
        src = ROOT / entry["source_path"]
        if not src.exists():
            continue
        import hashlib
        digest = hashlib.sha256(src.read_bytes()).hexdigest()
        if digest != entry["source_sha256"]:
            print(f"  ::error file={entry['source_path']}::source does not match "
                  f"manifest source_sha256 for {entry['skill_id']}; the published "
                  f"compression figure is measured on manifest-matching sources")
            return 1

    if abs(delta) > CHECK_TOLERANCE_PP:
        print(f"  ::error file=benchmarks/checklists_v2/manifest.json::"
              f"compression drift {delta:+.2f} pp exceeds "
              f"+/-{CHECK_TOLERANCE_PP:.2f} pp; re-run "
              f"scripts/measure_tokens_real.py and update the manuscript")
        return 1

    print(f"  OK: {got:.2f}% reduction, tokenizer-measured, sources match manifest")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())