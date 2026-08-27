#!/usr/bin/env python3
"""
Skill Delivery Experiment — IEEE Hardened Edition
==================================================
Benchmarks 4 skill injection strategies:
  1. control      - No skill injection
  2. full         - Entire SKILL.md prepended
  3. retrieved    - Only most relevant sections (TF-IDF matched, ~15% of skill)
  4. checklist    - Pre-compiled actionable checklist (benchmarks/checklists_ieee/)

Reliability features:
  - Full raw outputs archived per execution (benchmarks/raw_outputs_ieee/)
  - Provenance block (versions, SHA256 of all inputs, git state)
  - Per-task atomic checkpointing + --resume
  - Cross-vendor blind judge via OpenAI-compatible API (OrcaRouter)
  - Full statistics: Welch t, Mann-Whitney U, Cohen's d, Holm-Bonferroni,
    Shapiro-Wilk, Pearson/Spearman (RQ3), Kruskal-Wallis per domain (RQ4)
  - IEEE LaTeX table + CSV exports

Usage:
  python3 scripts/skill_delivery_experiment.py --tasks benchmarks/tasks_ieee.json --runs 5
  python3 scripts/skill_delivery_experiment.py --resume
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
import random
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path

import numpy as np
import scipy
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent

SKILL_SEARCH_PATHS = [
    ROOT / "skills",                      # repo-local skills (benchmark source of truth)
    Path.home() / ".agents" / "skills",   # global installs
    Path.home() / ".gemini" / "skills",
]

CHECKLIST_DIR = ROOT / "benchmarks" / "checklists_ieee"
CHECKLIST_V2_DIR = ROOT / "benchmarks" / "checklists_v2"
RAW_OUTPUT_DIR = ROOT / "benchmarks" / "raw_outputs_ieee"
RESULTS_PATH = ROOT / "benchmarks" / "delivery_results_ieee.json"
REPORT_PATH = ROOT / "benchmarks" / "delivery_report_ieee.md"

JUDGE_CRITERIA = ["correctness", "completeness", "maintainability", "architecture",
                  "security", "reasoning_quality", "instruction_adherence"]


# ─────────────────────────────────────────────────────────
# Token estimation (≈4 chars per token, GPT-standard approx)
# ─────────────────────────────────────────────────────────
def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def atomic_write_text(path: Path, text: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


def atomic_write_json(path: Path, data) -> None:
    atomic_write_text(path, json.dumps(data, indent=2))


# ─────────────────────────────────────────────────────────
# Skill Loading
# ─────────────────────────────────────────────────────────
def load_skill_md(skill_name: str) -> str:
    for base in SKILL_SEARCH_PATHS:
        p = base / skill_name / "SKILL.md"
        if p.exists():
            return p.read_text(encoding="utf-8")
    return ""


def load_checklist(skill_name: str, skill_md: str) -> tuple[str, str]:
    """Load pre-compiled checklist artifact; fall back to runtime extraction."""
    artifact = CHECKLIST_DIR / f"{skill_name}.txt"
    if artifact.exists():
        return artifact.read_text(encoding="utf-8"), "artifact"
    return strategy_checklist_runtime(skill_md, prompt=""), "runtime-fallback"


def load_checklist_v2(skill_name: str, skill_md: str) -> tuple[str, str]:
    """Load pre-compiled v2 balanced checklist artifact; fall back to runtime extraction."""
    artifact = CHECKLIST_V2_DIR / f"{skill_name}.txt"
    if artifact.exists():
        return artifact.read_text(encoding="utf-8"), "artifact_v2"
    return strategy_checklist_runtime(skill_md, prompt=""), "runtime-fallback"


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
def strategy_control(skill_md: str, prompt: str, skill_name: str = "") -> str:
    return prompt


def strategy_full(skill_md: str, prompt: str, skill_name: str = "") -> str:
    return f"[SKILL GUIDELINES]\n{skill_md}\n\n[TASK]\n{prompt}"


def strategy_retrieved(skill_md: str, prompt: str, skill_name: str = "", target_fraction: float = 0.15) -> str:
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


def strategy_checklist_runtime(skill_md: str, prompt: str = "", skill_name: str = "") -> str:
    """Runtime fallback: extract only actionable bullet points from the SKILL.md."""
    lines = skill_md.splitlines()
    bullets = []
    for line in lines:
        if re.match(r"^\s*[-*•]\s+\*\*", line) or re.match(r"^\s*[-*•]\s+[A-Z`]", line):
            clean = re.sub(r"^\s*[-*•]\s+", "", line).strip()
            bullets.append(f"- {clean}")
        elif re.match(r"^\s*\d+\.\s+", line):
            clean = re.sub(r"^\s*\d+\.\s+", "", line).strip()
            bullets.append(f"- {clean}")
    checklist = "\n".join(bullets)
    return f"[SKILL CHECKLIST]\n{checklist}\n\n[TASK]\n{prompt}"


def strategy_checklist(skill_md: str, prompt: str, skill_name: str = "") -> str:
    """Prefer the pre-compiled offline artifact (static build-time compilation v1: 70% cut)."""
    if skill_name:
        compiled, _ = load_checklist(skill_name, skill_md)
        if compiled.strip():
            return f"[SKILL CHECKLIST V1]\n{compiled}\n\n[TASK]\n{prompt}"
    return strategy_checklist_runtime(skill_md, prompt, skill_name)


def strategy_checklist_v2(skill_md: str, prompt: str, skill_name: str = "") -> str:
    """Prefer the pre-compiled offline v2 artifact (balanced compilation: ~40-50% cut with code/tables)."""
    if skill_name:
        compiled, _ = load_checklist_v2(skill_name, skill_md)
        if compiled.strip():
            return f"[ENGINEERING IMPLEMENTATION STANDARDS & ARCHITECTURAL CONSTRAINTS]\n{compiled}\n\n[TASK]\n{prompt}\n\n[INSTRUCTION]: Apply the above engineering standards and architectural constraints rigorously. Output your complete, production-grade code implementation and review directly in your markdown response."
    return strategy_checklist_runtime(skill_md, prompt, skill_name)


STRATEGIES = {
    "control":      strategy_control,
    "full":         strategy_full,
    "retrieved":    strategy_retrieved,
    "checklist":    strategy_checklist,
    "checklist_v2": strategy_checklist_v2,
}

STRATEGY_NAMES = list(STRATEGIES.keys())


# ─────────────────────────────────────────────────────────
# Executor Runner
# ─────────────────────────────────────────────────────────
QUOTA_RE = re.compile(r"Resets in\s*(?:(\d+)m)?\s*(\d+)s")

def run_cmd(prompt: str, model: str = None, backend: str = "cmd", timeout: int = 300,
            quota_retries: int = 4) -> tuple[int, str, str, float]:
    """Execute via cmd CLI (e.g. Qwen) or agy CLI (Gemini)."""
    if backend == "cmd":
        actual_model = model or "qwen/qwen3.7-flash"
        cmd_prompt = prompt + "\n\n[OUTPUT INSTRUCTION]: Provide your complete analysis and full code implementation directly in your markdown response. Do NOT create, write, or modify any files on disk."
        cmd = ["cmd", "-p", cmd_prompt, "--no-session", "--yolo", "-m", actual_model]
        start = time.perf_counter()
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            rc, out, err = proc.returncode, proc.stdout, proc.stderr
        except subprocess.TimeoutExpired:
            rc, out, err = 124, "", f"TIMEOUT after {timeout}s"
        except Exception as e:
            rc, out, err = 1, "", f"Exception: {e}"
        elapsed = time.perf_counter() - start
        return rc, out, err, elapsed

    cmd = ["agy", "--dangerously-skip-permissions"]
    if model:
        cmd.extend(["--model", model])
    cmd.extend(["-p", prompt])

    for attempt in range(quota_retries + 1):
        start = time.perf_counter()
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            rc, out, err = proc.returncode, proc.stdout, proc.stderr
        except subprocess.TimeoutExpired:
            rc, out, err = 124, "", f"TIMEOUT after {timeout}s"
        elapsed = time.perf_counter() - start

        if rc != 0 and "quota reached" in (err or "").lower() and attempt < quota_retries:
            m = QUOTA_RE.search(err or "")
            if m:
                minutes = int(m.group(1) or 0)
                seconds = int(m.group(2))
                wait = min(minutes * 60 + seconds + 45, 1800)
            else:
                wait = 900
            print(f"\n      ⏳ agy quota exhausted — sleeping {wait}s then retrying "
                  f"(attempt {attempt + 1}/{quota_retries})", flush=True)
            time.sleep(wait)
            continue
        return rc, out, err, elapsed
    return rc, out, err, elapsed


# ─────────────────────────────────────────────────────────
# Judge Backends
# ─────────────────────────────────────────────────────────
def build_judging_prompt(prompt: str, outputs: dict[str, str], label_map: dict[str, str], max_chars: int) -> str:
    labels = sorted(label_map.values())
    blocks = []
    for strat, label in sorted(label_map.items(), key=lambda x: x[1]):
        body = outputs[strat]
        if len(body) > max_chars:
            body = body[:max_chars] + "\n...[truncated]"
        blocks.append(f"[Response {label}]:\n{body}\n")

    score_template = ",\n    ".join(
        f'"{lbl}": {{"correctness":N,"completeness":N,"maintainability":N,"architecture":N,"security":N,"reasoning_quality":N,"instruction_adherence":N,"justification":"..."}}'
        for lbl in labels
    )
    ranking_template = json.dumps(labels)
    labels_str = ", ".join(labels)

    return f"""You are an expert AI evaluator. You will score {len(labels)} agent responses to the same task.

