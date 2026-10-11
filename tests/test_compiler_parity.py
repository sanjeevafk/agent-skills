"""Compiler parity tests -- direct port of the 24 unit tests that guarded
`crates/skills-compiler` before the Python port (Phase 1.6 of
PYTHON_PORT_PLAN.md).

These are NOT generic unit tests. Each one pins a byte-level behaviour that
the recorded artifacts in `benchmarks/checklists_v2/` and
`benchmarks/ablations/` depend on. The A4 cases in particular pin the type
eraser's *known gaps* on purpose: if one is ever "fixed", these tests must
fail so the change is reviewed against §8.4 rather than silently altering a
published ablation artifact.
"""

from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import skills_compiler as sc  # noqa: E402


def v2_opts() -> sc.CompilationOptions:
    return sc.checklist_v2("general")


def no_types_opts() -> sc.CompilationOptions:
    return sc.no_types("general")


def compile_md(md: str, opts: sc.CompilationOptions | None = None):
    return sc.compile_skill(md, opts or v2_opts())


# --- v2 baseline ---------------------------------------------------------
def test_v2_keeps_examples_tables_and_types():
    md = (
        "## Rules\n\n- Always validate input\n\n```typescript\n"
        "interface Config {\n  retries: number;\n}\n"
        "function f(x: string): number {\n  return x.length;\n}\n```\n\n"
        "| Param | Type |\n| --- | --- |\n| x | string |\n"
    )
    out, metrics = compile_md(md)
    assert "function f(x: string): number" in out, f"v2 must keep annotations:\n{out}"
    assert "| Param | Type |" in out, f"v2 must keep tables:\n{out}"
    assert "interface Config" in out, f"v2 must keep declarations:\n{out}"
    assert "ApiContract" in metrics["retained_components"]


# --- A4 type erasure (keep_types=false) ----------------------------------
def test_a4_erases_ts_annotations_but_keeps_structure():
    md = (
        "## Rules\n\n- Always validate input\n\n```typescript\n"
        "function validateFileUpload(file: File) {\n  return check(file);\n}\n```\n"
    )
    out, _ = compile_md(md, no_types_opts())
    assert "function validateFileUpload(file)" in out, f"params erased:\n{out}"
    assert "file: File" not in out, f"annotation removed:\n{out}"
    assert "return check(file);" in out, f"body kept:\n{out}"


def test_a4_drops_interface_declarations():
    md = (
        "## Rules\n\n- Always validate input\n\n```typescript\n"
        "interface Config {\n  retries: number;\n}\nconst x = 1;\n```\n"
    )
    out, _ = compile_md(md, no_types_opts())
    assert "interface Config" not in out, f"declaration dropped:\n{out}"
    assert "const x = 1;" in out, f"impl kept:\n{out}"


def test_a4_erases_python_annotations_and_returns():
    md = (
        "## Rules\n\n- Always validate input\n\n```python\n"
        "def handler(event: dict) -> bool:\n    return True\n```\n"
    )
    out, _ = compile_md(md, no_types_opts())
    assert "def handler(event):" in out, f"py signature erased:\n{out}"
    assert "-> bool" not in out, f"py return erased:\n{out}"


def test_a4_drops_python_protocol_declarations():
    md = (
        "## Rules\n\n- Always validate input\n\n```python\n"
        "class Store(Protocol):\n    def get(self, key: str) -> str:\n        ...\n```\n"
    )
    out, _ = compile_md(md, no_types_opts())
    assert "class Store(Protocol)" not in out, f"protocol dropped:\n{out}"


def test_a4_erases_type_predicate_return_annotations():
    md = (
        "## Rules\n\n- Always validate input\n\n```typescript\n"
        "function isT(x: unknown): x is T { return true; }\n```\n"
    )
    out, _ = compile_md(md, no_types_opts())
    assert "function isT(x) { return true; }" in out, f"type predicate erased:\n{out}"
    assert "x is T" not in out, f"predicate form removed:\n{out}"


