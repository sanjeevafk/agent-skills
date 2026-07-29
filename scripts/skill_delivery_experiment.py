#!/usr/bin/env python3
"""
Skill Delivery Experiment
=========================
Benchmarks 4 skill injection strategies:
  1. control      - No skill injection
  2. full         - Entire SKILL.md prepended
  3. retrieved    - Only most relevant sections (keyword-matched, ~15% of skill)
  4. checklist    - Actionable bullet points only (no explanations)

Usage:
  python3 scripts/skill_delivery_experiment.py --tasks benchmarks/tasks_hard.json --runs 2
"""
import argparse
import json
import math
import re
import subprocess
import time
import random
import string
from collections import defaultdict
from pathlib import Path
from datetime import datetime, timezone
from itertools import combinations

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent

# Skill paths (ordered: project-local first, then global)
SKILL_SEARCH_PATHS = [
    Path.home() / ".agents" / "skills",
    Path.home() / ".gemini" / "skills",
]

# ─────────────────────────────────────────────────────────
# Token estimation (≈4 chars per token, GPT-standard approx)
# ─────────────────────────────────────────────────────────
def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


# ─────────────────────────────────────────────────────────
# Skill Loading
# ─────────────────────────────────────────────────────────
def load_skill_md(skill_name: str) -> str:
    for base in SKILL_SEARCH_PATHS:
        p = base / skill_name / "SKILL.md"
        if p.exists():
            return p.read_text(encoding="utf-8")
    return ""


# ─────────────────────────────────────────────────────────
# Section Parsing  
# ─────────────────────────────────────────────────────────
def parse_sections(skill_md: str) -> list[dict]:
    """Split a SKILL.md into heading-based sections."""
    sections = []
    current_heading = "__preamble__"
    current_lines = []

    for line in skill_md.splitlines():
        heading_match = re.match(r"^(#{1,4})\s+(.*)", line)
        if heading_match:
            if current_lines:
                sections.append({
                    "heading": current_heading,
                    "level": len(re.match(r"^#+", current_heading).group()) if current_heading != "__preamble__" else 0,
                    "body": "\n".join(current_lines),
                })
            current_heading = line.strip()
            current_lines = []
        else:
            current_lines.append(line)

    if current_lines:
        sections.append({
            "heading": current_heading,
            "level": 0,
            "body": "\n".join(current_lines),
        })
    return sections


# ─────────────────────────────────────────────────────────
# TF-IDF Keyword Scorer (no external dependencies)
# ─────────────────────────────────────────────────────────
def tokenize(text: str) -> list[str]:
    return re.findall(r"\b[a-z]{3,}\b", text.lower())


def tfidf_score(query_tokens: set[str], section_body: str, all_sections: list[dict]) -> float:
    body_tokens = tokenize(section_body)
    if not body_tokens:
        return 0.0

    body_set = set(body_tokens)
    doc_count = len(all_sections)

    score = 0.0
    for token in query_tokens:
        tf = body_tokens.count(token) / len(body_tokens)
        df = sum(1 for s in all_sections if token in tokenize(s["body"]))
        idf = math.log((doc_count + 1) / (df + 1)) + 1
        score += tf * idf

    return score


# ─────────────────────────────────────────────────────────
# Injection Strategies
# ─────────────────────────────────────────────────────────
def strategy_control(skill_md: str, prompt: str) -> str:
    return prompt


def strategy_full(skill_md: str, prompt: str) -> str:
    return f"[SKILL GUIDELINES]\n{skill_md}\n\n[TASK]\n{prompt}"


def strategy_retrieved(skill_md: str, prompt: str, target_fraction: float = 0.15) -> str:
    sections = parse_sections(skill_md)
    query_tokens = set(tokenize(prompt))

    scored = [
        (tfidf_score(query_tokens, s["body"], sections), s)
        for s in sections
    ]
    scored.sort(key=lambda x: x[0], reverse=True)

    target_chars = int(len(skill_md) * target_fraction)
    selected = []
    total_chars = 0
    for score, section in scored:
        body = f"{section['heading']}\n{section['body']}"
        if total_chars + len(body) > target_chars and selected:
            break
        selected.append(body)
        total_chars += len(body)

    retrieved_context = "\n\n".join(selected)
    return f"[RELEVANT SKILL CONTEXT (retrieved)]\n{retrieved_context}\n\n[TASK]\n{prompt}"