[Original Task Prompt]:
{prompt}

---
{'---'.join(blocks)}
---

Score each response ({labels_str}) on these 7 criteria (1-5 each):
{', '.join(JUDGE_CRITERIA)}

Also determine the overall ranking from best to worst and write a pairwise comparison explaining why responses differ.

Respond with a single ```json ... ``` block following this exact structure:
{{
  "scores": {{
    {score_template}
  }},
  "ranking": {ranking_template},
  "pairwise_analysis": "2-3 sentence comparison explaining key quality differences"
}}"""


def parse_judge_json(text: str) -> dict | None:
    m = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
    raw = m.group(1) if m else text.strip()
    try:
        return json.loads(raw)
    except Exception:
        return None


def _judge_via_agy_once(judging_prompt: str, model: str = None, timeout: int = 900) -> tuple[dict | None, dict, str]:
    rc, stdout, stderr, elapsed = run_cmd(judging_prompt, model, timeout)
    usage = {"latency_s": round(elapsed, 2), "prompt_tokens": None, "completion_tokens": None}
    if rc != 0:
        return None, usage, f"agy exit {rc}: {stderr[:200]}"
    result = parse_judge_json(stdout)
    if result is None:
        return None, usage, "judge JSON parse failure"
    return result, usage, "ok"


def judge_via_agy(judging_prompt: str, model: str = None, timeout: int = 900,
                  retries: int = 4) -> tuple[dict | None, dict, str]:
    """Judge via agy CLI with exponential backoff (rides out transient rate limits)."""
    backoff = [30, 60, 120, 240]
    usage = {"latency_s": None, "prompt_tokens": None, "completion_tokens": None}
    last_err = "unknown"
    for attempt in range(retries + 1):
        result, usage, status = _judge_via_agy_once(judging_prompt, model, timeout)
        if result is not None:
            return result, usage, status
        last_err = status
        if attempt < retries:
            wait = backoff[min(attempt, len(backoff) - 1)]
            print(f"(judge retry {attempt + 1}/{retries} in {wait}s: {status[:80]})", end=" ", flush=True)
            time.sleep(wait)
    return None, usage, last_err


def judge_via_openai(judging_prompt: str, model: str, timeout: int = 600,
                     retries: int = 1) -> tuple[dict | None, dict, str]:
    base_url = os.environ.get("JUDGE_BASE_URL",
                              os.environ.get("ORCAROUTER_BASE_URL",
                                             "https://api.orcarouter.ai/v1")).rstrip("/")
    api_key = os.environ.get("JUDGE_API_KEY", os.environ.get("ORCAROUTER_API_KEY", ""))
    url = f"{base_url}/chat/completions"
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": judging_prompt}],
        "temperature": 0,
        "max_tokens": 4000,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    usage = {"latency_s": None, "prompt_tokens": None, "completion_tokens": None}
    last_err = "unknown"
    for attempt in range(retries + 1):
        start = time.perf_counter()
        try:
            req = urllib.request.Request(
                url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST"
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            usage["latency_s"] = round(time.perf_counter() - start, 2)
            u = data.get("usage") or {}
            usage["prompt_tokens"] = u.get("prompt_tokens")
            usage["completion_tokens"] = u.get("completion_tokens")
            content = data["choices"][0]["message"]["content"]
            result = parse_judge_json(content)
            if result is None:
                last_err = "judge JSON parse failure"
            else:
                return result, usage, "ok"
        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = e.read().decode("utf-8")[:300]
            except Exception:
                pass
            last_err = f"HTTP {e.code}: {body}"
        except Exception as e:
            last_err = f"{type(e).__name__}: {e}"
        if attempt < retries:
            time.sleep(5 * (attempt + 1))
    return None, usage, last_err


def _judge_via_cmd_once(judging_prompt: str, model: str = "deepseek/deepseek-v4-pro", timeout: int = 300) -> tuple[dict | None, dict, str]:
    cmd = ["cmd", "-p", judging_prompt, "--no-session", "--yolo", "-m", model]
    start = time.perf_counter()
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        rc, stdout, stderr = proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        return None, {"latency_s": timeout, "prompt_tokens": None, "completion_tokens": None}, f"cmd judge timed out after {timeout}s"
    except Exception as e:
        return None, {"latency_s": 0, "prompt_tokens": None, "completion_tokens": None}, f"cmd judge exception: {e}"

    elapsed = round(time.perf_counter() - start, 2)
    usage = {"latency_s": elapsed, "prompt_tokens": None, "completion_tokens": None}
    if rc != 0:
        return None, usage, f"cmd exit {rc}: {stderr[:200]}"
    result = parse_judge_json(stdout)
    if result is None:
        return None, usage, f"judge JSON parse failure (raw: {stdout[:120]}...)"
    return result, usage, "ok"


def judge_via_cmd(judging_prompt: str, model: str = "deepseek/deepseek-v4-pro", timeout: int = 300,
                  retries: int = 2) -> tuple[dict | None, dict, str]:
    usage = {"latency_s": None, "prompt_tokens": None, "completion_tokens": None}
    last_err = "unknown"
    for attempt in range(retries + 1):
        result, usage, status = _judge_via_cmd_once(judging_prompt, model, timeout)
        if result is not None:
            return result, usage, status
        last_err = status
        if attempt < retries:
            wait = 5 * (attempt + 1)
            print(f"(cmd judge retry {attempt + 1}/{retries} in {wait}s: {status[:80]})", end=" ", flush=True)
            time.sleep(wait)
    return None, usage, last_err


def run_judge(args, judging_prompt: str) -> tuple[dict | None, dict, str]:
    if args.judge_backend == "cmd":
        judge_model = args.judge_model or "deepseek/deepseek-v4-pro"
        return judge_via_cmd(judging_prompt, judge_model, timeout=min(args.exec_timeout, 300))
    elif args.judge_backend == "openai":
        return judge_via_openai(judging_prompt, args.judge_model)
    judge_model = None if args.judge_model in ("agy-default", "", None) else args.judge_model
    return judge_via_agy(judging_prompt, judge_model, timeout=min(args.exec_timeout, 300))


def preflight_cmd_judge(args) -> bool:
    model = args.judge_model or "deepseek/deepseek-v4-pro"
    print(f"🔎 Preflighting cmd judge ({model})...", end=" ", flush=True)
    cmd = ["cmd", "-p", "Reply with ONLY the single word OK.", "--no-session", "--yolo", "-m", model]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
        out = (proc.stdout + proc.stderr).strip()
        if "OK" in out and proc.returncode == 0:
            print("✅ OK")
            return True
        print(f"❌ Failed: {out[:120]}")
        return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


def preflight_openai_judge(args) -> bool:
    api_key = os.environ.get("JUDGE_API_KEY", os.environ.get("ORCAROUTER_API_KEY", ""))
    if not api_key:
        print("❌ JUDGE_API_KEY is not set — export it before launching.")
        return False
    base_url = os.environ.get("JUDGE_BASE_URL",
                              os.environ.get("ORCAROUTER_BASE_URL",
                                             "https://api.orcarouter.ai/v1")).rstrip("/")
    payload = {"model": args.judge_model,
               "messages": [{"role": "user", "content": "Reply with the single word OK."}],
               "max_tokens": 5, "temperature": 0}
    req = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        content = (data.get("choices") or [{}])[0].get("message", {}).get("content", "")
        print(f"✅ Judge preflight OK: {args.judge_model} @ {base_url} responded: {content.strip()[:40]!r}")
        return True
    except Exception as e:
        print(f"❌ Judge preflight failed: {type(e).__name__}: {e}")
        return False


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
            if sem > 0 and math.isfinite(sem):
                lo, hi = stats.t.interval(0.95, len(arr) - 1, loc=m, scale=sem)
                ci_lo = float(lo) if not (math.isnan(lo) or math.isinf(lo)) else m
                ci_hi = float(hi) if not (math.isnan(hi) or math.isinf(hi)) else m
        except Exception:
            pass
    return {"mean": round(m, 2), "median": round(med, 2), "std": round(s, 2),
            "ci_low": round(ci_lo, 2), "ci_high": round(ci_hi, 2), "n": len(arr)}


def cohens_d(a: list[float], b: list[float]) -> float:
    """Cohen's d with pooled SD (positive = a > b)."""
    a_arr, b_arr = np.asarray(a, float), np.asarray(b, float)
    n1, n2 = len(a_arr), len(b_arr)
    if n1 < 2 or n2 < 2:
        return 0.0
    s_pooled = math.sqrt(((n1 - 1) * np.var(a_arr, ddof=1) + (n2 - 1) * np.var(b_arr, ddof=1)) / (n1 + n2 - 2))
    if s_pooled == 0:
        return 0.0
    return round(float((np.mean(a_arr) - np.mean(b_arr)) / s_pooled), 3)


