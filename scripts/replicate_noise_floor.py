#!/usr/bin/env python3
"""Re-measure the test-retest floor on fresh generations.

NOT USED FOR ANY NUMBER IN THE PAPER. This is a side tool. The reported floor
comes from `verify_noise_floor.py` over the archived runs, which is the correct
population: a test-retest floor is only interpretable against the process that
produced the scores being interpreted. See section 8.5 of the manuscript for why
a fresh-generation estimate would not be comparable and is deliberately not
reported. The script is kept because it documents that reasoning and because the
design below is a faithful reproduction of the archived instrument.

Why this exists
---------------
`scripts/verify_noise_floor.py` recomputes sigma = 5.37 from the archived runs.
That establishes the figure is *recomputable*. It does not establish that the
archived sample's floor equals the instrument's true floor, and the paper says
so in its Future Work. This script closes that gap: it generates fresh repeats
on byte-identical prompts and re-estimates the floor from scratch.

Design fidelity
---------------
The replication reproduces the original instrument rather than inventing one:

* **Condition.** The `control` arm: the task prompt verbatim, with no skill
  content injected. In the archived benchmark this is the zero-skill baseline,
  and its prompt is byte-identical across repeats -- which is exactly the
  condition under which a test-retest floor is defined.
* **Executor independence.** Each repeat is a fresh `cmd -p --no-session`
  invocation, as in `scripts/skill_delivery_experiment.py`. Repeats MUST be
  independent or they are not a test-retest measurement: a continuing session
  would let the model condition on its own previous answers, which changes
  what is being measured. The cost of independence is that the CLI's ~41.7k
  system prefix is re-sent per repeat.
* **Judging structure.** All repeats of a task are scored in ONE judging
  window, using the original rubric template verbatim ("You will score N agent
  responses to the same task"). The archived protocol also judged all five
  arms of a task in a single window -- that is what makes slot-position bias
  observable -- so judging M same-condition repeats in one window is the same
  instrument with a different arm set.
* **Judging session reuse.** All judging calls run inside ONE `cmd` session so
  the CLI's system prefix is cache-written once instead of per task. This is a
  deliberate deviation from the archived protocol, in which each window was
  independent. It does not bias the estimate: sigma is a *within-task*
  quantity, and sharing a session across tasks affects between-task behaviour.
  It is recorded in the output so the deviation is auditable.

Usage:
    uv run python scripts/replicate_noise_floor.py --tasks 2 --repeats 5   # pilot
    uv run python scripts/replicate_noise_floor.py --tasks 8 --repeats 5   # full

The run is resumable: records are appended to the output JSONL as they
complete, and completed (task, repeat) pairs are skipped on restart.
"""

from __future__ import annotations

import argparse
import json
import math
import pathlib
import re
import statistics as st
import subprocess
import sys
import time

REPO = pathlib.Path(__file__).resolve().parents[1]
TASKS = REPO / "benchmarks" / "tasks_ieee.json"
OUT_DIR = REPO / "benchmarks"

CRITERIA = [
    "correctness", "completeness", "maintainability", "architecture",
    "security", "reasoning_quality", "instruction_adherence",
]

# sigma reported by the paper, recomputed from the archive.
PAPER_SIGMA = 5.365
PAPER_SIGMA_D = 3.760
PAPER_MDE = 3.613


def run_cmd(args: list[str], timeout: int) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
        return proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        return 124, "", f"TIMEOUT after {timeout}s"
    except Exception as exc:  # pragma: no cover - defensive
        return 1, "", f"exception: {exc}"


def generate(prompt: str, model: str, timeout: int) -> dict:
    """One independent executor call. Fresh session: repeats must not see each other."""
    args = ["cmd", "-p", prompt, "--no-session", "--yolo",
            "-m", model, "--output-format", "json"]
    start = time.perf_counter()
    rc, out, err = run_cmd(args, timeout)
    elapsed = time.perf_counter() - start
    text = ""
    for line in reversed(out.splitlines()):
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        if rec.get("type") == "result":
            text = rec.get("finalText", "") or ""
            usage = rec.get("usage", {}) or {}
            return {
                "ok": rc == 0 and bool(text.strip()),
                "text": text,
                "usage": {
                    "input": usage.get("inputTokens"),
                    "output": usage.get("outputTokens"),
                    "cache_read": usage.get("cacheReadTokens"),
                    "cache_write": usage.get("cacheWriteTokens"),
                },
                "elapsed_s": round(elapsed, 1),
                "returncode": rc,
                "stderr": err[:200],
            }
    return {"ok": False, "text": "", "usage": {},
            "elapsed_s": round(elapsed, 1), "returncode": rc, "stderr": err[:200]}


