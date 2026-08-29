#!/usr/bin/env python3
"""
Structural Ablation Experiment Runner — IEEE Study
==================================================
Executes targeted component-level ablations (A2: No Examples, A3: No Tables, A4: No Types)
on representative domain tasks from benchmarks/tasks_ablation_subset.json.

Evaluates executor outputs using a blind judge on the IEEE 7-criterion 35-point rubric.
Records ablation magnitude (token volume removed, % reduction) alongside raw scores.

Usage:
  python3 scripts/run_ablation_experiment.py --tasks benchmarks/tasks_ablation_subset.json --runs 3
  python3 scripts/run_ablation_experiment.py --dry-run
  python3 scripts/run_ablation_experiment.py --resume
"""

import argparse
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent

DEFAULT_TASKS = ROOT / "benchmarks" / "tasks_ablation_subset.json"
DEFAULT_ABLATIONS_DIR = ROOT / "benchmarks" / "ablations"
DEFAULT_RESULTS = ROOT / "benchmarks" / "ablation_results.json"
RAW_OUTPUTS_DIR = ROOT / "benchmarks" / "raw_outputs_ablations"

JUDGE_CRITERIA = [
    "correctness",
    "completeness",
    "maintainability",
    "architecture",
    "security",
    "reasoning_quality",
    "instruction_adherence",
]

DEFAULT_CONDITIONS = ["a2_no_examples", "a3_no_tables", "a4_no_types"]


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def atomic_write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    tmp.replace(path)


def load_ablation_file(ablations_dir: Path, skill_name: str, condition: str) -> Tuple[str, Path]:
    filename = f"{skill_name}_{condition}.md"
    file_path = ablations_dir / filename
    if not file_path.exists():
        raise FileNotFoundError(f"Ablation file not found: {file_path}")
    return file_path.read_text(encoding="utf-8"), file_path


def load_reference_skill_file(ablations_dir: Path, skill_name: str) -> str:
    full_path = ablations_dir / f"{skill_name}_a0_full.md"
    if full_path.exists():
        return full_path.read_text(encoding="utf-8")
    skill_md = ROOT / "skills" / skill_name / "SKILL.md"
    if skill_md.exists():
        return skill_md.read_text(encoding="utf-8")
    return ""


def build_executor_prompt(task_prompt: str, skill_content: str) -> str:
    if not skill_content.strip():
        return f"[TASK]\n{task_prompt}"
    return (
        f"[ENGINEERING IMPLEMENTATION STANDARDS & ARCHITECTURAL CONSTRAINTS]\n"
        f"{skill_content.strip()}\n\n"
        f"[TASK]\n{task_prompt}\n\n"
        f"[INSTRUCTION]: Apply the above engineering standards and architectural constraints rigorously. "
        f"Output your complete, production-grade code implementation and review directly in your markdown response text."
    )


def check_syntax(output: str) -> Tuple[int, List[str]]:
    blocks = re.findall(
        r"```(python|py|javascript|typescript|js|ts|sql)\n(.*?)```", output, re.DOTALL | re.IGNORECASE
    )
    checked = 0
    errors = []
    for lang, code in blocks:
        lang = lang.lower()
        checked += 1
        if lang in ["python", "py"]:
            try:
                compile(code, "<agent_output>", "exec")
            except SyntaxError as e:
                errors.append(f"Python syntax error at line {e.lineno}: {e.msg}")
            except Exception as e:
                errors.append(f"Python check error: {e}")
    return checked, errors


