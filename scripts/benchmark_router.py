#!/usr/bin/env python3
"""
benchmark_router.py — Level 1: retrieval hit-rate and latency across the 18 IEEE SE tasks.

Compares two routing methods over the same catalogue and the same queries:

  1. `tfidf`     lexical baseline, unigram TF-IDF over skill descriptions
  2. `two_stage` Stage 1 bi-encoder shortlist + Stage 2 Julia-1 decision
                 (scripts/julia_router.py)

Methodological corrections relative to the previous run
-------------------------------------------------------
* The lexical baseline is now genuine TF-IDF. The earlier "TF-IDF baseline"
  was a hand-weighted keyword scorer (exact-name 100, substring 30, tag 20,
  description 15, category 10) that scored 0/18 Top-1 by construction. The
  scoring function is ported from the delivery harness
  (`skill_delivery_experiment.py:tfidf_score`) so this baseline matches the
  `retrieved` arm of the macro benchmark.
* Gold labels are canonical and asserted to exist in the catalogue. Two tasks
  previously carried a router gold label that disagreed with the benchmark's
  skill binding; both are now resolved explicitly (see GOLD_OVERRIDES).
* The freebie task is reported but excluded from the headline number:
  `sec-webhook-audit-ieee`'s prompt opens with the literal skill name
  ("Security-review a FastAPI payment webhook..."), so any retriever that
  matches on names scores it for free.

Usage:
    uv run python scripts/benchmark_router.py
    uv run python scripts/benchmark_router.py --no-stage2   # Stage 1 only
"""

from __future__ import annotations

import argparse
import json
import math
import re
import statistics as st
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(REPO_ROOT / "scripts"))

TASKS_FILE = REPO_ROOT / "benchmarks" / "tasks_ieee.json"
INDEX_FILE = REPO_ROOT / "skills.json"
OUT_FILE = REPO_ROOT / "benchmarks" / "router_level1_results.json"

# Tasks whose benchmark-bound skill is the wrong label for retrieval purposes.
#   sre-node-leak-ieee binds `debugging-code`, which is not in the catalogue at
#   all (absent from disk), so it is unroutable by construction. The router's
#   `systematic-debugging` is present and is the better label for the task.
#   qa-ratelimiter-tdd-ieee binds `tdd`, which the prior router mislabelled as
#   `tdd-workflow`; the benchmark binding is canonical and is also what the
#   §8.4 ablation actually used, so `tdd` wins.
GOLD_OVERRIDES = {
    "sre-node-leak-ieee": "systematic-debugging",
    "qa-ratelimiter-tdd-ieee": "tdd",
}

# Prompt leaks the gold skill name verbatim; excluded from the headline rate.
FREEBIES = {"sec-webhook-audit-ieee"}


# --------------------------------------------------------------------------
# Lexical baseline: unigram TF-IDF
# --------------------------------------------------------------------------
def tokenize(text: str) -> list[str]:
    return re.findall(r"\b[a-z]{3,}\b", text.lower())


def build_tfidf_scores(skills: dict) -> dict:
    """Precompute per-skill TF-IDF vectors once (dict-of-weights)."""
    doc_tokens = {
        name: tokenize(meta.get("description", "") or name)
        for name, meta in skills.items()
    }
    n_docs = len(doc_tokens)
    df: dict[str, int] = {}
    for tokens in doc_tokens.values():
        for t in set(tokens):
            df[t] = df.get(t, 0) + 1

    vectors = {}
    for name, tokens in doc_tokens.items():
        if not tokens:
            vectors[name] = {}
            continue
        tf = {}
        for t in tokens:
            tf[t] = tf.get(t, 0) + 1
        total = len(tokens)
        vec = {}
        for t, count in tf.items():
            idf = math.log((n_docs + 1) / (df[t] + 1)) + 1
            vec[t] = (count / total) * idf
        vectors[name] = vec
    return vectors


def tfidf_rank(query: str, skills: dict, vectors: dict, top_k: int) -> list[str]:
    q_tokens = set(tokenize(query))
    scored = []
    for name, vec in vectors.items():
        if not vec:
            continue
        score = sum(w for t, w in vec.items() if t in q_tokens)
        if score > 0:
            scored.append((score, name))
    scored.sort(key=lambda x: (-x[0], x[1]))
    return [n for _, n in scored[:top_k]]


# --------------------------------------------------------------------------
def resolve_gold(task: dict, skills: dict) -> str | None:
    """Canonical gold label for a task, asserted to be routable."""
    gold = GOLD_OVERRIDES.get(task["id"], task["skill"])
    if gold not in skills:
        raise SystemExit(
            f"gold label {gold!r} for {task['id']} is absent from the catalogue; "
            "add an override or restore the skill."
        )
    return gold


