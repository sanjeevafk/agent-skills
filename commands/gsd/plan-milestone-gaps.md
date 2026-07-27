<!-- AUTO-GENERATED FILE — DO NOT EDIT MANUALLY -->
<!-- Source of truth: skills/gsd-plan-milestone-gaps/SKILL.md -->
---
description: "Create phases to close all gaps identified by milestone audit"
category: "gsd"
namespace: "/gsd/plan-milestone-gaps"
flat_command: "/gsd-plan-milestone-gaps"
---

# Command: gsd-plan-milestone-gaps (/gsd/plan-milestone-gaps)

> **Trigger**: Create phases to close all gaps identified by milestone audit
> **Category**: GSD Project Management
> **Source Skill**: [skills/gsd-plan-milestone-gaps/SKILL.md](file:///home/sanjeev/Downloads/agent-skills/skills/gsd-plan-milestone-gaps/SKILL.md)

---

<objective>
Create all phases necessary to close gaps identified by `/gsd-audit-milestone`.

Reads MILESTONE-AUDIT.md, groups gaps into logical phases, creates phase entries in ROADMAP.md, and offers to plan each phase.

One command creates all fix phases — no manual `/gsd-add-phase` per gap.
</objective>

<execution_context>
@~/.copilot/get-shit-done/workflows/plan-milestone-gaps.md
</execution_context>

<context>
**Audit results:**
Glob: .planning/v*-MILESTONE-AUDIT.md (use most recent)

Original intent and current planning state are loaded on demand inside the workflow.
</context>

<process>
Execute the plan-milestone-gaps workflow from @~/.copilot/get-shit-done/workflows/plan-milestone-gaps.md end-to-end.
Preserve all workflow gates (audit loading, prioritization, phase grouping, user confirmation, roadmap updates).
</process>
