#!/usr/bin/env python3
"""
Multi-Skill Scaling Experiment — IEEE Study (RQ5, measured)
===========================================================
Measures prompt-token compounding and score stability as the number of
concurrently loaded skills K grows, for `full` (verbatim manuals) vs
`checklist_v2` (structure-preserving compilation).

Design: K in {1, 5, 10, 20} x {full, checklist_v2} x tasks x runs.
The task's own skill is always position 1; distractors follow fixed
manifest order (controls position effects).

Two-phase operation (executor and judge may run on different days):
  python3 scripts/run_multiskill_experiment.py --execute-only   # executor runs now
  python3 scripts/run_multiskill_experiment.py --judge-only     # blind judging later
  python3 scripts/run_multiskill_experiment.py --resume         # either phase, resume

Prompt formats mirror scripts/skill_delivery_experiment.py:
  full: "[SKILL GUIDELINES - K SKILLS]\\n<manuals>\\n\\n[TASK]\\n<prompt>"
  v2:   "[ENGINEERING IMPLEMENTATION ...]\\n<checklists>\\n\\n[TASK]...[INSTRUCTION]..."
"""

import argparse
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent

DEFAULT_TASKS = ROOT / "benchmarks" / "tasks_multiskill_subset.json"
DEFAULT_MANIFEST = ROOT / "benchmarks" / "checklists_v2" / "manifest.json"
DEFAULT_RESULTS = ROOT / "benchmarks" / "multiskill_results_longcat.json"
RAW_OUTPUTS_DIR = ROOT / "benchmarks" / "raw_outputs_multiskill"

JUDGE_CRITERIA = [
    "correctness",
    "completeness",
    "maintainability",
    "architecture",
    "security",
    "reasoning_quality",
    "instruction_adherence",
]

DEFAULT_KS = [1, 5, 10, 20]
DEFAULT_STRATEGIES = ["full", "checklist_v2"]


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def atomic_write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    tmp.replace(path)


def load_skill_ids(manifest_path: Path) -> List[str]:
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    return sorted(data.get("skills", {}).keys())


def load_full_manual(skill: str) -> str:
    p = ROOT / "skills" / skill / "SKILL.md"
    if p.exists():
        return p.read_text(encoding="utf-8")
    # fallback: recursive search
    for cand in (ROOT / "skills").rglob("SKILL.md"):
        if cand.parent.name == skill:
            return cand.read_text(encoding="utf-8")
    raise FileNotFoundError(f"SKILL.md not found for {skill}")


def load_v2_checklist(skill: str) -> str:
    p = ROOT / "benchmarks" / "checklists_v2" / f"{skill}.txt"
    if p.exists():
        return p.read_text(encoding="utf-8")
    raise FileNotFoundError(f"checklist_v2 not found for {skill}")


def build_prompt(task_prompt: str, skill_docs: List[str], strategy: str) -> str:
    body = "\n\n---\n\n".join(d.strip() for d in skill_docs)
    if strategy == "full":
        return f"[SKILL GUIDELINES - {len(skill_docs)} SKILLS]\n{body}\n\n[TASK]\n{task_prompt}"
    return (
        "[ENGINEERING IMPLEMENTATION STANDARDS & ARCHITECTURAL CONSTRAINTS]\n"
        f"{body}\n\n[TASK]\n{task_prompt}\n\n"
        "[INSTRUCTION]: Apply the above engineering standards and architectural constraints rigorously. "
        "Output your complete, production-grade code implementation and review directly in your markdown response."
    )


def check_syntax(output: str) -> Tuple[int, List[str]]:
    blocks = re.findall(
        r"```(python|py|javascript|typescript|js|ts|sql)\n(.*?)```", output, re.DOTALL | re.IGNORECASE
    )
    checked, errors = 0, []
    for lang, code in blocks:
        checked += 1
        if lang.lower() in ("python", "py"):
            try:
                compile(code, "<agent_output>", "exec")
            except SyntaxError as e:
                errors.append(f"Python syntax error at line {e.lineno}: {e.msg}")
            except Exception as e:
                errors.append(f"Python check error: {e}")
    return checked, errors