def _finite(x):
    """Return x as a rounded float, or None if not finite (NaN/inf guard for JSON safety)."""
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return round(v, 5) if math.isfinite(v) else None


def welch_ttest(a: list[float], b: list[float]) -> tuple[float, float]:
    if len(a) < 2 or len(b) < 2:
        return 0.0, 1.0
    try:
        t, p = stats.ttest_ind(a, b, equal_var=False)
        t_f, p_f = _finite(t), _finite(p)
        return (t_f if t_f is not None else 0.0, p_f if p_f is not None else 1.0)
    except Exception:
        return 0.0, 1.0


def mannwhitney_u(a: list[float], b: list[float]) -> tuple[float, float]:
    if len(a) < 2 or len(b) < 2:
        return 0.0, 1.0
    try:
        res = stats.mannwhitneyu(a, b, alternative="two-sided")
        u_f, p_f = _finite(res.statistic), _finite(res.pvalue)
        return (u_f if u_f is not None else 0.0, p_f if p_f is not None else 1.0)
    except Exception:
        return 0.0, 1.0


def shapiro_wilk(vals: list[float]) -> dict:
    if len(vals) < 3:
        return {"W": None, "p": None, "n": len(vals)}
    try:
        w, p = stats.shapiro(vals)
        return {"W": _finite(w), "p": _finite(p), "n": len(vals)}
    except Exception:
        return {"W": None, "p": None, "n": len(vals)}


def holm_bonferroni(pvals: dict[str, float], alpha: float = 0.05) -> dict[str, dict]:
    """Holm-Bonferroni step-down correction. Returns {pair: {p, p_holm, significant}}."""
    m = len(pvals)
    ordered = sorted(pvals.items(), key=lambda kv: kv[1])
    out = {}
    running_max = 0.0
    for i, (name, p) in enumerate(ordered):
        adjusted = min(1.0, (m - i) * p)
        running_max = max(running_max, adjusted)
        out[name] = {"p": round(p, 5), "p_holm": round(running_max, 5),
                     "significant": running_max < alpha}
    return out


def correlations(x: list[float], y: list[float]) -> dict:
    none_result = {"pearson_r": None, "pearson_p": None, "spearman_rho": None, "spearman_p": None, "n": len(x)}
    if len(x) < 3:
        return none_result
    # Constant variance in either variable makes correlation undefined
    if len(set(x)) < 2 or len(set(y)) < 2:
        return none_result
    try:
        pr, pp = stats.pearsonr(x, y)
        sr, sp = stats.spearmanr(x, y)
        if any(v is None or math.isnan(float(v)) for v in (pr, pp, sr, sp)):
            return none_result
        return {"pearson_r": round(float(pr), 4), "pearson_p": round(float(pp), 5),
                "spearman_rho": round(float(sr), 4), "spearman_p": round(float(sp), 5), "n": len(x)}
    except Exception:
        return none_result


def kruskal_wallis(groups: dict[str, list[float]]) -> dict:
    valid = {k: v for k, v in groups.items() if len(v) >= 2}
    if len(valid) < 2:
        return {"H": None, "p": None, "k": len(valid)}
    try:
        h, p = stats.kruskal(*valid.values())
        h_f, p_f = _finite(h), _finite(p)
        return {"H": h_f, "p": p_f, "k": len(valid)}
    except Exception:
        return {"H": None, "p": None, "k": len(valid)}


# ─────────────────────────────────────────────────────────
# Prompt bloat analysis
# ─────────────────────────────────────────────────────────
def measure_prompt_bloat(skill_md: str, prompt: str, skill_name: str = "") -> dict:
    base_tokens = estimate_tokens(prompt)
    result = {}
    for name, fn in STRATEGIES.items():
        injected = fn(skill_md, prompt, skill_name)
        tok = estimate_tokens(injected)
        result[name] = {
            "total_tokens": tok,
            "overhead_tokens": tok - base_tokens,
            "overhead_pct": round((tok - base_tokens) / base_tokens * 100, 1),
            "chars": len(injected),
        }
    result["__skill_full_tokens"] = estimate_tokens(skill_md)
    result["__base_prompt_tokens"] = base_tokens
    return result


