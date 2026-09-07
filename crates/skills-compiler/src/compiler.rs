use std::collections::HashSet;
use regex::Regex;
use serde::{Deserialize, Serialize};
use crate::domain::Domain;
use crate::taxonomy::InformationComponent;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CompilationOptions {
    pub domain: Domain,
    pub keep_narrative: bool,
    pub keep_examples: bool,
    pub keep_types: bool,
    pub keep_tables: bool,
    pub keep_invariants: bool,
    pub max_code_lines: usize,
    pub header_directive: Option<String>,
}

impl Default for CompilationOptions {
    fn default() -> Self {
        Self {
            domain: Domain::General,
            keep_narrative: false, // Default: strip conversational fluff
            keep_examples: true,   // Default v2: preserve code syntax
            keep_types: true,      // Default v2: preserve type contracts
            keep_tables: true,     // Default v2: preserve schema tables
            keep_invariants: true, // Default v2: preserve invariants
            max_code_lines: 14,
            header_directive: Some("[ENGINEERING IMPLEMENTATION STANDARDS & ARCHITECTURAL CONSTRAINTS]".to_string()),
        }
    }
}

impl CompilationOptions {
    pub fn for_domain(domain: Domain) -> Self {
        let mut opts = Self::default();
        opts.domain = domain;
        opts.max_code_lines = domain.default_code_lines();
        opts
    }

    /// Macro-Ablation: checklist_v1 (Aggressive bulletization - strips code, types, tables)
    pub fn checklist_v1() -> Self {
        Self {
            domain: Domain::General,
            keep_narrative: false,
            keep_examples: false,
            keep_types: false,
            keep_tables: false,
            keep_invariants: true,
            max_code_lines: 0,
            header_directive: Some("[CHECKLIST GUIDELINES]".to_string()),
        }
    }