def run_executor(
    prompt: str,
    backend: str = "cmd",
    model: Optional[str] = None,
    timeout: int = 300,
    dry_run: bool = False,
) -> Tuple[int, str, str, float]:
    if dry_run:
        time.sleep(0.02)
        simulated_output = (
            f"# Solution Output\n\n```python\n# Implementation fulfilling requirements\ndef solution():\n"
            f"    return 'mock result for testing'\n```\n\nCompleted successfully."
        )
        return 0, simulated_output, "", 0.02

    start = time.perf_counter()
    if backend == "cmd":
        actual_model = model or "qwen/qwen3.7-flash"
        cmd = ["cmd", "-p", prompt, "--no-session", "--yolo", "-m", actual_model]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            elapsed = time.perf_counter() - start
            return proc.returncode, proc.stdout, proc.stderr, elapsed
        except subprocess.TimeoutExpired:
            return 124, "", f"TIMEOUT after {timeout}s", timeout
        except Exception as e:
            return 1, "", f"Execution exception: {e}", time.perf_counter() - start

    elif backend == "agy":
        cmd = ["agy", "--dangerously-skip-permissions"]
        if model:
            cmd.extend(["--model", model])
        cmd.extend(["-p", prompt])
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            elapsed = time.perf_counter() - start
            return proc.returncode, proc.stdout, proc.stderr, elapsed
        except subprocess.TimeoutExpired:
            return 124, "", f"TIMEOUT after {timeout}s", timeout
        except Exception as e:
            return 1, "", f"Execution exception: {e}", time.perf_counter() - start

    elif backend == "mock":
        time.sleep(0.01)
        return 0, "# Mock Code\n```python\npass\n```", "", 0.01

    else:
        raise ValueError(f"Unknown executor backend: {backend}")


def build_judge_prompt(task_prompt: str, agent_output: str, max_chars: int = 24000) -> str:
    body = agent_output
    if len(body) > max_chars:
        body = body[:max_chars] + "\n...[output truncated for judge context window]"

    return f"""You are an expert, impartial AI evaluator for software engineering implementations.
Evaluate the following coding agent response to the given task specification.

[Task Specification]:
{task_prompt}

---
[Agent Response to Evaluate]:
{body}
---

Award an integer score from 1 to 5 for EACH of the following 7 criteria:
1. correctness (technical correctness, lack of bugs or syntax flaws)
2. completeness (fulfills all stated functional and non-functional requirements)
3. maintainability (code structure, clarity, documentation, naming conventions)
4. architecture (appropriate design patterns, modular boundaries, separation of concerns)
5. security (proper threat mitigation, authorization, input validation, no secrets leaked)
6. reasoning_quality (logical breakdown, sound architectural trade-off justification)
7. instruction_adherence (follows exact constraints, output structure, and protocols)

Respond ONLY with a single JSON object in a ```json ... ``` code block with this exact format:
```json
{{
  "correctness": 4,
  "completeness": 4,
  "maintainability": 4,
  "architecture": 4,
  "security": 4,
  "reasoning_quality": 4,
  "instruction_adherence": 4,
  "justification": "Brief 2-3 sentence justification explaining strengths and deficiencies."
}}
```"""


def parse_judge_json(raw_text: str) -> Optional[Dict[str, Any]]:
    m = re.search(r"```json\s*(.*?)\s*```", raw_text, re.DOTALL | re.IGNORECASE)
    cleaned = m.group(1) if m else raw_text.strip()
    try:
        data = json.loads(cleaned)
        scores = {}
        for crit in JUDGE_CRITERIA:
            if crit not in data:
                return None
            val = int(data[crit])
            scores[crit] = max(1, min(5, val))
        scores["total_score"] = sum(scores[c] for c in JUDGE_CRITERIA)
        scores["justification"] = data.get("justification", "")
        return scores
    except Exception:
        return None


