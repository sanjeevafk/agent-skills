#!/usr/bin/env python3
"""
run_level2_benchmark.py — Level 2 End-to-End Code Generation & Blind Judge Evaluation.

Compares:
  - Arm A: 'retrieved_tfidf' (The IEEE paper's lexical TF-IDF section retrieval baseline)
  - Arm B: 'laya_dense_routed' (Two-stage BGE-small + Laya router pulling top-1 skill checklist_v2 from 440 skills)

Executor: Qwen 3.7 Flash via cmd CLI
Judge: DeepSeek V4 Pro via cmd CLI (blind 35-point rubric evaluation)
"""

import json
import os
import random
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

TASKS_FILE = ROOT / "benchmarks" / "tasks_ieee.json"
CHECKLIST_V2_DIR = ROOT / "benchmarks" / "checklists_v2"
OUTPUT_FILE = ROOT / "benchmarks" / "level2_results.json"

JUDGE_CRITERIA = ["correctness", "completeness", "maintainability", "architecture",
                  "security", "reasoning_quality", "instruction_adherence"]

def tokenize(text: str) -> list[str]:
    return [t.lower() for t in re.findall(r"\w+", text) if len(t) > 2]

def parse_sections(skill_md: str) -> list[dict]:
    sections = []
    current_heading = "__preamble__"
    current_lines = []
    for line in skill_md.splitlines():
        if line.startswith("#"):
            if current_lines:
                sections.append({"heading": current_heading, "body": "\n".join(current_lines)})
                current_lines = []
            current_heading = line.strip()
        else:
            current_lines.append(line)
    if current_lines:
        sections.append({"heading": current_heading, "body": "\n".join(current_lines)})
    return sections

def tfidf_score(query_tokens: set[str], doc: str, all_docs: list[dict]) -> float:
    doc_tokens = tokenize(doc)
    if not doc_tokens:
        return 0.0
    N = len(all_docs)
    score = 0.0
    for qt in query_tokens:
        tf = doc_tokens.count(qt) / len(doc_tokens)
        df = sum(1 for d in all_docs if qt in tokenize(d["body"]))
        idf = 1.0 + (N / (1.0 + df))
        score += tf * idf
    return score

def build_retrieved_tfidf_prompt(task_skill: str, prompt: str) -> tuple[str, int]:
    skill_file = ROOT / "skills" / task_skill / "SKILL.md"
    skill_md = skill_file.read_text(encoding="utf-8") if skill_file.exists() else ""
    sections = parse_sections(skill_md)
    query_tokens = set(tokenize(prompt))
    scored = [(tfidf_score(query_tokens, s["body"], sections), s) for s in sections]
    scored.sort(key=lambda x: x[0], reverse=True)

    target_chars = int(len(skill_md) * 0.15)
    selected = []
    total_chars = 0
    for score, section in scored:
        body = f"{section['heading']}\n{section['body']}"
        if total_chars + len(body) > target_chars and selected:
            break
        selected.append(body)
        total_chars += len(body)

    retrieved_context = "\n\n".join(selected)
    full_prompt = f"[RELEVANT SKILL CONTEXT (retrieved TF-IDF)]\n{retrieved_context}\n\n[TASK]\n{prompt}\n\n[OUTPUT INSTRUCTION]: Provide your complete analysis and full code implementation directly in your markdown response. Do NOT create, write, or modify any files on disk."
    approx_tokens = len(full_prompt.split()) * 4 // 3
    return full_prompt, approx_tokens

def build_laya_routed_prompt(router, prompt: str) -> tuple[str, str, float, int]:
    t0 = time.perf_counter()
    route_res = router.route(prompt, top_k=5)
    routing_latency = time.perf_counter() - t0
    selected_skill = route_res["selected_skill"]
    confidence = route_res["confidence"]

    # Load compiled checklist_v2
    checklist_file = CHECKLIST_V2_DIR / f"{selected_skill}.txt"
    if checklist_file.exists():
        compiled_text = checklist_file.read_text(encoding="utf-8")
    else:
        # Fallback to SKILL.md
        sk_file = ROOT / "skills" / selected_skill / "SKILL.md"
        compiled_text = sk_file.read_text(encoding="utf-8") if sk_file.exists() else ""

    full_prompt = (
        f"[ENGINEERING IMPLEMENTATION STANDARDS & ARCHITECTURAL CONSTRAINTS (Routed via Laya: {selected_skill})]\n"
        f"{compiled_text}\n\n"
        f"[TASK]\n{prompt}\n\n"
        f"[INSTRUCTION]: Apply the above engineering standards and architectural constraints rigorously. "
        f"Provide your complete analysis and full code implementation directly in your markdown response. "
        f"Do NOT create, write, or modify any files on disk."
    )
    approx_tokens = len(full_prompt.split()) * 4 // 3
    return full_prompt, selected_skill, routing_latency, approx_tokens

