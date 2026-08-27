#!/usr/bin/env python3
"""
Checklist Compiler v2 (Balanced Structure-Preserving Build Step)
==============================================================
Statically pre-compiles balanced, high-density instruction artifacts from
SKILL.md source files into benchmarks/checklists_v2/.

Compiler v2 Design Principles:
  1. Preserves Implementation Depth: Retains code signatures, SQL/DDL snippets,
     exact syntax templates, and decision tables.
  2. Prunes Conversational Narrative: Removes narrative prose, introduction fluff,
     "When to Activate" boilerplate, and navigation guides.
  3. Compacts Large Code Blocks: Keeps syntax signatures, interfaces, and core DDL/rules
     while eliminating repetitive implementation boilerplate.
  4. Prevents Context Collapse: Addresses Brevity Bias (Zhang et al., 2025) by
     keeping essential structural anchors while achieving ~40-50% token reduction.
  5. Determinism guarantees: Byte-identical reproducibility via SHA256 manifest.

Usage:
  python3 scripts/compile_checklists_v2.py                    # compile from tasks_ieee.json
  python3 scripts/compile_checklists_v2.py --skills database-migrations security-review
  python3 scripts/compile_checklists_v2.py --out benchmarks/checklists_v2
"""
import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TASKS = ROOT / "benchmarks" / "tasks_ieee.json"
DEFAULT_OUT = ROOT / "benchmarks" / "checklists_v2"

EXTRACTOR_VERSION = "2.0.0"

HEADING_RE = re.compile(r"^(#{1,4})\s+(.*)")
BULLET_RE = re.compile(r"^\s*[-*•]\s+(.*)$")
NUMBERED_RE = re.compile(r"^\s*\d+[.)]\s+(.*)$")
BOLD_LINE_RE = re.compile(r"^\s*\*\*([^*]+):?\*\*:?\s*(.*)$")
TABLE_ROW_RE = re.compile(r"^\s*\|(.+)\|\s*$")
TABLE_SEP_RE = re.compile(r"^\s*\|[\s:|-]+\|\s*$")
FENCE_RE = re.compile(r"^\s*(```|~~~)")

SKIP_SECTION_TITLES = {
    "when to activate",
    "when to use",
    "overview",
    "introduction",
    "prerequisites",
    "installation",
    "related skills",
    "table of contents",
    "origin",
    "metadata",
    "resources",
    "related tools",
    "recommended plugins",
    "further reading",
    "references",
}


def strip_yaml_frontmatter(text: str) -> str:
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            return parts[2].lstrip("\r\n")
    return text


def compact_code_block(fence_lines: list[str], max_body_lines: int = 14) -> list[str]:
    """Preserve essential signatures, SQL statements, and syntax templates while compacting huge blocks."""
    if len(fence_lines) <= max_body_lines + 2:
        return fence_lines
    
    header = fence_lines[0]
    footer = fence_lines[-1]
    body = fence_lines[1:-1]
    
    # Filter out redundant blank lines in code
    compact_body = [l for l in body if l.strip()]
    if len(compact_body) <= max_body_lines:
        return [header] + compact_body + [footer]
    
    # Select top essential lines + trailing signatures
    head_slice = compact_body[:max_body_lines - 3]
    tail_slice = compact_body[-2:]
    return [header] + head_slice + ["  # ... [syntax pattern continues] ..."] + tail_slice + [footer]


def is_actionable_v2(text: str) -> bool:
    t = text.strip()
    if not t or len(t) < 6:
        return False
    if t.startswith("**") or t.startswith("`") or t.startswith("["):
        return True
    first = t[0]
    if first.isupper():
        return True
    return bool(re.match(r"^(use|avoid|never|always|set|add|run|enable|disable|keep|prefer|check|ensure|require|pin|scope|limit|wrap|store|mount|define|quote|index|batch|validate|verify|reject|fail|retry|cache|mask|exclude|include)\b", t, re.IGNORECASE))


