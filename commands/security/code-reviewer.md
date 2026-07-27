<!-- AUTO-GENERATED FILE — DO NOT EDIT MANUALLY -->
<!-- Source of truth: skills/code-reviewer/SKILL.md -->
---
description: "Senior full-stack code review focused on correctness, architecture, security, and maintainability."
category: "security"
namespace: "/security/code-reviewer"
flat_command: "/code-reviewer"
---

# Command: code-reviewer (/security/code-reviewer)

> **Trigger**: Senior full-stack code review focused on correctness, architecture, security, and maintainability.
> **Category**: Security, Compliance & Hardening
> **Source Skill**: [skills/code-reviewer/SKILL.md](file:///home/sanjeev/Downloads/agent-skills/skills/code-reviewer/SKILL.md)

---

# Code Reviewer (Senior Full-Stack)

## Objective
Perform a rigorous review of changed code and return prioritized, actionable findings.

## Review Process
1. Scope changes with git diff and identify risk areas (auth, billing, data writes, migrations, concurrency).
2. Validate correctness and edge-case handling.
3. Check architecture and separation of concerns.
4. Evaluate TypeScript strictness and API contracts.
5. Evaluate Supabase auth/RLS implications and secret handling.
6. Evaluate UI accessibility and Tailwind/Radix composition quality.
7. Check test adequacy (Vitest + Playwright) and regression coverage.

## Severity Rubric
- P0: Security issue, data loss, or critical correctness bug.
- P1: High-risk logic flaw or production reliability risk.
- P2: Maintainability or test gap that should be fixed soon.
- P3: Optional improvement.

## Output Format
- Summary: approve or request changes.
- Findings grouped by severity with file references.
- Suggested fix for each finding.
- Test gaps and missing scenarios.
- Final recommendation.

## Guardrails
- Be specific and evidence-based.
- Prefer minimal, safe fixes over broad rewrites.
- If no issues found, state residual risk and untested areas.