# ─────────────────────────────────────────────────────────
# Provenance
# ─────────────────────────────────────────────────────────
def build_provenance(args, tasks: list[dict]) -> dict:
    prov = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "python_version": sys.version.split()[0],
        "numpy_version": np.__version__,
        "scipy_version": scipy.__version__,
        "executor_cli": "agy",
        "executor_model_flag": args.models or "agy-default",
        "judge_backend": args.judge_backend,
        "judge_model": args.judge_model,
        "judge_max_chars_per_response": args.judge_chars,
        "runs_per_cell": args.runs,
        "seed": args.seed,
        "tasks_file": rel_path(args.tasks),
        "tasks_file_sha256": sha256_file(args.tasks),
        "script_sha256": sha256_file(Path(__file__).resolve()),
        "skills": {},
        "checklist_sources": {},
        "checklist_manifest_sha256": None,
    }
    try:
        prov["agy_version"] = subprocess.run(["agy", "--version"], capture_output=True,
                                             text=True, timeout=15).stdout.strip()
    except Exception:
        prov["agy_version"] = "unavailable"
    try:
        g = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                           timeout=10, cwd=ROOT)
        prov["git_sha"] = g.stdout.strip()[:12]
        d = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True,
                           timeout=10, cwd=ROOT)
        prov["git_dirty"] = bool(d.stdout.strip())
    except Exception:
        prov["git_sha"] = "unavailable"
        prov["git_dirty"] = None

    if CHECKLIST_DIR.joinpath("manifest.json").exists():
        prov["checklist_manifest_sha256"] = sha256_file(CHECKLIST_DIR / "manifest.json")

    for t in tasks:
        skill = t["skill"]
        if skill in prov["skills"]:
            continue
        skill_path = next((b / skill / "SKILL.md" for b in SKILL_SEARCH_PATHS
                           if (b / skill / "SKILL.md").exists()), None)
        prov["skills"][skill] = {
            "path": rel_path(skill_path) if skill_path else None,
            "sha256": sha256_file(skill_path) if skill_path else None,
            "bytes": skill_path.stat().st_size if skill_path else 0,
        }
        chk = CHECKLIST_DIR / f"{skill}.txt"
        prov["checklist_sources"][skill] = (
            {"artifact": rel_path(chk), "sha256": sha256_file(chk)} if chk.exists()
            else {"artifact": None, "sha256": None}
        )
    return prov


def rel_path(p: Path) -> str:
    try:
        return str(Path(p).resolve().relative_to(ROOT))
    except (ValueError, TypeError):
        return str(p)


# ─────────────────────────────────────────────────────────
# Exports: LaTeX tables + CSVs
# ─────────────────────────────────────────────────────────
def tex_escape(s: str) -> str:
    return str(s).replace("_", r"\_").replace("%", r"\%").replace("&", r"\&")