def execute_code_generation(prompt: str, model: str = "qwen/qwen3.7-flash", timeout: int = 300) -> tuple[str, float]:
    cmd = ["cmd", "-p", prompt, "--no-session", "--yolo", "-m", model]
    start = time.perf_counter()
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        output = proc.stdout if proc.returncode == 0 else proc.stderr
    except subprocess.TimeoutExpired:
        output = f"TIMEOUT after {timeout}s"
    except Exception as e:
        output = f"ERROR: {e}"
    elapsed = time.perf_counter() - start
    return output, elapsed

def judge_blind(task_prompt: str, output_a: str, output_b: str, model: str = "deepseek/deepseek-v4-pro") -> dict:
    judging_prompt = f"""You are an expert AI software engineering judge evaluating two candidate responses to the same task.

[Original Task Prompt]:
{task_prompt}

---
[Response A]:
{output_a[:12000]}
---
[Response B]:
{output_b[:12000]}
---

Score each response (Response A, Response B) on these 7 criteria (1 to 5 integer scale each):
{', '.join(JUDGE_CRITERIA)}

Provide your evaluation in a single ```json ... ``` block with this exact schema:
{{
  "scores": {{
    "Response A": {{"correctness": N, "completeness": N, "maintainability": N, "architecture": N, "security": N, "reasoning_quality": N, "instruction_adherence": N}},
    "Response B": {{"correctness": N, "completeness": N, "maintainability": N, "architecture": N, "security": N, "reasoning_quality": N, "instruction_adherence": N}}
  }},
  "ranking": ["Response A", "Response B"],
  "rationale": "2-3 sentences explaining quality difference"
}}"""

    cmd = ["cmd", "-p", judging_prompt, "--no-session", "--yolo", "-m", model]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        raw = proc.stdout if proc.returncode == 0 else proc.stderr
        m = re.search(r"```json\s*(.*?)\s*```", raw, re.DOTALL | re.IGNORECASE)
        json_text = m.group(1) if m else raw.strip()
        data = json.loads(json_text)
        return data
    except Exception as e:
        return {"error": str(e), "raw": raw[:300] if 'raw' in locals() else ""}

