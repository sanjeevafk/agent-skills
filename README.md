# Agent Skills Framework

[![License](https://img.shields.io/github/license/sanjeevafk/agent-skills?style=flat-square)](https://github.com/sanjeevafk/agent-skills/blob/main/LICENSE)
![Agentic Engineering](https://img.shields.io/badge/Agentic-Engineering-1F8A70?style=flat-square)
![Skills Count](https://img.shields.io/badge/Skills-388-blue?style=flat-square)
![Rules Count](https://img.shields.io/badge/Rules-16-purple?style=flat-square)

A telemetry-driven, self-documenting AI capability framework. Manage, sync, and export skills, command namespaces, subagents, and 14 classic software engineering book standards across **Claude Code, Antigravity, Cursor, Windsurf, GitHub Copilot, and Codex**.

---

## ⚡ Quick 1-Command Setup

Clone the repository and run the automated installer. The installer sets up PATH configuration, shell aliases (`gskills`), builds all command wrappers, indexes, dependency graphs, and automatically syncs skills across all installed AI agent runtimes (`~/.gemini`, `~/.agents`, `~/.cursor`, `~/.copilot`):

```bash
git clone https://github.com/sanjeevafk/agent-skills.git && cd agent-skills && ./scripts/install-global-skills.sh
```

After opening a new shell:

```bash
# Verify installation
gskills status

# Run full framework build
gskills build-all
```

---

## 🎯 Architecture: Single Source of Truth

The repository enforces strict separation between **canonical sources of truth** and **auto-generated artifacts**:

```
agent-skills/
│
├── 🧠 skills/               [CANONICAL] 388 Modular Capability Manuals
├── 📜 rules/                [CANONICAL] 16 Always-On Standards & 14 Book Guidelines
│
├── ⚡ commands/             [GENERATED] Namespaced & Flat Command Wrappers
├── 🔍 skills.json           [GENERATED] Complete Reverse-Indexed Metadata Registry
├── 📦 exports/              [GENERATED] Multi-Client IDE Rules (.cursorrules, .agentrules, etc.)
└── 📖 docs/                 [GENERATED] Catalog, Dependency Graphs & Analytics Dashboards
```

---

## 🚀 Command Namespaces & Slash Commands

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

## 📚 What are the Files in `docs/` For?

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

## 📦 Multi-Client Rule Exports

Export your entire skills collection and 14 book standards into single-file rulesets for any editor:

```bash
# Export all client rule formats at once (.agentrules, .cursorrules, .windsurfrules, copilot-instructions.md)
gskills export --format all --output-dir ~/my-project

# Export specific format
gskills export --format cursor --output-dir ~/my-project
```

---

## 🛠️ `gskills` CLI Reference

```bash
gskills build-all         # Run full index, command generation, graph, lint, docs, and exports
gskills verify            # Run validation, integration tests, syntax, and compilation checks
gskills benchmark         # Measure validation, generation, and test-suite performance
gskills sync              # Copy skills across ~/.gemini, ~/.agents, ~/.cursor, ~/.copilot, ~/.codex
gskills index             # Rebuild skills.json index
gskills generate-commands # Auto-generate namespaced & flat command wrappers
gskills graph            # Build skill dependency tree & Mermaid graph
gskills lint             # Audit repository for duplicates and description similarities
gskills telemetry        # Record and generate skill usage analytics
gskills generate-docs    # Regenerate catalog & metrics dashboards
gskills backup           # Create timestamped tar.gz backups of all agent roots
```
