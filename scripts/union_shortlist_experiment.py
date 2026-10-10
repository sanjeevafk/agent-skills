#!/usr/bin/env python3
"""
union_shortlist_experiment.py — is the routing bottleneck retrieval or reranking?

Motivation
----------
The corrected Level 1 study (§8.7) found that a lexical retriever and a dense
retriever agree on only 4 of 17 top-1 answers, while both reach the same Top-5
recall (11/17). That pattern — different winners, identical recall — says the two
retrievers fail on *different* tasks, so a union of their shortlists should
surface the gold skill on more queries than either alone.

This script measures that directly, and then asks the follow-up question that
matters for design: **does the existing reranker realise the extra recall, or
destroy it?**

Reported quantities
--------------------
  recall@5 per retriever and for the union shortlist
  the union ORACLE ceiling — how many tasks a *perfect* reranker over the union
  would get right, which upper-bounds any reranking strategy
  what Julia-1 actually achieves over that union
  the shortfall, i.e. how many recoverable tasks the reranker throws away

No judge model and no API calls are involved; this is pure retrieval plus a local
decision model, so it costs nothing to reproduce.

Usage:
    uv run python scripts/union_shortlist_experiment.py
    uv run python scripts/union_shortlist_experiment.py --k 3
    uv run python scripts/union_shortlist_experiment.py --no-rerank
"""

from __future__ import annotations

import argparse
import json
import pathlib
import statistics as st
import sys
import time

import numpy as np

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

TASKS_FILE = REPO / "benchmarks" / "tasks_ieee.json"
INDEX_FILE = REPO / "skills_canonical.json"
OUT_FILE = REPO / "benchmarks" / "union_shortlist_results.json"