def compile_checklist_v2(skill_md: str) -> str:
    raw_text = strip_yaml_frontmatter(skill_md)
    lines = raw_text.splitlines()

    out_lines: list[str] = []
    seen: set[str] = set()
    in_fence = False
    fence_buffer: list[str] = []
    in_skip_section = False
    current_section_level = 0
    pending_heading: str | None = None

    for line in lines:
        stripped = line.strip()

        # Handle fenced code blocks
        if FENCE_RE.match(line):
            if not in_fence:
                in_fence = True
                fence_buffer = [line]
            else:
                in_fence = False
                fence_buffer.append(line)
                if not in_skip_section:
                    compact_fence = compact_code_block(fence_buffer, max_body_lines=12)
                    if pending_heading is not None:
                        out_lines.append(pending_heading)
                        pending_heading = None
                    out_lines.extend(compact_fence)
                    out_lines.append("")
                fence_buffer = []
            continue

        if in_fence:
            fence_buffer.append(line)
            continue

        # Handle headings
        h = HEADING_RE.match(line)
        if h:
            level = len(h.group(1))
            title = h.group(2).strip()
            norm_title = title.lower().rstrip(":")

            if norm_title in SKIP_SECTION_TITLES:
                in_skip_section = True
                current_section_level = level
                pending_heading = None
                continue
            elif in_skip_section and level <= current_section_level:
                in_skip_section = False

            if in_skip_section:
                continue

            if level == 1:
                pending_heading = None
                continue

            pending_heading = f"{'#' * level} {title}"
            continue

        if in_skip_section:
            continue

        # Handle Table Rows (Preserve full markdown tables)
        if TABLE_ROW_RE.match(line):
            if pending_heading is not None:
                out_lines.append(pending_heading)
                pending_heading = None
            out_lines.append(line)
            continue

        # Handle List Items (bullets, numbered lists, checkboxes)
        m = BULLET_RE.match(line) or NUMBERED_RE.match(line)
        if m:
            content = m.group(1).strip()
            if not is_actionable_v2(content):
                continue
            norm_key = content.lower()[:60]
            if norm_key in seen:
                continue
            seen.add(norm_key)

            if pending_heading is not None:
                out_lines.append(pending_heading)
                pending_heading = None
            out_lines.append(f"- {content}")
            continue

        # Handle Bold Definition Lines
        b = BOLD_LINE_RE.match(line)
        if b:
            label, rest = b.group(1).strip().rstrip(":"), b.group(2).strip()
            norm_key = label.lower()
            if norm_key in seen:
                continue
            seen.add(norm_key)

            if pending_heading is not None:
                out_lines.append(pending_heading)
                pending_heading = None
            if rest:
                out_lines.append(f"**{label}:** {rest}")
            else:
                out_lines.append(f"**{label}**")
            continue

    # Clean up multiple blank lines
    result_lines: list[str] = []
    prev_blank = False
    for l in out_lines:
        if not l.strip():
            if not prev_blank:
                result_lines.append("")
                prev_blank = True
        else:
            result_lines.append(l)
            prev_blank = False

    return "\n".join(result_lines).strip() + "\n"


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
    ap = argparse.ArgumentParser(description="Compile SKILL.md files into balanced v2 instruction artifacts")
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

    print(f"🔧 Compiling {len(skills)} v2 checklists -> {args.out}\n")
    print(f"{'skill':<36} {'src_bytes':>9} {'v2_bytes':>9} {'v2_lines':>9} {'tok_full':>8} {'tok_v2':>7} {'reduction':>9}")
    print("-" * 92)

    total_full_tok = 0
    total_v2_tok = 0

    for skill in skills:
        src = ROOT / "skills" / skill / "SKILL.md"
        if not src.exists():
            print(f"❌ {skill}: source not found at {src}")
            continue

        src_bytes = src.read_bytes()
        skill_md = src_bytes.decode("utf-8")
        checklist_v2 = compile_checklist_v2(skill_md)

        if not checklist_v2.strip():
            print(f"⚠️  {skill}: extraction produced an empty checklist — skipping write")
            continue

        out_path = args.out / f"{skill}.txt"
        out_bytes = checklist_v2.encode("utf-8")
        out_path.write_bytes(out_bytes)

        tok_full, tok_v2 = estimate_tokens(skill_md), estimate_tokens(checklist_v2)
        total_full_tok += tok_full
        total_v2_tok += tok_v2

        reduction = round((1 - tok_v2 / tok_full) * 100, 1)
        print(f"✅ {skill:<34} {len(src_bytes):>9} {len(out_bytes):>9} "
              f"{checklist_v2.count(chr(10)):>9} {tok_full:>8} {tok_v2:>7} {reduction:>8}%")

        manifest["checklists"][skill] = {
            "source": rel_path(src),
            "source_sha256": sha256_bytes(src_bytes),
            "source_bytes": len(src_bytes),
            "artifact": rel_path(out_path),
            "artifact_sha256": sha256_bytes(out_bytes),
            "artifact_bytes": len(out_bytes),
            "artifact_lines": checklist_v2.count("\n"),
            "tokens_full_estimate": tok_full,
            "tokens_checklist_estimate": tok_v2,
            "token_reduction_pct": reduction,
        }

    overall_reduction = round((1 - total_v2_tok / total_full_tok) * 100, 1) if total_full_tok else 0.0
    manifest["overall_token_reduction_pct"] = overall_reduction
    manifest_path = args.out / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    print("-" * 92)
    print(f"📊 Overall Token Reduction across all {len(skills)} skills: {overall_reduction}% (Full: {total_full_tok} tok -> v2: {total_v2_tok} tok)")
    print(f"📄 Manifest: {manifest_path} ({len(manifest['checklists'])} entries)")


if __name__ == "__main__":
    main()