def judging_prompt(task_prompt: str, outputs: list[str], max_chars: int) -> str:
    """Verbatim structure of build_judging_prompt in skill_delivery_experiment.py."""
    labels = [chr(ord("A") + i) for i in range(len(outputs))]
    blocks = []
    for label, body in sorted(zip(labels, outputs)):
        if len(body) > max_chars:
            body = body[:max_chars] + "\n...[truncated]"
        blocks.append(f"[Response {label}]:\n{body}\n")
    score_template = ",\n    ".join(
        f'"{lbl}": {{"correctness":N,"completeness":N,"maintainability":N,'
        f'"architecture":N,"security":N,"reasoning_quality":N,'
        f'"instruction_adherence":N,"justification":"..."}}'
        for lbl in labels
    )
    labels_str = ", ".join(labels)
    return f"""You are an expert AI evaluator. You will score {len(labels)} agent responses to the same task.

[Original Task Prompt]:
{task_prompt}

---
{'---'.join(blocks)}
---

Score each response ({labels_str}) on these 7 criteria (1-5 each):
{', '.join(CRITERIA)}

Also determine the overall ranking from best to worst and write a pairwise comparison explaining why responses differ.

Respond with a single ```json ... ``` block following this exact structure:
{{
  "scores": {{
    {score_template}
  }},
  "ranking": {json.dumps(labels)},
  "pairwise_analysis": "2-3 sentence comparison explaining key quality differences"
}}"""