    /// Macro-Ablation: checklist_v2 (Balanced structure-preserving static compilation)
    pub fn checklist_v2(domain: Domain) -> Self {
        Self::for_domain(domain)
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CompilationMetrics {
    pub original_chars: usize,
    pub original_estimated_tokens: usize,
    pub compiled_chars: usize,
    pub compiled_estimated_tokens: usize,
    pub token_reduction_percentage: f64,
    pub retained_components: Vec<InformationComponent>,
}

pub struct Compiler {
    heading_re: Regex,
    bullet_re: Regex,
    numbered_re: Regex,
    bold_line_re: Regex,
    table_row_re: Regex,
    fence_re: Regex,
    fence_info_re: Regex,
    action_verb_re: Regex,
    // A4 (no-types) patterns: named contract declarations dropped entirely.
    type_decl_re: Regex,
    py_contract_re: Regex,
    // A4 inline type erasure (typed code fences only): annotations removed,
    // surrounding code structure preserved.
    as_cast_re: Regex,
    sig_line_re: Regex,
    param_annot_re: Regex,
    return_annot_re: Regex,
    py_return_annot_re: Regex,
    typed_prop_re: Regex,
    skip_sections: HashSet<&'static str>,
}

impl Compiler {
    pub fn new() -> Self {
        let mut skip_sections = HashSet::new();
        skip_sections.insert("when to activate");
        skip_sections.insert("when to use");
        skip_sections.insert("overview");
        skip_sections.insert("introduction");
        skip_sections.insert("prerequisites");
        skip_sections.insert("installation");
        skip_sections.insert("related skills");
        skip_sections.insert("table of contents");
        skip_sections.insert("origin");
        skip_sections.insert("metadata");
        skip_sections.insert("resources");
        skip_sections.insert("related tools");
        skip_sections.insert("recommended plugins");
        skip_sections.insert("further reading");
        skip_sections.insert("references");

        Self {
            heading_re: Regex::new(r"^(#{1,4})\s+(.*)").unwrap(),
            bullet_re: Regex::new(r"^\s*[-*•]\s+(.*)$").unwrap(),
            numbered_re: Regex::new(r"^\s*\d+[.)]\s+(.*)$").unwrap(),
            bold_line_re: Regex::new(r"^\s*\*\*([^*]+):?\*\*:?\s*(.*)$").unwrap(),
            table_row_re: Regex::new(r"^\s*\|(.+)\|\s*$").unwrap(),
            fence_re: Regex::new(r"^\s*(```|~~~)(.*)").unwrap(),
            fence_info_re: Regex::new(r"^\s*(?:```|~~~)\s*([A-Za-z0-9_+#-]+)").unwrap(),
            action_verb_re: Regex::new(r"(?i)^(use|avoid|never|always|set|add|run|enable|disable|keep|prefer|check|ensure|require|pin|scope|limit|wrap|store|mount|define|quote|index|batch|validate|verify|reject|fail|retry|cache|mask|exclude|include)\b").unwrap(),
            // Named type/interface contract declarations (TS + Python).
            type_decl_re: Regex::new(r"^\s*(export\s+(default\s+)?)?(interface\s+[A-Za-z_]\w*|type\s+[A-Za-z_]\w*\s*=|enum\s+[A-Za-z_]\w*|abstract\s+class\s+[A-Za-z_]\w*)").unwrap(),
            py_contract_re: Regex::new(r"^\s*class\s+[A-Za-z_]\w*\s*\([^)]*\b(Protocol|ABC|Generic|TypedDict)\b[^)]*\)\s*:?\s*$").unwrap(),
            // `x as Type` / `x as const` casts.
            as_cast_re: Regex::new(r"\s+as\s+(const\b|[A-Za-z_][\w<>\[\].]*)").unwrap(),
            // Signature-shaped lines only (declarators, not call sites):
            // `function f(`, `export async function f(`, arrow `const f = (`,
            // `def f(`, or a bare `name(` leader.
            sig_line_re: Regex::new(r"^\s*(export\s+)?(async\s+)?(function\s+[A-Za-z_]\w*|(const|let|var)\s+[A-Za-z_]\w*\s*=\s*(async\s*)?\(|def\s+[A-Za-z_]\w*|[A-Za-z_]\w*\s*\()").unwrap(),
            // `name: Type` annotations (params, variable annotations).
            param_annot_re: Regex::new(r"(\w)\s*:\s*[A-Za-z_][\w.<>\[\]]*(?:\s*\|\s*[A-Za-z_][\w.<>\[\]]*)*").unwrap(),
            // `): ReturnType {` / `): ReturnType =` (TS/JS). No look-ahead
            // in the regex crate: capture the terminator and re-emit it.
            return_annot_re: Regex::new(r"\)\s*:\s*[A-Za-z_][\w.<>\[\]| ]*?(\s*[{=;]|\s*$)").unwrap(),
            // `-> ReturnType:` (Python). Same terminator-capture trick.
            py_return_annot_re: Regex::new(r"\s*->\s*[A-Za-z_][\w.<>\[\]|, ]*?(\s*:)").unwrap(),
            // Standalone typed-property lines: `key: Type,` / `key: Type;` (object type literals).
            typed_prop_re: Regex::new(r"^(\s*(?:readonly\s+)?[A-Za-z_]\w*\??)\s*:\s*[A-Za-z_][\w.<>\[\]| ]*?\s*(;|,)?\s*$").unwrap(),
            skip_sections,
        }
    }

    pub fn strip_yaml_frontmatter<'a>(&self, text: &'a str) -> &'a str {
        if text.starts_with("---") {
            let parts: Vec<&str> = text.splitn(3, "---").collect();
            if parts.len() >= 3 {
                return parts[2].trim_start_matches(|c| c == '\r' || c == '\n');
            }
        }
        text
    }

    pub fn is_actionable(&self, text: &str) -> bool {
        let t = text.trim();
        if t.len() < 6 {
            return false;
        }
        if t.starts_with("**") || t.starts_with('`') || t.starts_with('[') {
            return true;
        }
        if let Some(first) = t.chars().next() {
            if first.is_uppercase() {
                return true;
            }
        }
        self.action_verb_re.is_match(t)
    }

    /// True when a line declares a named type/interface contract
    /// (TS `interface`/`type`/`enum`/`abstract class`, Python
    /// `Protocol`/`ABC`/`Generic`/`TypedDict` bases). Used by the A4
    /// (no-types) ablation: such lines are dropped entirely.
    pub fn is_type_declaration_line(&self, line: &str) -> bool {
        self.type_decl_re.is_match(line) || self.py_contract_re.is_match(line)
    }