def strategy_checklist(skill_md: str, prompt: str) -> str:
    """Extract only actionable bullet points from the SKILL.md."""
    lines = skill_md.splitlines()
    bullets = []
    heading = ""
    for line in lines:
        if re.match(r"^#{1,4}\s+", line):
            heading = line.strip()
        elif re.match(r"^\s*[-*•]\s+\*\*", line) or re.match(r"^\s*[-*•]\s+[A-Z`]", line):
            # Bold bullets or capitalised/code bullets (actionable rules)
            clean = re.sub(r"^\s*[-*•]\s+", "", line).strip()
            bullets.append(f"- {clean}")
        elif re.match(r"^\s*\d+\.\s+", line):
            clean = re.sub(r"^\s*\d+\.\s+", "", line).strip()
            bullets.append(f"- {clean}")

    checklist = "\n".join(bullets)
    return f"[SKILL CHECKLIST]\n{checklist}\n\n[TASK]\n{prompt}"


STRATEGIES = {
    "control":   strategy_control,
    "full":      strategy_full,
    "retrieved": strategy_retrieved,
    "checklist": strategy_checklist,
}

STRATEGY_NAMES = list(STRATEGIES.keys())


# ─────────────────────────────────────────────────────────
# Runner
# ─────────────────────────────────────────────────────────
def run_cmd(prompt: str, model: str = None) -> tuple[int, str, str, float]:
    cmd = ["agy", "--dangerously-skip-permissions"]
    if model:
        cmd.extend(["--model", model])
    cmd.extend(["-p", prompt])
    start = time.perf_counter()
    proc = subprocess.run(cmd, capture_output=True, text=True)
    elapsed = time.perf_counter() - start
    return proc.returncode, proc.stdout, proc.stderr, elapsed


def run_4way_judge(prompt: str, outputs: dict[str, str], label_map: dict[str, str], model: str = None) -> dict | None:
    """
    Blind 4-way judge. label_map: {strategy_name -> blind_label (A/B/C/D)}
    """
    blocks = []
    for strat, label in label_map.items():
        blocks.append(f"[Response {label}]:\n{outputs[strat][:1500]}...")  # truncate for judge context

    all_criteria = ["correctness", "completeness", "maintainability", "architecture",
                    "security", "reasoning_quality", "instruction_adherence"]

    judging_prompt = f"""You are an expert AI evaluator. You will score four agent responses to the same task.

[Original Task Prompt]:
{prompt}

---
{''.join(f"{b}---" + chr(10) for b in blocks)}

Score each response (A, B, C, D) on these 7 criteria (1-5 each):
{', '.join(all_criteria)}

Also determine the overall ranking from best to worst and write a pairwise comparison explaining why responses differ.

Respond with a single ```json ... ``` block following this exact structure:
{{
  "scores": {{
    "A": {{"correctness":N,"completeness":N,"maintainability":N,"architecture":N,"security":N,"reasoning_quality":N,"instruction_adherence":N,"justification":"..."}},
    "B": {{"correctness":N,"completeness":N,"maintainability":N,"architecture":N,"security":N,"reasoning_quality":N,"instruction_adherence":N,"justification":"..."}},
    "C": {{"correctness":N,"completeness":N,"maintainability":N,"architecture":N,"security":N,"reasoning_quality":N,"instruction_adherence":N,"justification":"..."}},
    "D": {{"correctness":N,"completeness":N,"maintainability":N,"architecture":N,"security":N,"reasoning_quality":N,"instruction_adherence":N,"justification":"..."}}
  }},
  "ranking": ["A","B","C","D"],
  "pairwise_analysis": "2-3 sentence comparison explaining key quality differences"
}}"""

    rc, stdout, stderr, _ = run_cmd(judging_prompt, model)
    if rc == 0:
        m = re.search(r"```json\s*(.*?)\s*```", stdout, re.DOTALL | re.IGNORECASE)
        raw = m.group(1) if m else stdout.strip()
        try:
            return json.loads(raw)
        except Exception as e:
            print(f"  ⚠️ Judge parse error: {e}")
    else:
        print(f"  ⚠️ Judge failed (exit {rc}): {stderr[:200]}")
    return None


