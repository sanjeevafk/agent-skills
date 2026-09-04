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
    action_verb_re: Regex,
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
            action_verb_re: Regex::new(r"(?i)^(use|avoid|never|always|set|add|run|enable|disable|keep|prefer|check|ensure|require|pin|scope|limit|wrap|store|mount|define|quote|index|batch|validate|verify|reject|fail|retry|cache|mask|exclude|include)\b").unwrap(),
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
        let mut in_skip_section = false;
        let mut current_section_level = 0;
        let mut pending_heading: Option<String> = None;
        let mut retained_components = Vec::new();

        for line in lines {
            // 1. Handle code fences
            if self.fence_re.is_match(line) {
                if !in_fence {
                    in_fence = true;
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
                }
                continue;
            }

            if in_fence {
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
