"""Structure-preserving static compiler for coding-agent skills (SKILL.md).

Python port of the former `crates/skills-compiler` (Rust v0.2.0), retained
because its output is the provenance record for the study in
`paper/` -- the committed artifacts under `benchmarks/checklists_v2/`,
`benchmarks/ablations/` and the per-condition prompts were all produced by
that compiler. The port is a byte-for-byte reimplementation, verified against
the Rust binary on identical input for every compilation mode (see
`tests/test_compiler_parity.py` and `scripts/verify_compiled_artifacts.py`).

Changing compiler behaviour changes published numbers. Behaviour that is
known-imperfect (the A4 type eraser's known gaps) is pinned by tests
deliberately so a future fix surfaces as a test failure rather than as silent
drift away from the recorded artifacts.

CLI:
    python scripts/skills_compiler.py compile --input skills/tdd/SKILL.md
    python scripts/skills_compiler.py from-tasks --tasks benchmarks/tasks_ieee.json
    python scripts/skills_compiler.py ablate --input skills/tdd/SKILL.md
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from dataclasses import dataclass, replace
from pathlib import Path

COMPILER_VERSION = "python-port 1.0 (byte-equivalent to skills-compiler 0.2.0)"

REPO = Path(__file__).resolve().parents[1]

# --- regex table, transcribed 1:1 from Compiler::new() --------------------
HEADING_RE = re.compile(r"^(#{1,4})\s+(.*)")
BULLET_RE = re.compile(r"^\s*[-*•]\s+(.*)$")
NUMBERED_RE = re.compile(r"^\s*\d+[.)]\s+(.*)$")
BOLD_LINE_RE = re.compile(r"^\s*\*\*([^*]+):?\*\*:?\s*(.*)$")
TABLE_ROW_RE = re.compile(r"^\s*\|(.+)\|\s*$")
FENCE_RE = re.compile(r"^\s*(```|~~~)(.*)")
FENCE_INFO_RE = re.compile(r"^\s*(?:```|~~~)\s*([A-Za-z0-9_+#-]+)")
ACTION_VERB_RE = re.compile(
    r"^(use|avoid|never|always|set|add|run|enable|disable|keep|prefer|check|"
    r"ensure|require|pin|scope|limit|wrap|store|mount|define|quote|index|"
    r"batch|validate|verify|reject|fail|retry|cache|mask|exclude|include)\b",
    re.IGNORECASE,
)
TYPE_DECL_RE = re.compile(
    r"^\s*(export\s+(default\s+)?)?(interface\s+[A-Za-z_]\w*"
    r"|type\s+[A-Za-z_]\w*\s*=|enum\s+[A-Za-z_]\w*"
    r"|abstract\s+class\s+[A-Za-z_]\w*)"
)
PY_CONTRACT_RE = re.compile(
    r"^\s*class\s+[A-Za-z_]\w*\s*\([^)]*\b(Protocol|ABC|Generic|TypedDict)\b"
    r"[^)]*\)\s*:?\s*$"
)
AS_CAST_RE = re.compile(r"\s+as\s+(const\b|[A-Za-z_][\w<>\[\].]*)")
SIG_LINE_RE = re.compile(
    r"^\s*(export\s+)?(async\s+)?(function\s+[A-Za-z_]\w*"
    r"|(const|let|var)\s+[A-Za-z_]\w*\s*=\s*(async\s*)?\("
    r"|def\s+[A-Za-z_]\w*|[A-Za-z_]\w*\s*\()"
)
PARAM_ANNOT_RE = re.compile(
    r"(\w)\s*:\s*[A-Za-z_][\w.<>\[\]]*(?:\s*\|\s*[A-Za-z_][\w.<>\[\]]*)*"
)
RETURN_ANNOT_RE = re.compile(r"\)\s*:\s*[A-Za-z_][\w.<>\[\]| ]*?(\s*[{=;]|\s*$)")
PY_RETURN_ANNOT_RE = re.compile(r"\s*->\s*[A-Za-z_][\w.<>\[\]|, ]*?(\s*:)")
TYPED_PROP_RE = re.compile(
    r"^(\s*(?:readonly\s+)?[A-Za-z_]\w*\??)\s*:\s*[A-Za-z_][\w.<>\[\]| ]*?\s*(;|,)?\s*$"
)

SKIP_SECTIONS = {
    "when to activate", "when to use", "overview", "introduction",
    "prerequisites", "installation", "related skills", "table of contents",
    "origin", "metadata", "resources", "related tools",
    "recommended plugins", "further reading", "references",
}

TYPED_LANGS = {
    "typescript", "ts", "tsx", "javascript", "js", "jsx", "python", "py",
}

# Domain::default_code_lines() -- keyed by the Domain enum name.
DOMAIN_DEFAULT_CODE_LINES = {
    "architecture": 14, "database": 16, "devops": 14, "sre": 14,
    "security": 12, "testing": 18, "general": 14,
}
# main.rs's task-string -> Domain mapping. Anything unlisted is General.
TASK_DOMAIN_TO_DOMAIN = {
    "architecture & refactoring": "architecture", "architecture": "architecture",
    "databases & persistence": "database", "databases": "database",
    "devops & cloud": "devops", "devops": "devops",
    "sre & debugging": "sre", "sre": "sre",
    "security & auditing": "security", "security": "security",
    "testing & qa": "testing", "testing": "testing",
}
DEFAULT_HEADER = (
    "[ENGINEERING IMPLEMENTATION STANDARDS & ARCHITECTURAL CONSTRAINTS]"
)
V1_HEADER = "[CHECKLIST GUIDELINES]"


@dataclass(frozen=True)
class CompilationOptions:
    """Field-for-field mirror of the Rust CompilationOptions struct."""
    keep_narrative: bool = False
    keep_examples: bool = True
    keep_types: bool = True
    keep_tables: bool = True
    keep_invariants: bool = True
    keep_frontmatter: bool = False
    max_code_lines: int = 14
    header_directive: str | None = DEFAULT_HEADER


def checklist_v2(domain: str = "general") -> CompilationOptions:
    """Domain is a Domain enum name, matching the Rust signature."""
    return CompilationOptions(
        max_code_lines=DOMAIN_DEFAULT_CODE_LINES.get(domain, 14)
    )


def checklist_v1() -> CompilationOptions:
    return CompilationOptions(
        keep_narrative=False, keep_examples=False, keep_types=False,
        keep_tables=False, keep_invariants=True, keep_frontmatter=False,
        max_code_lines=0, header_directive=V1_HEADER,
    )


def no_examples(domain: str = "general") -> CompilationOptions:
    return replace(checklist_v2(domain), keep_examples=False)


def no_tables(domain: str = "general") -> CompilationOptions:
    return replace(checklist_v2(domain), keep_tables=False)


def no_types(domain: str = "general") -> CompilationOptions:
    return replace(checklist_v2(domain), keep_types=False)


# --- fidelity helpers ----------------------------------------------------
def blen(s: str) -> int:
    """Rust `&str::len()` -- bytes, not code points."""
    return len(s.encode("utf-8"))


def split_on_lf(s: str) -> list[str]:
    """Rust `split_inclusive('\\n')`: split only on \\n, keep the delimiter.

    Python's `str.splitlines()` also splits on \\r \\v \\f \\x1c \\x85 \\u2028 \\u2029,
    which would desynchronise the frontmatter scanner from Rust.
    """
    out: list[str] = []
    cur: list[str] = []
    for ch in s:
        cur.append(ch)
        if ch == "\n":
            out.append("".join(cur))
            cur = []
    if cur:
        out.append("".join(cur))
    return out


def parse_frontmatter(text: str) -> tuple[str, str] | None:
    """Compiler::parse_frontmatter.

    Under YAML 1.2 closing document markers cannot be indented, so the scan
    matches only unindented `---` / `...` at end of line.
    """
    if text.startswith("\ufeff"):
        text = text[1:]
    if not text.startswith("---"):
        return None
    rest = text[3:]
    first_nl = rest.find("\n")
    if first_nl == -1:
        return None
    if rest[:first_nl].rstrip("\r\n").strip() != "":
        return None
    search_start = 3 + first_nl + 1
    offset = 0
    for line in split_on_lf(text[search_start:]):
        if line.rstrip("\r\n") in ("---", "..."):
            closing_end = search_start + offset + len(line)
            return text[:closing_end].rstrip("\r\n"), text[closing_end:].lstrip("\r\n")
        offset += len(line)
    return None


def is_actionable(text: str) -> bool:
    """Compiler::is_actionable."""
    t = text.strip()
    if blen(t) < 6:
        return False
    if t.startswith("**") or t.startswith("`") or t.startswith("["):
        return True
    if t and t[0].isupper():   # Rust: first.is_uppercase() (per-char property)
        return True
    return bool(ACTION_VERB_RE.match(t))


def is_type_declaration_line(line: str) -> bool:
    return bool(TYPE_DECL_RE.search(line) or PY_CONTRACT_RE.search(line))


def is_typed_code_lang(info: str) -> bool:
    """Fences in these languages have meaningful inline annotations.

    YAML, Docker, Bash and SQL fences are never type-erased: their
    `key: value` pairs and DDL columns are schema/content, not ApiContract.
    """
    lang = re.split(r"[^A-Za-z0-9+#]", info)[0].lower() if info else ""
    return lang in TYPED_LANGS


def fence_lang(info_line: str) -> str:
    m = FENCE_INFO_RE.search(info_line)
    return m.group(1).lower() if m else ""


def erase_type_annotations(line: str) -> str:
    """Compiler::erase_type_annotations -- structural type erasure.

    `f(x: T): R {` -> `f(x) {`; `v as T` -> `v`; `def f(x: T) -> R:` ->
    `def f(x):`. Comment-only lines are never touched. `name: Type` erasure is
    scoped to signature-shaped lines so object literals, zod schemas and call
    sites pass through byte-identical.
    """
    trimmed = line.lstrip()
    if trimmed.startswith(("//", "#", "/*", "*")):
        return line
    out = line
    if " as " in out:
        out = AS_CAST_RE.sub("", out)
    if SIG_LINE_RE.search(out):
        if ":" in out and "(" in out:
            for _ in range(3):
                nxt = PARAM_ANNOT_RE.sub(r"\1", out)
                if nxt == out:
                    break
                out = nxt
        if ")" in out and ":" in out:
            out = RETURN_ANNOT_RE.sub(r")\1", out)
        if "->" in out:
            out = PY_RETURN_ANNOT_RE.sub(r"\1", out)
    if "(" not in out and ")" not in out:
        m = TYPED_PROP_RE.match(out)
        if m:
            out = f"{m.group(1)}{m.group(2) or ''}"
    return out


def compact_code_block(fence_lines: list[str], max_body_lines: int) -> list[str]:
    """Compiler::compact_code_block."""
    if len(fence_lines) <= max_body_lines + 2 or max_body_lines == 0:
        return list(fence_lines)
    header, footer = fence_lines[0], fence_lines[-1]
    compact_body = [l for l in fence_lines[1:-1] if l.strip()]
    if len(compact_body) <= max_body_lines:
        return [header, *compact_body, footer]
    head_count = max(max_body_lines - 3, 0)
    res = [header]
    res.extend(compact_body[:head_count])
    res.append("  # ... [syntax pattern continues] ...")
    res.extend(compact_body[len(compact_body) - 2:])
    res.append(footer)
    return res


def compile_skill(skill_md: str, opts: CompilationOptions) -> tuple[str, dict]:
    """Compiler::compile."""
    parsed = parse_frontmatter(skill_md)
    if parsed:
        # Mirrors Rust: the block is kept only when keep_frontmatter is set,
        # but the body is stripped either way.
        frontmatter_opt = parsed[0] if opts.keep_frontmatter else None
        raw_text = parsed[1]
    else:
        frontmatter_opt, raw_text = None, skill_md

    out_lines: list[str] = []
    seen: set[str] = set()
    in_fence = False
    fence_buffer: list[str] = []
    fence_typed = False
    in_skip_section = False
    current_section_level = 0
    pending_heading: str | None = None
    retained_components: list[str] = []
    saw_type_contract = False

    for line in raw_text.split("\n"):
        # 1. code fences
        if FENCE_RE.search(line):
            if not in_fence:
                in_fence = True
                fence_typed = is_typed_code_lang(fence_lang(line))
                fence_buffer = [line]
            else:
                in_fence = False
                fence_buffer.append(line)
                if (not in_skip_section and opts.keep_examples
                        and opts.max_code_lines > 0):
                    compact = compact_code_block(fence_buffer, opts.max_code_lines)
                    if pending_heading is not None:
                        out_lines.append(pending_heading)
                        pending_heading = None
                    out_lines.extend(compact)
                    out_lines.append("")
                    if "Example" not in retained_components:
                        retained_components.append("Example")
                fence_buffer.clear()
                fence_typed = False
            continue

        if in_fence:
            if not opts.keep_types:
                # A4: drop named contract declarations outright.
                if is_type_declaration_line(line):
                    saw_type_contract = True
                    continue
                if fence_typed:
                    erased = erase_type_annotations(line)
                    if erased != line:
                        saw_type_contract = True
                    if not erased.strip() and line.strip():
                        continue
                    fence_buffer.append(erased)
                    continue
            else:
                # keep_types: flag only. The line falls through and is KEPT --
                # dropping here is a silent data-loss bug.
                if is_type_declaration_line(line):
                    saw_type_contract = True
                elif fence_typed and erase_type_annotations(line) != line:
                    saw_type_contract = True
            fence_buffer.append(line)
            continue

        # 2. headings
        m = HEADING_RE.match(line)
        if m:
            level = len(m.group(1))
            title = m.group(2).strip()
            norm_title = title.lower().rstrip(":")

            if norm_title in SKIP_SECTIONS and not opts.keep_narrative:
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

        if is_type_declaration_line(line):
            saw_type_contract = True
            if not opts.keep_types:
                continue

        # 3. tables
        if TABLE_ROW_RE.search(line):
            if opts.keep_tables:
                if pending_heading is not None:
                    out_lines.append(pending_heading)
                    pending_heading = None
                out_lines.append(line)
                if "Table" not in retained_components:
                    retained_components.append("Table")
            continue

        # 4. list items
        m = BULLET_RE.match(line) or NUMBERED_RE.match(line)
        if m:
            content = m.group(1).strip()
            if not is_actionable(content):
                continue
            norm_key = content.lower()[:60]
            if norm_key in seen:
                continue
            seen.add(norm_key)
            if pending_heading is not None:
                out_lines.append(pending_heading)
                pending_heading = None
            out_lines.append(f"- {content}")
            if "Policy" not in retained_components:
                retained_components.append("Policy")
            continue

        # 5. bold definition lines
        m = BOLD_LINE_RE.match(line)
        if m:
            label = m.group(1).strip().rstrip(":")
            rest = m.group(2).strip()
            norm_key = label.lower()
            if norm_key in seen:
                continue
            seen.add(norm_key)
            if pending_heading is not None:
                out_lines.append(pending_heading)
                pending_heading = None
            out_lines.append(f"**{label}**" if not rest else f"**{label}:** {rest}")
            if "Invariant" not in retained_components:
                retained_components.append("Invariant")
            continue

    # 6. assemble, collapsing repeated blank lines
    final_lines: list[str] = []
    if frontmatter_opt is not None:
        final_lines.append(frontmatter_opt.replace("\r\n", "\n"))
        final_lines.append("")
    if opts.header_directive:
        final_lines.append(opts.header_directive)
        final_lines.append("")

    prev_blank = False
    for l in out_lines:
        if not l.strip():
            if not prev_blank:
                final_lines.append("")
                prev_blank = True
        else:
            final_lines.append(l)
            prev_blank = False

    compiled_text = "\n".join(final_lines).strip() + "\n"
    if opts.keep_types and saw_type_contract and "ApiContract" not in retained_components:
        retained_components.append("ApiContract")

    original_chars = blen(skill_md)
    original_tokens = max(original_chars, 1) // 4
    compiled_chars = blen(compiled_text)
    compiled_tokens = max(compiled_chars, 1) // 4
    reduction = (
        (original_tokens - compiled_tokens) / original_tokens * 100.0
        if original_tokens > 0 else 0.0
    )
    return compiled_text, {
        "original_chars": original_chars,
        "original_estimated_tokens": original_tokens,
        "compiled_chars": compiled_chars,
        "compiled_estimated_tokens": compiled_tokens,
        "token_reduction_percentage": reduction,
        "retained_components": retained_components,
    }


# --- batch drivers -------------------------------------------------------
def resolve_skill_path(skill_name: str, skills_root: Path) -> Path:
    """Direct `skills/<name>/SKILL.md` first, else walk for a matching parent."""
    direct = skills_root / skill_name / "SKILL.md"
    if direct.exists():
        return direct
    for p in skills_root.rglob("SKILL.md"):
        if p.parent.name == skill_name:
            return p
    raise FileNotFoundError(f"{skill_name}: source not found in {skills_root}/")


def utc_timestamp() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def from_tasks(tasks_path: Path, out_dir: Path, skills_root: Path | None = None) -> dict:
    skills_root = skills_root or (REPO / "skills")
    tasks = json.loads(tasks_path.read_text(encoding="utf-8"))
    out_dir.mkdir(parents=True, exist_ok=True)

    entries: dict[str, dict] = {}
    total_orig = total_comp = 0
    seen: set[str] = set()

    for t in tasks:
        skill = t.get("skill") or ""
        if not skill or skill in seen:
            continue
        seen.add(skill)
        try:
            src = resolve_skill_path(skill, skills_root)
        except FileNotFoundError as exc:
            print(f"❌ {exc}", file=sys.stderr)
            continue

        content = src.read_text(encoding="utf-8")
        task_domain = (t.get("domain") or "").lower()
        domain = TASK_DOMAIN_TO_DOMAIN.get(task_domain, "general")
        opts = checklist_v2(domain)
        compiled, metrics = compile_skill(content, opts)

        out_file = out_dir / f"{skill}.txt"
        out_file.write_text(compiled, encoding="utf-8")

        total_orig += metrics["original_estimated_tokens"]
        total_comp += metrics["compiled_estimated_tokens"]
        try:
            rel_src = str(src.relative_to(skills_root.parent))
            rel_out = str(out_file.relative_to(skills_root.parent))
        except ValueError:
            rel_src, rel_out = str(src), str(out_file)
        entries[skill] = {
            "skill_id": skill,
            "source_path": rel_src,
            "source_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
            "compiled_path": rel_out,
            "compiled_sha256": hashlib.sha256(compiled.encode("utf-8")).hexdigest(),
            "metrics": metrics,
        }
        print(f"✅ {skill:<34} {metrics['original_chars']:>8}B -> "
              f"{metrics['compiled_chars']:>7}B  "
              f"{metrics['token_reduction_percentage']:>5.1f}%")

    agg = ((total_orig - total_comp) / total_orig * 100.0) if total_orig else 0.0
    manifest = {
        "compiler_version": COMPILER_VERSION,
        "timestamp_utc": utc_timestamp(),
        "total_skills": len(entries),
        "total_source_tokens": total_orig,
        "total_compiled_tokens": total_comp,
        "aggregate_token_reduction_pct": agg,
        "skills": {k: entries[k] for k in sorted(entries)},
    }
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"\nCompiled {len(entries)} skills into {out_dir}")
    print(f"Total token delta: {total_orig} -> {total_comp} ({agg:.1f}% reduction)")
    return manifest


ABLATIONS = [
    ("a0_full", lambda d: None),                 # passthrough of the raw source
    ("a1_v2_balanced", lambda d: checklist_v2(d)),
    ("a2_no_examples", lambda d: no_examples(d)),
    ("a3_no_tables", lambda d: no_tables(d)),
    ("a4_no_types", lambda d: no_types(d)),
    ("a5_v1_bullets", lambda d: checklist_v1()),
]


def ablate(input_path: Path, out_dir: Path, domain: str = "general") -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    content = input_path.read_text(encoding="utf-8")
    name = input_path.parent.name
    written = []
    for suffix, make_opts in ABLATIONS:
        opts = make_opts(domain)
        target = out_dir / f"{name}_{suffix}.md"
        if opts is None:
            text = content
        else:
            text, _ = compile_skill(content, opts)
        target.write_text(text, encoding="utf-8")
        written.append(target)
    print(f"Generated {len(written)} ablation variants (A0-A5) for {name} in {out_dir}")
    return written


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="skills-compiler", description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)

    c = sub.add_parser("compile", help="Compile a single SKILL.md")
    c.add_argument("-i", "--input", required=True, type=Path)
    c.add_argument("-o", "--output", type=Path)
    c.add_argument("-d", "--domain", default="general")
    c.add_argument("--no-examples", action="store_true")
    c.add_argument("--no-types", action="store_true")
    c.add_argument("--no-tables", action="store_true")
    c.add_argument("--max-code-lines", type=int)
    c.add_argument("--keep-frontmatter", action="store_true")

    f = sub.add_parser("from-tasks", help="Batch compile from a tasks JSON")
    f.add_argument("-t", "--tasks", type=Path, default=REPO / "benchmarks/tasks_ieee.json")
    f.add_argument("-o", "--out-dir", type=Path, default=REPO / "benchmarks/checklists_v2")

    a = sub.add_parser("ablate", help="Generate the A0-A5 ablation series")
    a.add_argument("-i", "--input", required=True, type=Path)
    a.add_argument("-o", "--out-dir", required=True, type=Path)
    a.add_argument("-d", "--domain", default="general")

    args = p.parse_args(argv)

    if args.command == "compile":
        content = args.input.read_text(encoding="utf-8")
        opts = checklist_v2(args.domain)
        if args.no_examples:
            opts = replace(opts, keep_examples=False)
        if args.no_types:
            opts = replace(opts, keep_types=False)
        if args.no_tables:
            opts = replace(opts, keep_tables=False)
        if args.max_code_lines is not None:
            opts = replace(opts, max_code_lines=args.max_code_lines)
        if args.keep_frontmatter:
            opts = replace(opts, keep_frontmatter=True)
        compiled, metrics = compile_skill(content, opts)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(compiled, encoding="utf-8")
            print(f"Compiled {args.input} -> {args.output} "
                  f"(Tokens: {metrics['original_estimated_tokens']} -> "
                  f"{metrics['compiled_estimated_tokens']}, "
                  f"Reduction: {metrics['token_reduction_percentage']:.1f}%)")
        else:
            sys.stdout.write(compiled)
        return 0

    if args.command == "from-tasks":
        from_tasks(args.tasks, args.out_dir)
        return 0

    if args.command == "ablate":
        ablate(args.input, args.out_dir, args.domain)
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())