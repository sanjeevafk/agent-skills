# Agent Skills Framework

[![License](https://img.shields.io/github/license/sanjeevafk/agent-skills?style=flat-square)](https://github.com/sanjeevafk/agent-skills/blob/main/LICENSE)
![Agentic Engineering](https://img.shields.io/badge/Agentic-Engineering-1F8A70?style=flat-square)
![Skills Count](https://img.shields.io/badge/Skills-390-blue?style=flat-square)
![Rules Count](https://img.shields.io/badge/Rules-16-purple?style=flat-square)

A telemetry-driven, self-documenting AI capability framework. Manage, sync, and export skills, command namespaces, subagents, and 14 classic software engineering book standards across **Claude Code, Antigravity, Cursor, Windsurf, GitHub Copilot, and Codex**.

---

## Quick 1-Command Setup

Clone the repository and run the automated installer. The installer sets up PATH configuration, shell aliases (`gskills`), builds all command wrappers, indexes, dependency graphs, and automatically syncs skills across all installed AI agent runtimes (`~/.gemini`, `~/.agents`, `~/.cursor`, `~/.copilot`):

```bash
git clone https://github.com/sanjeevafk/agent-skills.git && cd agent-skills && ./scripts/install-global-skills.sh
```

After opening a new shell:

```bash
# Verify installation
skills status

# Run full framework build
skills build-all
```

---

## Architecture: Single Source of Truth

The repository enforces strict separation between **canonical sources of truth** and **auto-generated artifacts**:

```
agent-skills/
|
|-- skills/                 [CANONICAL] 390 Modular Capability Manuals
|-- rules/                  [CANONICAL] 16 Always-On Standards & 14 Book Guidelines
|
|-- commands/               [GENERATED] Namespaced & Flat Command Wrappers
|-- skills.json             [GENERATED] Complete Reverse-Indexed Metadata Registry
|-- exports/                [GENERATED] Multi-Client IDE Rules (.cursorrules, .agentrules, etc.)
`-- docs/                   [GENERATED] Catalog, Dependency Graphs & Analytics Dashboards
```

---

## Command Namespaces & Slash Commands

Every skill and rule automatically receives a namespaced slash command, flat command, and shorthand alias:

| Namespace | Example Commands | Target Capability |
| :--- | :--- | :--- |
| **`/debug/`** | `/debug/systematic`, `/debug/root-cause` | Root-cause isolation, test failure diagnosis |
| **`/web/`** | `/web/nextjs-15-expert`, `/web/supabase-expert` | Frontend, App Router, RLS, Tailwind & Radix UI |
| **`/lang/`** | `/lang/python-ts-interop-mcp-builder` | Language systems & multi-language interop |
| **`/style/`** | `/style/google-style-python`, `/style/google-ts` | Google Style Guides & NASA JPL coding rules |
| **`/gsd/`** | `/gsd/plan-phase`, `/gsd/execute-phase` | GSD milestone roadmap & phase planning |
| **`/devops/`** | `/devops/docker-patterns`, `/devops/vercel-deploy` | Containerization, deployment & CI/CD |
| **`/rule/`** | `/rule/clean-code`, `/rule/user-global-rules` | 14 Classic software books & `/learn` directives |

> **Backward Compatibility**: Flat commands (e.g. `/systematic-debugging`, `/nextjs-15-expert`) and shorthand aliases (`/google-ts`, `/noslop`, `/adhd`) remain 100% supported.

---

## What are the Files in `docs/` For?

The `docs/` folder contains both **auto-generated operational artifacts** and **core architecture policies**:

### Auto-Generated Reports & Dashboards (Derived via `gskills build-all`):
* **`docs/SKILLS_CATALOG.md`**: Complete, searchable directory of all 388 skills categorized by domain.
* **`docs/NAMESPACE_REFERENCE.md`**: Complete mapping matrix of namespaced commands to target skills and flat aliases.
* **`docs/DEPENDENCY_GRAPH.md`**: Prerequisite dependency resolution matrix and visual Mermaid graph.
* **`docs/HEALTH_DASHBOARD.md`**: System health metrics, token budget estimations, and category statistics.
* **`docs/DUPLICATE_REPORT.md`**: Similarity linter report identifying near-identical skills and alias conflicts.
* **`docs/TELEMETRY_REPORT.md`**: Usage metrics tracking invocation counts, success rates, and token usage.

### Core Architecture Policies (Hand-Curated):
* **`docs/ENGINEERING_PRINCIPLES.md`**: Core engineering philosophy and coding standards.
* **`docs/OPERATIONS.md`**: Operational guide for managing skills, syncing, and running builds.
* **`docs/SECURITY.md`**: Security architecture and Tirith guardrail configuration.

---

## Multi-Client Rule Exports

Export your entire skills collection and 14 book standards into single-file rulesets for any editor:

---

## Empirical Benchmarks & Delivery Experiments

The framework includes a comprehensive evaluation harness ([`benchmarks/`](file:///home/sanjeev/Downloads/agent-skills/benchmarks)) measuring both **tooling performance** and **LLM task execution quality**.

### 1. Skill Delivery Strategy Experiment (`delivery_report_latest.md`)

We evaluated 4 skill delivery strategies across hard engineering tasks (`security-review`, `debugging-code`, `tdd`):

| Strategy | Avg Quality Score (/35) | Win Count | Input Token Overhead | Latency |
| :--- | :--- | :--- | :--- | :--- |
| **`checklist`** 🏆 | **34.5 / 35** | **2 Wins (1st Place)** | **+82% to +174%** (150–460 tokens) | 112.75s |
| **`full`** | **29.0 / 35** | 0 Wins | **+1330% to +3639%** (1,000–3,100+ tokens) | 79.15s |
| **`retrieved`** | **29.0 / 35** | 0 Wins | **+164% to +532%** (200–540 tokens) | 68.97s |
| **`control`** | **27.0 / 35** | 0 Wins | **0%** (Baseline ~80 tokens) | 130.48s |

> **Key Finding**: Delivering skills as concise, high-density **checklists** out-performs multi-page `SKILL.md` dumps by **+5.5 points** while reducing prompt bloat by over **90%**.

### 2. Framework Tooling Performance (`benchmark-results.json`)

* **Skill Validation (`validate_skills`)**: 155.96 ms median (across 416 skills)
* **Index Building (`build_index`)**: 255.82 ms median
* **Command Wrapper Generation (`generate_commands`)**: 157.70 ms median
* **Doc & Portal Generation (`generate_docs`)**: 47.17 ms median
* **Full Integration Test Suite (`verify_all`)**: 1,082.28 ms median (~1.08s)

---

## Checklist Injection Architecture

Based on empirical benchmark findings, `agent-skills` implements a **2-Tier Checklist Delivery Pipeline**:

```
[Raw SKILL.md] ──► [Build Time: skills build-all] ──► [Extract/Truncate Checklists]
                                                                  │
                                                                  ▼
[Live Task Execution] ◄── [Load Cached < 1ms] ◄── [.agentrules / commands/ / exports/]
```

1. **Build-Time Extraction (Offline Pre-Compilation)**:
   * During `skills build-all` or `skills export`, the exporter ([`scripts/export_skills.py`](file:///home/sanjeev/Downloads/agent-skills/scripts/export_skills.py#L170)) automatically parses `SKILL.md` files.
   * It extracts the `## Checklist` and `## Verification Steps` headers while stripping long prose and code examples, creating compact rulesets for `.agentrules`, `.cursorrules`, `.windsurfrules`, and `copilot-instructions.md`.

2. **Runtime Intent-Driven Ingestion**:
   * When an agent (Claude Code, Antigravity, Cursor) detects a task matching a skill trigger, it loads the **cached checklist** in `< 1ms` (~150 tokens) instead of reading 3,000-token manuals.
   * This provides max quality (34.5/35 score) while eliminating prompt bloat.

---

## `skills` CLI Reference

```bash
skills build-all         # Run full index, command generation, graph, lint, docs, and exports
skills verify            # Run validation, integration tests, syntax, and compilation checks
skills benchmark         # Measure validation, generation, and test-suite performance
skills sync              # Copy skills across ~/.gemini, ~/.agents, ~/.cursor, ~/.copilot, ~/.codex
skills index             # Rebuild skills.json index
skills generate-commands # Auto-generate namespaced & flat command wrappers
skills graph            # Build skill dependency tree & Mermaid graph
skills lint             # Audit repository for duplicates and description similarities
skills telemetry        # Record and generate skill usage analytics
skills generate-docs    # Regenerate catalog & metrics dashboards
skills backup           # Create timestamped tar.gz backups of all agent roots
```

> **Test coverage note:** `skills verify` currently validates all 416 skills, generated command coverage, repository integrity, filesystem safety, shell syntax, and Python compilation. LLM task behavior and delivery strategies are benchmarked via `benchmarks/run_tasks_benchmark.py` and `benchmarks/skill_delivery_experiment.py`.