def test_a4_never_touches_switch_case_labels():
    # Regression guard: `case 1:` must not be mistaken for a typed property.
    md = (
        "## Rules\n\n- Always validate input\n\n```typescript\n"
        "function f(x: number) {\n  switch (x) {\n"
        '    case 1: return "a";\n    default: return "b";\n  }\n}\n```\n'
    )
    out, _ = compile_md(md, no_types_opts())
    assert 'case 1: return "a";' in out, f"case label intact:\n{out}"
    assert 'default: return "b";' in out, f"default label intact:\n{out}"
    assert "x: number" not in out, f"fn param still erased:\n{out}"


# --- Known limitations, characterised deliberately ------------------------
# These pin CURRENT behaviour so the gaps stay explicit and any future fix
# surfaces as a failure to be reviewed on purpose rather than silently
# changing the recorded A4 ablation artifacts. Their practical impact is
# bounded: across the 18 evaluated skills the realised A4 magnitude is 0.9%
# (security-review) and 0.0% elsewhere, so they do not materially affect
# §8.4. See benchmarks/COMPILER_PROVENANCE.md ("Known limitations").

def test_a4_known_gap_optional_param_annotation_survives():
    md = (
        "## Rules\n\n- Always validate input\n\n```typescript\n"
        "function g(a: string, b?: number): Promise<void> {}\n```\n"
    )
    out, _ = compile_md(md, no_types_opts())
    assert "b?: number" in out, f"KNOWN GAP: optional-param not erased:\n{out}"
    assert "g(a," in out, f"required param still erased:\n{out}"


def test_a4_known_gap_variable_annotation_survives():
    md = "## Rules\n\n- Always validate input\n\n```typescript\nconst arr: string[] = [];\n```\n"
    out, _ = compile_md(md, no_types_opts())
    assert "arr: string[]" in out, f"KNOWN GAP: variable annotation not erased:\n{out}"


def test_a4_known_gap_generic_call_type_arguments_survive():
    md = (
        "## Rules\n\n- Always validate input\n\n```typescript\n"
        "const m = new Map<string, number>();\n```\n"
    )
    out, _ = compile_md(md, no_types_opts())
    assert "Map<string, number>" in out, f"KNOWN GAP: generic call args not erased:\n{out}"


# --- A4 must not over-erasure -------------------------------------------
def test_a4_keeps_conceptual_interface_prose():
    md = (
        "## Workflow\n\n- Design interfaces for testability\n"
        "- Confirm with user what interface changes are needed\n"
    )
    out, _ = compile_md(md, no_types_opts())
    assert "Design interfaces for testability" in out, f"conceptual prose kept:\n{out}"


def test_a4_never_touches_yaml_values_or_sql_ddl():
    md = (
        "## Rules\n\n- Pin base images\n\n```yaml\nservices:\n  web:\n"
        '    ports:\n      - "8080:3000"\n```\n\n```sql\n'
        "CREATE TABLE t (id BIGINT PRIMARY KEY);\n```\n"
    )
    out, _ = compile_md(md, no_types_opts())
    assert '"8080:3000"' in out, f"yaml values kept:\n{out}"
    assert "BIGINT" in out, f"sql ddl kept:\n{out}"


def test_a4_never_touches_string_literals_or_arrows():
    md = (
        "## Rules\n\n- Always validate input\n\n```typescript\n"
        'const msg = "ratio 16:9 ok";\nconst f = (x) => x + 1;\n```\n'
    )
    out, _ = compile_md(md, no_types_opts())
    assert '"ratio 16:9 ok"' in out, f"string literal kept:\n{out}"
    assert "(x) => x + 1;" in out, f"arrow kept:\n{out}"


def test_a4_never_touches_comments_or_call_sites():
    md = (
        "## Rules\n\n- Always validate input\n\n```typescript\n"
        "// FAIL: WRONG: localStorage (vulnerable to XSS)\n"
        "await db.users.delete({ where: { id: userId } })\n"
        "const schema = z.object({ email: z.string() });\n```\n"
    )
    out, _ = compile_md(md, no_types_opts())
    assert "// FAIL: WRONG: localStorage (vulnerable to XSS)" in out, f"comment kept:\n{out}"
    assert "{ where: { id: userId } }" in out, f"call-site literal kept:\n{out}"
    assert "email: z.string()" in out, f"schema line kept:\n{out}"


