#!/usr/bin/env python3
"""
benchmark_router.py — Level 1 Benchmark: Zero-cost hit-rate and latency evaluation across 18 IEEE SE tasks.

Compares:
1. Baseline: Naive keyword/token matching (scripts/search_skills.py logic)
2. Laya Router: Stage 1 precomputed vector dot-product + Stage 2 Laya cross-encoder
"""

import json
import re
import sys
import time
from pathlib import Path
import numpy as np

REPO_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(REPO_ROOT / 'scripts'))

TASKS_FILE = REPO_ROOT / 'benchmarks' / 'tasks_ieee.json'
INDEX_FILE = REPO_ROOT / 'skills.json'
NPY_FILE = REPO_ROOT / 'skills_embeddings.npy'
MANIFEST_FILE = REPO_ROOT / 'skills_manifest.json'

# Ground-truth alias mapping for task spec variations
SKILL_ALIASES = {
    "tdd": "tdd-workflow",
    "debugging-code": "systematic-debugging"
}

def normalize_skill_name(name: str) -> str:
    return SKILL_ALIASES.get(name, name)

def naive_keyword_search(query: str, skills_dict: dict, top_k: int = 5):
    tokens = [t.lower() for t in re.findall(r'\w+', query) if len(t) > 2]
    scored = []
    for name, meta in skills_dict.items():
        score = 0
        desc = meta.get('description', '').lower()
        tags = [t.lower() for t in meta.get('tags', [])]
        category = meta.get('category', '').lower()

        for qt in tokens:
            if qt == name.lower():
                score += 100
            elif qt in name.lower():
                score += 30
            if qt in desc:
                score += 15
            if any(qt in t for t in tags):
                score += 20
            if qt in category:
                score += 10
        if score > 0:
            scored.append((score, name))

    scored.sort(key=lambda x: x[0], reverse=True)
    results = [s[1] for s in scored[:top_k]]
    return results

def run_benchmark():
    if not TASKS_FILE.exists():
        print(f"Error: {TASKS_FILE} not found.")
        sys.exit(1)

    print("Loading test dataset and index...")
    with open(TASKS_FILE, 'r', encoding='utf-8') as f:
        tasks = json.load(f)

    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        skills_data = json.load(f)
    skills_dict = skills_data['skills']

    # Initialize Laya router
    from laya_router import LayaSkillRouter
    router = LayaSkillRouter()

    print(f"\nRunning Level 1 Benchmark across {len(tasks)} IEEE Tasks (440 Skills)...")
    print("=" * 95)
    print(f"{'Task ID':<30} | {'Expected Skill':<22} | {'Laya Top-1':<22} | {'S1-Top5':<7} | {'Match':<5}")
    print("-" * 95)

    laya_top1_hits = 0
    laya_top5_hits = 0
    kw_top1_hits = 0
    kw_top5_hits = 0

    embed_times = []
    dot_times = []
    predict_times = []
    total_times = []

    task_results = []

    for t in tasks:
        task_id = t['id']
        expected_raw = t['skill']
        expected = normalize_skill_name(expected_raw)
        prompt = t['prompt']

        # 1. Baseline Keyword Search
        kw_candidates = naive_keyword_search(prompt, skills_dict, top_k=5)
        kw_top1 = kw_candidates[0] if kw_candidates else None
        if kw_top1 == expected:
            kw_top1_hits += 1
        if expected in kw_candidates:
            kw_top5_hits += 1

        # 2. Laya Two-Stage Router
        res = router.route(prompt, top_k=5)
        laya_top1 = res['selected_skill']
        laya_top5 = [cand['name'] for cand in res['shortlisted_top_k']]

        s = res['stats']
        embed_times.append(s['query_embed_ms'])
        dot_times.append(s['shortlist_dot_ms'])
        predict_times.append(s['laya_predict_ms'])
        total_times.append(s['query_embed_ms'] + s['shortlist_dot_ms'] + s['laya_predict_ms'])

        top1_match = (laya_top1 == expected)
        top5_match = (expected in laya_top5)

        if top1_match:
            laya_top1_hits += 1
        if top5_match:
            laya_top5_hits += 1

        match_str = "YES" if top1_match else ("(TOP5)" if top5_match else "NO")
        in_top5_str = "YES" if top5_match else "NO"

        print(f"{task_id:<30} | {expected:<22} | {laya_top1:<22} | {in_top5_str:<7} | {match_str:<5}")

        task_results.append({
            "task_id": task_id,
            "expected": expected,
            "laya_top1": laya_top1,
            "laya_top5": laya_top5,
            "top1_match": top1_match,
            "top5_match": top5_match,
            "kw_top1": kw_top1,
            "kw_top5": kw_candidates,
            "stats": s
        })

    n = len(tasks)
    print("=" * 95)
    print("\nBENCHMARK RESULTS SUMMARY (N = 18 Tasks):")
    print(f"  • Laya Router Top-1 Accuracy:  {laya_top1_hits}/{n} ({laya_top1_hits / n * 100:.1f}%)")
    print(f"  • Laya Stage 1 Top-5 Recall:   {laya_top5_hits}/{n} ({laya_top5_hits / n * 100:.1f}%)")
    print(f"  • Baseline Keyword Top-1 Acc:  {kw_top1_hits}/{n} ({kw_top1_hits / n * 100:.1f}%)")
    print(f"  • Baseline Keyword Top-5 Rec:  {kw_top5_hits}/{n} ({kw_top5_hits / n * 100:.1f}%)")

    print("\nLATENCY PROFILING (Across 18 Tasks, Pure CPU):")
    print(f"  • Stage 1 Vector Dot Product:   mean={np.mean(dot_times):.2f} ms, p50={np.median(dot_times):.2f} ms, p95={np.percentile(dot_times, 95):.2f} ms (across 440 skills)")
    print(f"  • Stage 1 Query Embedding:     mean={np.mean(embed_times):.2f} ms, p50={np.median(embed_times):.2f} ms, p95={np.percentile(embed_times, 95):.2f} ms")
    print(f"  • Stage 2 Laya Cross-Encoder:   mean={np.mean(predict_times):.2f} ms, p50={np.median(predict_times):.2f} ms, p95={np.percentile(predict_times, 95):.2f} ms")
    print(f"  • Total Pipeline Latency:       mean={np.mean(total_times):.2f} ms, p50={np.median(total_times):.2f} ms, p95={np.percentile(total_times, 95):.2f} ms")

    # Save benchmark trace
    output_report = REPO_ROOT / 'benchmarks' / 'router_level1_results.json'
    with open(output_report, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "total_tasks": n,
            "metrics": {
                "laya_top1_accuracy": laya_top1_hits / n,
                "laya_top5_recall": laya_top5_hits / n,
                "keyword_top1_accuracy": kw_top1_hits / n,
                "keyword_top5_recall": kw_top5_hits / n,
                "latency_ms": {
                    "dot_product_p50": float(np.median(dot_times)),
                    "dot_product_p95": float(np.percentile(dot_times, 95)),
                    "query_embed_p50": float(np.median(embed_times)),
                    "laya_predict_p50": float(np.median(predict_times)),
                    "total_pipeline_p50": float(np.median(total_times))
                }
            },
            "task_runs": task_results
        }, f, indent=2)

    print(f"\nFull benchmark trace saved to: {output_report}\n")

if __name__ == '__main__':
    run_benchmark()
