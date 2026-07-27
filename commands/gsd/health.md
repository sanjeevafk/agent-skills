<!-- AUTO-GENERATED FILE — DO NOT EDIT MANUALLY -->
<!-- Source of truth: skills/gsd-health/SKILL.md -->
---
description: "Diagnose planning directory health and optionally repair issues"
category: "gsd"
namespace: "/gsd/health"
flat_command: "/gsd-health"
---

# Command: gsd-health (/gsd/health)

> **Trigger**: Diagnose planning directory health and optionally repair issues
> **Category**: GSD Project Management
> **Source Skill**: [skills/gsd-health/SKILL.md](file:///home/sanjeev/Downloads/agent-skills/skills/gsd-health/SKILL.md)

---

<objective>
Validate `.planning/` directory integrity and report actionable issues. Checks for missing files, invalid configurations, inconsistent state, and orphaned plans.
</objective>

<execution_context>
@~/.copilot/get-shit-done/workflows/health.md
</execution_context>

<process>
Execute the health workflow from @~/.copilot/get-shit-done/workflows/health.md end-to-end.
Parse --repair flag from arguments and pass to workflow.
</process>
