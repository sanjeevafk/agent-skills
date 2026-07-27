<!-- AUTO-GENERATED FILE — DO NOT EDIT MANUALLY -->
<!-- Source of truth: skills/gsd-pause-work/SKILL.md -->
---
description: "Create context handoff when pausing work mid-phase"
category: "gsd"
namespace: "/gsd/pause-work"
flat_command: "/gsd-pause-work"
---

# Command: gsd-pause-work (/gsd/pause-work)

> **Trigger**: Create context handoff when pausing work mid-phase
> **Category**: GSD Project Management
> **Source Skill**: [skills/gsd-pause-work/SKILL.md](file:///home/sanjeev/Downloads/agent-skills/skills/gsd-pause-work/SKILL.md)

---

<objective>
Create `.continue-here.md` handoff file to preserve complete work state across sessions.

Routes to the pause-work workflow which handles:
- Current phase detection from recent files
- Complete state gathering (position, completed work, remaining work, decisions, blockers)
- Handoff file creation with all context sections
- Git commit as WIP
- Resume instructions
</objective>

<execution_context>
@~/.copilot/get-shit-done/workflows/pause-work.md
</execution_context>

<context>
State and phase progress are gathered in-workflow with targeted reads.
</context>

<process>
**Follow the pause-work workflow** from `@~/.copilot/get-shit-done/workflows/pause-work.md`.

The workflow handles all logic including:
1. Phase directory detection
2. State gathering with user clarifications
3. Handoff file writing with timestamp
4. Git commit
5. Confirmation with resume instructions
</process>