def assert_no_prompt_leak(tasks: list[dict], gold_by_id: dict[str, str]) -> list[str]:
    """Report tasks whose prompt contains the gold label's distinctive tokens."""
    leaks = []
    for t in tasks:
        gold = gold_by_id.get(t["id"], "")
        words = [w for w in re.split(r"[^a-z]+", gold.lower()) if len(w) > 3]
        prompt_tokens = set(tokenize(t["prompt"]))
        if words and all(w in prompt_tokens for w in words):
            leaks.append(t["id"])
    return leaks


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--top-k", type=int, default=5)
    ap.add_argument("--no-stage2", action="store_true",
                    help="Stage 1 dense retrieval only; skips the Julia-1 decision")
    args = ap.parse_args()

    tasks = json.loads(TASKS_FILE.read_text(encoding="utf-8"))
    index = json.loads(INDEX_FILE.read_text(encoding="utf-8"))
    skills = index["skills"]

    print(f"catalogue: {len(skills)} skills | tasks: {len(tasks)} | top_k={args.top_k}\n")

    gold_by_id = {t["id"]: resolve_gold(t, skills) for t in tasks}
    leaks = assert_no_prompt_leak(tasks, gold_by_id)
    print(f"prompt-leak tasks detected: {leaks or 'none'}")
    print(f"excluded as freebies      : {sorted(FREEBIES & set(gold_by_id))}\n")

    vectors = build_tfidf_scores(skills)

    router = None
    if not args.no_stage2:
        from julia_router import JuliaSkillRouter

        router = JuliaSkillRouter()
        print(f"two-stage router ready: {router.n_skills} skills\n")

    rows = []
    for t in tasks:
        gold = gold_by_id[t["id"]]
        query = t["prompt"]

        t0 = time.perf_counter()
        kw_top5 = tfidf_rank(query, skills, vectors, args.top_k)
        tf_ms = (time.perf_counter() - t0) * 1000

        if router:
            res = router.route(query, top_k=args.top_k)
            dense_top5 = [c["name"] for c in res["shortlisted"]]
            dense_top1 = res["selected_skill"]
            stats = res["stats"]
        else:
            order = router_top1 = None
            dense_top5, dense_top1 = [], None
            stats = {}

        rows.append({
            "task_id": t["id"],
            "gold": gold,
            "freebie": t["id"] in FREEBIES,
            "tfidf_top1": kw_top5[0] if kw_top5 else None,
            "tfidf_top5": kw_top5,
            "tfidf_top1_match": bool(kw_top5) and kw_top5[0] == gold,
            "tfidf_top5_match": gold in kw_top5,
            "tfidf_ms": round(tf_ms, 2),
            "two_stage_top1": dense_top1,
            "two_stage_top5": dense_top5,
            "two_stage_top1_match": dense_top1 == gold,
            "two_stage_top5_match": gold in dense_top5,
            "two_stage_confidence": res["confidence"] if router else None,
            "latency": stats,
        })

        mark = " *" if t["id"] in FREEBIES else ""
        print(
            f"  {t['id'][:32]:32} gold={gold[:24]:24} "
            f"tfidf={'Y' if rows[-1]['tfidf_top1_match'] else 'n'}/"
            f"{'Y' if rows[-1]['tfidf_top5_match'] else 'n'}  "
            f"2stage={'Y' if rows[-1]['two_stage_top1_match'] else 'n'}/"
            f"{'Y' if rows[-1]['two_stage_top5_match'] else 'n'}{mark}"
        )

    scored = [r for r in rows if not r["freebie"]]
    summary = {
        "n_total": len(rows),
        "n_scored": len(scored),
        "n_excluded_freebie": len(rows) - len(scored),
        "catalogue_size": len(skills),
        "top_k": args.top_k,
    }

    print("\n" + "=" * 66)
    print(f"{'method':<12}{'Top-1':>12}{'Top-5':>12}   (excluding {len(rows) - len(scored)} freebie)")
    print("-" * 66)
    for label, k1, k5 in (
        ("tfidf", "tfidf_top1_match", "tfidf_top5_match"),
        ("two_stage", "two_stage_top1_match", "two_stage_top5_match"),
    ):
        if args.no_stage2 and label == "two_stage":
            continue
        t1 = sum(1 for r in scored if r[k1])
        t5 = sum(1 for r in scored if r[k5])
        n = len(scored)
        print(f"{label:<12}{t1}/{n} ({100*t1/n:.1f}%){t5}/{n} ({100*t5/n:.1f}%)")
    print("=" * 66)

    lat = [r["latency"].get("total_ms") for r in rows if r.get("latency")]
    if lat:
        print(f"two-stage latency ms: p50={st.median(lat):.1f} "
              f"mean={st.mean(lat):.1f} max={max(lat):.1f}")
    tf_lat = [r["tfidf_ms"] for r in rows]
    print(f"tfidf latency ms   : p50={st.median(tf_lat):.2f} max={max(tf_lat):.2f}")

    payload = {
        "metadata": {
            "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "benchmark": "Level 1 retrieval hit-rate",
            "baseline": "unigram TF-IDF (ported from skill_delivery_experiment.py)",
            "router": "BAAI/bge-small-en-v1.5 + SupersonicLabs/Julia-1",
            "stage2_enabled": not args.no_stage2,
            "gold_overrides": GOLD_OVERRIDES,
            "excluded_freebie_tasks": sorted(FREEBIES),
            "catalogue_size": len(skills),
        },
        "summary": summary,
        "task_runs": rows,
    }
    OUT_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"\nwrote {OUT_FILE.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())