def export_latex_tables(all_data: dict, out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    summary = all_data["summary"]
    order = STRATEGY_NAMES

    # Table 1: main results
    rows = []
    for s in order:
        sc = summary[s]["score_stats"]
        rows.append(
            f"{tex_escape(s)} & {sc['mean']:.2f} & [{sc['ci_low']:.2f}, {sc['ci_high']:.2f}] & "
            f"{sc['median']:.2f} & {sc['std']:.2f} & {summary[s]['wins']} & {summary[s]['rank_pts_stats']['mean']:.2f} \\\\"
        )
    tex = """% Auto-generated by skill_delivery_experiment.py — do not edit by hand.
\\begin{table}[t]
\\centering
\\caption{Task quality by delivery strategy (blind cross-vendor LLM judge, 35-point rubric, $N$ runs per cell). CI: 95\\% confidence interval of the mean.}
\\label{tab:main-results}
\\begin{tabular}{lrrrrrr}
\\toprule
Strategy & Mean & 95\\% CI & Median & Std & Wins & Rank pts \\\\
\\midrule
""" + "\n".join(rows) + """
\\bottomrule
\\end{tabular}
\\end{table}
"""
    p = out_dir / "table_main_results.tex"
    p.write_text(tex)
    paths.append(p)

    # Table 2: pairwise comparisons
    pw = all_data.get("pairwise_stats", {})
    rows = []
    for pair in sorted(pw.keys()):
        v = pw[pair]
        sig = r"\textbf{Yes}" if v["holm"]["significant"] else "No"
        a, b = pair.split("_vs_")
        d = v["cohens_d"]
        d_str = f"{d:+.2f}" if d is not None else "--"
        rows.append(
            f"{tex_escape(a)} vs {tex_escape(b)} & {v['welch']['t']:.2f} & {v['welch']['p']:.4f} & "
            f"{v['mannwhitney']['U']:.0f} & {v['mannwhitney']['p']:.4f} & {d_str} & {sig} \\\\"
        )
    tex = """% Auto-generated by skill_delivery_experiment.py — do not edit by hand.
\\begin{table}[t]
\\centering
\\caption{Pairwise comparisons of judge scores. Welch's $t$-test, Mann--Whitney $U$, Cohen's $d$ (positive favours the first strategy). Holm--Bonferroni correction over all six comparisons.}
\\label{tab:pairwise}
\\begin{tabular}{lrrrrrc}
\\toprule
Comparison & $t$ & $p$ (Welch) & $U$ & $p$ (MW) & Cohen's $d$ & Holm sig. \\\\
\\midrule
""" + "\n".join(rows) + """
\\bottomrule
\\end{tabular}
\\end{table}
"""
    p = out_dir / "table_pairwise.tex"
    p.write_text(tex)
    paths.append(p)

    # Table 3: token efficiency + latency
    base_in = summary["control"]["in_tok_stats"]["mean"] or 1
    rows = []
    for s in order:
        it = summary[s]["in_tok_stats"]
        ot = summary[s]["out_tok_stats"]
        lc = summary[s]["latency_stats"]
        overhead = (it["mean"] - base_in) / base_in * 100
        rows.append(
            f"{tex_escape(s)} & {it['mean']:.0f} & {ot['mean']:.0f} & {overhead:+.1f}\\% & {lc['mean']:.1f} \\\\"
        )
    tex = """% Auto-generated by skill_delivery_experiment.py — do not edit by hand.
\\begin{table}[t]
\\centering
\\caption{Token overhead and end-to-end latency by delivery strategy (mean over all executions). Overhead is relative to the un-injected control prompt.}
\\label{tab:tokens}
\\begin{tabular}{lrrrr}
\\toprule
Strategy & In tokens & Out tokens & Overhead & Latency (s) \\\\
\\midrule
""" + "\n".join(rows) + """
\\bottomrule
\\end{tabular}
\\end{table}
"""
    p = out_dir / "table_tokens.tex"
    p.write_text(tex)
    paths.append(p)

    # Table 4: per-domain breakdown
    dom = all_data.get("domain_analysis", {})
    rows = []
    for dname in sorted(dom.keys()):
        dv = dom[dname]
        means = dv["strategy_means"]
        kw = dv["kruskal"]
        delta = dv["delta_checklist_vs_full"]
        cells = " & ".join(f"{means.get(s, float('nan')):.1f}" for s in order)
        kwp = f"{kw['p']:.3f}" if kw.get("p") is not None else "--"
        rows.append(
            f"{tex_escape(dname)} & {cells} & {delta:+.1f} & {kwp} \\\\"
        )
    tex = """% Auto-generated by skill_delivery_experiment.py — do not edit by hand.
\\begin{table}[t]
\\centering
\\caption{Mean judge score per software engineering domain (RQ4). $\\Delta$ is the checklist-minus-full difference; $p$ is Kruskal--Wallis across the four strategies within the domain.}
\\label{tab:domains}
\\begin{tabular}{lrrrrrrr}
\\toprule
Domain & control & full & retrieved & checklist & $\\Delta$ (chk$-$full) & KW $p$ \\\\
\\midrule
""" + "\n".join(rows) + """
\\bottomrule
\\end{tabular}
\\end{table}
"""
    p = out_dir / "table_domains.tex"
    p.write_text(tex)
    paths.append(p)
    return paths


def export_csvs(all_data: dict, out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []

    # summary.csv
    lines = ["strategy,score_mean,score_median,score_std,ci_low,ci_high,n,wins,"
             "latency_mean_s,in_tokens_mean,out_tokens_mean,rank_pts_mean"]
    for s in STRATEGY_NAMES:
        sm = all_data["summary"][s]
        sc, lc = sm["score_stats"], sm["latency_stats"]
        lines.append(f"{s},{sc['mean']},{sc['median']},{sc['std']},{sc['ci_low']},{sc['ci_high']},{sc['n']},"
                     f"{sm['wins']},{lc['mean']},{sm['in_tok_stats']['mean']},{sm['out_tok_stats']['mean']},"
                     f"{sm['rank_pts_stats']['mean']}")
    p = out_dir / "summary.csv"
    p.write_text("\n".join(lines) + "\n")
    paths.append(p)

    # runs.csv (long format, one row per execution)
    lines = ["task,domain,skill,strategy,run,ok,judge_total,correctness,completeness,maintainability,"
             "architecture,security,reasoning_quality,instruction_adherence,latency_s,input_tokens,output_tokens,"
             "missing_keywords_count"]
    for t in all_data["tasks"]:
        for strat, runs in t["strategy_runs"].items():
            for r in runs:
                js = r.get("judge_scores", {}) or {}
                lines.append(",".join(str(x) for x in [
                    t["id"], t.get("domain", ""), t["skill"], strat, r.get("run", ""),
                    r.get("ok", False), r.get("judge_total", ""),
                    js.get("correctness", ""), js.get("completeness", ""), js.get("maintainability", ""),
                    js.get("architecture", ""), js.get("security", ""), js.get("reasoning_quality", ""),
                    js.get("instruction_adherence", ""), r.get("latency", ""),
                    r.get("input_tokens", ""), r.get("output_tokens", ""),
                    len(r.get("missing_keywords", [])),
                ]))
    p = out_dir / "runs.csv"
    p.write_text("\n".join(lines) + "\n")
    paths.append(p)

    # bloat.csv (static token analysis per task)
    lines = ["task,skill,base_prompt_tokens,skill_full_tokens," + ",".join(
        f"{s}_total,{s}_overhead,{s}_overhead_pct" for s in STRATEGY_NAMES)]
    for t in all_data["tasks"]:
        b = t.get("bloat", {})
        row = [t["id"], t["skill"], b.get("__base_prompt_tokens", ""), b.get("__skill_full_tokens", "")]
        for s in STRATEGY_NAMES:
            bd = b.get(s, {})
            row += [bd.get("total_tokens", ""), bd.get("overhead_tokens", ""), bd.get("overhead_pct", "")]
        lines.append(",".join(str(x) for x in row))
    p = out_dir / "bloat.csv"
    p.write_text("\n".join(lines) + "\n")
    paths.append(p)

    # domain_deltas.csv
    dom = all_data.get("domain_analysis", {})
    lines = ["domain," + ",".join(STRATEGY_NAMES) + ",delta_checklist_vs_full,kw_H,kw_p"]
    for dname in sorted(dom.keys()):
        dv = dom[dname]
        means = dv["strategy_means"]
        kw = dv["kruskal"]
        lines.append(",".join(str(x) for x in [
            dname] + [means.get(s, "") for s in STRATEGY_NAMES] +
            [dv["delta_checklist_vs_full"], kw.get("H", ""), kw.get("p", "")]))
    p = out_dir / "domain_deltas.csv"
    p.write_text("\n".join(lines) + "\n")
    paths.append(p)
    return paths


# ─────────────────────────────────────────────────────────
# Analysis: aggregate statistics, RQ3/RQ4
# ─────────────────────────────────────────────────────────
def aggregate_analysis(all_data: dict) -> None:
    strategy_scores = defaultdict(list)
    strategy_lats = defaultdict(list)
    strategy_in_toks = defaultdict(list)
    strategy_out_toks = defaultdict(list)
    strategy_wins = defaultdict(int)
    rank_points = defaultdict(list)

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
            for rank, strat in enumerate(jd["ranking"]):
                rank_points[strat].append(len(STRATEGY_NAMES) - rank)
            if jd["ranking"]:
                strategy_wins[jd["ranking"][0]] += 1

    summary = {}
    for strat in STRATEGY_NAMES:
        summary[strat] = {
            "score_stats": compute_stats(strategy_scores[strat]),
            "latency_stats": compute_stats(strategy_lats[strat]),
            "in_tok_stats": compute_stats(strategy_in_toks[strat]),
            "out_tok_stats": compute_stats(strategy_out_toks[strat]),
            "rank_pts_stats": compute_stats(rank_points[strat]),
            "wins": strategy_wins[strat],
            "shapiro": shapiro_wilk(strategy_scores[strat]),
        }
    all_data["summary"] = summary
    all_data["raw_score_counts"] = {s: len(v) for s, v in strategy_scores.items()}

    # Pairwise: Welch + Mann-Whitney + Cohen's d, then Holm-Bonferroni
    pairwise = {}
    for s1, s2 in combinations(STRATEGY_NAMES, 2):
        t, p_w = welch_ttest(strategy_scores[s1], strategy_scores[s2])
        u, p_mw = mannwhitney_u(strategy_scores[s1], strategy_scores[s2])
        pairwise[f"{s1}_vs_{s2}"] = {
            "welch": {"t": t, "p": round(p_w, 5)},
            "mannwhitney": {"U": round(u, 1), "p": round(p_mw, 5)},
            "cohens_d": cohens_d(strategy_scores[s1], strategy_scores[s2]),
            "n_a": len(strategy_scores[s1]),
            "n_b": len(strategy_scores[s2]),
        }
    holm = holm_bonferroni({k: v["welch"]["p"] for k, v in pairwise.items()})
    for k, v in holm.items():
        pairwise[k]["holm"] = v
    all_data["pairwise_stats"] = pairwise

    # RQ4: per-domain analysis + Kruskal-Wallis
    domain_scores = defaultdict(lambda: defaultdict(list))
    for task_record in all_data["tasks"]:
        d = task_record.get("domain", "unknown")
        for strat, runs in task_record["strategy_runs"].items():
            for r in runs:
                if r.get("ok") and "judge_total" in r:
                    domain_scores[d][strat].append(r["judge_total"])
    domain_analysis = {}
    for d, strat_scores in domain_scores.items():
        means = {s: round(float(np.mean(v)), 2) for s, v in strat_scores.items() if v}
        delta = (round(means.get("checklist", 0) - means.get("full", 0), 2)
                 if "checklist" in means and "full" in means else None)
        domain_analysis[d] = {
            "strategy_means": means,
            "delta_checklist_vs_full": delta,
            "kruskal": kruskal_wallis(dict(strat_scores)),
        }
    all_data["domain_analysis"] = domain_analysis

    # RQ3: skill size vs quality delta (checklist - full)
    xs, ys, per_task = [], [], {}
    for task_record in all_data["tasks"]:
        full_scores = [r["judge_total"] for r in task_record["strategy_runs"].get("full", [])
                       if r.get("ok") and "judge_total" in r]
        chk_scores = [r["judge_total"] for r in task_record["strategy_runs"].get("checklist", [])
                      if r.get("ok") and "judge_total" in r]
        if not full_scores or not chk_scores:
            continue
        skill = task_record["skill"]
        size = all_data.get("provenance", {}).get("skills", {}).get(skill, {}).get("bytes", 0)
        delta = float(np.mean(chk_scores)) - float(np.mean(full_scores))
        xs.append(size)
        ys.append(round(delta, 2))
        per_task[task_record["id"]] = {"skill": skill, "skill_bytes": size,
                                       "delta_checklist_minus_full": round(delta, 2)}
    all_data["rq3_skillsize_vs_delta"] = {
        "per_task": per_task,
        "correlation": correlations([float(x) for x in xs], ys),
    }

    # Recommendation engine
    best_score_strat = max(summary, key=lambda s: summary[s]["score_stats"]["mean"])
    fastest_strat = min(summary, key=lambda s: summary[s]["latency_stats"]["mean"] or 9999)
    most_wins_strat = max(summary, key=lambda s: summary[s]["wins"])
    lowest_bloat = min(STRATEGY_NAMES, key=lambda s: summary[s]["in_tok_stats"]["mean"] or 9999)
    all_data["recommendation"] = {
        "best_score": best_score_strat,
        "most_wins": most_wins_strat,
        "fastest": fastest_strat,
        "lowest_bloat": lowest_bloat,
    }


# ─────────────────────────────────────────────────────────
# Markdown Report
# ─────────────────────────────────────────────────────────
def generate_report(all_data: dict, tasks: list, args) -> str:
    summary = all_data["summary"]
    pairwise = all_data.get("pairwise_stats", {})
    most_wins_strat = all_data["recommendation"]["most_wins"]

    lines = [
        "# Skill Delivery Experiment — IEEE Run\n",
        f"> **Generated**: `{all_data['timestamp']}`  ",
        f"> **Tasks**: {len(tasks)} | **Runs per strategy**: {args.runs} | **Strategies**: {len(STRATEGY_NAMES)}  ",
        f"> **Executor**: `{all_data.get('provenance', {}).get('executor_model_flag', 'agy-default')}` | "
        f"**Judge**: `{args.judge_backend}:{args.judge_model}` | **Seed**: {args.seed}",
        "\n---\n",
        "## 📊 Executive Dashboard\n",
        "| Strategy | Avg Score /35 | 95% CI | Median | Std | Wins | Avg Latency | Avg In Tok | Avg Out Tok |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for strat in STRATEGY_NAMES:
        s = summary[strat]
        sc, lc = s["score_stats"], s["latency_stats"]
        marker = " 🏆" if strat == most_wins_strat else ""
        lines.append(
            f"| `{strat}` | **{sc['mean']}** | `[{sc['ci_low']}, {sc['ci_high']}]` | {sc['median']} | "
            f"{sc['std']} | {s['wins']}{marker} | {lc['mean']}s | {s['in_tok_stats']['mean']} | "
            f"{s['out_tok_stats']['mean']} |"
        )

    lines += ["\n---\n", "## 🔬 Normality Diagnostics (Shapiro–Wilk on judge scores)\n",
              "| Strategy | W | p | n | Verdict |", "|---|---|---|---|---|"]
    for strat in STRATEGY_NAMES:
        sw = summary[strat]["shapiro"]
        if sw["p"] is None:
            lines.append(f"| `{strat}` | -- | -- | {sw['n']} | insufficient n |")
        else:
            verdict = "normal (p>0.05)" if sw["p"] > 0.05 else "**non-normal** (parametric tests cautious)"
            lines.append(f"| `{strat}` | {sw['W']} | {sw['p']} | {sw['n']} | {verdict} |")

    lines += ["\n---\n", "## 📐 Pairwise Comparisons (Welch t + Mann–Whitney U + Cohen's d, Holm-corrected)\n",
              "| Pair | t | p (Welch) | U | p (MW) | Cohen's d | Holm p | Significant? |", "|---|---|---|---|---|---|---|---|"]
    for pair in sorted(pairwise.keys()):
        v = pairwise[pair]
        sig = "⭐ Yes" if v["holm"]["significant"] else "No"
        lines.append(
            f"| `{pair}` | {v['welch']['t']} | {v['welch']['p']} | {v['mannwhitney']['U']} | "
            f"{v['mannwhitney']['p']} | {v['cohens_d']} | {v['holm']['p_holm']} | {sig} |"
        )

    lines += ["\n---\n", "## 🌍 Per-Domain Analysis (RQ4)\n",
              "| Domain | " + " | ".join(STRATEGY_NAMES) + " | Δ (chk−full) | Kruskal–Wallis p |",
              "|---|" + "---|" * (len(STRATEGY_NAMES) + 2)]
    for dname in sorted(all_data.get("domain_analysis", {}).keys()):
        dv = all_data["domain_analysis"][dname]
        means = dv["strategy_means"]
        kwp = dv["kruskal"].get("p")
        kwp_str = f"{kwp}" if kwp is not None else "--"
        cells = " | ".join(f"{means.get(s, '--')}" for s in STRATEGY_NAMES)
        lines.append(f"| {dname} | {cells} | {dv['delta_checklist_vs_full']} | {kwp_str} |")

    rq3 = all_data.get("rq3_skillsize_vs_delta", {})
    corr = rq3.get("correlation", {})
    lines += ["\n---\n", "## 📈 RQ3: Skill Size vs Quality Delta (checklist − full)\n",
              f"- Pearson r: `{corr.get('pearson_r')}` (p={corr.get('pearson_p')})",
              f"- Spearman ρ: `{corr.get('spearman_rho')}` (p={corr.get('spearman_p')})",
              f"- n tasks: {corr.get('n')}", "", "| Task | Skill | Bytes | Δ (chk−full) |", "|---|---|---|---|"]
    for tid, v in rq3.get("per_task", {}).items():
        lines.append(f"| `{tid}` | `{v['skill']}` | {v['skill_bytes']} | {v['delta_checklist_minus_full']} |")

    usage = all_data.get("judge_usage", [])
    if usage:
        pt = sum(u.get("prompt_tokens") or 0 for u in usage)
        ct = sum(u.get("completion_tokens") or 0 for u in usage)
        lines += ["\n---\n", "## ⚖️ Judge Usage & Cost Accounting\n",
                  f"- Judge calls: {len(usage)} | prompt tokens: {pt:,} | completion tokens: {ct:,}",
                  f"- Model: `{args.judge_model}` via `{args.judge_backend}`"]

    lines += ["\n---\n", "## 💡 Final Recommendation\n",
              f"- **Highest average judge score**: `{all_data['recommendation']['best_score']}`",
              f"- **Most first-place wins**: `{most_wins_strat}`",
              f"- **Lowest latency**: `{all_data['recommendation']['fastest']}`",
              f"- **Lowest prompt bloat**: `{all_data['recommendation']['lowest_bloat']}`"]

    pending_n = len(all_data.get("pending_judges", []))
    if pending_n:
        lines += ["",
                  f"> [!WARNING]",
                  f"> {pending_n} judge evaluations failed and are queued in `pending_judges`. "
                  f"Run `python3 scripts/skill_delivery_experiment.py --judge-only` (after limits reset) to score them without re-executing. "
                  f"Stats above EXCLUDE queued runs until recovered."]

    lines += ["\n---\n", "## 🧬 Per-Task Judge Explanations\n"]
    for task_record in all_data["tasks"]:
        lines.append(f"### Task `{task_record['id']}` (domain: {task_record.get('domain', '?')})\n")
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

    return "\n".join(lines)


# ─────────────────────────────────────────────────────────
# Judge-only recovery pass (scores queued runs without re-executing)
# ─────────────────────────────────────────────────────────
def process_pending_judges(args, all_data: dict, limit: int = 0) -> None:
    pending = all_data.get("pending_judges", [])
    print(f"\n⚖️  Judge-only recovery pass: {len(pending)} pending evaluations"
          + (f" (limit: {limit}/this pass)" if limit else ""))
    still_pending = []
    consecutive_fails = 0
    recovered = 0
    for p in pending:
        if limit and recovered >= limit:
            still_pending.append(p)
            continue
        prompt_path = Path(p["prompt_file"])
        if not prompt_path.exists():
            print(f"  ❌ {p['task_id']} run{p['run']}: prompt file missing — dropping")
            continue
        judging_prompt = prompt_path.read_text(encoding="utf-8")
        judge_res, judge_usage, status = run_judge(args, judging_prompt)
        judge_usage.update({"task": p["task_id"], "run": p["run"],
                            "model": args.judge_model, "pass": "judge-only"})
        all_data.setdefault("judge_usage", []).append(judge_usage)

        task = next((t for t in all_data["tasks"] if t["id"] == p["task_id"]), None)
        if judge_res is None or task is None:
            p["last_error"] = status
            p["failed_at"] = datetime.now(timezone.utc).isoformat()
            still_pending.append(p)
            consecutive_fails += 1
            print(f"  ❌ {p['task_id']} run{p['run']}: {status[:100]}")
            if consecutive_fails >= 3:
                print("  😴 3 consecutive failures — cooling down 10 min")
                time.sleep(600)
                consecutive_fails = 0
            continue
        consecutive_fails = 0

        rev_label = {v: k for k, v in p["label_map"].items()}
        scores_by_strategy = {}
        for label, strat in rev_label.items():
            if label in judge_res.get("scores", {}) and strat in p["metrics"]:
                sc = judge_res["scores"][label]
                scores_by_strategy[strat] = sc
                total = sum(v for k, v in sc.items() if k != "justification")
                p["metrics"][strat]["judge_total"] = total
                p["metrics"][strat]["judge_scores"] = sc

        ranking_strats = [rev_label.get(lbl) for lbl in judge_res.get("ranking", [])]
        ranking_strats = [s for s in ranking_strats if s is not None]

        task["judging"].append({
            "run": p["run"],
            "label_map": p["label_map"],
            "ranking": ranking_strats,
            "pairwise_analysis": judge_res.get("pairwise_analysis", ""),
            "scores_by_strategy": scores_by_strategy,
            "recovered_via": "judge-only",
        })
        for strat, metrics in p["metrics"].items():
            task["strategy_runs"][strat].append(metrics)

        print(f"  ✅ {p['task_id']} run{p['run']}: ranking={' > '.join(ranking_strats)}")
        recovered += 1
        atomic_write_json(RESULTS_PATH, all_data)
        time.sleep(2)
    all_data["pending_judges"] = still_pending
    print(f"⚖️  Recovery pass done: {recovered} recovered, {len(still_pending)} still pending")


# ─────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Skill Delivery Strategy Experiment (IEEE hardened)")
    parser.add_argument("--tasks", type=Path, default=ROOT / "benchmarks" / "tasks_ieee.json")
    parser.add_argument("--runs", type=int, default=5, help="Runs per task per strategy")
    parser.add_argument("--executor-backend", choices=["cmd", "agy"], default="cmd",
                        help="cmd = Command Code CLI (Qwen); agy = agy CLI (Gemini)")
    parser.add_argument("--executor-model", type=str, default="qwen/qwen3.7-flash",
                        help="Executor model id (e.g. qwen/qwen3.7-flash for cmd)")
    parser.add_argument("--models", type=str, default=None, help="Executor model override (comma-separated)")
    parser.add_argument("--judge-backend", choices=["cmd", "agy", "openai"], default="cmd",
                        help="cmd = Command Code CLI (DeepSeek Pro); agy = agy CLI; openai = OpenAI-compatible API")
    parser.add_argument("--judge-model", type=str, default="deepseek/deepseek-v4-pro",
                        help="Judge model id (e.g. deepseek/deepseek-v4-pro for cmd, or claude-sonnet-4-6 for agy)")
    parser.add_argument("--judge-chars", type=int, default=10000,
                        help="Max chars of each response shown to the judge")
    parser.add_argument("--exec-timeout", type=int, default=900, help="Per-execution timeout (s)")
    parser.add_argument("--seed", type=int, default=20260824)
    parser.add_argument("--resume", action="store_true", help="Skip tasks already complete in checkpoint")
    parser.add_argument("--judge-only", action="store_true",
                        help="Re-judge queued failed evaluations from the checkpoint (no re-execution)")
    parser.add_argument("--judge-limit", type=int, default=0,
                        help="Max successful judge evaluations this invocation (0 = unlimited); "
                             "extras are queued for --judge-only (e.g. 45 for OpenRouter free tier)")
    parser.add_argument("--skip-preflight", action="store_true")
    parser.add_argument("--tables-dir", type=Path, default=ROOT / "benchmarks" / "tables_ieee")
    parser.add_argument("--csv-dir", type=Path, default=ROOT / "benchmarks" / "csv_ieee")
    args = parser.parse_args()

    random.seed(args.seed)
    np.random.seed(args.seed % (2**32))

    with open(args.tasks) as f:
        tasks = json.load(f)

    if args.judge_backend == "cmd" and not args.skip_preflight:
        if not preflight_cmd_judge(args):
            raise SystemExit(1)
    elif args.judge_backend == "openai" and not args.skip_preflight:
        if not preflight_openai_judge(args):
            raise SystemExit(1)

    default_model = args.executor_model if args.executor_backend == "cmd" else None
    models = [m.strip() for m in args.models.split(",")] if args.models else [default_model]

    # Resume support
    all_data = None
    if args.resume and RESULTS_PATH.exists():
        all_data = json.loads(RESULTS_PATH.read_text())
        done = {t["id"] for t in all_data["tasks"]
                if all(len(t["strategy_runs"].get(s, [])) >= args.runs for s in STRATEGY_NAMES)}
        print(f"♻️  Resume: {len(done)}/{len(tasks)} tasks already complete — skipping them")
        tasks = [t for t in tasks if t["id"] not in done]
        if not tasks:
            print("✅ All tasks already complete — regenerating analysis/exports only.")
    if all_data is None:
        all_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "runs_per_task": args.runs,
            "strategies": STRATEGY_NAMES,
            "tasks": [],
        }

    all_data["provenance"] = build_provenance(args, json.loads(args.tasks.read_text()))
    prov = all_data["provenance"]

    if args.judge_only:
        if not all_data.get("tasks"):
            print("❌ No checkpoint data to recover.")
            raise SystemExit(1)
        process_pending_judges(args, all_data, limit=args.judge_limit)
    else:
        print(f"🧪 Skill Delivery Experiment | {len(tasks)} tasks × {args.runs} runs × {len(STRATEGY_NAMES)} strategies")
        print(f"   Strategies: {STRATEGY_NAMES}")
        exec_str = f"{args.executor_backend}:{args.executor_model}" if args.executor_backend == "cmd" else f"agy ({prov.get('agy_version', '?')})"
        print(f"   Executor: {exec_str} | Judge: {args.judge_backend}:{args.judge_model}\n")

        RAW_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        def checkpoint():
            atomic_write_json(RESULTS_PATH, all_data)

        for model in models:
            judge_budget_used = 0
            for task in tasks:
                task_id = task["id"]
                prompt = task["prompt"]
                must_incl = task["must_include"]
                skill = task["skill"]
                domain = task.get("domain", "unknown")

                # Resume top-up: keep existing runs, execute only the missing ones
                existing = next((t for t in all_data["tasks"] if t["id"] == task_id), None) if args.resume else None
                done_runs = 0
                if existing is not None:
                    done_runs = len(existing["strategy_runs"]["control"])
                    pending_runs = [p["run"] for p in all_data.get("pending_judges", []) if p["task_id"] == task_id]
                    if pending_runs:
                        done_runs = max(done_runs, max(pending_runs))

                if existing is not None and done_runs > 0:
                    start_run = done_runs + 1
                    task_record = existing
                    print(f"\n♻️  Top-up: {task_id} already has {done_runs}/{args.runs} runs — executing runs {start_run}..{args.runs}")
                    if start_run > args.runs:
                        print("   already complete — skipping")
                        continue
                else:
                    # Fresh start (no record, or nothing valid to preserve — e.g. quota-corrupted
                    # records with 0 runs): replaces old state entirely
                    start_run = 1
                    task_record = None

                skill_md = load_skill_md(skill)
                if not skill_md:
                    print(f"⚠️  Skill '{skill}' not found — control only for task {task_id}")

                bloat = measure_prompt_bloat(skill_md or "", prompt, skill)
                print(f"\n{'='*60}")
                print(f"📝 Task: {task_id} [{domain}] | Skill: {skill}")
                print(f"   Prompt tokens (base): {bloat['__base_prompt_tokens']}")
                for s in STRATEGY_NAMES:
                    print(f"   [{s:12s}] total={bloat[s]['total_tokens']} tokens (+{bloat[s]['overhead_tokens']}, +{bloat[s]['overhead_pct']}%)")

                if task_record is None:
                    task_record = {
                        "id": task_id,
                        "skill": skill,
                        "domain": domain,
                        "model": model or "Default Model",
                        "bloat": bloat,
                        "strategy_runs": {s: [] for s in STRATEGY_NAMES},
                        "judging": [],
                    }
                    # Fresh start: drop stale pending-judge entries from a previous pass
                    all_data["pending_judges"] = [p for p in all_data.get("pending_judges", [])
                                                  if p["task_id"] != task_id]

                consecutive_judge_fails = 0

                for run_idx in range(start_run, args.runs + 1):
                    print(f"\n  ── Run {run_idx}/{args.runs} ──")

                    shuffled = STRATEGY_NAMES.copy()
                    random.shuffle(shuffled)
                    labels_list = [chr(ord("A") + i) for i in range(len(shuffled))]
                    label_map = {s: lbl for s, lbl in zip(shuffled, labels_list)}
                    rev_label = {v: k for k, v in label_map.items()}

                    outputs = {}
                    run_metrics = {}
                    task_raw_dir = RAW_OUTPUT_DIR / task_id
                    task_raw_dir.mkdir(parents=True, exist_ok=True)

                    for strat in STRATEGY_NAMES:
                        inject_fn = STRATEGIES[strat]
                        injected = inject_fn(skill_md or "", prompt, skill)
                        input_tok = estimate_tokens(injected)

                        print(f"  🔁 [{strat:12s}] executing...", end=" ", flush=True)
                        rc, out, err, latency = run_cmd(
                            injected,
                            model=model or args.executor_model,
                            backend=args.executor_backend,
                            timeout=args.exec_timeout,
                        )

                        # Archive raw output regardless of success (audit trail)
                        (task_raw_dir / f"{strat}_run{run_idx}.txt").write_text(
                            f"[exit={rc} latency={latency:.2f}s]\n{out}", encoding="utf-8")

                        if rc != 0:
                            print(f"❌ FAILED (exit {rc}) {err[:120]}")
                            outputs[strat] = ""
                            run_metrics[strat] = {"ok": False, "run": run_idx, "error": err[:300]}
                            continue

                        output_tok = estimate_tokens(out)
                        missing_kws = [p for p in must_incl if not re.search(p, out, re.IGNORECASE)]

                        print(f"✅ {latency:.1f}s | in≈{input_tok}tok out≈{output_tok}tok")
                        outputs[strat] = out
                        run_metrics[strat] = {
                            "ok": True,
                            "run": run_idx,
                            "latency": round(latency, 2),
                            "input_tokens": input_tok,
                            "output_tokens": output_tok,
                            "missing_keywords": missing_kws,
                        }

                    valid_strats = [s for s in STRATEGY_NAMES if run_metrics.get(s, {}).get("ok")]
                    if len(valid_strats) < 2:
                        print("  ⚠️  Too few valid outputs for judging — skipping")
                        continue

                    valid_label_map = {s: label_map[s] for s in valid_strats}
                    judging_prompt = build_judging_prompt(prompt, outputs, valid_label_map, args.judge_chars)
                    judge_prompt_file = task_raw_dir / f"judge_prompt_run{run_idx}.txt"
                    judge_prompt_file.write_text(judging_prompt, encoding="utf-8")

                    print(f"  ⚖️  Blind {len(valid_strats)}-way judge ({args.judge_backend}:{args.judge_model}) ...", end=" ", flush=True)
                    if args.judge_limit and judge_budget_used >= args.judge_limit:
                        judge_res = None
                        judge_usage = {"latency_s": None, "prompt_tokens": None, "completion_tokens": None}
                        judge_status = f"judge-limit {args.judge_limit} reached — queued for --judge-only"
                    else:
                        judge_res, judge_usage, judge_status = run_judge(args, judging_prompt)
                        if judge_res is not None:
                            judge_budget_used += 1

                    (task_raw_dir / f"judge_run{run_idx}.json").write_text(json.dumps({
                        "label_map": valid_label_map,
                        "status": judge_status,
                        "usage": judge_usage,
                        "raw_result": judge_res,
                    }, indent=2), encoding="utf-8")

                    judge_usage.update({"task": task_id, "run": run_idx, "model": args.judge_model})
                    all_data.setdefault("judge_usage", []).append(judge_usage)

                    if not judge_res:
                        print(f"❌ judge failed: {judge_status}")
                        all_data.setdefault("pending_judges", []).append({
                            "task_id": task_id, "run": run_idx, "skill": skill, "domain": domain,
                            "label_map": valid_label_map,
                            "metrics": {s: run_metrics[s] for s in valid_strats},
                            "prompt_file": str(judge_prompt_file),
                            "failed_at": datetime.now(timezone.utc).isoformat(),
                            "last_error": judge_status,
                        })
                        consecutive_judge_fails += 1
                        if consecutive_judge_fails >= 3:
                            print("  😴 3 consecutive judge failures — cooling down 10 min (rate limit?)")
                            time.sleep(600)
                            consecutive_judge_fails = 0
                        checkpoint()
                        continue
                    consecutive_judge_fails = 0
                    print("✅")

                    unblinded_scores = {}
                    for label, strat in rev_label.items():
                        if strat in valid_strats and label in judge_res.get("scores", {}):
                            unblinded_scores[strat] = judge_res["scores"][label]
                            total = sum(v for k, v in judge_res["scores"][label].items() if k != "justification")
                            run_metrics[strat]["judge_total"] = total
                            run_metrics[strat]["judge_scores"] = judge_res["scores"][label]

                    ranking_strats = [rev_label.get(lbl) for lbl in judge_res.get("ranking", [])]
                    ranking_strats = [s for s in ranking_strats if s is not None]

                    task_record["judging"].append({
                        "run": run_idx,
                        "label_map": valid_label_map,
                        "ranking": ranking_strats,
                        "pairwise_analysis": judge_res.get("pairwise_analysis", ""),
                        "scores_by_strategy": unblinded_scores,
                    })

                    for strat in valid_strats:
                        task_record["strategy_runs"][strat].append(run_metrics[strat])

                    score_line = " | ".join(
                        f"{s}={run_metrics[s].get('judge_total','?')}/35"
                        for s in STRATEGY_NAMES if run_metrics.get(s, {}).get("ok")
                    )
                    print(f"  🏆 Ranking: {' > '.join(ranking_strats)}")
                    print(f"     Scores: {score_line}")

                # Replace any partial record for this task, then checkpoint
                all_data["tasks"] = [t for t in all_data["tasks"] if t["id"] != task_id]
                all_data["tasks"].append(task_record)
                checkpoint()
                print(f"\n  💾 Checkpoint saved ({len(all_data['tasks'])} tasks done)")

    # ─────────────────────────────────────────────────────
    # Final analysis + exports
    # ─────────────────────────────────────────────────────
    aggregate_analysis(all_data)
    all_data["completed_at"] = datetime.now(timezone.utc).isoformat()
    checkpoint()

    table_paths = export_latex_tables(all_data, args.tables_dir)
    csv_paths = export_csvs(all_data, args.csv_dir)
    report = generate_report(all_data, json.loads(args.tasks.read_text()), args)
    atomic_write_text(REPORT_PATH, report)

    summary = all_data["summary"]
    print("\n" + "=" * 60)
    print("🏆 Skill Delivery Experiment Complete!")
    print(f"   Best Score Strategy : {all_data['recommendation']['best_score']}")
    print(f"   Most Wins           : {all_data['recommendation']['most_wins']}")
    print(f"   Fastest             : {all_data['recommendation']['fastest']}")
    print(f"   Lowest Bloat        : {all_data['recommendation']['lowest_bloat']}")
    print(f"\n   Scores (avg/35):")
    for strat in STRATEGY_NAMES:
        print(f"     {strat:12s}: {summary[strat]['score_stats']['mean']}")
    pending_n = len(all_data.get("pending_judges", []))
    if pending_n:
        print(f"\n   ⚠️  {pending_n} judge evaluations queued — recover with: python3 {Path(__file__).name} --judge-only")
    print(f"\n   Results : {RESULTS_PATH}")
    print(f"   Report  : {REPORT_PATH}")
    for p in table_paths:
        print(f"   Table   : {p}")
    for p in csv_paths:
        print(f"   CSV     : {p}")
    print("=" * 60)


if __name__ == "__main__":
    main()