    /// True for fenced code languages where inline type annotations are
    /// meaningful (TypeScript/JavaScript/Python families). YAML, Docker,
    /// Bash, and SQL fences are never type-erased: their `key: value`
    /// pairs and DDL column definitions are schema/content, not
    /// `ApiContract` annotations per the skill information taxonomy.
    pub fn is_typed_code_lang(info: &str) -> bool {
        let lang = info
            .split(|c: char| !c.is_alphanumeric() && c != '+' && c != '#')
            .next()
            .unwrap_or("")
            .to_lowercase();
        matches!(
            lang.as_str(),
            "typescript" | "ts" | "tsx" | "javascript" | "js" | "jsx" | "python" | "py"
        )
    }

    fn fence_lang(info_line: &str, info_re: &Regex) -> String {
        info_re
            .captures(info_line)
            .and_then(|c| c.get(1))
            .map(|m| m.as_str().to_lowercase())
            .unwrap_or_default()
    }

    /// Erase type annotations from a single code line while preserving
    /// executable structure ("type erasure"): `f(x: T): R {` becomes
    /// `f(x) {`, `v as T` becomes `v`, `def f(x: T) -> R:` becomes
    /// `def f(x):`. Comment-only lines are never touched. `name: Type`
    /// erasure applies only to signature-shaped lines so object literals
    /// (`{ where: { id: userId } }`), zod schemas, and call sites pass
    /// through byte-identical. Returns the original line when nothing matches.
    pub fn erase_type_annotations(&self, line: &str) -> String {
        let trimmed = line.trim_start();
        if trimmed.starts_with("//") || trimmed.starts_with('#') || trimmed.starts_with("/*") || trimmed.starts_with('*')
        {
            return line.to_string();
        }
        let mut out = line.to_string();
        // `x as Type` casts (any code line).
        if out.contains(" as ") {
            out = self.as_cast_re.replace_all(&out, "").to_string();
        }
        // Signature-scoped erasure.
        if self.sig_line_re.is_match(&out) {
            if out.contains(':') && out.contains('(') {
                for _ in 0..3 {
                    let next = self.param_annot_re.replace_all(&out, "$1").to_string();
                    if next == out {
                        break;
                    }
                    out = next;
                }
            }
            // Return-type annotations: `): R {` and `-> R:`.
            if out.contains(')') && out.contains(':') {
                out = self.return_annot_re.replace(&out, ")${1}").to_string();
            }
            if out.contains("->") {
                out = self.py_return_annot_re.replace(&out, "$1").to_string();
            }
        }
        // Standalone typed-property lines without call syntax.
        if !out.contains('(') && !out.contains(')') {
            if let Some(caps) = self.typed_prop_re.captures(&out.clone()) {
                let name = caps.get(1).map(|m| m.as_str()).unwrap_or("");
                let trailing = caps.get(2).map(|m| m.as_str()).unwrap_or("");
                out = format!("{}{}", name, trailing);
            }
        }
        out
    }

    pub fn compact_code_block(&self, fence_lines: &[String], max_body_lines: usize) -> Vec<String> {
        if fence_lines.len() <= max_body_lines + 2 || max_body_lines == 0 {
            return fence_lines.to_vec();
        }

        let header = &fence_lines[0];
        let footer = &fence_lines[fence_lines.len() - 1];
        let body = &fence_lines[1..fence_lines.len() - 1];

        let compact_body: Vec<&String> = body.iter().filter(|l| !l.trim().is_empty()).collect();
        if compact_body.len() <= max_body_lines {
            let mut res = vec![header.clone()];
            res.extend(compact_body.into_iter().cloned());
            res.push(footer.clone());
            return res;
        }

        let head_count = max_body_lines.saturating_sub(3);
        let mut res = vec![header.clone()];
        for l in compact_body.iter().take(head_count) {
            res.push((*l).clone());
        }
        res.push("  # ... [syntax pattern continues] ...".to_string());
        for l in compact_body.iter().skip(compact_body.len().saturating_sub(2)) {
            res.push((*l).clone());
        }
        res.push(footer.clone());
        res
    }

