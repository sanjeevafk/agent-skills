<!-- AUTO-GENERATED FILE — DO NOT EDIT MANUALLY -->
<!-- Source of truth: skills/gsd-ui-review/SKILL.md -->
---
description: "Retroactive 6-pillar visual audit of implemented frontend code"
category: "gsd"
namespace: "/gsd/ui-review"
flat_command: "/gsd-ui-review"
---

# Command: gsd-ui-review (/gsd/ui-review)

> **Trigger**: Retroactive 6-pillar visual audit of implemented frontend code
> **Category**: GSD Project Management
> **Source Skill**: [skills/gsd-ui-review/SKILL.md](file:///home/sanjeev/Downloads/agent-skills/skills/gsd-ui-review/SKILL.md)

---

<objective>
Conduct a retroactive 6-pillar visual audit. Produces UI-REVIEW.md with
graded assessment (1-4 per pillar). Works on any project.
Output: {phase_num}-UI-REVIEW.md
</objective>

<execution_context>
@~/.copilot/get-shit-done/workflows/ui-review.md
@~/.copilot/get-shit-done/references/ui-brand.md
</execution_context>

<context>
Phase: $ARGUMENTS — optional, defaults to last completed phase.
</context>

<process>
Execute @~/.copilot/get-shit-done/workflows/ui-review.md end-to-end.
Preserve all workflow gates.
</process>
