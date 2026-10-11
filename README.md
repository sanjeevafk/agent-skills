# Agent Skills Warehouse

A curated cold-storage warehouse and offline catalog of 2,700+ specialized agent skill suites across **Claude Code, Google Antigravity, OpenAI Codex, OpenCode, and Pi**, designed to prevent prompt bloat and context collapse in daily agent sessions.

---

## 1. What This Repository Is

To preserve frontier LLM attention and eliminate 20,000+ token per-turn overhead, the environment uses a strict two-tier architecture:

1. **Active Runtime Tier (`canonical/`, mirrored to `~/.agents/skills/`):** A minimal, hardened suite of ~75 production skills wired into active coding agents (<2,500 prompt tokens per turn).
2. **Cold-Storage Warehouse (`skills/` & `collections/`):** An offline repository housing **556 modular skills** across 9 core engineering domains and **2,200+ specialized domain playbooks** (cybersecurity MITRE/NIST, Hugging Face, bioinformatics, financial modeling, and reference architectures), bridged dynamically on-demand via `skill-router`.

---

## 2. Accompanying Research Paper

This repository also serves as the artifact and benchmark testbed for the empirical software engineering paper:

> **Compress the Prose, Keep the Syntax: What Agent Skill Files Actually Do, and Why You Probably Don't Need a Router**

### Core Empirical Findings

The study evaluated 396 blind trials across an 18-task engineering benchmark (Qwen 3.7 Flash generating, DeepSeek V4 Pro judging a 35-point rubric) plus 87 ablation runs:

- **Compressing Prose is Free; Deleting Syntax is Not:** Structure-preserving static compilation (`checklist_v2`) cuts **30.0% of prompt tokens** (saving 680 tokens per skill/turn) with no measurable quality penalty compared to uncompressed multi-thousand-token manuals (24.96/35 vs. 25.17/35, paired $p = 0.7672$).
- **Syntax-Stripping Context Collapse:** Aggressively stripping narrative prose in policy-centric domains (Security, Databases) is completely safe. However, removing executable code fixtures in syntax-dense tasks (e.g., TDD RED/GREEN tracer patterns) causes immediate collapse ($\Delta = -8.50$ points; 0 of 6 runs passing).
- **You Probably Don't Need a Router:** Testing selection across the 522-skill catalogue revealed that multi-stage neural routing (dense retrieval + cross-encoder reranker) is a net loss (5/17 Top-1) compared to a tuned lexical TF-IDF baseline (8/17 Top-1). Passing the entire 522-skill catalogue in context in a single prompt achieved **14/17 Top-1**, matching the union oracle ceiling. At this catalogue scale, an in-context pass outperforms neural retrieval pipelines.

---

## 3. Quick Commands

```bash
# Search skills by keyword
uv run python scripts/search_skills.py <keyword>

# Rebuild catalog index (skills.json)
uv run python scripts/build_index.py

# Validate SKILL.md frontmatter blocks
uv run python scripts/check_frontmatter.py

# Run compiler verification on benchmarks
uv run python scripts/verify_compiled_artifacts.py
```
