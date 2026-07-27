<!-- AUTO-GENERATED FILE — DO NOT EDIT MANUALLY -->
<!-- Source of truth: skills/gsd-ui-phase/SKILL.md -->
---
description: "Generate UI design contract (UI-SPEC.md) for frontend phases"
category: "gsd"
namespace: "/gsd/ui-phase"
flat_command: "/gsd-ui-phase"
---

# Command: gsd-ui-phase (/gsd/ui-phase)

> **Trigger**: Generate UI design contract (UI-SPEC.md) for frontend phases
> **Category**: GSD Project Management
> **Source Skill**: [skills/gsd-ui-phase/SKILL.md](file:///home/sanjeev/Downloads/agent-skills/skills/gsd-ui-phase/SKILL.md)

---

<objective>
Create a UI design contract (UI-SPEC.md) for a frontend phase.
Orchestrates gsd-ui-researcher and gsd-ui-checker.
Flow: Validate → Research UI → Verify UI-SPEC → Done
</objective>

<execution_context>
@~/.copilot/get-shit-done/workflows/ui-phase.md
@~/.copilot/get-shit-done/references/ui-brand.md
</execution_context>

<context>
Phase number: $ARGUMENTS — optional, auto-detects next unplanned phase if omitted.
</context>

<process>
Execute @~/.copilot/get-shit-done/workflows/ui-phase.md end-to-end.
Preserve all workflow gates.
</process>
