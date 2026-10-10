#!/usr/bin/env python3
"""
direct_choice_experiment.py — let the generator choose the skill itself.

Motivation
----------
§8.7 compares retrieval strategies that all *rank* a catalogue and return one
skill. But the macro benchmark (§8.1-§8.5) already runs under **oracle skill
binding**: the relevant skill is assumed known and injected. Nobody has measured
the case that actually matters operationally — no retrieval at all. Paste every
skill into the prompt and let the model pick.

This measures that directly. Three arms, same generator, same tasks:

  `union_reranked`  union shortlist (lexical+dense top-5), Julia-1 picks one
                    -- the best current pipeline, 5/17 from §8.7
  `full_catalogue`  every routable skill's description in one prompt, model
                    picks one -- no retrieval, single forward pass
  `oracle`          the correct skill injected (the macro benchmark's
                    assumption), for reference -- not run here

The `full_catalogue` arm is the interesting one: it removes the retrieval
bottleneck entirely. The 522-skill catalogue fits in ~11k tokens, well inside
Qwen 3.7 Flash's context, so the experiment is cheap and needs no vector store.

What it does and does not establish
-----------------------------------
It answers "is routing worth it at all?", which §8.7 never asked. If the model
selects as well or better with the whole catalogue in context, then a retrieval
stage is pure overhead; if it selects much worse, retrieval is earning its keep.
Either way the result bears directly on whether the negative §8.7 finding is
about rerankers or about routing itself.

Requires the opencode backend with a capable model (default
openrouter/qwen/qwen3.7-flash, the same generator as the macro benchmark).
Costs API calls; use --dry-run to inspect prompts for free.

Usage:
    uv run python scripts/direct_choice_experiment.py --dry-run
    uv run python scripts/direct_choice_experiment.py --arms full_catalogue
    uv run python scripts/direct_choice_experiment.py --runs 3
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import statistics as st
import sys
import time

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

TASKS_FILE = REPO / "benchmarks" / "tasks_ieee.json"
INDEX_FILE = REPO / "skills_canonical.json"
OUT_FILE = REPO / "benchmarks" / "direct_choice_results.json"

FREEBIES = {"sec-webhook-audit-ieee"}
DESC_WORDS = 15  # catalogue description cap in the menu


def build_menu(index: dict[str, dict]) -> str:
    """Numbered catalogue menu. Names included — see note below.

    Names are shown here deliberately. A real deployment that dumps the
    catalogue into the prompt *does* give the model the skill names, so hiding
    them would measure an artificial condition. §8.7's Stage 1 excluded names
    to avoid leaking the answer when a query happens to mention a skill; here the
    query is the task description and every arm sees the same menu, so the
    comparison is fair.
    """
    lines = []
    for i, (name, meta) in enumerate(index.items(), 1):
        desc = " ".join((meta.get("description") or "").split()[:DESC_WORDS])
        lines.append(f"{i}. {name} — {desc}")
    return "\n".join(lines)


def build_direct_prompt(task_prompt: str, menu: str, n_skills: int) -> str:
    return f"""You are selecting the single most relevant engineering skill for the task below.

Here is the complete catalogue of {n_skills} available skills:

{menu}

=== TASK ===
{task_prompt}

=== INSTRUCTION ===
Choose the ONE skill whose purpose most directly matches this task.
Reply with only the skill name, exactly as written in the catalogue. No
explanation, no punctuation, no numbering."""


def extract_choice(text: str, valid: set[str]) -> tuple[str | None, str]:
    """Pull a skill name out of the model's reply. Returns (name, raw)."""
    raw = (text or "").strip()
    if not raw:
        return None, raw
    # Strip common wrappers.
    cleaned = raw.strip("`\"' \n\t")
    cleaned = re.sub(r"^(skill|name|answer)\s*[:\-]\s*", "", cleaned, flags=re.I)
    if cleaned in valid:
        return cleaned, raw
    # Model may have added a line number or trailing punctuation.
    m = re.match(r"^\d+[\.\)]\s*(.+)$", cleaned)
    if m and m.group(1).strip() in valid:
        return m.group(1).strip(), raw
    # Last resort: exact name appearing anywhere in a short reply.
    if len(cleaned) < 200:
        for name in valid:
            if re.search(rf"\b{re.escape(name)}\b", cleaned):
                return name, raw
    return None, raw


def parse_opencode_json(stream: str) -> tuple[dict | None, str]:
    """Extract final text and real token usage from the NDJSON event stream."""
    usage, chunks = None, []
    for line in (stream or "").splitlines():
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
                    "cost": evt.get("part", {}).get("cost"),
                }
    return usage, "".join(chunks)


