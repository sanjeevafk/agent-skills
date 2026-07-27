<!-- AUTO-GENERATED FILE — DO NOT EDIT MANUALLY -->
<!-- Source of truth: skills/gsd-new-project/SKILL.md -->
---
description: "Initialize a new project with deep context gathering and PROJECT.md"
category: "gsd"
namespace: "/gsd/new-project"
flat_command: "/gsd-new-project"
---

# Command: gsd-new-project (/gsd/new-project)

> **Trigger**: Initialize a new project with deep context gathering and PROJECT.md
> **Category**: GSD Project Management
> **Source Skill**: [skills/gsd-new-project/SKILL.md](file:///home/sanjeev/Downloads/agent-skills/skills/gsd-new-project/SKILL.md)

---

<context>
**Flags:**
- `--auto` — Automatic mode. After config questions, runs research → requirements → roadmap without further interaction. Expects idea document via @ reference.
</context>

<objective>
Initialize a new project through unified flow: questioning → research (optional) → requirements → roadmap.

**Creates:**
- `.planning/PROJECT.md` — project context
- `.planning/config.json` — workflow preferences
- `.planning/research/` — domain research (optional)
- `.planning/REQUIREMENTS.md` — scoped requirements
- `.planning/ROADMAP.md` — phase structure
- `.planning/STATE.md` — project memory

**After this command:** Run `/gsd-plan-phase 1` to start execution.
</objective>

<execution_context>
@~/.copilot/get-shit-done/workflows/new-project.md
@~/.copilot/get-shit-done/references/questioning.md
@~/.copilot/get-shit-done/references/ui-brand.md
@~/.copilot/get-shit-done/templates/project.md
@~/.copilot/get-shit-done/templates/requirements.md
</execution_context>

<process>
Execute the new-project workflow from @~/.copilot/get-shit-done/workflows/new-project.md end-to-end.
Preserve all workflow gates (validation, approvals, commits, routing).
</process>