def run_cmd(prompt: str, model: str, timeout: int, dry_run: bool, mock_text: str = "") -> Tuple[int, str, str, float, str]:
    if dry_run:
        time.sleep(0.02)
        return 0, mock_text or "# mock", "", 0.02, "mock"
    start = time.perf_counter()
    # Linux caps a single argv string at ~128KB (MAX_ARG_STRLEN); large
    # multi-skill prompts exceed it, so pipe them via stdin instead.
    # The model sees byte-identical prompt text either way.
    if len(prompt.encode("utf-8")) > 100_000:
        cmd = ["cmd", "-p", "--no-session", "--yolo", "-m", model]
        delivery = "stdin"
        try:
            proc = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=timeout)
            return proc.returncode, proc.stdout, proc.stderr, time.perf_counter() - start, delivery
        except subprocess.TimeoutExpired:
            return 124, "", f"TIMEOUT after {timeout}s", float(timeout), delivery
        except Exception as e:
            return 1, "", f"Execution exception: {e}", time.perf_counter() - start, delivery
    cmd = ["cmd", "-p", prompt, "--no-session", "--yolo", "-m", model]
    delivery = "argv"
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return proc.returncode, proc.stdout, proc.stderr, time.perf_counter() - start, delivery
    except subprocess.TimeoutExpired:
        return 124, "", f"TIMEOUT after {timeout}s", float(timeout), delivery
    except Exception as e:
        return 1, "", f"Execution exception: {e}", time.perf_counter() - start, delivery


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
            scores[crit] = max(1, min(5, int(data[crit])))
        scores["total_score"] = sum(scores[c] for c in JUDGE_CRITERIA)
        scores["justification"] = data.get("justification", "")
        return scores
    except Exception:
        return None