FREEBIES = {"sec-webhook-audit-ieee"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=5, help="candidates per retriever")
    ap.add_argument("--no-rerank", action="store_true",
                    help="skip the Julia-1 pass; report recall only")
    args = ap.parse_args()

    from benchmark_router import GOLD_OVERRIDES, build_tfidf_scores, tfidf_rank
    from julia_router import JuliaSkillRouter

    index = json.loads(INDEX_FILE.read_text(encoding="utf-8"))["skills"]
    tfidf_vectors = build_tfidf_scores(index)

    router = JuliaSkillRouter()
    skill_names = [s["name"] for s in router.skills]
    tasks = json.loads(TASKS_FILE.read_text(encoding="utf-8"))
    gold = {t["id"]: GOLD_OVERRIDES.get(t["id"], t["skill"]) for t in tasks}

    rows = []
    for task in tasks:
        if task["id"] in FREEBIES:
            continue
        g, q = gold[task["id"]], task["prompt"]

        t0 = time.perf_counter()
        lex = tfidf_rank(q, index, tfidf_vectors, args.k)
        lex_ms = (time.perf_counter() - t0) * 1000

        t0 = time.perf_counter()
        q_vec = router.bi_encoder.encode(
            [f"Represent this sentence for searching relevant passages: {q}"],
            normalize_embeddings=True,
        )
        sims = router.vectors @ np.asarray(q_vec, dtype=np.float32).reshape(-1)
        order = np.argsort(-sims)
        dense = [skill_names[i] for i in order[:args.k]]
        dense_ms = (time.perf_counter() - t0) * 1000

        # Union: lexical first, dense appended, order-preserving dedupe.
        union = list(dict.fromkeys(lex + dense))

        row = {
            "task_id": task["id"],
            "gold": g,
            "tfidf_top1": lex[0] if lex else None,
            "tfidf_top5": lex,
            "dense_top1": dense[0] if dense else None,
            "dense_top5": dense,
            "union": union,
            "union_size": len(union),
            "tfidf_recall": g in lex,
            "dense_recall": g in dense,
            "union_recall": g in union,
            "union_lexfirst_top1_match": bool(union) and union[0] == g,
            "tfidf_ms": round(lex_ms, 2),
            "dense_ms": round(dense_ms, 2),
        }

        if not args.no_rerank:
            # Julia-1 caps at 20 options; union@5 averages 9 so this rarely binds.
            capped = union[:20]
            if len(capped) < 2:
                capped = (capped * 2)[:2]
            t0 = time.perf_counter()
            decision = router._decide(
                q,
                [router._option_text(s, index[s].get("description") or "") for s in capped],
            )
            pick = capped[int(decision["index"])]
            row["rerank_pick"] = pick
            row["rerank_top1_match"] = pick == g
            row["rerank_overrode_correct"] = g in union and pick != g
            row["rerank_ms"] = round((time.perf_counter() - t0) * 1000, 2)

        rows.append(row)
        rr = "" if args.no_rerank else (
            f" rerank={row['rerank_pick'][:24]:24}{' HIT' if row['rerank_top1_match'] else ''}"
            + ("  <- overrode a correct shortlist hit" if row["rerank_overrode_correct"] else "")
        )
        print(f"  {task['id'][:30]:30} lex={'Y' if row['tfidf_recall'] else 'n'} "
              f"dense={'Y' if row['dense_recall'] else 'n'} "
              f"union={'Y' if row['union_recall'] else 'n'} "
              f"(size {row['union_size']:2}){rr}")

    n = len(rows)
    recall = {
        "tfidf": sum(r["tfidf_recall"] for r in rows),
        "dense": sum(r["dense_recall"] for r in rows),
        "union": sum(r["union_recall"] for r in rows),
    }
    summary = {
        "k_per_retriever": args.k,
        "n_tasks": n,
        "recall_at_k": recall,
        "mean_union_size": round(st.mean(r["union_size"] for r in rows), 2),
        "tfidf_top1": sum(1 for r in rows if r["tfidf_top1"] == r["gold"]),
        "dense_top1": sum(1 for r in rows if r["dense_top1"] == r["gold"]),
        "union_lexfirst_top1": sum(1 for r in rows if r["union_lexfirst_top1_match"]),
    }
    if not args.no_rerank:
        summary["rerank_top1"] = sum(1 for r in rows if r["rerank_top1_match"])
        summary["oracle_ceiling"] = recall["union"]
        summary["rerank_overrode_correct"] = sum(1 for r in rows if r["rerank_overrode_correct"])
        summary["rerank_recall_lost"] = recall["union"] - summary["rerank_top1"]

    print("\n" + "=" * 70)
    print(f"{'metric':<34}{'value':>10}")
    print("-" * 70)
    print(f"{'recall@' + str(args.k) + '  lexical':<34}{recall['tfidf']}/{n:>9}")
    print(f"{'recall@' + str(args.k) + '  dense':<34}{recall['dense']}/{n:>9}")
    print(f"{'recall@' + str(args.k) + '  UNION':<34}{recall['union']}/{n:>9}")
    print(f"{'mean union size':<34}{summary['mean_union_size']:>10}")
    print(f"{'top-1  lexical':<34}{summary['tfidf_top1']}/{n:>9}")
    print(f"{'top-1  dense':<34}{summary['dense_top1']}/{n:>9}")
    print(f"{'top-1  union (lex-first)':<34}{summary['union_lexfirst_top1']}/{n:>9}")
    if not args.no_rerank:
        print(f"{'top-1  union + Julia-1 rerank':<34}{summary['rerank_top1']}/{n:>9}")
        print(f"{'ORACLE ceiling over union':<34}{summary['oracle_ceiling']}/{n:>9}")
        print(f"{'rerank overrode a correct hit':<34}{summary['rerank_overrode_correct']:>10}")
        print(f"{'recall lost to reranking':<34}{summary['rerank_recall_lost']:>10}")
    print("=" * 70)

    payload = {
        "metadata": {
            "experiment": "union shortlist: lexical + dense",
            "k_per_retriever": args.k,
            "catalogue": len(index),
            "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "rerank_enabled": not args.no_rerank,
        },
        "summary": summary,
        "task_runs": rows,
    }
    OUT_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"\nwrote {OUT_FILE.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())