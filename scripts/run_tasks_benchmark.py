#!/usr/bin/env python3
import argparse
import json
import re
import subprocess
import time
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent

def run_cmd(prompt: str) -> tuple[int, str, str]:
    cmd = ["agy", "--dangerously-skip-permissions", "-p", prompt]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.returncode, proc.stdout, proc.stderr

def main():
    parser = argparse.ArgumentParser(description="Run LLM-as-a-Judge Skills Benchmark")
    parser.add_argument("--tasks", type=Path, default=ROOT / "benchmarks" / "tasks.json", help="Path to tasks JSON file")
    parser.add_argument("--output", type=Path, default=ROOT / "benchmarks" / "results.json", help="Path to write JSON results")
    parser.add_argument("--report", type=Path, default=ROOT / "benchmarks" / "report.md", help="Path to write Markdown report")
    args = parser.parse_args()
    
    if not args.tasks.exists():
        print(f"❌ Error: Tasks file not found at {args.tasks}")
        return
        
    with open(args.tasks, "r") as f:
        tasks = json.load(f)
        
    results = []
    total_passed = 0
    total_score = 0
    
    print(f"🚀 Starting Benchmark: {len(tasks)} tasks from {args.tasks.name}...")
    
    for task in tasks:
        task_id = task["id"]
        prompt = task["prompt"]
        must_include = task["must_include"]
        skill = task["skill"]
        
        print(f"\n──────────────────────────────────────────────────")
        print(f"📝 Running Task: {task_id} (using skill: {skill})")
        print(f"Prompt: \"{prompt}\"")
        
        # 1. Generate Response
        start_time = time.perf_counter()
        rc, output, err = run_cmd(prompt)
        elapsed = time.perf_counter() - start_time
        
        if rc != 0:
            print(f"❌ Execution failed: {err}")
            results.append({
                "id": task_id,
                "skill": skill,
                "passed": False,
                "score": 0,
                "time_seconds": round(elapsed, 2),
                "error": err
            })
            continue
            
        print(f"⚡ Generated response in {elapsed:.2f}s")
        
        # 2. Check Baseline Keywords (Using Regex Patterns for flexibility)
        missing_keywords = []
        for pattern in must_include:
            if not re.search(pattern, output, re.IGNORECASE):
                missing_keywords.append(pattern)
        has_keywords = len(missing_keywords) == 0
        
        # 3. LLM-as-a-Judge Evaluation Prompt
        judging_prompt = f"""You are an expert AI evaluator judging the output of a coding agent.

[Task ID]: {task_id}
[Skill Checked]: {skill}
[Original Prompt]: {prompt}

---
[Agent Response under Review]:
{output}
---

Evaluate the response strictly. Award a score from 1 to 5:
- 5: Outstanding. Technically accurate, covers all requirements, highly detailed, and actionable.
- 4: Very Good. Accurate and covers key risks/assertions, but misses minor details or could be more detailed.
- 3: Average. Correct at a high level, but generic or misses details.
- 2: Poor. Incomplete, generic, or has technical errors.
- 1: Fail. Completely wrong, off-topic, or did not follow instructions.

Your response MUST follow this exact format:
Score: [number]
Justification: [2-3 sentences explaining why this score was awarded]"""

        print(f"⚖️ Sending response to LLM-as-a-Judge...")
        judge_rc, judge_output, judge_err = run_cmd(judging_prompt)
        
        score = 0
        justification = "Failed to parse judge output."
        
        if judge_rc == 0:
            # Parse Score: [number]
            score_match = re.search(r"Score:\s*([1-5])", judge_output, re.IGNORECASE)
            if score_match:
                score = int(score_match.group(1))
            
            # Parse Justification: [text]
            just_match = re.search(r"Justification:\s*(.*)", judge_output, re.IGNORECASE | re.DOTALL)
            if just_match:
                justification = just_match.group(1).strip()
            else:
                justification = judge_output.strip()
        else:
            justification = f"Judging error: {judge_err}"
            
        passed = has_keywords and score >= 3
        if passed:
            total_passed += 1
            print(f"✅ PASSED (Score: {score}/5) - {justification[:100]}...")
        else:
            print(f"❌ FAILED (Score: {score}/5) - {justification[:100]}...")
            if missing_keywords:
                print(f"   Missing keywords/patterns: {missing_keywords}")
            
        total_score += score
        results.append({
            "id": task_id,
            "skill": skill,
            "passed": passed,
            "score": score,
            "time_seconds": round(elapsed, 2),
            "missing_keywords": missing_keywords,
            "justification": justification,
            "output_preview": output[:250] + "..." if len(output) > 250 else output
        })
        
    avg_score = round(total_score / len(tasks), 1) if tasks else 0
    
    # 4. Generate JSON results
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_tasks": len(tasks),
        "passed": total_passed,
        "pass_rate": f"{total_passed}/{len(tasks)} ({total_passed/len(tasks)*100:.1f}%)",
        "average_score": f"{avg_score}/5.0",
        "tasks": results
    }
    
    with open(args.output, "w") as f:
        json.dump(summary, f, indent=2)
        
    # 5. Generate Markdown Report
    report_lines = [
        f"# Agent Skills Benchmark Evaluation Report ({args.tasks.stem.replace('_', ' ').title()})\n",
        f"> **Generated at**: `{summary['generated_at']}`",
        f"> **Overall Pass Rate**: `{summary['pass_rate']}`",
        f"> **Average Judge Score**: `{summary['average_score']}`\n",
        "## Performance Scorecard\n",
        "| Task ID | Skill | Status | Latency | Score | Justification |",
        "|---|---|---|---|---|---|",
    ]
    
    for r in results:
        status_icon = "🟢 Pass" if r["passed"] else "🔴 Fail"
        latency = f"{r['time_seconds']}s"
        score_str = f"**{r['score']}/5**" if r.get('score') else "N/A"
        report_lines.append(f"| `{r['id']}` | `{r['skill']}` | {status_icon} | {latency} | {score_str} | {r.get('justification', 'N/A')} |")
        
    report_lines.append("\n---\n")
    report_lines.append("### Detailed Outputs and Audits\n")
    for r in results:
        report_lines.append(f"#### Task: `{r['id']}`")
        report_lines.append(f"- **Skill**: `{r['skill']}`")
        if r.get("missing_keywords"):
            report_lines.append(f"- **Missing Baseline Keywords**: `{r['missing_keywords']}`")
        report_lines.append(f"- **Output Preview**:\n```text\n{r.get('output_preview', '')}\n```\n")
        
    args.report.write_text("\n".join(report_lines), encoding="utf-8")
    
    print("\n===========================================")
    print(f"🏆 Benchmark Complete!")
    print(f"   Pass Rate: {summary['pass_rate']}")
    print(f"   Avg Score: {summary['average_score']}")
    print(f"   JSON Results: {args.output}")
    print(f"   Markdown Report: {args.report}")
    print("===========================================")

if __name__ == "__main__":
    main()
