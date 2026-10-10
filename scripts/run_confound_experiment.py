#!/usr/bin/env python3
"""Confound experiment: does the trailing [INSTRUCTION] directive drive
checklist_v2's higher output volume?

Background
----------
Finding 2 of the manuscript reports that structure-preserving compilation
(`checklist_v2`) elicited the highest mean output token volume (5,431 vs 4,588
for uncompressed manuals, +18.4%). That claim is confounded.

In `scripts/skill_delivery_experiment.py`, `strategy_checklist_v2` is the ONLY
delivery arm that appends a trailing directive to the prompt:

    [INSTRUCTION]: Apply the above engineering standards and architectural
    constraints rigorously. Output your complete, production-grade code
    implementation and review directly in your markdown response.

An instruction to "output your complete, production-grade code implementation"
plausibly produces more output on its own. The experiment cannot attribute the
+843 tokens to compression versus that directive.

This script isolates the variable. For each task it renders the *exact* prompt
the archived run used (condition `v2_with_directive`) and a second prompt
identical except for the removal of exactly that trailing directive
(condition `v2_no_directive`). The no-directive prompt is produced by string
surgery on the with-directive prompt, so the directive is provably the only
difference; `assert` enforces this before any spend.

Design notes
------------
* **Half A only.** Finding 2 is a statement about output volume, which is a
  generator-side metric. No judge is invoked, so no rubric scoring happens and
  no cost is incurred on the evaluation side.
* **Conditions are always compared to each other**, never against the archived
  396 evaluations. Judge and generator non-determinism across sessions makes
  cross-session comparison noisy even with an identical model.
* **Real token counts** are recorded when the backend reports usage, so the
  result is not dependent on the `len(text) // 4` estimator used elsewhere in
  this repository.

Usage
-----
Validate prompts without spending anything:

    uv run python scripts/run_confound_experiment.py --dry-run

Run the experiment (option B, no top-up required):

    uv run python scripts/run_confound_experiment.py \
        --backend opencode --model openrouter/qwen/qwen3.7-flash \
        --tasks sec-webhook-audit-ieee,sre-flaky-ci-ieee

Exit codes: 0 = success, 1 = failure, 2 = usage/dry-run with no results written.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import statistics as st
import subprocess
import sys
import time
from collections import defaultdict

REPO = pathlib.Path(__file__).resolve().parents[1]
TASKS_FILE = REPO / "benchmarks" / "tasks_ieee.json"
DEFAULT_OUT = REPO / "benchmarks" / "confound_results.json"
RAW_DIR = REPO / "benchmarks" / "raw_outputs_confound"

# The exact trailing directive appended by strategy_checklist_v2.
DIRECTIVE_RE = re.compile(
    r"\n\n\[INSTRUCTION\]: Apply the above engineering standards and "
    r"architectural constraints rigorously\. Output your complete, "
    r"production-grade code implementation and review directly in your "
    r"markdown response\.$"
)

OUTPUT_GUARD = (
    "\n\n[OUTPUT INSTRUCTION]: Provide your complete analysis and full code "
    "implementation directly in your markdown response text. Do NOT create, "
    "write, or modify any files on disk."
)

DEFAULT_TASKS = [
    # Spread across five of the six domains so the directive effect is not
    # measured on a single task type. TDD is included deliberately: it is the
    # task whose skill actually mattered (RQ4, delta -8.50), so it tests
    # whether the directive's effect interacts with genuinely useful content.
    "sec-webhook-audit-ieee",        # Security & Auditing
    "sre-flaky-ci-ieee",             # SRE & Debugging
    "qa-ratelimiter-tdd-ieee",       # Testing & QA
    "db-analytics-query-ieee",       # Databases & Persistence
    "devops-ml-docker-ieee",         # DevOps & Cloud
]


# --------------------------------------------------------------------------
# Prompt construction
# --------------------------------------------------------------------------
def build_prompts(task: dict, skill_md: str, compiled: str) -> dict[str, str]:
    """Render the two conditions from one shared skill block.

    The no-directive variant is derived by removing exactly the trailing
    directive from the with-directive prompt, so the directive is the only
    difference between the two strings.
    """
    base = (
        f"[ENGINEERING IMPLEMENTATION STANDARDS & ARCHITECTURAL CONSTRAINTS]\n"
        f"{compiled}\n\n[TASK]\n{task['prompt']}"
    )
    with_directive = base + (
        "\n\n[INSTRUCTION]: Apply the above engineering standards and "
        "architectural constraints rigorously. Output your complete, "
        "production-grade code implementation and review directly in your "
        "markdown response."
    )

    stripped, n = DIRECTIVE_RE.subn("", with_directive)
    if n != 1:
        raise AssertionError(
            f"expected exactly one trailing directive to strip, found {n}"
        )
    if stripped + "\n\n" not in with_directive and stripped == with_directive:
        raise AssertionError("directive removal was a no-op")

    # Prove the two prompts differ only by the directive.
    assert stripped.endswith(task["prompt"]), "stripped prompt must end at the task"
    assert with_directive.startswith(stripped), "stripped must be a prefix of full"
    assert with_directive[len(stripped):] == with_directive[len(stripped):]
    delta = with_directive[len(stripped):]
    assert delta.startswith("\n\n[INSTRUCTION]:"), f"unexpected delta: {delta[:60]!r}"

    return {"v2_with_directive": with_directive, "v2_no_directive": stripped}


def load_reference(task: dict) -> tuple[str, str]:
    """Return (skill_md, compiled_v2) for a task, from the repository."""
    from skill_delivery_experiment import load_checklist_v2  # noqa: PLC0415

    skill_name = task["skill"]
    skill_md = (REPO / "skills" / skill_name / "SKILL.md").read_text(encoding="utf-8")
    compiled, source = load_checklist_v2(skill_name, skill_md)
    if source != "artifact_v2":
        raise SystemExit(
            f"no committed v2 artifact for '{skill_name}' (got {source!r}); "
            "run the Rust compiler first"
        )
    return skill_md, compiled


# --------------------------------------------------------------------------
# Execution backends
# --------------------------------------------------------------------------
def run_opencode(prompt: str, model: str, timeout: int, retries: int = 2) -> dict:
    """Execute via the opencode CLI, capturing real token usage.

    stdin must be closed: without </dev/null the CLI blocks waiting on input
    rather than exiting after the run.

    The CLI hangs intermittently rather than failing fast: observed latencies
    are cleanly bimodal, with successes finishing in 52-109s and failures
    hanging until the timeout expires. Nothing lands in between, so a hang is
    not a slow model and will not resolve on its own. Retries recover these.
    """
    cmd = ["opencode", "run", "--format", "json", "-m", model, prompt + OUTPUT_GUARD]

    result = None
    for attempt in range(retries + 1):
        start = time.perf_counter()
        try:
            with open("/dev/null", "r") as devnull:
                proc = subprocess.run(
                    cmd, stdin=devnull, capture_output=True, text=True, timeout=timeout
                )
            rc, out, err = proc.returncode, proc.stdout, proc.stderr
        except subprocess.TimeoutExpired:
            rc, out, err = 124, "", f"TIMEOUT after {timeout}s"
        except Exception as exc:  # noqa: BLE001
            rc, out, err = 1, "", f"Exception: {exc}"
        elapsed = time.perf_counter() - start

        usage, text = _parse_opencode_json(out)
        result = {
            "rc": rc, "stderr": err[-400:], "latency_s": round(elapsed, 2),
            "output": text, "usage": usage, "raw_stream": out if rc else "",
        }
        result["attempts"] = attempt + 1

        if rc == 0 and text.strip():
            return result
        if attempt < retries:
            backoff = 5 * (attempt + 1)
            print(f"       (attempt {attempt + 1} failed rc={rc}, "
                  f"{elapsed:.0f}s; retrying in {backoff}s)")
            time.sleep(backoff)

    return result


def run_cmd(prompt: str, model: str, timeout: int) -> dict:
    """Execute via the cmd CLI (requires Command Code credits)."""
    cmd = ["cmd", "-p", prompt + OUTPUT_GUARD, "--no-session", "--yolo", "-m", model]
    start = time.perf_counter()
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        rc, out, err = proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        rc, out, err = 124, "", f"TIMEOUT after {timeout}s"
    except Exception as exc:  # noqa: BLE001
        rc, out, err = 1, "", f"Exception: {exc}"
    elapsed = time.perf_counter() - start
    return {
        "rc": rc, "stderr": err[-400:], "latency_s": round(elapsed, 2),
        "output": out, "usage": None, "raw_stream": "",
    }


def _parse_opencode_json(stream: str) -> tuple[dict | None, str]:
    """Extract final text and real token usage from the NDJSON event stream."""
    usage, chunks = None, []
    for line in stream.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            evt = json.loads(line)
        except json.JSONDecodeError:
            continue
        if evt.get("type") == "text":
            part = evt.get("part", {})
            if isinstance(part.get("text"), str):
                chunks.append(part["text"])
        elif evt.get("type") == "step_finish":
            tokens = evt.get("part", {}).get("tokens")
            if tokens:
                usage = {
                    "input": tokens.get("input"),
                    "output": tokens.get("output"),
                    "reasoning": tokens.get("reasoning"),
                    "cache_read": (tokens.get("cache") or {}).get("read"),
                    "cache_write": (tokens.get("cache") or {}).get("write"),
                    "cost": evt.get("part", {}).get("cost"),
                }
    return usage, "".join(chunks)


# --------------------------------------------------------------------------
# Experiment
# --------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--backend", choices=["opencode", "cmd"], default="opencode")
    ap.add_argument("--model", default=None,
                    help="default: openrouter/qwen/qwen3.7-flash (opencode) / qwen/qwen3.7-flash (cmd)")
    ap.add_argument("--tasks", default=",".join(DEFAULT_TASKS),
                    help="comma-separated task ids from benchmarks/tasks_ieee.json")
    ap.add_argument("--runs", type=int, default=3, help="repeats per condition")
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--out", type=pathlib.Path, default=DEFAULT_OUT)
    ap.add_argument("--dry-run", action="store_true",
                    help="validate and print prompts; make no network calls")
    ap.add_argument("--resume", action="store_true",
                    help="reuse runs already recorded in --out and only fill gaps")
    args = ap.parse_args()

    model = args.model or (
        "openrouter/qwen/qwen3.7-flash" if args.backend == "opencode"
        else "qwen/qwen3.7-flash"
    )
    sys.path.insert(0, str(REPO / "scripts"))

    all_tasks = {t["id"]: t for t in json.loads(TASKS_FILE.read_text(encoding="utf-8"))}
    wanted = [x.strip() for x in args.tasks.split(",") if x.strip()]
    missing = [x for x in wanted if x not in all_tasks]
    if missing:
        raise SystemExit(f"unknown task id(s): {missing}")

    print(f"backend : {args.backend}")
    print(f"model   : {model}")
    print(f"tasks   : {len(wanted)}   runs/condition: {args.runs}")
    print(f"output  : {args.out}\n")

    prompts_by_task: dict[str, dict[str, str]] = {}
    for task_id in wanted:
        task = all_tasks[task_id]
        try:
            _, compiled = load_reference(task)
        except SystemExit as exc:
            print(f"  SKIP {task_id}: {exc}")
            continue
        prompts_by_task[task_id] = build_prompts(task, "", compiled)

    print(f"prompts validated for {len(prompts_by_task)} task(s)")
    sample = next(iter(prompts_by_task.values()), None)
    if sample:
        print(f"  directive is {len(sample['v2_with_directive']) - len(sample['v2_no_directive'])} chars")
        print(f"  condition difference is exactly the trailing [INSTRUCTION] block\n")

    if args.dry_run:
        for task_id, pr in prompts_by_task.items():
            print(f"--- {task_id} ---")
            print(f"  v2_with_directive: {len(pr['v2_with_directive'])} chars")
            print(f"  v2_no_directive  : {len(pr['v2_no_directive'])} chars")
            print(f"  task tail        : {pr['v2_no_directive'][-90:]!r}")
        print("\nDRY RUN: no network calls made, no results written.")
        return 2

    runner = run_opencode if args.backend == "opencode" else run_cmd
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    # Resume support: a full run is 30 generations of 60-110s each and the CLI
    # hangs intermittently, so completed cells are checkpointed after every run.
    records: list[dict] = []
    total_cost = 0.0
    if args.resume and args.out.exists():
        prior = json.loads(args.out.read_text(encoding="utf-8"))
        records = prior.get("runs", [])
        total_cost = prior.get("metadata", {}).get("total_cost_usd", 0.0)
        done = {(r["task_id"], r["condition"], r["run"]) for r in records}
        print(f"resuming: {len(done)} prior runs on record\n")
    else:
        done = set()
    for task_id, pr in prompts_by_task.items():
        for cond, prompt in pr.items():
            for idx in range(1, args.runs + 1):
                if (task_id, cond, idx) in done:
                    print(f"  skip  {task_id[:34]:34} {cond:18} r{idx} (already on record)")
                    continue

                res = runner(prompt, model, args.timeout)
                ok = res["rc"] == 0 and res["output"].strip()
                tokens = None
                if ok and res.get("usage") and res["usage"].get("output") is not None:
                    tokens = res["usage"]["output"]
                est = len(res["output"]) // 4 if ok else 0

                raw_path = None
                if ok:
                    raw_path = RAW_DIR / f"{task_id}_{cond}_r{idx}.txt"
                    raw_path.write_text(res["output"], encoding="utf-8")

                cost = (res.get("usage") or {}).get("cost") or 0.0
                total_cost += cost

                flag = "ok " if ok else "FAIL"
                tok_disp = f"out={tokens}" if tokens is not None else f"out~{est}"
                att = res.get("attempts", 1)
                att_disp = "" if att == 1 else f" (after {att} attempts)"
                print(f"  {flag} {task_id[:34]:34} {cond:18} r{idx} "
                      f"{res['latency_s']:6.1f}s {tok_disp}{att_disp}", flush=True)

                records.append({
                    "task_id": task_id, "condition": cond, "run": idx,
                    "ok": ok, "rc": res["rc"], "attempts": att,
                    "output_tokens_real": tokens, "output_tokens_est": est,
                    "input_tokens_real": (res.get("usage") or {}).get("input"),
                    "cost_usd": cost, "latency_s": res["latency_s"],
                    "output_chars": len(res["output"]),
                    "raw_output_file": str(raw_path.relative_to(REPO)) if raw_path else None,
                    "stderr": res["stderr"][:200],
                })
                done.add((task_id, cond, idx))

                # Checkpoint after every run so an interrupted run loses nothing.
                _checkpoint(args, records, total_cost, model, args.runs, sample)

    summary = summarise(records)
    payload = {
        "metadata": {
            "experiment": "checklist_v2 trailing-directive confound",
            "scope": "Half A (output volume only; no judge invoked)",
            "backend": args.backend, "model": model,
            "runs_per_condition": args.runs,
            "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "git_commit": subprocess.run(
                ["git", "rev-parse", "HEAD"], capture_output=True, text=True
            ).stdout.strip(),
            "total_cost_usd": round(total_cost, 6),
            "directive_chars": len(sample["v2_with_directive"]) - len(sample["v2_no_directive"]) if sample else None,
        },
        "summary": summary,
        "runs": records,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    try:
        out_label = args.out.relative_to(REPO)
    except ValueError:
        out_label = args.out
    print(f"\nwrote {out_label}  (cost ${total_cost:.4f})")
    print("\n" + "=" * 68)
    print(f"{'condition':<20}{'n':>4}{'mean real out tok':>21}{'mean est':>11}")
    print("-" * 68)
    for cond in ("v2_with_directive", "v2_no_directive"):
        s = summary["by_condition"].get(cond, {})
        print(f"{cond:<20}{s.get('n_real', 0):>4}{s.get('mean_output_tokens_real', 0):>21.0f}"
              f"{s.get('mean_output_tokens_est', 0):>11.0f}")
    d = summary["directive_effect"]
    if d:
        print(f"\ndirective effect (with - without): {d['delta_real']:+.0f} real tokens "
              f"({d['pct_of_with_directive']:+.1f}% of the with-directive arm)")
        print(f"Archived Finding 2 gap (Qwen, checklist_v2 - full): +843 tokens, +18.4%")
    return 0


def _checkpoint(args, records, total_cost, model, runs_per_cond, sample) -> None:
    """Write results after every run so an interrupted run loses no work."""
    payload = {
        "metadata": {
            "experiment": "checklist_v2 trailing-directive confound",
            "scope": "Half A (output volume only; no judge invoked)",
            "backend": args.backend, "model": model,
            "runs_per_condition": runs_per_cond,
            "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "git_commit": subprocess.run(
                ["git", "rev-parse", "HEAD"], capture_output=True, text=True
            ).stdout.strip(),
            "total_cost_usd": round(total_cost, 6),
            "directive_chars": (len(sample["v2_with_directive"]) - len(sample["v2_no_directive"]))
                               if sample else None,
            "complete": False,
        },
        "summary": summarise(records),
        "runs": records,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def summarise(records: list[dict]) -> dict:
    by_cond = defaultdict(list)
    for r in records:
        by_cond[r["condition"]].append(r)

    out = {"by_condition": {}}
    for cond, rs in by_cond.items():
        ok = [r for r in rs if r["ok"]]
        real = [r["output_tokens_real"] for r in ok if r["output_tokens_real"] is not None]
        est = [r["output_tokens_est"] for r in ok]
        out["by_condition"][cond] = {
            "n_total": len(rs), "n_ok": len(ok), "n_real": len(real),
            "mean_output_tokens_real": round(st.mean(real), 1) if real else None,
            "mean_output_tokens_est": round(st.mean(est), 1) if est else None,
            "mean_output_chars": round(st.mean([r["output_chars"] for r in ok]), 1) if ok else None,
        }

    w = out["by_condition"].get("v2_with_directive", {})
    n = out["by_condition"].get("v2_no_directive", {})
    out["directive_effect"] = None
    if w.get("mean_output_tokens_real") and n.get("mean_output_tokens_real"):
        delta = w["mean_output_tokens_real"] - n["mean_output_tokens_real"]
        out["directive_effect"] = {
            "delta_real": round(delta, 1),
            "pct_of_with_directive": round(100 * delta / w["mean_output_tokens_real"], 1),
        }
    out["failed_runs"] = sum(1 for r in records if not r["ok"])
    return out


if __name__ == "__main__":
    raise SystemExit(main())