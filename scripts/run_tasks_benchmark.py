#!/usr/bin/env python3
import argparse
import json
import math
import os
import re
import subprocess
import tempfile
import time
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent

def run_cmd(prompt: str, model: str = None) -> tuple[int, str, str]:
    cmd = ["agy", "--dangerously-skip-permissions"]
    if model:
        cmd.extend(["--model", model])
    cmd.extend(["-p", prompt])
    
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.returncode, proc.stdout, proc.stderr

def run_judge(prompt: str, out_a: str, out_b: str, model: str = None) -> dict:
    judging_prompt = f"""You are an expert AI evaluator judging two coding agent responses head-to-head.

[Original Task Prompt]:
{prompt}

---
[Agent Response A]:
{out_a}
---
[Agent Response B]:
{out_b}
---

Evaluate both responses strictly. You MUST award a score from 1 to 5 for each of these criteria:
- correctness (technical accuracy, lack of errors)
- completeness (covers all requirements in the prompt)
- maintainability (clean, documented, easy to extend)
- architecture (structure, patterns used)
- security (covers security boundaries, prevents leaks/vulnerabilities)
- reasoning_quality (logical breakdown, explanations)
- instruction_adherence (follows original prompts)

You must output a single JSON object inside a ```json ... ``` code block. Follow this structure:
{{
  "A": {{
    "correctness": [1-5],
    "completeness": [1-5],
    "maintainability": [1-5],
    "architecture": [1-5],
    "security": [1-5],
    "reasoning_quality": [1-5],
    "instruction_adherence": [1-5],
    "justification": "Why this score was given"
  }},
  "B": {{
    "correctness": [1-5],
    "completeness": [1-5],
    "maintainability": [1-5],
    "architecture": [1-5],
    "security": [1-5],
    "reasoning_quality": [1-5],
    "instruction_adherence": [1-5],
    "justification": "Why this score was given"
  }},
  "winner": "A" or "B" or "Draw",
  "comparison_summary": "Overall comparison summary"
}}

Respond ONLY with the JSON code block. Blind yourself to which output is Control or Treatment."""

    rc, stdout, stderr = run_cmd(judging_prompt, model)
    if rc == 0:
        json_match = re.search(r"```json\s*(.*?)\s*```", stdout, re.DOTALL | re.IGNORECASE)
        json_str = json_match.group(1) if json_match else stdout
        json_str = json_str.strip()
        try:
            return json.loads(json_str)
        except Exception as e:
            print(f"⚠️ Failed to parse judge JSON: {e}. Raw stdout was:\n{stdout}")
            
    print(f"⚠️ Judge call failed with code {rc}. Stderr: {stderr}")
    return None


def check_code_syntax(output: str) -> tuple[int, list[str]]:
    # Extract code blocks
    blocks = re.findall(r"```(python|javascript|typescript|js|ts)\n(.*?)```", output, re.DOTALL | re.IGNORECASE)
    errors = []
    checked = 0
    for lang, code in blocks:
        lang = lang.lower()
        checked += 1
        suffix = f".{lang if lang != 'typescript' and lang != 'ts' else 'ts'}"
        with tempfile.NamedTemporaryFile("w", suffix=suffix, delete=False) as f:
            f.write(code)
            temp_path = f.name
        try:
            if lang == "python":
                res = subprocess.run(["python3", "-m", "py_compile", temp_path], capture_output=True, text=True)
                if res.returncode != 0:
                    errors.append(f"Python syntax error: {res.stderr or res.stdout}")
            elif lang in ["javascript", "js"]:
                res = subprocess.run(["node", "--check", temp_path], capture_output=True, text=True)
                if res.returncode != 0:
                    errors.append(f"JS syntax error: {res.stderr or res.stdout}")
        except Exception as e:
            errors.append(f"Verifier tool execution error: {e}")
        finally:
            Path(temp_path).unlink(missing_ok=True)
    return checked, errors