def test_a4_erases_const_arrow_params():
    md = (
        "## Rules\n\n- Always validate input\n\n```typescript\n"
        "const f = (x: string): number => x.length;\n```\n"
    )
    out, _ = compile_md(md, no_types_opts())
    assert "const f = (x) => x.length;" in out, f"arrow sig erased:\n{out}"


# --- other ablation modes ------------------------------------------------
def test_no_examples_strips_fences_but_keeps_rules():
    md = "## Rules\n\n- Always validate input\n\n```python\nx: int = 1\n```\n"
    out, _ = compile_md(md, replace(v2_opts(), keep_examples=False))
    assert "x: int" not in out, f"fence stripped:\n{out}"
    assert "Always validate input" in out, f"rule kept:\n{out}"


def test_no_tables_strips_pipe_rows():
    md = "## Rules\n\n- Always validate input\n\n| A | B |\n| --- | --- |\n| 1 | 2 |\n"
    out, _ = compile_md(md, replace(v2_opts(), keep_tables=False))
    assert "| A | B |" not in out, f"table stripped:\n{out}"
    assert "Always validate input" in out, f"rule kept:\n{out}"


# --- language detection --------------------------------------------------
def test_typed_lang_detection():
    assert sc.is_typed_code_lang("typescript")
    assert sc.is_typed_code_lang("TS")
    assert sc.is_typed_code_lang("python")
    assert sc.is_typed_code_lang("py")
    assert not sc.is_typed_code_lang("yaml")
    assert not sc.is_typed_code_lang("dockerfile")
    assert not sc.is_typed_code_lang("bash")
    assert not sc.is_typed_code_lang("sql")
    assert not sc.is_typed_code_lang("")


# --- frontmatter ---------------------------------------------------------
def test_keep_frontmatter_preserves_yaml_header():
    md = "---\nname: my-skill\ndescription: A test skill\n---\n\n## Rules\n\n- Do the thing\n"
    out, _ = compile_md(md, replace(v2_opts(), keep_frontmatter=True))
    assert out.startswith("---\nname: my-skill\ndescription: A test skill\n---"), (
        f"frontmatter preserved:\n{out}"
    )
    assert "Do the thing" in out, f"rule kept:\n{out}"


def test_frontmatter_with_embedded_triple_dash_in_value():
    md = (
        "---\nname: complex-skill\n"
        'description: "Handles foo --- bar correctly"\n---\n\n'
        "## Rules\n\n- Always test edge cases\n"
    )
    out, _ = compile_md(md, replace(v2_opts(), keep_frontmatter=True))
    assert out.startswith(
        "---\nname: complex-skill\ndescription: \"Handles foo --- bar correctly\"\n---"
    ), f"embedded --- preserved:\n{out}"
    assert "Always test edge cases" in out, f"rule kept:\n{out}"


def test_frontmatter_with_crlf_normalized():
    md = (
        "---\r\nname: crlf-skill\r\ndescription: Windows line endings\r\n---\r\n\r\n"
        "## Rules\r\n\r\n- Validate line endings\r\n"
    )
    out, _ = compile_md(md, replace(v2_opts(), keep_frontmatter=True))
    assert "\r\n" not in out, "CRLF normalized to LF"
    assert out.startswith(
        "---\nname: crlf-skill\ndescription: Windows line endings\n---"
    ), f"frontmatter clean:\n{out}"
    assert "Validate line endings" in out, f"rule kept:\n{out}"