def run_judge(
    task_prompt: str,
    agent_output: str,
    backend: str = "cmd",
    model: Optional[str] = None,
    timeout: int = 300,
    dry_run: bool = False,
) -> Tuple[Optional[Dict[str, Any]], Dict[str, Any], str]:
    if dry_run or backend == "mock":
        mock_scores = {c: 4 for c in JUDGE_CRITERIA}
        mock_scores["total_score"] = 28
        mock_scores["justification"] = "Dry run mock evaluation passed."
        return mock_scores, {"latency_s": 0.02}, "ok"

    judge_prompt = build_judge_prompt(task_prompt, agent_output)
    start = time.perf_counter()

    if backend == "cmd":
        actual_model = model or "deepseek/deepseek-v4-pro"
        cmd = ["cmd", "-p", judge_prompt, "--no-session", "--yolo", "-m", actual_model]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            elapsed = time.perf_counter() - start
            usage = {"latency_s": round(elapsed, 2)}
            if proc.returncode != 0:
                return None, usage, f"cmd error {proc.returncode}: {proc.stderr[:200]}"
            parsed = parse_judge_json(proc.stdout)
            if parsed is None:
                return None, usage, "Failed to parse judge JSON"
            return parsed, usage, "ok"
        except subprocess.TimeoutExpired:
            return None, {"latency_s": timeout}, f"Judge timeout after {timeout}s"
        except Exception as e:
            return None, {"latency_s": 0}, f"Judge exception: {e}"

    elif backend == "agy":
        cmd = ["agy", "--dangerously-skip-permissions"]
        if model:
            cmd.extend(["--model", model])
        cmd.extend(["-p", judge_prompt])
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            elapsed = time.perf_counter() - start
            usage = {"latency_s": round(elapsed, 2)}
            if proc.returncode != 0:
                return None, usage, f"agy error {proc.returncode}: {proc.stderr[:200]}"
            parsed = parse_judge_json(proc.stdout)
            if parsed is None:
                return None, usage, "Failed to parse judge JSON"
            return parsed, usage, "ok"
        except subprocess.TimeoutExpired:
            return None, {"latency_s": timeout}, f"Judge timeout after {timeout}s"
        except Exception as e:
            return None, {"latency_s": 0}, f"Judge exception: {e}"

    else:
        raise ValueError(f"Unknown judge backend: {backend}")


def get_git_commit() -> str:
    try:
        proc = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True)
        return proc.stdout.strip()
    except Exception:
        return "unknown"