def load_skill_md(skill_name: str) -> str:
    index_file = ROOT / "skills.json"
    if index_file.exists():
        try:
            with open(index_file, "r") as f:
                index = json.load(f)
            skill_info = index.get("skills", {}).get(skill_name, {})
            if skill_info.get("rel_path"):
                skill_path = ROOT / skill_info["rel_path"]
                if skill_path.exists():
                    return skill_path.read_text(encoding="utf-8")
        except Exception:
            pass
            
    # Fallback to direct search
    fallback_path = ROOT / "skills" / skill_name / "SKILL.md"
    if fallback_path.exists():
        return fallback_path.read_text(encoding="utf-8")
    return ""

def compute_stats(scores: list[float]) -> dict:
    if not scores:
        return {"mean": 0, "median": 0, "std_dev": 0, "ci_low": 0, "ci_high": 0}
    arr = np.array(scores)
    mean = np.mean(arr)
    median = np.median(arr)
    std_dev = np.std(arr, ddof=1) if len(arr) > 1 else 0
    
    ci_low, ci_high = mean, mean
    if len(arr) > 1:
        try:
            sem = stats.sem(arr)
            ci = stats.t.interval(0.95, len(arr)-1, loc=mean, scale=sem)
            ci_low = ci[0] if not (np.isnan(ci[0]) or np.isinf(ci[0])) else mean
            ci_high = ci[1] if not (np.isnan(ci[1]) or np.isinf(ci[1])) else mean
        except Exception:
            pass
            
    return {
        "mean": round(float(mean), 2),
        "median": round(float(median), 2),
        "std_dev": round(float(std_dev), 2),
        "ci_low": round(float(ci_low), 2),
        "ci_high": round(float(ci_high), 2)
    }

def run_t_test(treatment: list[float], control: list[float]) -> tuple[float, float]:
    if len(treatment) < 2 or len(control) < 2:
        return 0.0, 1.0
    try:
        t_stat, p_val = stats.ttest_ind(treatment, control, equal_var=False)
        return round(float(t_stat), 3), round(float(p_val), 4)
    except Exception:
        return 0.0, 1.0

def compile_trends(results_dir: Path) -> list[dict]:
    history_files = sorted(results_dir.glob("run_*.json"))
    trends = []
    for f in history_files:
        try:
            with open(f, "r") as fh:
                data = json.load(fh)
            trends.append({
                "timestamp": data.get("timestamp"),
                "pass_rate_treatment": data.get("treatment_summary", {}).get("pass_rate"),
                "pass_rate_control": data.get("control_summary", {}).get("pass_rate"),
                "avg_score_treatment": data.get("treatment_summary", {}).get("avg_score"),
                "avg_score_control": data.get("control_summary", {}).get("avg_score"),
                "latency_treatment": data.get("treatment_summary", {}).get("avg_latency"),
                "latency_control": data.get("control_summary", {}).get("avg_latency"),
            })
        except Exception:
            pass
    return trends

