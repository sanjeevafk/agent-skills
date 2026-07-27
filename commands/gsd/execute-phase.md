<!-- AUTO-GENERATED FILE — DO NOT EDIT MANUALLY -->
<!-- Source of truth: skills/gsd-execute-phase/SKILL.md -->
---
description: "Execute all plans in a phase with wave-based parallelization"
category: "gsd"
namespace: "/gsd/execute-phase"
flat_command: "/gsd-execute-phase"
---

# Command: gsd-execute-phase (/gsd/execute-phase)

> **Trigger**: Execute all plans in a phase with wave-based parallelization
> **Category**: GSD Project Management
> **Source Skill**: [skills/gsd-execute-phase/SKILL.md](file:///home/sanjeev/Downloads/agent-skills/skills/gsd-execute-phase/SKILL.md)

---

<objective>
Execute all plans in a phase using wave-based parallel execution.

Orchestrator stays lean: discover plans, analyze dependencies, group into waves, spawn subagents, collect results. Each subagent loads the full execute-plan context and handles its own plan.

Context budget: ~15% orchestrator, 100% fresh per subagent.
</objective>

<execution_context>
@~/.copilot/get-shit-done/workflows/execute-phase.md
@~/.copilot/get-shit-done/references/ui-brand.md
</execution_context>

<context>
Phase: $ARGUMENTS

**Flags:**
- `--gaps-only` — Execute only gap closure plans (plans with `gap_closure: true` in frontmatter). Use after verify-work creates fix plans.

Context files are resolved inside the workflow via `gsd-tools init execute-phase` and per-subagent `<files_to_read>` blocks.
</context>

<process>
Execute the execute-phase workflow from @~/.copilot/get-shit-done/workflows/execute-phase.md end-to-end.
Preserve all workflow gates (wave execution, checkpoint handling, verification, state updates, routing).
</process>