def parse_scores(text: str, n: int) -> dict[str, int] | None:
    m = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
    raw = m.group(1) if m else text.strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None
    scores = data.get("scores") or {}
    out = {}
    for label in [chr(ord("A") + i) for i in range(n)]:
        rec = scores.get(label)
        if not isinstance(rec, dict):
            return None
        try:
            total = sum(int(rec[c]) for c in CRITERIA)
        except (KeyError, TypeError, ValueError):
            return None
        if not 7 <= total <= 35:
            return None
        out[label] = total
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tasks", type=int, default=8)
    ap.add_argument("--repeats", type=int, default=5)
    ap.add_argument("--executor", default="qwen/qwen3.7-flash")
    ap.add_argument("--judge", default="deepseek/deepseek-v4-pro")
    ap.add_argument("--max-chars", type=int, default=10000)
    ap.add_argument("--gen-timeout", type=int, default=600)
    ap.add_argument("--judge-timeout", type=int, default=900)
    ap.add_argument("--out", default="replication_fresh_results.jsonl")
    args = ap.parse_args()

    tasks = json.loads(TASKS.read_text())
    if not TASKS.exists():
        sys.exit(f"task file absent: {TASKS}")
    selected = tasks[: args.tasks]

    out_path = OUT_DIR / args.out
    done: set[tuple[str, int]] = set()
    if out_path.exists():
        for line in out_path.read_text().splitlines():
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("phase") == "generate" and rec.get("ok"):
                done.add((rec["task_id"], rec["repeat"]))

    print(f"Replication: {len(selected)} tasks x {args.repeats} repeats")
    print(f"  executor={args.executor}  judge={args.judge}")
    print(f"  resuming, {len(done)} generations already complete\n")

    fh = out_path.open("a", encoding="utf-8")

    # ---- Phase 1: independent generation -----------------------------------
    print("Phase 1/2  generation (independent sessions -- repeats must not")
    print("           see each other, or this is not a test-retest measurement)")
    for task in selected:
        tid = task["id"]
        prompt = task["prompt"]          # control condition: prompt verbatim
        for rep in range(args.repeats):
            if (tid, rep) in done:
                continue
            res = generate(prompt, args.executor, args.gen_timeout)
            rec = {
                "phase": "generate", "task_id": tid, "repeat": rep,
                "condition": "control_fresh", "model": args.executor,
                "ok": res["ok"], "text": res["text"], "usage": res["usage"],
                "elapsed_s": res["elapsed_s"], "ts": time.time(),
            }
            fh.write(json.dumps(rec) + "\n"); fh.flush()
            status = "ok " if res["ok"] else "FAIL"
            print(f"  [{status}] {tid:36s} r{rep}  {res['elapsed_s']:6.1f}s  "
                  f"{len(res['text']):6d} ch")

    # ---- Phase 2: judging, one session reused across tasks ------------------
    print("\nPhase 2/2  judging (all repeats of a task in ONE window, matching")
    print("           the original protocol; one session so the CLI system")
    print("           prefix is cache-written once, not per task)")
    judged: set[str] = set()
    if out_path.exists():
        for line in out_path.read_text().splitlines():
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("phase") == "judge" and rec.get("ok"):
                judged.add(rec["task_id"])

    cont = ["-c"]
    for task in selected:
        tid = task["id"]
        if tid in judged:
            continue
        outputs = []
        for rep in range(args.repeats):
            for line in reversed(out_path.read_text().splitlines()):
                rec = json.loads(line)
                if (rec.get("phase") == "generate" and rec.get("task_id") == tid
                        and rec.get("repeat") == rep and rec.get("ok")):
                    outputs.append(rec["text"]); break
        if len(outputs) != args.repeats:
            print(f"  [SKIP] {tid}: only {len(outputs)}/{args.repeats} generations")
            continue

        jp = judging_prompt(task["prompt"], outputs, args.max_chars)
        cargs = ["cmd", "-p", jp, "--yolo", "-m", args.judge,
                 "--output-format", "json", *cont]
        start = time.perf_counter()
        rc, out, err = run_cmd(cargs, args.judge_timeout)
        elapsed = time.perf_counter() - start
        cont = ["-c"]  # reuse the same session for the next task

        final = ""
        usage = {}
        for line in reversed(out.splitlines()):
            try:
                rec2 = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec2.get("type") == "result":
                final = rec2.get("finalText", "") or ""
                usage = rec2.get("usage", {}) or {}
                break

        scores = parse_scores(final, args.repeats)
        rec = {
            "phase": "judge", "task_id": tid, "ok": scores is not None,
            "scores": scores, "model": args.judge,
            "usage": {
                "input": usage.get("inputTokens"),
                "output": usage.get("outputTokens"),
                "cache_read": usage.get("cacheReadTokens"),
                "cache_write": usage.get("cacheWriteTokens"),
            },
            "elapsed_s": round(elapsed, 1), "ts": time.time(),
            "rc": rc, "raw": final if scores is None else None,
            "stderr": err[:200],
        }
        fh.write(json.dumps(rec) + "\n"); fh.flush()
        status = "ok " if scores else "FAIL"
        print(f"  [{status}] {tid:36s} {elapsed:6.1f}s  scores={scores}")
        if scores is None:
            print(f"         raw: {final[:180]!r}")
    fh.close()

    # ---- Analysis -----------------------------------------------------------
    print("\nAnalysis")
    gens, judges = {}, {}
    for line in out_path.read_text().splitlines():
        rec = json.loads(line)
        if rec.get("phase") == "generate" and rec.get("ok"):
            gens[(rec["task_id"], rec["repeat"])] = rec
        if rec.get("phase") == "judge" and rec.get("ok"):
            judges[rec["task_id"]] = rec

    per_task, ss, df = {}, 0.0, 0
    for tid, jrec in judges.items():
        vals = [jrec["scores"][chr(ord("A") + i)] for i in range(args.repeats)]
        if len(set(vals)) == 1 and args.repeats > 1:
            per_task[tid] = {"scores": vals, "sd": 0.0}
        else:
            per_task[tid] = {"scores": vals, "sd": st.stdev(vals)}
        m = st.mean(vals)
        ss += sum((v - m) ** 2 for v in vals)
        df += len(vals) - 1

    if df == 0:
        print("  insufficient complete cells to estimate a floor")
        return 1

    sigma = math.sqrt(ss / df)
    sds = [v["sd"] for v in per_task.values()]
    print(f"  tasks with a complete window : {len(per_task)}")
    print(f"  fresh pooled within-task SD  : {sigma:.3f}")
    print(f"  per-task SD range            : {min(sds):.2f} - {max(sds):.2f}")
    print(f"  archived sigma (paper)       : {PAPER_SIGMA:.3f}")
    print(f"  difference                   : {sigma - PAPER_SIGMA:+.3f}")
    ratio = sigma / PAPER_SIGMA
    print(f"  ratio fresh/archived         : {ratio:.2f}x")

    usage_in = usage_out = cache_r = cache_w = 0
    for rec in list(gens.values()) + list(judges.values()):
        u = rec.get("usage") or {}
        usage_in += u.get("input") or 0
        usage_out += u.get("output") or 0
        cache_r += u.get("cache_read") or 0
        cache_w += u.get("cache_write") or 0
    print(f"\n  tokens: input={usage_in:,} output={usage_out:,} "
          f"cache_read={cache_r:,} cache_write={cache_w:,}")

    summary = {
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "design": {
            "condition": "control (task prompt verbatim, no skill content)",
            "executor": args.executor, "judge": args.judge,
            "tasks": len(per_task), "repeats_per_task": args.repeats,
            "executor_sessions": "independent per repeat (required for a valid"
                                 " test-retest estimate)",
            "judging": "all repeats of a task in one window; one session reused"
                       " across tasks (deviation from the archived protocol,"
                       " which used independent windows)",
            "max_chars_per_response": args.max_chars,
        },
        "fresh_sigma": sigma,
        "per_task_sd_range": [min(sds), max(sds)],
        "archived_sigma": PAPER_SIGMA,
        "sigma_ratio_fresh_over_archived": ratio,
        "sigma_difference": sigma - PAPER_SIGMA,
        "per_task": per_task,
        "usage": {"input": usage_in, "output": usage_out,
                  "cache_read": cache_r, "cache_write": cache_w},
    }
    sp = OUT_DIR / "replication_fresh_summary.json"
    sp.write_text(json.dumps(summary, indent=2))
    print(f"\n  wrote {sp.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())