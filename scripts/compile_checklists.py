#!/usr/bin/env python3
"""
Checklist Compiler (Offline Build Step)
=======================================
Statically pre-compiles high-density actionable checklists from SKILL.md
source files into runtime-ready artifacts under benchmarks/checklists_ieee/.

This is the "compile-time" step of the 2-tier delivery pipeline:
  SKILL.md (source) --[deterministic extraction]--> checklist (target)

Determinism guarantees:
  - No timestamps, no randomness, no LLM calls in the emitted checklists.
  - Identical input bytes -> identical output bytes (verified via SHA256 manifest).

Usage:
  python3 scripts/compile_checklists.py                    # compile from tasks_ieee.json
  python3 scripts/compile_checklists.py --skills tdd redis-patterns
"""
import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TASKS = ROOT / "benchmarks" / "tasks_ieee.json"
DEFAULT_OUT = ROOT / "benchmarks" / "checklists_ieee"

EXTRACTOR_VERSION = "1.1.0"

HEADING_RE = re.compile(r"^(#{1,4})\s+(.*)")
BULLET_RE = re.compile(r"^\s*[-*•]\s+(.*)$")
NUMBERED_RE = re.compile(r"^\s*\d+[.)]\s+(.*)$")
BOLD_LINE_RE = re.compile(r"^\s*\*\*([^*]+):?\*\*:?\s*(.*)$")
TABLE_ROW_RE = re.compile(r"^\s*\|(.+)\|\s*$")
TABLE_SEP_RE = re.compile(r"^\s*\|[\s:|-]+\|\s*$")
FENCE_RE = re.compile(r"^\s*(```|~~~)")


def actionable(text: str) -> bool:
    """A bullet is actionable if it reads like a rule, not prose navigation."""
    t = text.strip()
    if not t or len(t) < 8:
        return False
    # Bold-led bullets: - **Always X** (strongest signal)
    if t.startswith("**"):
        return True
    # Capitalised imperative or code-led bullets: - Run tests..., - `npm ci` ...
    first = t[0]
    if first.isupper() or first == "`":
        return True
    # Imperative verb fallback (lowercase start but imperative form)
    return bool(re.match(r"^(use|avoid|never|always|set|add|run|enable|disable|keep|prefer|check|ensure|require|pin|scope|limit|wrap|store|mount|define|quote|index|batch|validate|verify|reject|fail|retry|cache|mask|exclude|include)\b", t, re.IGNORECASE))


def compile_checklist(skill_md: str) -> str:
    """Deterministically extract an actionable checklist from SKILL.md."""
    out_lines: list[str] = []
    seen: set[str] = set()
    in_fence = False
    pending_heading: str | None = None  # emitted lazily, only if bullets follow

    for line in skill_md.splitlines():
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        h = HEADING_RE.match(line)
        if h:
            pending_heading = None  # deeper heading supersedes ancestor
            # Headings are anchors for bullets; skip top-level title
            level = len(h.group(1))
            title = h.group(2).strip()
            if level > 1 and title:
                pending_heading = f"{'#' * (level - 1)} {title}"
            continue

        m = BULLET_RE.match(line) or NUMBERED_RE.match(line)
        if m:
            raw = m.group(1).strip()
        else:
            b = BOLD_LINE_RE.match(line)
            t = TABLE_ROW_RE.match(line)
            if b and not t:
                label, rest = b.group(1).strip().rstrip(":").strip(), b.group(2).strip()
                # Bold definition lines read as rules when followed by prose
                raw = f"**{label}:** {rest}" if rest else f"**{label}**"
            elif t and not TABLE_SEP_RE.match(line):
                cells = [c.strip().replace("**", "") for c in t.group(1).split("|")]
                cells = [c for c in cells if c]
                if len(cells) < 2:
                    continue
                raw = f"{cells[0]}: {' | '.join(cells[1:])}"
            else:
                continue
        # Normalise numbered items to bullets; collapse internal whitespace
        clean = re.sub(r"\s+", " ", raw)
        if not actionable(clean):
            continue
        key = clean.lower()
        if key in seen:
            continue
        seen.add(key)
        if pending_heading is not None:
            out_lines.append(pending_heading)
            pending_heading = None
        out_lines.append(f"- {clean}")

    return "\n".join(out_lines).strip() + "\n"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def rel_path(p: Path) -> str:
    try:
        return str(p.resolve().relative_to(ROOT))
    except ValueError:
        return str(p.resolve())


def main() -> None:
    ap = argparse.ArgumentParser(description="Compile SKILL.md files into actionable checklists")
    ap.add_argument("--tasks", type=Path, default=DEFAULT_TASKS, help="Task JSON defining the skill set")
    ap.add_argument("--skills", nargs="*", help="Explicit skill names (overrides --tasks)")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output directory")
    args = ap.parse_args()

    if args.skills:
        skills = args.skills
    else:
        with open(args.tasks) as f:
            skills = sorted({t["skill"] for t in json.load(f)})

    args.out.mkdir(parents=True, exist_ok=True)
    manifest = {
        "extractor_version": EXTRACTOR_VERSION,
        "compiled_at": datetime.now(timezone.utc).isoformat(),
        "source_of_truth": str(args.tasks) if not args.skills else "cli-args",
        "checklists": {},
    }

    print(f"🔧 Compiling {len(skills)} checklists -> {args.out}\n")
    print(f"{'skill':<36} {'src_bytes':>9} {'chk_bytes':>9} {'chk_lines':>9} {'tok_full':>8} {'tok_chk':>7} {'reduction':>9}")
    print("-" * 92)

    for skill in skills:
        src = ROOT / "skills" / skill / "SKILL.md"
        if not src.exists():
            print(f"❌ {skill}: source not found at {src}")
            continue

        src_bytes = src.read_bytes()
        skill_md = src_bytes.decode("utf-8")
        checklist = compile_checklist(skill_md)

        if not checklist.strip():
            print(f"⚠️  {skill}: extraction produced an empty checklist — skipping write")
            continue

        out_path = args.out / f"{skill}.txt"
        out_bytes = checklist.encode("utf-8")
        out_path.write_bytes(out_bytes)

        tok_full, tok_chk = estimate_tokens(skill_md), estimate_tokens(checklist)
        reduction = round((1 - tok_chk / tok_full) * 100, 1)
        print(f"✅ {skill:<34} {len(src_bytes):>9} {len(out_bytes):>9} "
              f"{checklist.count(chr(10)):>9} {tok_full:>8} {tok_chk:>7} {reduction:>8}%")

        manifest["checklists"][skill] = {
            "source": rel_path(src),
            "source_sha256": sha256_bytes(src_bytes),
            "source_bytes": len(src_bytes),
            "artifact": rel_path(out_path),
            "artifact_sha256": sha256_bytes(out_bytes),
            "artifact_bytes": len(out_bytes),
            "artifact_lines": checklist.count("\n"),
            "tokens_full_estimate": tok_full,
            "tokens_checklist_estimate": tok_chk,
            "token_reduction_pct": reduction,
        }

    manifest_path = args.out / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    print("-" * 92)
    print(f"📄 Manifest: {manifest_path} ({len(manifest['checklists'])} entries)")


if __name__ == "__main__":
    main()