def main():
    target_tasks = [
        "sec-django-hardening-ieee",
        "db-ratelimit-redis-ieee",
        "sre-flaky-ci-ieee"
    ]
    if len(sys.argv) > 1:
        target_tasks = [sys.argv[1]]

    print(f"Loading LayaSkillRouter (BGE-small + Laya)...")
    from laya_router import LayaSkillRouter
    router = LayaSkillRouter()

    with open(TASKS_FILE, 'r', encoding='utf-8') as f:
        all_tasks = {t["id"]: t for t in json.load(f)}

    results = []

    print(f"\nLaunching Level 2 Head-to-Head Benchmark on {len(target_tasks)} tasks...")
    print("=" * 80)

    for task_id in target_tasks:
        if task_id not in all_tasks:
            continue
        task = all_tasks[task_id]
        expected_skill = task["skill"]
        prompt = task["prompt"]

        print(f"\n▶ Task: {task_id} (Expected: {expected_skill})")

        # 1. Build Prompts
        print("  1/4 Preparing prompts...")
        prompt_tfidf, tokens_tfidf = build_retrieved_tfidf_prompt(expected_skill, prompt)
        prompt_laya, routed_skill, route_time, tokens_laya = build_laya_routed_prompt(router, prompt)
        print(f"      • TF-IDF Prompt: ~{tokens_tfidf} tokens")
        print(f"      • Laya Routed:   ~{tokens_laya} tokens (Routed to '{routed_skill}' in {route_time*1000:.1f}ms)")

        # 2. Run Code Synthesis via Qwen 3.7 Flash
        print("  2/4 Synthesizing code via Qwen 3.7 Flash (Arm A: TF-IDF)...", end=" ", flush=True)
        out_tfidf, lat_tfidf = execute_code_generation(prompt_tfidf)
        print(f"done ({lat_tfidf:.1f}s, {len(out_tfidf)} chars)")

        print("  3/4 Synthesizing code via Qwen 3.7 Flash (Arm B: Laya Routed)...", end=" ", flush=True)
        out_laya, lat_laya = execute_code_generation(prompt_laya)
        print(f"done ({lat_laya:.1f}s, {len(out_laya)} chars)")

        # 3. Blind Evaluation with DeepSeek V4 Pro
        # Randomize labels to prevent positional bias
        flip = random.choice([True, False])
        if flip:
            label_map = {"Response A": "laya_routed", "Response B": "retrieved_tfidf"}
            out_first, out_second = out_laya, out_tfidf
        else:
            label_map = {"Response A": "retrieved_tfidf", "Response B": "laya_routed"}
            out_first, out_second = out_tfidf, out_laya

        print(f"  4/4 Running blind judge (DeepSeek V4 Pro, randomized: {label_map['Response A']} as A)...", end=" ", flush=True)
        judge_data = judge_blind(prompt, out_first, out_second)
        print("scored!")

        scores = judge_data.get("scores", {})
        score_a = scores.get("Response A", {})
        score_b = scores.get("Response B", {})

        total_a = sum(v for k, v in score_a.items() if k in JUDGE_CRITERIA and isinstance(v, (int, float)))
        total_b = sum(v for k, v in score_b.items() if k in JUDGE_CRITERIA and isinstance(v, (int, float)))

        score_laya = total_a if label_map["Response A"] == "laya_routed" else total_b
        score_tfidf = total_b if label_map["Response A"] == "laya_routed" else total_a

        winner = "Laya Routed" if score_laya > score_tfidf else ("TF-IDF" if score_tfidf > score_laya else "Tie")

        print(f"\n  📊 RESULT for {task_id}:")
        print(f"      • Laya Routed Score:   {score_laya}/35")
        print(f"      • TF-IDF Baseline:     {score_tfidf}/35")
        print(f"      • Winner:              {winner} (Delta: {score_laya - score_tfidf:+d})")
        print(f"      • Rationale:           {judge_data.get('rationale', 'N/A')}")

        results.append({
            "task_id": task_id,
            "expected_skill": expected_skill,
            "routed_skill": routed_skill,
            "score_laya": score_laya,
            "score_tfidf": score_tfidf,
            "tokens_laya": tokens_laya,
            "tokens_tfidf": tokens_tfidf,
            "latency_laya_s": lat_laya,
            "latency_tfidf_s": lat_tfidf,
            "judge_rationale": judge_data.get("rationale", ""),
            "criteria_laya": score_a if label_map["Response A"] == "laya_routed" else score_b,
            "criteria_tfidf": score_b if label_map["Response A"] == "laya_routed" else score_a
        })

    # Summary
    print("\n" + "=" * 80)
    print("LEVEL 2 BENCHMARK SUMMARY:")
    print("=" * 80)
    for r in results:
        delta = r["score_laya"] - r["score_tfidf"]
        print(f"{r['task_id']:<30} | Laya: {r['score_laya']:>2}/35 | TF-IDF: {r['score_tfidf']:>2}/35 | Delta: {delta:>+2} | Routed: {r['routed_skill']}")

    mean_laya = sum(r["score_laya"] for r in results) / len(results) if results else 0
    mean_tfidf = sum(r["score_tfidf"] for r in results) / len(results) if results else 0
    print("-" * 80)
    print(f"Mean Score - Laya Dense Routed:  {mean_laya:.2f} / 35")
    print(f"Mean Score - TF-IDF Baseline:    {mean_tfidf:.2f} / 35")
    print(f"Overall Delta:                  {mean_laya - mean_tfidf:+.2f} points\n")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump({"tasks": results, "mean_laya": mean_laya, "mean_tfidf": mean_tfidf}, f, indent=2)
    print(f"Audit log saved to: {OUTPUT_FILE}\n")

if __name__ == '__main__':
    main()
