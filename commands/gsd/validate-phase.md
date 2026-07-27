<!-- AUTO-GENERATED FILE — DO NOT EDIT MANUALLY -->
<!-- Source of truth: skills/gsd-validate-phase/SKILL.md -->
---
description: "Retroactively audit and fill Nyquist validation gaps for a completed phase"
category: "gsd"
namespace: "/gsd/validate-phase"
flat_command: "/gsd-validate-phase"
---

# Command: gsd-validate-phase (/gsd/validate-phase)

> **Trigger**: Retroactively audit and fill Nyquist validation gaps for a completed phase
> **Category**: GSD Project Management
> **Source Skill**: [skills/gsd-validate-phase/SKILL.md](file:///home/sanjeev/Downloads/agent-skills/skills/gsd-validate-phase/SKILL.md)

---

<objective>
Audit Nyquist validation coverage for a completed phase. Three states:
- (A) VALIDATION.md exists — audit and fill gaps
- (B) No VALIDATION.md, SUMMARY.md exists — reconstruct from artifacts
- (C) Phase not executed — exit with guidance

Output: updated VALIDATION.md + generated test files.
</objective>

<execution_context>
@~/.copilot/get-shit-done/workflows/validate-phase.md
</execution_context>

<context>
Phase: $ARGUMENTS — optional, defaults to last completed phase.
</context>

<process>
Execute @~/.copilot/get-shit-done/workflows/validate-phase.md.
Preserve all workflow gates.
</process>
