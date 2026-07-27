<!-- AUTO-GENERATED FILE — DO NOT EDIT MANUALLY -->
<!-- Source of truth: skills/gsd-do/SKILL.md -->
---
description: "Route freeform text to the right GSD command automatically"
category: "gsd"
namespace: "/gsd/do"
flat_command: "/gsd-do"
---

# Command: gsd-do (/gsd/do)

> **Trigger**: Route freeform text to the right GSD command automatically
> **Category**: GSD Project Management
> **Source Skill**: [skills/gsd-do/SKILL.md](file:///home/sanjeev/Downloads/agent-skills/skills/gsd-do/SKILL.md)

---

<objective>
Analyze freeform natural language input and dispatch to the most appropriate GSD command.

Acts as a smart dispatcher — never does the work itself. Matches intent to the best GSD command using routing rules, confirms the match, then hands off.

Use when you know what you want but don't know which `/gsd-*` command to run.
</objective>

<execution_context>
@~/.copilot/get-shit-done/workflows/do.md
@~/.copilot/get-shit-done/references/ui-brand.md
</execution_context>

<context>
$ARGUMENTS
</context>

<process>
Execute the do workflow from @~/.copilot/get-shit-done/workflows/do.md end-to-end.
Route user intent to the best GSD command and invoke it.
</process>
