<!-- AUTO-GENERATED FILE — DO NOT EDIT MANUALLY -->
<!-- Source of truth: skills/gsd-remove-phase/SKILL.md -->
---
description: "Remove a future phase from roadmap and renumber subsequent phases"
category: "gsd"
namespace: "/gsd/remove-phase"
flat_command: "/gsd-remove-phase"
---

# Command: gsd-remove-phase (/gsd/remove-phase)

> **Trigger**: Remove a future phase from roadmap and renumber subsequent phases
> **Category**: GSD Project Management
> **Source Skill**: [skills/gsd-remove-phase/SKILL.md](file:///home/sanjeev/Downloads/agent-skills/skills/gsd-remove-phase/SKILL.md)

---

<objective>
Remove an unstarted future phase from the roadmap and renumber all subsequent phases to maintain a clean, linear sequence.

Purpose: Clean removal of work you've decided not to do, without polluting context with cancelled/deferred markers.
Output: Phase deleted, all subsequent phases renumbered, git commit as historical record.
</objective>

<execution_context>
@~/.copilot/get-shit-done/workflows/remove-phase.md
</execution_context>

<context>
Phase: $ARGUMENTS

Roadmap and state are resolved in-workflow via `init phase-op` and targeted reads.
</context>

<process>
Execute the remove-phase workflow from @~/.copilot/get-shit-done/workflows/remove-phase.md end-to-end.
Preserve all validation gates (future phase check, work check), renumbering logic, and commit.
</process>