def test_no_frontmatter_with_table_not_corrupted():
    md = "# Title\n\n| Col A | Col B |\n| --- | --- |\n| Val 1 | Val 2 |\n\n- Some bullet\n"
    out, _ = compile_md(md)
    assert "| Col A | Col B |" in out, f"table header kept:\n{out}"
    assert "| --- | --- |" in out, f"table divider kept:\n{out}"
    assert "Some bullet" in out, f"bullet kept:\n{out}"


def test_frontmatter_indented_delimiter_not_closing():
    md = (
        "---\nname: indented-test\nnotes: |\n  Some block scalar\n"
        "  ---\n  still in frontmatter\n---\n\n## Rules\n\n- Keep going\n"
    )
    out, _ = compile_md(md, replace(v2_opts(), keep_frontmatter=True))
    assert out.startswith(
        "---\nname: indented-test\nnotes: |\n  Some block scalar\n"
        "  ---\n  still in frontmatter\n---"
    ), f"indented --- does not close frontmatter:\n{out}"
    assert "Keep going" in out, f"rule kept:\n{out}"


def test_frontmatter_with_utf8_bom():
    md = (
        "\ufeff---\nname: bom-skill\ndescription: UTF-8 BOM test\n---\n\n"
        "## Rules\n\n- Handle BOM\n"
    )
    out, _ = compile_md(md, replace(v2_opts(), keep_frontmatter=True))
    assert out.startswith(
        "---\nname: bom-skill\ndescription: UTF-8 BOM test\n---"
    ), f"BOM stripped and frontmatter preserved:\n{out}"
    assert "Handle BOM" in out, f"rule kept:\n{out}"


# --- port-specific: the trap that cost 240 silent bytes ------------------
def test_keep_types_does_not_drop_declarations_in_fences():
    """Regression guard for the port.

    With keep_types=true a type-declaration line is *flagged* and then falls
    through to be kept. The first port `continue`d unconditionally, which
    deleted `interface`/`type` declarations from v2 output -- a 240-byte
    silent divergence that only surfaced under diffing, not byte counts.
    """
    md = (
        "## Rules\n\n- Always validate input\n\n```typescript\n"
        "interface AdminUser { name: string; role: 'admin'; permissions: string[] }\n"
        "type ReadonlyAdminUser = Readonly<AdminUser>;\n```\n"
    )
    out, metrics = compile_md(md)
    assert "interface AdminUser" in out, f"declaration kept under v2:\n{out}"
    assert "type ReadonlyAdminUser = Readonly<AdminUser>;" in out, f"alias kept:\n{out}"
    assert "ApiContract" in metrics["retained_components"]


def test_domain_code_line_budgets_match_the_rust_enum():
    """`--domain database` is 16 code lines, not the 14 fallback.

    The first port keyed its budget table by *task string* while the CLI
    accepts *Domain enum names*, so `--domain database` silently fell through
    to General and truncated code blocks.
    """
    for domain, lines in [("general", 14), ("architecture", 14), ("database", 16),
                          ("devops", 14), ("sre", 14), ("security", 12),
                          ("testing", 18)]:
        assert sc.checklist_v2(domain).max_code_lines == lines, domain


def test_task_domain_strings_all_resolve_to_known_domains():
    """Every domain string in the real benchmark file maps to a valid Domain.

    The previous version of this test ended with
    `TASK_DOMAIN_TO_DOMAIN.get("something else", "general") == "general"`,
    which only asserted that `dict.get` returns its default -- it could not
    fail. The property that actually matters is that no typo in the table
    silently routes a real task to a wrong (or unknown) domain, which is what
    truncated code blocks during the port.
    """
    import json
    from pathlib import Path

    tasks = json.loads(
        (Path(__file__).resolve().parents[1] / "benchmarks/tasks_ieee.json")
        .read_text(encoding="utf-8")
    )
    used = {(t.get("domain") or "").lower() for t in tasks if t.get("skill")}
    unknown = sorted(
        d for d in used
        if sc.TASK_DOMAIN_TO_DOMAIN.get(d, "general") not in sc.DOMAIN_DEFAULT_CODE_LINES
    )
    assert not unknown, f"task domains resolving to an unknown Domain: {unknown}"