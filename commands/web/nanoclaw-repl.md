<!-- AUTO-GENERATED FILE — DO NOT EDIT MANUALLY -->
<!-- Source of truth: skills/nanoclaw-repl/SKILL.md -->
---
description: "Operate and extend NanoClaw v2, ECC's zero-dependency session-aware REPL built on claude -p."
category: "web"
namespace: "/web/nanoclaw-repl"
flat_command: "/nanoclaw-repl"
---

# Command: nanoclaw-repl (/web/nanoclaw-repl)

> **Trigger**: Operate and extend NanoClaw v2, ECC's zero-dependency session-aware REPL built on claude -p.
> **Category**: Web & Frontend Development
> **Source Skill**: [skills/nanoclaw-repl/SKILL.md](file:///home/sanjeev/Downloads/agent-skills/skills/nanoclaw-repl/SKILL.md)

---

# NanoClaw REPL

Use this skill when running or extending `scripts/claw.js`.

## Capabilities

- persistent markdown-backed sessions
- model switching with `/model`
- dynamic skill loading with `/load`
- session branching with `/branch`
- cross-session search with `/search`
- history compaction with `/compact`
- export to md/json/txt with `/export`
- session metrics with `/metrics`

## Operating Guidance

1. Keep sessions task-focused.
2. Branch before high-risk changes.
3. Compact after major milestones.
4. Export before sharing or archival.

## Extension Rules

- keep zero external runtime dependencies
- preserve markdown-as-database compatibility
- keep command handlers deterministic and local