def main():
    parser = argparse.ArgumentParser(description="Run targeted structural ablation experiments.")
    parser.add_argument("--tasks", type=Path, default=DEFAULT_TASKS, help="Path to ablation task JSON")
    parser.add_argument("--ablations-dir", type=Path, default=DEFAULT_ABLATIONS_DIR, help="Path to ablations dir")
    parser.add_argument("--conditions", nargs="+", default=DEFAULT_CONDITIONS, help="Ablation conditions to run")
    parser.add_argument("--runs", type=int, default=3, help="Number of repetitions per condition")
    parser.add_argument("--executor-backend", default="cmd", choices=["cmd", "agy", "mock"], help="Executor backend")
    parser.add_argument("--executor-model", default="qwen/qwen3.7-flash", help="Executor model name")
    parser.add_argument("--judge-backend", default="cmd", choices=["cmd", "agy", "mock"], help="Judge backend")
    parser.add_argument("--judge-model", default="deepseek/deepseek-v4-pro", help="Judge model name")
    parser.add_argument("--out-results", type=Path, default=DEFAULT_RESULTS, help="Output results JSON path")
    parser.add_argument("--resume", action="store_true", help="Resume from existing progress")
    parser.add_argument("--dry-run", action="store_true", help="Perform offline dry-run test without API calls")

    args = parser.parse_args()

    if not args.tasks.exists():
        print(f"Error: Tasks file {args.tasks} does not exist.", file=sys.stderr)
        sys.exit(1)

    tasks_data = json.loads(args.tasks.read_text(encoding="utf-8"))
    RAW_OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    results_data = {
        "metadata": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "git_commit": get_git_commit(),
            "executor_backend": args.executor_backend,
            "executor_model": args.executor_model,
            "judge_backend": args.judge_backend,
            "judge_model": args.judge_model,
            "runs_per_condition": args.runs,
            "conditions_evaluated": args.conditions,
            "dry_run": args.dry_run,
        },
        "runs": [],
    }

    if args.resume and args.out_results.exists():
        try:
            existing = json.loads(args.out_results.read_text(encoding="utf-8"))
            results_data["runs"] = existing.get("runs", [])
            print(f"Resuming with {len(results_data['runs'])} completed runs loaded.")
        except Exception as e:
            print(f"Warning: Failed to load resume file: {e}. Starting fresh.")

    completed_keys = {
        (r["task_id"], r["condition"], r["run_index"]) for r in results_data["runs"]
    }

    total_runs = len(tasks_data) * len(args.conditions) * args.runs
    current_run = len(completed_keys)

    print("=" * 70)
    print(f"IEEE Structural Ablation Runner: {total_runs} total runs planned")
    print(f"Tasks: {len(tasks_data)} | Conditions: {args.conditions} | Runs/Cell: {args.runs}")
    print(f"Executor: {args.executor_backend} ({args.executor_model})")
    print(f"Judge: {args.judge_backend} ({args.judge_model})")
    print(f"Dry Run: {args.dry_run}")
    print("=" * 70)

    for task_idx, task in enumerate(tasks_data, 1):
        task_id = task["id"]
        skill_name = task["skill"]
        domain = task.get("domain", "General")
        prompt = task["prompt"]

        ref_content = load_reference_skill_file(args.ablations_dir, skill_name)
        ref_tokens = estimate_tokens(ref_content)

        for condition in args.conditions:
            try:
                ablation_content, file_path = load_ablation_file(args.ablations_dir, skill_name, condition)
            except FileNotFoundError as e:
                print(f"Skipping {task_id} / {condition}: {e}")
                continue

            ablation_tokens = estimate_tokens(ablation_content)
            removed_tokens = max(0, ref_tokens - ablation_tokens)
            reduction_pct = round((removed_tokens / max(1, ref_tokens)) * 100, 2)

            mag_info = {
                "reference_tokens": ref_tokens,
                "ablation_tokens": ablation_tokens,
                "removed_tokens": removed_tokens,
                "reduction_percentage": reduction_pct,
            }

            for r_idx in range(1, args.runs + 1):
                if (task_id, condition, r_idx) in completed_keys:
                    continue

                current_run += 1
                print(
                    f"[{current_run}/{total_runs}] Task: {task_id} | Cond: {condition} | Run {r_idx}/{args.runs} ... ",
                    end="",
                    flush=True,
                )

                exec_prompt = build_executor_prompt(prompt, ablation_content)
                rc, stdout, stderr, exec_time = run_executor(
                    exec_prompt,
                    backend=args.executor_backend,
                    model=args.executor_model,
                    dry_run=args.dry_run,
                )

                if rc != 0:
                    print(f"FAILED (exec error {rc})")
                    continue

                output_tokens = estimate_tokens(stdout)
                syntax_checked, syntax_errs = check_syntax(stdout)

                raw_filename = f"{task_id}_{condition}_r{r_idx}.txt"
                raw_path = RAW_OUTPUTS_DIR / raw_filename
                raw_path.write_text(stdout, encoding="utf-8")

                judge_scores, judge_usage, judge_status = run_judge(
                    prompt,
                    stdout,
                    backend=args.judge_backend,
                    model=args.judge_model,
                    dry_run=args.dry_run,
                )

                if judge_scores is None:
                    print(f"FAILED (judge: {judge_status})")
                    continue

                score = judge_scores.get("total_score", 0)
                print(f"DONE (Score: {score}/35 | Latency: {round(exec_time, 1)}s)")

                record = {
                    "run_id": f"{task_id}_{condition}_r{r_idx}",
                    "task_id": task_id,
                    "skill": skill_name,
                    "domain": domain,
                    "condition": condition,
                    "run_index": r_idx,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "magnitude": mag_info,
                    "execution": {
                        "latency_s": round(exec_time, 2),
                        "output_tokens": output_tokens,
                        "syntax_checked": syntax_checked,
                        "syntax_errors": syntax_errs,
                        "raw_output_file": str(raw_path.relative_to(ROOT)),
                    },
                    "judge": {
                        "backend": args.judge_backend,
                        "model": args.judge_model,
                        "scores": judge_scores,
                        "usage": judge_usage,
                    },
                }

                results_data["runs"].append(record)
                completed_keys.add((task_id, condition, r_idx))
                atomic_write_json(args.out_results, results_data)

    print("\n" + "=" * 70)
    print(f"Ablation experiment finished! Saved {len(results_data['runs'])} records to {args.out_results}")
    print("=" * 70)


if __name__ == "__main__":
    main()