# ─────────────────────────────────────────────────────────
# Statistics helpers
# ─────────────────────────────────────────────────────────
def compute_stats(vals: list[float]) -> dict:
    if not vals:
        return {"mean": 0, "median": 0, "std": 0, "ci_low": 0, "ci_high": 0, "n": 0}
    arr = np.array(vals, dtype=float)
    m = float(np.mean(arr))
    med = float(np.median(arr))
    s = float(np.std(arr, ddof=1)) if len(arr) > 1 else 0.0
    ci_lo, ci_hi = m, m
    if len(arr) > 1:
        try:
            sem = stats.sem(arr)
            lo, hi = stats.t.interval(0.95, len(arr) - 1, loc=m, scale=sem)
            ci_lo = float(lo) if not (math.isnan(lo) or math.isinf(lo)) else m
            ci_hi = float(hi) if not (math.isnan(hi) or math.isinf(hi)) else m
        except Exception:
            pass
    return {"mean": round(m, 2), "median": round(med, 2), "std": round(s, 2),
            "ci_low": round(ci_lo, 2), "ci_high": round(ci_hi, 2), "n": len(arr)}


def pairwise_ttest(a: list[float], b: list[float]) -> tuple[float, float]:
    if len(a) < 2 or len(b) < 2:
        return 0.0, 1.0
    try:
        t, p = stats.ttest_ind(a, b, equal_var=False)
        return round(float(t), 3), round(float(p), 4)
    except Exception:
        return 0.0, 1.0


# ─────────────────────────────────────────────────────────
# Prompt bloat analysis
# ─────────────────────────────────────────────────────────
def measure_prompt_bloat(skill_md: str, prompt: str) -> dict:
    base_tokens = estimate_tokens(prompt)
    result = {}
    for name, fn in STRATEGIES.items():
        injected = fn(skill_md, prompt)
        tok = estimate_tokens(injected)
        result[name] = {
            "total_tokens": tok,
            "overhead_tokens": tok - base_tokens,
            "overhead_pct": round((tok - base_tokens) / base_tokens * 100, 1),
            "chars": len(injected),
        }
    # Include raw skill size for reference
    result["__skill_full_tokens"] = estimate_tokens(skill_md)
    result["__base_prompt_tokens"] = base_tokens
    return result


