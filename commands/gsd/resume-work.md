<!-- AUTO-GENERATED FILE — DO NOT EDIT MANUALLY -->
<!-- Source of truth: skills/gsd-resume-work/SKILL.md -->
---
description: "Resume work from previous session with full context restoration"
category: "gsd"
namespace: "/gsd/resume-work"
flat_command: "/gsd-resume-work"
---

# Command: gsd-resume-work (/gsd/resume-work)

> **Trigger**: Resume work from previous session with full context restoration
> **Category**: GSD Project Management
> **Source Skill**: [skills/gsd-resume-work/SKILL.md](file:///home/sanjeev/Downloads/agent-skills/skills/gsd-resume-work/SKILL.md)

---

<objective>
Restore complete project context and resume work seamlessly from previous session.

Routes to the resume-project workflow which handles:

- STATE.md loading (or reconstruction if missing)
- Checkpoint detection (.continue-here files)
- Incomplete work detection (PLAN without SUMMARY)
- Status presentation
- Context-aware next action routing
  </objective>

<execution_context>
@~/.copilot/get-shit-done/workflows/resume-project.md
</execution_context>

<process>
**Follow the resume-project workflow** from `@~/.copilot/get-shit-done/workflows/resume-project.md`.

The workflow handles all resumption logic including:

1. Project existence verification
2. STATE.md loading or reconstruction
3. Checkpoint and incomplete work detection
4. Visual status presentation
5. Context-aware option offering (checks CONTEXT.md before suggesting plan vs discuss)
6. Routing to appropriate next command
7. Session continuity updates
   </process>
