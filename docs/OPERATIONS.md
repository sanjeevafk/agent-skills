# Operations & Architecture Guide

> Operational manual for managing skills, command namespaces, rule compilation, and multi-agent synchronization.

---

## 1. Single Source of Truth Architecture

All capabilities are maintained under two canonical directories:
* **`skills/`**: Modular skill manuals (`SKILL.md`).
* **`rules/`**: Baseline engineering standards, 14 book rulesets, and `/learn` directives.

All command wrappers (`commands/`), index registries (`skills.json`), dependency graphs (`docs/DEPENDENCY_GRAPH.md`), catalog docs (`docs/SKILLS_CATALOG.md`), and multi-IDE rules (`.agentrules`, `.cursorrules`, `.windsurfrules`, `copilot-instructions.md`) are **auto-generated build artifacts**.

---

## 2. CLI Tooling Reference (`gskills`)

```bash
# Build the complete pipeline end-to-end
gskills build-all

# Synchronize skills across ~/.gemini, ~/.agents, ~/.cursor, ~/.copilot, ~/.codex
gskills sync

# Rebuild skills.json index
gskills index

# Auto-generate namespaced (/debug/, /web/, /rule/) and flat command wrappers
gskills generate-commands

# Resolve prerequisite dependency tree & render Mermaid graph
gskills graph

# Audit skills repository for potential duplicates and alias collisions
gskills lint

# Record and view skill usage analytics
gskills telemetry report

# Export multi-client IDE rules to a project folder
gskills export --format all --output-dir ~/my-project

# Create timestamped tar.gz backups of all agent environment roots
gskills backup
```

---

## 3. Command Namespaces & Slash Commands

Skills and rules are assigned namespaced commands for instant invocation:

* **`/debug/`**: Systematic debugging, root-cause isolation (`/debug/systematic`, `/debug/root-cause`).
* **`/web/`**: Modern web stack guidance (`/web/nextjs-15-expert`, `/web/supabase-expert`, `/web/tailwind-radix-expert`).
* **`/lang/`**: Language systems & interop (`/lang/python-ts-interop-mcp-builder`).
* **`/style/`**: Coding conventions (`/style/google-style-python`, `/style/google-ts`, `/style/nasa-jpl`).
* **`/gsd/`**: Milestone & phase management (`/gsd/plan-phase`, `/gsd/execute-phase`, `/gsd/progress`).
* **`/devops/`**: Deployment & containerization (`/devops/docker-patterns`, `/devops/vercel-deploy`).
* **`/rule/`**: Explicit rule invocation (`/rule/clean-code`, `/rule/user-global-rules`, `/rule/refactoring`).

---

## 4. Multi-Client Rule Exports

When opening any project in Cursor, Windsurf, Copilot, or generic LLM harnesses, compile your rules into the target repository:

```bash
# Export all rule formats (.agentrules, .cursorrules, .windsurfrules, copilot-instructions.md)
gskills export --format all --output-dir ~/my-project
```

This ensures any AI assistant touching your project automatically inherits all 388 skill guidelines and 16 core engineering book rules.
