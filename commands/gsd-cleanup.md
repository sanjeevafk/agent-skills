<!-- AUTO-GENERATED FILE — DO NOT EDIT MANUALLY -->
<!-- Source of truth: skills/gsd-cleanup/SKILL.md -->
---
description: "Archive accumulated phase directories from completed milestones"
category: "gsd"
namespace: "/gsd/cleanup"
flat_command: "/gsd-cleanup"
---

# Command: gsd-cleanup (/gsd/cleanup)

> **Trigger**: Archive accumulated phase directories from completed milestones
> **Category**: GSD Project Management
> **Source Skill**: [skills/gsd-cleanup/SKILL.md](file:///home/sanjeev/Downloads/agent-skills/skills/gsd-cleanup/SKILL.md)

---

<objective>
Archive phase directories from completed milestones into `.planning/milestones/v{X.Y}-phases/`.

Use when `.planning/phases/` has accumulated directories from past milestones.
</objective>

<execution_context>
@~/.copilot/get-shit-done/workflows/cleanup.md
</execution_context>

<process>
Follow the cleanup workflow at @~/.copilot/get-shit-done/workflows/cleanup.md.
Identify completed milestones, show a dry-run summary, and archive on confirmation.
</process>
