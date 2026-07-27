<!-- AUTO-GENERATED FILE — DO NOT EDIT MANUALLY -->
<!-- Source of truth: skills/gsd-verify-work/SKILL.md -->
---
description: "Validate built features through conversational UAT"
category: "gsd"
namespace: "/gsd/verify-work"
flat_command: "/gsd-verify-work"
---

# Command: gsd-verify-work (/gsd/verify-work)

> **Trigger**: Validate built features through conversational UAT
> **Category**: GSD Project Management
> **Source Skill**: [skills/gsd-verify-work/SKILL.md](file:///home/sanjeev/Downloads/agent-skills/skills/gsd-verify-work/SKILL.md)

---

<objective>
Validate built features through conversational testing with persistent state.

Purpose: Confirm what Claude built actually works from user's perspective. One test at a time, plain text responses, no interrogation. When issues are found, automatically diagnose, plan fixes, and prepare for execution.

Output: {phase_num}-UAT.md tracking all test results. If issues found: diagnosed gaps, verified fix plans ready for /gsd-execute-phase
</objective>

<execution_context>
@~/.copilot/get-shit-done/workflows/verify-work.md
@~/.copilot/get-shit-done/templates/UAT.md
</execution_context>

<context>
Phase: $ARGUMENTS (optional)
- If provided: Test specific phase (e.g., "4")
- If not provided: Check for active sessions or prompt for phase

Context files are resolved inside the workflow (`init verify-work`) and delegated via `<files_to_read>` blocks.
</context>

<process>
Execute the verify-work workflow from @~/.copilot/get-shit-done/workflows/verify-work.md end-to-end.
Preserve all workflow gates (session management, test presentation, diagnosis, fix planning, routing).
</process>