    pub fn compile(&self, skill_md: &str, opts: &CompilationOptions) -> (String, CompilationMetrics) {
        let raw_text = self.strip_yaml_frontmatter(skill_md);
        let lines: Vec<&str> = raw_text.lines().collect();

        let mut out_lines: Vec<String> = Vec::new();
        let mut seen: HashSet<String> = HashSet::new();
        let mut in_fence = false;
        let mut fence_buffer: Vec<String> = Vec::new();
        let mut fence_typed = false;
        let mut in_skip_section = false;
        let mut current_section_level = 0;
        let mut pending_heading: Option<String> = None;
        let mut retained_components = Vec::new();
        let mut saw_type_contract = false;

        for line in lines {
            // 1. Handle code fences
            if self.fence_re.is_match(line) {
                if !in_fence {
                    in_fence = true;
                    fence_typed =
                        Self::is_typed_code_lang(&Self::fence_lang(line, &self.fence_info_re));
                    fence_buffer = vec![line.to_string()];
                } else {
                    in_fence = false;
                    fence_buffer.push(line.to_string());
                    if !in_skip_section && opts.keep_examples && opts.max_code_lines > 0 {
                        let compact = self.compact_code_block(&fence_buffer, opts.max_code_lines);
                        if let Some(h) = pending_heading.take() {
                            out_lines.push(h);
                        }
                        out_lines.extend(compact);
                        out_lines.push(String::new());
                        if !retained_components.contains(&InformationComponent::Example) {
                            retained_components.push(InformationComponent::Example);
                        }
                    }
                    fence_buffer.clear();
                    fence_typed = false;
                }
                continue;
            }

            if in_fence {
                // A4 (no-types): drop named contract declarations; erase
                // inline annotations in typed-language fences only.
                if !opts.keep_types {
                    if self.is_type_declaration_line(line) {
                        saw_type_contract = true;
                        continue;
                    }
                    if fence_typed {
                        let erased = self.erase_type_annotations(line);
                        if erased != line {
                            saw_type_contract = true;
                        }
                        if erased.trim().is_empty() && !line.trim().is_empty() {
                            continue;
                        }
                        fence_buffer.push(erased);
                        continue;
                    }
                } else if self.is_type_declaration_line(line)
                    || (fence_typed && self.erase_type_annotations(line) != line)
                {
                    saw_type_contract = true;
                }
                fence_buffer.push(line.to_string());
                continue;
            }

            // 2. Handle Headings
            if let Some(caps) = self.heading_re.captures(line) {
                let level = caps[1].len();
                let title = caps[2].trim();
                let norm_title = title.to_lowercase().trim_end_matches(':').to_string();

                if self.skip_sections.contains(norm_title.as_str()) && !opts.keep_narrative {
                    in_skip_section = true;
                    current_section_level = level;
                    pending_heading = None;
                    continue;
                } else if in_skip_section && level <= current_section_level {
                    in_skip_section = false;
                }

                if in_skip_section {
                    continue;
                }

                if level == 1 {
                    pending_heading = None;
                    continue;
                }

                pending_heading = Some(format!("{} {}", "#".repeat(level), title));
                continue;
            }

            if in_skip_section {
                continue;
            }

            // 2b. A4 (no-types): drop named type/interface contract
            // declarations in prose. Conceptual mentions of the word
            // "interface" (e.g. "design interfaces for testability") do
            // NOT match the declaration patterns and are retained.
            if self.is_type_declaration_line(line) {
                saw_type_contract = true;
                if !opts.keep_types {
                    continue;
                }
            }

            // 3. Handle Tables
            if self.table_row_re.is_match(line) {
                if opts.keep_tables {
                    if let Some(h) = pending_heading.take() {
                        out_lines.push(h);
                    }
                    out_lines.push(line.to_string());
                    if !retained_components.contains(&InformationComponent::Table) {
                        retained_components.push(InformationComponent::Table);
                    }
                }
                continue;
            }

            // 4. Handle List Items
            if let Some(caps) = self.bullet_re.captures(line).or_else(|| self.numbered_re.captures(line)) {
                let content = caps[1].trim();
                if !self.is_actionable(content) {
                    continue;
                }
                let norm_key: String = content.to_lowercase().chars().take(60).collect();
                if seen.contains(&norm_key) {
                    continue;
                }
                seen.insert(norm_key);

                if let Some(h) = pending_heading.take() {
                    out_lines.push(h);
                }
                out_lines.push(format!("- {}", content));
                if !retained_components.contains(&InformationComponent::Policy) {
                    retained_components.push(InformationComponent::Policy);
                }
                continue;
            }

            // 5. Handle Bold Definition Lines
            if let Some(caps) = self.bold_line_re.captures(line) {
                let label = caps[1].trim().trim_end_matches(':');
                let rest = caps[2].trim();
                let norm_key = label.to_lowercase();
                if seen.contains(&norm_key) {
                    continue;
                }
                seen.insert(norm_key);

                if let Some(h) = pending_heading.take() {
                    out_lines.push(h);
                }
                if rest.is_empty() {
                    out_lines.push(format!("**{}**", label));
                } else {
                    out_lines.push(format!("**{}:** {}", label, rest));
                }
                if !retained_components.contains(&InformationComponent::Invariant) {
                    retained_components.push(InformationComponent::Invariant);
                }
                continue;
            }
        }

        // Clean redundant blank lines
        let mut final_lines: Vec<String> = Vec::new();
        if let Some(ref dir) = opts.header_directive {
            final_lines.push(dir.clone());
            final_lines.push(String::new());
        }

        let mut prev_blank = false;
        for l in out_lines {
            if l.trim().is_empty() {
                if !prev_blank {
                    final_lines.push(String::new());
                    prev_blank = true;
                }
            } else {
                final_lines.push(l);
                prev_blank = false;
            }
        }

        let compiled_text = final_lines.join("\n").trim().to_string() + "\n";
        if opts.keep_types
            && saw_type_contract
            && !retained_components.contains(&InformationComponent::ApiContract)
        {
            retained_components.push(InformationComponent::ApiContract);
        }
        let original_chars = skill_md.len();
        let original_tokens = original_chars.max(1) / 4;
        let compiled_chars = compiled_text.len();
        let compiled_tokens = compiled_chars.max(1) / 4;
        let reduction = if original_tokens > 0 {
            ((original_tokens as f64 - compiled_tokens as f64) / original_tokens as f64) * 100.0
        } else {
            0.0
        };

        let metrics = CompilationMetrics {
            original_chars,
            original_estimated_tokens: original_tokens,
            compiled_chars,
            compiled_estimated_tokens: compiled_tokens,
            token_reduction_percentage: reduction,
            retained_components,
        };

        (compiled_text, metrics)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::domain::Domain;

    fn compiler() -> Compiler {
        Compiler::new()
    }

    fn v2_opts() -> CompilationOptions {
        CompilationOptions::checklist_v2(Domain::General)
    }

    fn no_types_opts() -> CompilationOptions {
        let mut o = CompilationOptions::checklist_v2(Domain::General);
        o.keep_types = false;
        o
    }

    #[test]
    fn v2_keeps_examples_tables_and_types() {
        let md = "## Rules\n\n- Always validate input\n\n```typescript\ninterface Config {\n  retries: number;\n}\nfunction f(x: string): number {\n  return x.length;\n}\n```\n\n| Param | Type |\n| --- | --- |\n| x | string |\n";
        let (out, metrics) = compiler().compile(md, &v2_opts());
        assert!(out.contains("function f(x: string): number"), "v2 must keep annotations:\n{}", out);
        assert!(out.contains("| Param | Type |"), "v2 must keep tables:\n{}", out);
        assert!(out.contains("interface Config"), "v2 must keep declarations:\n{}", out);
        assert!(metrics.retained_components.contains(&InformationComponent::ApiContract));
    }

    #[test]
    fn a4_erases_ts_annotations_but_keeps_structure() {
        let md = "## Rules\n\n- Always validate input\n\n```typescript\nfunction validateFileUpload(file: File) {\n  return check(file);\n}\n```\n";
        let (out, _) = compiler().compile(md, &no_types_opts());
        assert!(out.contains("function validateFileUpload(file)"), "params erased:\n{}", out);
        assert!(!out.contains("file: File"), "annotation removed:\n{}", out);
        assert!(out.contains("return check(file);"), "body kept:\n{}", out);
    }

    #[test]
    fn a4_drops_interface_declarations() {
        let md = "## Rules\n\n- Always validate input\n\n```typescript\ninterface Config {\n  retries: number;\n}\nconst x = 1;\n```\n";
        let (out, _) = compiler().compile(md, &no_types_opts());
        assert!(!out.contains("interface Config"), "declaration dropped:\n{}", out);
        assert!(out.contains("const x = 1;"), "impl kept:\n{}", out);
    }

    #[test]
    fn a4_erases_python_annotations_and_returns() {
        let md = "## Rules\n\n- Always validate input\n\n```python\ndef handler(event: dict) -> bool:\n    return True\n```\n";
        let (out, _) = compiler().compile(md, &no_types_opts());
        assert!(out.contains("def handler(event):"), "py signature erased:\n{}", out);
        assert!(!out.contains("-> bool"), "py return erased:\n{}", out);
    }

    #[test]
    fn a4_drops_python_protocol_declarations() {
        let md = "## Rules\n\n- Always validate input\n\n```python\nclass Store(Protocol):\n    def get(self, key: str) -> str:\n        ...\n```\n";
        let (out, _) = compiler().compile(md, &no_types_opts());
        assert!(!out.contains("class Store(Protocol)"), "protocol dropped:\n{}", out);
    }

    #[test]
    fn a4_keeps_conceptual_interface_prose() {
        let md = "## Workflow\n\n- Design interfaces for testability\n- Confirm with user what interface changes are needed\n";
        let (out, _) = compiler().compile(md, &no_types_opts());
        assert!(out.contains("Design interfaces for testability"), "conceptual prose kept:\n{}", out);
    }

    #[test]
    fn a4_never_touches_yaml_values_or_sql_ddl() {
        let md = "## Rules\n\n- Pin base images\n\n```yaml\nservices:\n  web:\n    ports:\n      - \"8080:3000\"\n```\n\n```sql\nCREATE TABLE t (id BIGINT PRIMARY KEY);\n```\n";
        let (out, _) = compiler().compile(md, &no_types_opts());
        assert!(out.contains("\"8080:3000\""), "yaml values kept:\n{}", out);
        assert!(out.contains("BIGINT"), "sql ddl kept:\n{}", out);
    }

    #[test]
    fn a4_never_touches_string_literals_or_arrows() {
        let md = "## Rules\n\n- Always validate input\n\n```typescript\nconst msg = \"ratio 16:9 ok\";\nconst f = (x) => x + 1;\n```\n";
        let (out, _) = compiler().compile(md, &no_types_opts());
        assert!(out.contains("\"ratio 16:9 ok\""), "string literal kept:\n{}", out);
        assert!(out.contains("(x) => x + 1;"), "arrow kept:\n{}", out);
    }

    #[test]
    fn a4_never_touches_comments_or_call_sites() {
        let md = "## Rules\n\n- Always validate input\n\n```typescript\n// FAIL: WRONG: localStorage (vulnerable to XSS)\nawait db.users.delete({ where: { id: userId } })\nconst schema = z.object({ email: z.string() });\n```\n";
        let (out, _) = compiler().compile(md, &no_types_opts());
        assert!(out.contains("// FAIL: WRONG: localStorage (vulnerable to XSS)"), "comment kept:\n{}", out);
        assert!(out.contains("{ where: { id: userId } }"), "call-site literal kept:\n{}", out);
        assert!(out.contains("email: z.string()"), "schema line kept:\n{}", out);
    }

    #[test]
    fn a4_erases_const_arrow_params() {
        let md = "## Rules\n\n- Always validate input\n\n```typescript\nconst f = (x: string): number => x.length;\n```\n";
        let (out, _) = compiler().compile(md, &no_types_opts());
        assert!(out.contains("const f = (x) => x.length;"), "arrow sig erased:\n{}", out);
    }

    #[test]
    fn no_examples_strips_fences_but_keeps_rules() {
        let md = "## Rules\n\n- Always validate input\n\n```python\nx: int = 1\n```\n";
        let mut o = v2_opts();
        o.keep_examples = false;
        let (out, _) = compiler().compile(md, &o);
        assert!(!out.contains("x: int"), "fence stripped:\n{}", out);
        assert!(out.contains("Always validate input"), "rule kept:\n{}", out);
    }

    #[test]
    fn no_tables_strips_pipe_rows() {
        let md = "## Rules\n\n- Always validate input\n\n| A | B |\n| --- | --- |\n| 1 | 2 |\n";
        let mut o = v2_opts();
        o.keep_tables = false;
        let (out, _) = compiler().compile(md, &o);
        assert!(!out.contains("| A | B |"), "table stripped:\n{}", out);
        assert!(out.contains("Always validate input"), "rule kept:\n{}", out);
    }

    #[test]
    fn typed_lang_detection() {
        assert!(Compiler::is_typed_code_lang("typescript"));
        assert!(Compiler::is_typed_code_lang("TS"));
        assert!(Compiler::is_typed_code_lang("python"));
        assert!(Compiler::is_typed_code_lang("py"));
        assert!(!Compiler::is_typed_code_lang("yaml"));
        assert!(!Compiler::is_typed_code_lang("dockerfile"));
        assert!(!Compiler::is_typed_code_lang("bash"));
        assert!(!Compiler::is_typed_code_lang("sql"));
        assert!(!Compiler::is_typed_code_lang(""));
    }
}