def main():
    parser = argparse.ArgumentParser(description="A/B Rigorous Agent Evaluation Harness")
    parser.add_argument("--tasks", type=Path, default=ROOT / "benchmarks" / "tasks.json", help="Path to tasks JSON file")
    parser.add_argument("--runs", type=int, default=3, help="Number of A/B runs per task")
    parser.add_argument("--models", type=str, default=None, help="Comma-separated list of model IDs to test")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "benchmarks" / "results", help="Directory to save run files")
    args = parser.parse_args()
    
    args.output_dir.mkdir(parents=True, exist_ok=True)
    schema_path = ROOT / "benchmarks" / "judge_schema.json"
    
    if not args.tasks.exists():
        print(f"❌ Tasks file not found at {args.tasks}")
        return
        
    with open(args.tasks, "r") as f:
        tasks = json.load(f)
        
    models = [m.strip() for m in args.models.split(",")] if args.models else [None]
    
    run_timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    run_log_file = args.output_dir / f"run_{run_timestamp}.json"
    report_file = args.output_dir / f"report_{run_timestamp}.md"
    
    full_results = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tasks_file": str(args.tasks),
        "runs_per_task": args.runs,
        "models": models,
        "runs": []
    }
    
    print(f"🏁 Starting Rigorous A/B Benchmark: {len(tasks)} tasks × {args.runs} runs per model...")
    
    for model in models:
        model_name = model or "Default Model"
        print(f"\n🚀 Evaluating Model: {model_name}")
        
        for task in tasks:
            task_id = task["id"]
            prompt = task["prompt"]
            must_include = task["must_include"]
            skill = task["skill"]
            
            print(f"\n==================================================")
            print(f"📝 Task: {task_id} | Skill: {skill}")
            
            # Load skill context
            skill_md = load_skill_md(skill)
            if not skill_md:
                print(f"⚠️ Warning: Could not find skill context for '{skill}'. Using empty treatment instructions.")
                
            treatment_prompt = f"""[INSTRUCTIONS]
Use these guidelines to complete the task:
{skill_md}

[TASK PROMPT]
{prompt}"""

            control_runs = []
            treatment_runs = []
            
            for r_idx in range(1, args.runs + 1):
                print(f"\n--- Run {r_idx}/{args.runs} ---")
                
                # 1. Run Control (No Skill Context)
                print("🔵 Executing Control Run...")
                start_c = time.perf_counter()
                rc_c, out_c, err_c = run_cmd(prompt, model)
                lat_c = time.perf_counter() - start_c
                
                # 2. Run Treatment (Injected Skill Context)
                print("🟢 Executing Treatment Run...")
                start_t = time.perf_counter()
                rc_t, out_t, err_t = run_cmd(treatment_prompt, model)
                lat_t = time.perf_counter() - start_t
                
                if rc_c != 0 or rc_t != 0:
                    print(f"⚠️ Run failed! Control exit: {rc_c}, Treatment exit: {rc_t}")
                    continue
                    
                # 3. Objective Validation (Syntax checks on generated code blocks)
                c_blocks, c_errors = check_code_syntax(out_c)
                t_blocks, t_errors = check_code_syntax(out_t)
                
                # 4. Blinded LLM Judging
                # Randomly assign A and B to blind the judge
                is_swapped = (r_idx % 2 == 0)
                out_a, out_b = (out_t, out_c) if is_swapped else (out_c, out_t)
                
                print("⚖️ Submitting responses to blinded LLM-as-a-Judge...")
                judge_res = run_judge(prompt, out_a, out_b, model)
                
                if not judge_res:
                    print("⚠️ Judging failed! Skipping this run.")
                    continue
                    
                # Unblind scores
                scores_c = judge_res["B"] if is_swapped else judge_res["A"]
                scores_t = judge_res["A"] if is_swapped else judge_res["B"]
                
                winner_blind = judge_res["winner"]
                if winner_blind == "Draw":
                    winner = "Draw"
                elif winner_blind == "A":
                    winner = "Treatment" if is_swapped else "Control"
                else:
                    winner = "Control" if is_swapped else "Treatment"
                    
                # Baseline keyword verification
                missing_c = [p for p in must_include if not re.search(p, out_c, re.IGNORECASE)]
                missing_t = [p for p in must_include if not re.search(p, out_t, re.IGNORECASE)]
                
                control_runs.append({
                    "latency": lat_c,
                    "scores": scores_c,
                    "total_score": sum(v for k, v in scores_c.items() if k != "justification"),
                    "missing_keywords": missing_c,
                    "code_blocks_checked": c_blocks,
                    "code_errors": c_errors,
                    "output_preview": out_c[:200] + "..." if len(out_c) > 200 else out_c
                })
                
                treatment_runs.append({
                    "latency": lat_t,
                    "scores": scores_t,
                    "total_score": sum(v for k, v in scores_t.items() if k != "justification"),
                    "missing_keywords": missing_t,
                    "code_blocks_checked": t_blocks,
                    "code_errors": t_errors,
                    "output_preview": out_t[:200] + "..." if len(out_t) > 200 else out_t
                })
                
                print(f"🏆 Winner: {winner} | Scores: Treatment {treatment_runs[-1]['total_score']} vs Control {control_runs[-1]['total_score']}")
                
            # Compile stats for this task
            c_scores = [r["total_score"] for r in control_runs]
            t_scores = [r["total_score"] for r in treatment_runs]
            c_lats = [r["latency"] for r in control_runs]
            t_lats = [r["latency"] for r in treatment_runs]
            
            t_wins = sum(1 for c, t in zip(c_scores, t_scores) if t > c)
            c_wins = sum(1 for c, t in zip(c_scores, t_scores) if c > t)
            draws = sum(1 for c, t in zip(c_scores, t_scores) if c == t)
            
            t_stat, p_val = run_t_test(t_scores, c_scores)
            
            task_result = {
                "id": task_id,
                "skill": skill,
                "model": model_name,
                "win_ratio": f"{t_wins}-{c_wins}-{draws}",
                "t_statistic": t_stat,
                "p_value": p_val,
                "control_stats": compute_stats(c_scores),
                "treatment_stats": compute_stats(t_scores),
                "control_latency": compute_stats(c_lats),
                "treatment_latency": compute_stats(t_lats),
                "runs": {
                    "control": control_runs,
                    "treatment": treatment_runs
                }
            }
            
            full_results["runs"].append(task_result)
            
    # Calculate Overall Summaries
    all_c_scores = []
    all_t_scores = []
    all_c_lats = []
    all_t_lats = []
    total_t_wins = 0
    total_c_wins = 0
    total_draws = 0
    
    for r in full_results["runs"]:
        c_sc = [run["total_score"] for run in r["runs"]["control"]]
        t_sc = [run["total_score"] for run in r["runs"]["treatment"]]
        all_c_scores.extend(c_sc)
        all_t_scores.extend(t_sc)
        all_c_lats.extend([run["latency"] for run in r["runs"]["control"]])
        all_t_lats.extend([run["latency"] for run in r["runs"]["treatment"]])
        
        for c, t in zip(c_sc, t_sc):
            if t > c: total_t_wins += 1
            elif c > t: total_c_wins += 1
            else: total_draws += 1
            
    overall_t_stat, overall_p_val = run_t_test(all_t_scores, all_c_scores)
    
    t_summary = compute_stats(all_t_scores)
    c_summary = compute_stats(all_c_scores)
    t_lat_sum = compute_stats(all_t_lats)
    c_lat_sum = compute_stats(all_c_lats)
    
    total_comparisons = total_t_wins + total_c_wins + total_draws
    win_rate = (total_t_wins / total_comparisons * 100) if total_comparisons > 0 else 0
    
    full_results["treatment_summary"] = {
        "pass_rate": f"{total_t_wins}/{total_comparisons}",
        "avg_score": t_summary["mean"],
        "avg_latency": t_lat_sum["mean"]
    }
    full_results["control_summary"] = {
        "pass_rate": f"{total_c_wins}/{total_comparisons}",
        "avg_score": c_summary["mean"],
        "avg_latency": c_lat_sum["mean"]
    }
    
    with open(run_log_file, "w") as f:
        json.dump(full_results, f, indent=2)
        
    # Compile trends
    trends = compile_trends(args.output_dir)
    
    # Generate Markdown Report
    report_lines = [
        f"# Rigorous Agent-Skills Evaluation Report ({args.tasks.stem.replace('_', ' ').title()})\n",
        f"> **Generated at**: `{full_results['timestamp']}`",
        f"> **Total Comparisons**: `{total_comparisons}` | **Runs per Task**: `{args.runs}`\n",
        "## 📊 Executive Dashboard\n",
        "| Metric | Treatment (Agent + Skill) | Control (Base Agent) | Impact / Delta |",
        "|---|---|---|---|",
        f"| **Win Rate** | **{win_rate:.1f}%** ({total_t_wins} wins) | {total_c_wins / total_comparisons * 100:.1f}% ({total_c_wins} wins) | **+{win_rate - (total_c_wins / total_comparisons * 100):.1f}%** |",
        f"| **Average Score** (max 35) | **{t_summary['mean']}** | {c_summary['mean']} | **+{round(t_summary['mean'] - c_summary['mean'], 2)}** |",
        f"| **95% Confidence Score** | `[{t_summary['ci_low']}, {t_summary['ci_high']}]` | `[{c_summary['ci_low']}, {c_summary['ci_high']}]` | - |",
        f"| **Avg Latency** (duration) | {t_lat_sum['mean']}s | {c_lat_sum['mean']}s | **{round(((t_lat_sum['mean'] - c_lat_sum['mean'])/c_lat_sum['mean']*100), 1)}%** ({round(t_lat_sum['mean'] - c_lat_sum['mean'], 2)}s) |",
        f"| **Statistical Significance** | **p = {overall_p_val}** (t = {overall_t_stat}) | - | {'✅ Significant (p < 0.05)' if overall_p_val < 0.05 else '❌ Not Significant (p >= 0.05)'} |",
        "\n---\n",
        "## 🔍 Task-level Breakdown\n",
        "| Task ID | Skill | Model | Win/Loss/Draw | Avg Score (T vs C) | Avg Latency (T vs C) | p-value |",
        "|---|---|---|---|---|---|---|",
    ]
    
    for r in full_results["runs"]:
        t_stat_task = r["t_statistic"]
        p_val_task = r["p_value"]
        p_sig_indicator = "⭐" if p_val_task < 0.05 else ""
        report_lines.append(f"| `{r['id']}` | `{r['skill']}` | `{r['model']}` | {r['win_ratio']} | **{r['treatment_stats']['mean']}** vs {r['control_stats']['mean']} | {r['treatment_latency']['mean']}s vs {r['control_latency']['mean']}s | {p_val_task}{p_sig_indicator} |")
        
    if trends:
        report_lines.append("\n---\n")
        report_lines.append("## 📈 Historical Regression Trends\n")
        report_lines.append("| Run Timestamp | Treatment Score | Control Score | Score Delta | Treatment Latency | Control Latency |")
        report_lines.append("|---|---|---|---|---|---|")
        for t in trends[-10:]: # Show last 10 runs
            delta = round(t['avg_score_treatment'] - t['avg_score_control'], 2)
            report_lines.append(f"| `{t['timestamp']}` | **{t['avg_score_treatment']}** | {t['avg_score_control']} | **+{delta}** | {t['latency_treatment']}s | {t['latency_control']}s |")
            
    report_lines.append("\n---\n")
    report_lines.append("### 🧬 Detailed Run Artifacts\n")
    for r in full_results["runs"]:
        report_lines.append(f"#### Task: `{r['id']}` (`{r['model']}`)")
        report_lines.append(f"- **Skill**: `{r['skill']}`")
        report_lines.append(f"- **T-Test**: `t = {r['t_statistic']}`, `p = {r['p_value']}`")
        
        for idx, (run_c, run_t) in enumerate(zip(r["runs"]["control"], r["runs"]["treatment"]), 1):
            report_lines.append(f"\n**Run {idx}:**")
            report_lines.append(f"*   **Control Score**: `{run_c['total_score']}/35` (Latency: {run_c['latency']:.1f}s)")
            if run_c["missing_keywords"]:
                report_lines.append(f"    *   *Missing Keywords*: `{run_c['missing_keywords']}`")
            if run_c["code_errors"]:
                report_lines.append(f"    *   *Syntax Check Failures*: `{run_c['code_errors']}`")
            report_lines.append(f"*   **Treatment Score**: `{run_t['total_score']}/35` (Latency: {run_t['latency']:.1f}s)")
            if run_t["missing_keywords"]:
                report_lines.append(f"    *   *Missing Keywords*: `{run_t['missing_keywords']}`")
            if run_t["code_errors"]:
                report_lines.append(f"    *   *Syntax Check Failures*: `{run_t['code_errors']}`")
            report_lines.append(f"    *   *Judge Justification*: {run_t['scores'].get('justification', 'N/A')}")
        report_lines.append("\n")
        
    report_file.write_text("\n".join(report_lines), encoding="utf-8")
    
    # Symlink/Copy Latest Report
    latest_report = args.output_dir / "../report_latest.md"
    latest_json = args.output_dir / "../results_latest.json"
    latest_report.write_text("\n".join(report_lines), encoding="utf-8")
    latest_json.write_text(json.dumps(full_results, indent=2) + "\n", encoding="utf-8")
    
    print("\n===========================================")
    print(f"🏆 A/B Benchmark Suite Complete!")
    print(f"   Win Rate: {win_rate:.1f}%")
    print(f"   Avg Score Improvement: +{round(t_summary['mean'] - c_summary['mean'], 2)}")
    print(f"   Overall P-value: {overall_p_val}")
    print(f"   JSON Results: {run_log_file}")
    print(f"   Markdown Report: {report_file}")
    print("===========================================")

if __name__ == "__main__":
    main()
