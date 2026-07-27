<!-- AUTO-GENERATED FILE — DO NOT EDIT MANUALLY -->
<!-- Source of truth: skills/gsd-insert-phase/SKILL.md -->
---
description: "Insert urgent work as decimal phase (e.g., 72.1) between existing phases"
category: "gsd"
namespace: "/gsd/insert-phase"
flat_command: "/gsd-insert-phase"
---

# Command: gsd-insert-phase (/gsd/insert-phase)

> **Trigger**: Insert urgent work as decimal phase (e.g., 72.1) between existing phases
> **Category**: GSD Project Management
> **Source Skill**: [skills/gsd-insert-phase/SKILL.md](file:///home/sanjeev/Downloads/agent-skills/skills/gsd-insert-phase/SKILL.md)

---

<objective>
Insert a decimal phase for urgent work discovered mid-milestone that must be completed between existing integer phases.

Uses decimal numbering (72.1, 72.2, etc.) to preserve the logical sequence of planned phases while accommodating urgent insertions.

Purpose: Handle urgent work discovered during execution without renumbering entire roadmap.
</objective>

<execution_context>
@~/.copilot/get-shit-done/workflows/insert-phase.md
</execution_context>

<context>
Arguments: $ARGUMENTS (format: <after-phase-number> <description>)

Roadmap and state are resolved in-workflow via `init phase-op` and targeted tool calls.
</context>

<process>
Execute the insert-phase workflow from @~/.copilot/get-shit-done/workflows/insert-phase.md end-to-end.
Preserve all validation gates (argument parsing, phase verification, decimal calculation, roadmap updates).
</process>