# ─────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Skill Delivery Strategy Experiment")
    parser.add_argument("--tasks", type=Path, default=ROOT / "benchmarks" / "tasks_hard.json")
    parser.add_argument("--runs", type=int, default=2, help="Runs per task per strategy")
    parser.add_argument("--models", type=str, default=None)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "benchmarks" / "delivery_results")
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    with open(args.tasks) as f:
        tasks = json.load(f)

    models = [m.strip() for m in args.models.split(",")] if args.models else [None]
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    all_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "runs_per_task": args.runs,
        "strategies": STRATEGY_NAMES,
        "tasks": [],
    }

    print(f"🧪 Skill Delivery Experiment | {len(tasks)} tasks × {args.runs} runs × {len(STRATEGY_NAMES)} strategies")
    print(f"   Strategies: {STRATEGY_NAMES}\n")

    for model in models:
        model_name = model or "Default Model"

        for task in tasks:
            task_id   = task["id"]
            prompt    = task["prompt"]
            must_incl = task["must_include"]
            skill     = task["skill"]

            skill_md = load_skill_md(skill)
            if not skill_md:
                print(f"⚠️  Skill '{skill}' not found — control only for task {task_id}")

            # Bloat analysis
            bloat = measure_prompt_bloat(skill_md or "", prompt)

            print(f"\n{'='*60}")
            print(f"📝 Task: {task_id} | Skill: {skill}")
            print(f"   Prompt tokens (base): {bloat['__base_prompt_tokens']}")
            for s in STRATEGY_NAMES:
                print(f"   [{s:12s}] total={bloat[s]['total_tokens']} tokens (+{bloat[s]['overhead_tokens']}, +{bloat[s]['overhead_pct']}%)")

            task_record = {
                "id": task_id,
                "skill": skill,
                "model": model_name,
                "bloat": bloat,
                "strategy_runs": {s: [] for s in STRATEGY_NAMES},
                "judging": [],
            }

            for run_idx in range(1, args.runs + 1):
                print(f"\n  ── Run {run_idx}/{args.runs} ──")

                # Randomly assign blind labels for this run
                shuffled = STRATEGY_NAMES.copy()
                random.shuffle(shuffled)
                label_map = {s: lbl for s, lbl in zip(shuffled, ["A", "B", "C", "D"])}
                rev_label = {v: k for k, v in label_map.items()}  # label -> strategy

                outputs = {}
                run_metrics = {}

                # Execute all 4 strategies
                for strat in STRATEGY_NAMES:
                    inject_fn = STRATEGIES[strat]
                    injected  = inject_fn(skill_md or "", prompt)
                    input_tok = estimate_tokens(injected)

                    print(f"  🔁 [{strat:12s}] executing...", end=" ", flush=True)
                    rc, out, err, latency = run_cmd(injected, model)

                    if rc != 0:
                        print(f"❌ FAILED (exit {rc})")
                        outputs[strat] = ""
                        run_metrics[strat] = {"ok": False, "error": err[:200]}
                        continue

                    output_tok  = estimate_tokens(out)
                    missing_kws = [p for p in must_incl if not re.search(p, out, re.IGNORECASE)]

                    print(f"✅ {latency:.1f}s | in≈{input_tok}tok out≈{output_tok}tok")
                    outputs[strat] = out
                    run_metrics[strat] = {
                        "ok": True,
                        "latency": round(latency, 2),
                        "input_tokens": input_tok,
                        "output_tokens": output_tok,
                        "missing_keywords": missing_kws,
                        "output_preview": out[:300] + "..." if len(out) > 300 else out,
                    }

                # 4-way blind judge
                valid_strats = [s for s in STRATEGY_NAMES if run_metrics.get(s, {}).get("ok")]
                if len(valid_strats) < 2:
                    print("  ⚠️  Too few valid outputs for judging — skipping")
                    continue

                # Build valid label_map for this run
                valid_label_map = {s: label_map[s] for s in valid_strats}

                print(f"  ⚖️  Blind {len(valid_strats)}-way judge (labels: {valid_label_map}) ...", end=" ", flush=True)
                judge_res = run_4way_judge(prompt, outputs, valid_label_map, model)

                if not judge_res:
                    print("❌ judge failed")
                    continue

                print("✅")

                # Unblind scores
                unblinded_scores = {}
                for label, strat in rev_label.items():
                    if strat in valid_strats and label in judge_res.get("scores", {}):
                        unblinded_scores[strat] = judge_res["scores"][label]
                        total = sum(v for k, v in judge_res["scores"][label].items() if k != "justification")
                        run_metrics[strat]["judge_total"] = total
                        run_metrics[strat]["judge_scores"] = judge_res["scores"][label]

                # Unblind ranking
                ranking_strats = [rev_label.get(lbl) for lbl in judge_res.get("ranking", [])]
                ranking_strats = [s for s in ranking_strats if s is not None]

                judge_record = {
                    "run": run_idx,
                    "label_map": label_map,
                    "ranking": ranking_strats,
                    "pairwise_analysis": judge_res.get("pairwise_analysis", ""),
                    "scores_by_strategy": unblinded_scores,
                }
                task_record["judging"].append(judge_record)

                for strat in valid_strats:
                    task_record["strategy_runs"][strat].append(run_metrics[strat])

                # Print run results
                score_line = " | ".join(
                    f"{s}={run_metrics[s].get('judge_total','?')}/35"
                    for s in STRATEGY_NAMES if run_metrics.get(s, {}).get("ok")
                )
                print(f"  🏆 Ranking: {' > '.join(ranking_strats)}")
                print(f"     Scores: {score_line}")

            all_data["tasks"].append(task_record)

    # ─────────────────────────────────────────────────────
    # Aggregate statistics & pairwise comparisons
    # ─────────────────────────────────────────────────────
    strategy_scores  = defaultdict(list)
    strategy_lats    = defaultdict(list)
    strategy_in_toks = defaultdict(list)
    strategy_out_toks= defaultdict(list)
    strategy_wins    = defaultdict(int)
    rank_points      = defaultdict(list)  # 1st place = 4pts ... 4th = 1pt

    for task_record in all_data["tasks"]:
        for strat, runs in task_record["strategy_runs"].items():
            for r in runs:
                if r.get("ok"):
                    if "judge_total" in r:
                        strategy_scores[strat].append(r["judge_total"])
                    strategy_lats[strat].append(r["latency"])
                    strategy_in_toks[strat].append(r["input_tokens"])
                    strategy_out_toks[strat].append(r["output_tokens"])

        for jd in task_record["judging"]:
            ranking = jd["ranking"]
            for rank, strat in enumerate(ranking):
                pts = len(STRATEGY_NAMES) - rank
                rank_points[strat].append(pts)
            if ranking:
                strategy_wins[ranking[0]] += 1

    summary = {}
    for strat in STRATEGY_NAMES:
        summary[strat] = {
            "score_stats":    compute_stats(strategy_scores[strat]),
            "latency_stats":  compute_stats(strategy_lats[strat]),
            "in_tok_stats":   compute_stats(strategy_in_toks[strat]),
            "out_tok_stats":  compute_stats(strategy_out_toks[strat]),
            "rank_pts_stats": compute_stats(rank_points[strat]),
            "wins":           strategy_wins[strat],
        }

    # Pairwise t-tests
    pairwise = {}
    for s1, s2 in combinations(STRATEGY_NAMES, 2):
        t, p = pairwise_ttest(strategy_scores[s1], strategy_scores[s2])
        pairwise[f"{s1}_vs_{s2}"] = {"t": t, "p": p, "sig": p < 0.05}

    all_data["summary"] = summary
    all_data["pairwise_ttests"] = pairwise

    # ─────────────────────────────────────────────────────
    # Recommendation engine
    # ─────────────────────────────────────────────────────
    best_score_strat = max(summary, key=lambda s: summary[s]["score_stats"]["mean"])
    fastest_strat    = min(summary, key=lambda s: summary[s]["latency_stats"]["mean"] or 9999)
    most_wins_strat  = max(summary, key=lambda s: summary[s]["wins"])
    lowest_bloat     = min(STRATEGY_NAMES, key=lambda s: summary[s]["in_tok_stats"]["mean"] or 9999)

    # Per-skill category — which strategy ranked highest
    skill_category_best = defaultdict(lambda: defaultdict(list))
    for task_record in all_data["tasks"]:
        skill = task_record["skill"]
        for jd in task_record["judging"]:
            ranking = jd["ranking"]
            for rank, strat in enumerate(ranking):
                skill_category_best[skill][strat].append(len(STRATEGY_NAMES) - rank)

    category_winners = {}
    for skill, strat_pts in skill_category_best.items():
        category_winners[skill] = max(strat_pts, key=lambda s: np.mean(strat_pts[s]) if strat_pts[s] else 0)

    recommendation = {
        "best_score":     best_score_strat,
        "most_wins":      most_wins_strat,
        "fastest":        fastest_strat,
        "lowest_bloat":   lowest_bloat,
        "category_winners": category_winners,
    }
    all_data["recommendation"] = recommendation

    # ─────────────────────────────────────────────────────
    # Save JSON
    # ─────────────────────────────────────────────────────
    json_out = args.output_dir / f"delivery_run_{ts}.json"
    json_out.write_text(json.dumps(all_data, indent=2))

    # ─────────────────────────────────────────────────────
    # Generate Markdown Report
    # ─────────────────────────────────────────────────────
    lines = [
        "# Skill Delivery Strategy Experiment\n",
        f"> **Generated at**: `{all_data['timestamp']}`  ",
        f"> **Tasks**: {len(tasks)} | **Runs per strategy**: {args.runs} | **Strategies**: {len(STRATEGY_NAMES)}",
        "\n---\n",
        "## 📊 Executive Dashboard\n",
        "| Strategy | Avg Score /35 | 95% CI | Wins | Avg Latency | Avg Input Tokens | Avg Output Tokens |",
        "|---|---|---|---|---|---|---|",
    ]

    for strat in STRATEGY_NAMES:
        s = summary[strat]
        sc = s["score_stats"]
        lc = s["latency_stats"]
        it = s["in_tok_stats"]
        ot = s["out_tok_stats"]
        win_marker = " 🏆" if strat == most_wins_strat else ""
        lines.append(
            f"| `{strat}` | **{sc['mean']}** | `[{sc['ci_low']}, {sc['ci_high']}]` | "
            f"{s['wins']}{win_marker} | {lc['mean']}s | {it['mean']} | {ot['mean']} |"
        )

    lines += [
        "\n---\n",
        "## 🔬 Prompt Bloat Analysis\n",
    ]

    # Bloat table per task
    for task_record in all_data["tasks"]:
        bloat = task_record["bloat"]
        lines.append(f"### Task `{task_record['id']}` (Skill: `{task_record['skill']}`)\n")
        lines.append("| Strategy | Total Tokens | Overhead Tokens | Overhead % |")
        lines.append("|---|---|---|---|")
        base = bloat["__base_prompt_tokens"]
        full = bloat["full"]["total_tokens"]
        lines.append(f"| `control`   | {base} | 0 | 0% |")
        for s in ["full", "retrieved", "checklist"]:
            bd = bloat[s]
            lines.append(f"| `{s}` | {bd['total_tokens']} | +{bd['overhead_tokens']} | +{bd['overhead_pct']}% |")
        lines.append(f"\n> Skill full tokens: **{bloat['__skill_full_tokens']}** | Retrieved target: ~15% = **{int(bloat['__skill_full_tokens'] * 0.15)}** tokens\n")

    lines += [
        "\n---\n",
        "## 📐 Pairwise Comparisons (Welch t-test)\n",
        "| Pair | t-statistic | p-value | Significant? |",
        "|---|---|---|---|",
    ]

    for pair, vals in pairwise.items():
        sig = "⭐ Yes (p < 0.05)" if vals["sig"] else "No"
        lines.append(f"| `{pair}` | {vals['t']} | {vals['p']} | {sig} |")

    lines += [
        "\n---\n",
        "## 🏅 Per-Skill-Category Winners\n",
        "| Skill Category | Best Strategy |",
        "|---|---|",
    ]

    for skill, winner in category_winners.items():
        lines.append(f"| `{skill}` | **`{winner}`** |")

    lines += [
        "\n---\n",
        "## 💡 Final Recommendation\n",
        f"- **Highest average judge score**: `{best_score_strat}`",
        f"- **Most first-place wins**: `{most_wins_strat}`",
        f"- **Lowest latency**: `{fastest_strat}`",
        f"- **Lowest prompt bloat**: `{lowest_bloat}`",
        "",
        "### Optimal Delivery Method by Skill Category\n",
    ]

    for skill, winner in category_winners.items():
        lines.append(f"- **{skill}** → `{winner}`")

    lines += [
        "",
        "> [!IMPORTANT]",
        "> This experiment measures **how** skills are delivered — not whether they work.",
        "> The optimal strategy may vary by skill category, task complexity, and model.",
        "",
    ]

    lines += [
        "\n---\n",
        "## 🧬 Per-Task Judge Explanations\n",
    ]

    for task_record in all_data["tasks"]:
        lines.append(f"### Task `{task_record['id']}`\n")
        for jd in task_record["judging"]:
            lines.append(f"**Run {jd['run']}:**")
            lines.append(f"- Ranking: `{' > '.join(jd['ranking'])}`")
            lines.append(f"- Analysis: {jd['pairwise_analysis']}")

            if jd.get("scores_by_strategy"):
                lines.append("")
                lines.append("  | Strategy | Score /35 | Justification |")
                lines.append("  |---|---|---|")
                for strat, sc_data in jd["scores_by_strategy"].items():
                    total = sum(v for k, v in sc_data.items() if k != "justification")
                    just = sc_data.get("justification", "")[:200]
                    lines.append(f"  | `{strat}` | {total} | {just} |")
            lines.append("")

    md_out = args.output_dir / f"delivery_report_{ts}.md"
    md_out.write_text("\n".join(lines), encoding="utf-8")
    # Copy as latest
    (args.output_dir.parent / "delivery_report_latest.md").write_text("\n".join(lines), encoding="utf-8")
    (args.output_dir.parent / "delivery_results_latest.json").write_text(json.dumps(all_data, indent=2))

    # ─────────────────────────────────────────────────────
    # Terminal summary
    # ─────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("🏆 Skill Delivery Experiment Complete!")
    print(f"   Best Score Strategy : {best_score_strat}")
    print(f"   Most Wins           : {most_wins_strat}")
    print(f"   Fastest             : {fastest_strat}")
    print(f"   Lowest Bloat        : {lowest_bloat}")
    print(f"\n   Scores (avg/35):")
    for strat in STRATEGY_NAMES:
        print(f"     {strat:12s}: {summary[strat]['score_stats']['mean']}")
    print(f"\n   JSON:   {json_out}")
    print(f"   Report: {md_out}")
    print("=" * 60)


if __name__ == "__main__":
    main()