def run_opencode(prompt: str, model: str, timeout: int, retries: int = 2) -> dict:
    """Generate via the opencode CLI. stdin must be closed or it blocks."""
    cmd = ["opencode", "run", "--format", "json", "-m", model, prompt]
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

        usage, text = parse_opencode_json(out)
        result = {
            "rc": rc, "output": text, "usage": usage,
            "latency_s": round(elapsed, 2), "attempts": attempt + 1,
            "stderr": err[-300:],
        }
        if rc == 0 and text.strip():
            return result
        if attempt < retries:
            time.sleep(5 * (attempt + 1))
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default="full_catalogue",
                    help="comma-separated: full_catalogue,union_reranked")
    ap.add_argument("--model", default="openrouter/qwen/qwen3.7-flash")
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--out", type=pathlib.Path, default=OUT_FILE)
    args = ap.parse_args()

    from benchmark_router import GOLD_OVERRIDES

    index = json.loads(INDEX_FILE.read_text(encoding="utf-8"))["skills"]
    tasks = json.loads(TASKS_FILE.read_text(encoding="utf-8"))
    tasks = [t for t in tasks if t["id"] not in FREEBIES]
    gold = {t["id"]: GOLD_OVERRIDES.get(t["id"], t["skill"]) for t in tasks}
    valid = set(index)

    menu = build_menu(index)
    est_tokens = len(menu) // 4
    print(f"catalogue: {len(index)} routable skills | menu ~{est_tokens:,} tokens (cap {DESC_WORDS} words/desc)")
    print(f"tasks    : {len(tasks)} (freebie excluded) | model: {args.model}")
    print(f"arms     : {args.arms} | runs/cell: {args.runs}\n")

    if args.dry_run:
        sample = tasks[0]
        prompt = build_direct_prompt(sample["prompt"], menu, len(index))
        print(f"--- sample prompt ({sample['id']}), head ---")
        print(prompt[:600])
        print("  ...")
        print(f"--- tail ---\n{prompt[-420:]}")
        print(f"\nprompt ~{len(prompt) // 4:,} tokens. DRY RUN: no API calls.")
        return 2

    arms = [a.strip() for a in args.arms.split(",") if a.strip()]
    records = []
    total_cost = 0.0

    for arm in arms:
        print(f"\n{'=' * 68}\nARM: {arm}\n{'=' * 68}")
        for task in tasks:
            if arm == "full_catalogue":
                prompt = build_direct_prompt(task["prompt"], menu, len(index))
            elif arm == "union_reranked":
                # Delegate to the existing §8.7 pipeline rather than re-implementing it.
                print(f"  (union_reranked reads the §8.7 archive; run benchmark_router.py)")
                continue
            else:
                print(f"  unknown arm {arm!r}, skipping")
                continue

            picks = []
            for run_idx in range(1, args.runs + 1):
                res = run_opencode(prompt, args.model, args.timeout)
                name, raw = extract_choice(res["output"], valid)
                cost = (res.get("usage") or {}).get("cost") or 0.0
                total_cost += cost
                ok = name is not None
                picks.append(name)
                rec = {
                    "arm": arm, "task_id": task["id"], "gold": gold[task["id"]],
                    "run": run_idx, "parsed": ok, "pick": name, "raw": raw[:200],
                    "match": name == gold[task["id"]],
                    "latency_s": res["latency_s"], "attempts": res["attempts"],
                    "input_tokens": (res.get("usage") or {}).get("input"),
                    "output_tokens": (res.get("usage") or {}).get("output"),
                    "cost_usd": cost,
                }
                records.append(rec)
                flag = "ok " if ok else "UNPARSED"
                mark = "HIT" if rec["match"] else "   "
                print(f"  {flag} r{run_idx} {task['id'][:28]:28} -> "
                      f"{(name or raw[:28])[:28]:28} {mark} ({res['latency_s']:.0f}s)")

        # per-arm summary after its tasks
        arm_recs = [r for r in records if r["arm"] == arm]
        if arm_recs:
            parsed = [r for r in arm_recs if r["parsed"]]
            hits = sum(1 for r in arm_recs if r["match"])
            any_hit = len({r["task_id"] for r in arm_recs if r["match"]})
            print(f"\n  {arm}: top-1 {hits}/{len(arm_recs)} runs "
                  f"({100*hits/len(arm_recs):.1f}%) | tasks solved at least once "
                  f"{any_hit}/{len(tasks)} | unparsed {len(arm_recs)-len(parsed)}")

    payload = {
        "metadata": {
            "experiment": "direct choice: no retrieval, model picks from full catalogue",
            "arms": arms, "model": args.model, "runs_per_cell": args.runs,
            "catalogue": len(index), "desc_word_cap": DESC_WORDS,
            "menu_estimated_tokens": est_tokens,
            "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "total_cost_usd": round(total_cost, 4),
            "freebie_excluded": sorted(FREEBIES),
        },
        "runs": records,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"\nwrote {args.out.name}  (cost ${total_cost:.4f})")
    return 0


if __name__ == "__main__":
    import subprocess  # noqa: E402  (used by run_opencode)
    raise SystemExit(main())