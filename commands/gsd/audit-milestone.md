<!-- AUTO-GENERATED FILE — DO NOT EDIT MANUALLY -->
<!-- Source of truth: skills/gsd-audit-milestone/SKILL.md -->
---
description: "Audit milestone completion against original intent before archiving"
category: "gsd"
namespace: "/gsd/audit-milestone"
flat_command: "/gsd-audit-milestone"
---

# Command: gsd-audit-milestone (/gsd/audit-milestone)

> **Trigger**: Audit milestone completion against original intent before archiving
> **Category**: GSD Project Management
> **Source Skill**: [skills/gsd-audit-milestone/SKILL.md](file:///home/sanjeev/Downloads/agent-skills/skills/gsd-audit-milestone/SKILL.md)

---

<objective>
Verify milestone achieved its definition of done. Check requirements coverage, cross-phase integration, and end-to-end flows.

**This command IS the orchestrator.** Reads existing VERIFICATION.md files (phases already verified during execute-phase), aggregates tech debt and deferred gaps, then spawns integration checker for cross-phase wiring.
</objective>

<execution_context>
@~/.copilot/get-shit-done/workflows/audit-milestone.md
</execution_context>

<context>
Version: $ARGUMENTS (optional — defaults to current milestone)

Core planning files are resolved in-workflow (`init milestone-op`) and loaded only as needed.

**Completed Work:**
Glob: .planning/phases/*/*-SUMMARY.md
Glob: .planning/phases/*/*-VERIFICATION.md
</context>

<process>
Execute the audit-milestone workflow from @~/.copilot/get-shit-done/workflows/audit-milestone.md end-to-end.
Preserve all workflow gates (scope determination, verification reading, integration check, requirements coverage, routing).
</process>