def get_git_commit() -> str:
    try:
        proc = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True)
        return proc.stdout.strip()
    except Exception:
        return "unknown"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run multi-skill scaling experiments.")
    parser.add_argument("--tasks", type=Path, default=DEFAULT_TASKS)
    parser.add_argument("--ks", nargs="+", type=int, default=DEFAULT_KS)
    parser.add_argument("--strategies", nargs="+", default=DEFAULT_STRATEGIES)
    parser.add_argument("--runs", type=int, default=2)
    parser.add_argument("--executor-backend", default="cmd", choices=["cmd", "mock"])
    parser.add_argument("--executor-model", default="meituan/longcat-2.0:free")
    parser.add_argument("--judge-backend", default="cmd", choices=["cmd", "mock"])
    parser.add_argument("--judge-model", default="deepseek/deepseek-v4-pro")
    parser.add_argument("--out-results", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument("--exec-timeout", type=int, default=300)
    parser.add_argument("--judge-timeout", type=int, default=300)
    parser.add_argument("--execute-only", action="store_true")
    parser.add_argument("--judge-only", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not args.tasks.exists():
        print(f"Error: tasks file {args.tasks} missing", file=sys.stderr)
        sys.exit(1)
    tasks_data = json.loads(args.tasks.read_text(encoding="utf-8"))
    all_skills = load_skill_ids(DEFAULT_MANIFEST)
    RAW_OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    results: Dict[str, Any] = {
        "metadata": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "git_commit": get_git_commit(),
            "compiler_version": "0.2.0",
            "executor_backend": args.executor_backend,
            "executor_model": args.executor_model,
            "judge_backend": args.judge_backend,
            "judge_model": args.judge_model,
            "ks": args.ks,
            "strategies": args.strategies,
            "runs": args.runs,
            "dry_run": args.dry_run,
        },
        "runs": [],
    }
    if args.resume and args.out_results.exists():
        try:
            existing = json.loads(args.out_results.read_text(encoding="utf-8"))
            results["runs"] = existing.get("runs", [])
            print(f"Resuming with {len(results['runs'])} completed runs loaded.")
        except Exception as e:
            print(f"Warning: resume load failed: {e}. Starting fresh.")

    have_exec = {(r["task_id"], r["strategy"], r["k"], r["run_index"])
                 for r in results["runs"] if "raw_output_file" in r.get("execution", {})}
    have_judge = {(r["task_id"], r["strategy"], r["k"], r["run_index"])
                  for r in results["runs"] if "scores" in r.get("judge", {})}

    total = len(tasks_data) * len(args.ks) * len(args.strategies) * args.runs
    print("=" * 70)
    print(f"Multi-Skill Scaling Runner: {total} planned "
          f"({len(tasks_data)} tasks x K={args.ks} x {args.strategies} x {args.runs} runs)")
    print(f"Executor: {args.executor_model} | Judge: {args.judge_model}")
    print(f"Modes: execute-only={args.execute_only} judge-only={args.judge_only} dry={args.dry_run}")
    print("=" * 70)

    do_exec = not args.judge_only
    do_judge = not args.execute_only
    n_done = 0

    for task in tasks_data:
        task_id, own_skill = task["id"], task["skill"]
        distractors = [s for s in all_skills if s != own_skill]
        for k in args.ks:
            _picked = [own_skill] + distractors[: max(0, k - 1)]
            for strategy in args.strategies:
                loader = load_full_manual if strategy == "full" else load_v2_checklist
                try:
                    docs = [loader(s) for s in _picked]
                except FileNotFoundError as e:
                    print(f"Skipping {task_id} K={k} {strategy}: {e}")
                    continue
                prompt = build_prompt(task["prompt"], docs, strategy)
                in_tok = estimate_tokens(prompt)
                for r_idx in range(1, args.runs + 1):
                    key = (task_id, strategy, k, r_idx)
                    rec = next((r for r in results["runs"]
                                if (r["task_id"], r["strategy"], r["k"], r["run_index"]) == key), None)
                    if rec is None:
                        rec = {
                            "run_id": f"{task_id}_K{k}_{strategy}_r{r_idx}",
                            "task_id": task_id, "strategy": strategy, "k": k,
                            "skills": _picked, "run_index": r_idx,
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "prompt_tokens": in_tok,
                            "execution": {}, "judge": {},
                        }
                        results["runs"].append(rec)

                    if do_exec and key not in have_exec:
                        n_done += 1
                        print(f"[{n_done}/{total}] EXEC {task_id} K={k} {strategy} r{r_idx} "
                              f"({in_tok} tok) ... ", end="", flush=True)
                        rc, stdout, stderr, elapsed, delivery = run_cmd(
                            prompt, args.executor_model, args.exec_timeout,
                            args.dry_run or args.executor_backend == "mock",
                            mock_text="# Solution\n```python\ndef solution():\n    return 'mock'\n```\n")
                        if rc != 0:
                            print(f"FAILED (exec error {rc}: {stderr[:120]})")
                            continue
                        checked, errs = check_syntax(stdout)
                        raw_path = RAW_OUTPUTS_DIR / f"{task_id}_K{k}_{strategy}_r{r_idx}.txt"
                        raw_path.write_text(stdout, encoding="utf-8")
                        rec["execution"] = {
                            "latency_s": round(elapsed, 2),
                            "exec_timeout_s": args.exec_timeout,
                            "delivery": delivery,
                            "output_tokens": estimate_tokens(stdout),
                            "syntax_checked": checked, "syntax_errors": errs,
                            "raw_output_file": str(raw_path.relative_to(ROOT)),
                        }
                        have_exec.add(key)
                        atomic_write_json(args.out_results, results)
                        print(f"DONE ({estimate_tokens(stdout)} out-tok, {elapsed:.0f}s)")

                    if do_judge and key in have_exec and key not in have_judge:
                        raw_rel = rec["execution"].get("raw_output_file", "")
                        raw_path = ROOT / raw_rel if raw_rel else None
                        if not raw_path or not raw_path.exists():
                            print(f"Skipping judge {key}: raw output missing")
                            continue
                        n_done += 1
                        print(f"[{n_done}/{total}] JUDGE {task_id} K={k} {strategy} r{r_idx} ... ",
                              end="", flush=True)
                        agent_out = raw_path.read_text(encoding="utf-8")
                        jp = build_judge_prompt(task["prompt"], agent_out)
                        if args.dry_run or args.judge_backend == "mock":
                            sc = {c: 4 for c in JUDGE_CRITERIA}
                            sc["total_score"] = 28
                            sc["justification"] = "Dry run mock evaluation."
                            rec["judge"] = {"scores": sc, "usage": {"latency_s": 0.02}}
                        else:
                            rc, out, err, elapsed, _ = run_cmd(
                                jp, args.judge_model, args.judge_timeout, False)
                            if rc != 0:
                                print(f"FAILED (judge error {rc}: {err[:120]})")
                                continue
                            parsed = parse_judge_json(out)
                            if parsed is None:
                                print("FAILED (judge JSON parse)")
                                continue
                            rec["judge"] = {
                                "backend": args.judge_backend, "model": args.judge_model,
                                "scores": parsed, "usage": {"latency_s": round(elapsed, 2)},
                            }
                        have_judge.add(key)
                        atomic_write_json(args.out_results, results)
                        print(f"DONE ({rec['judge']['scores']['total_score']}/35)")

    print("\n" + "=" * 70)
    print(f"Finished. {len(have_exec)} executed, {len(have_judge)} judged. Saved to {args.out_results}")
    print("=" * 70)


if __name__ == "__main__":
    main()
