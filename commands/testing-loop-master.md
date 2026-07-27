<!-- AUTO-GENERATED FILE — DO NOT EDIT MANUALLY -->
<!-- Source of truth: skills/testing-loop-master/SKILL.md -->
---
description: "Plan, write, run, and iterate tests until behavior is validated with deterministic coverage."
category: "web"
namespace: "/web/testing-loop-master"
flat_command: "/testing-loop-master"
---

# Command: testing-loop-master (/web/testing-loop-master)

> **Trigger**: Plan, write, run, and iterate tests until behavior is validated with deterministic coverage.
> **Category**: Web & Frontend Development
> **Source Skill**: [skills/testing-loop-master/SKILL.md](file:///home/sanjeev/Downloads/agent-skills/skills/testing-loop-master/SKILL.md)

---

# Testing Loop Master

## Objective
Drive a complete red-green-refactor testing cycle for backend, frontend, and integration paths.

## Workflow
1. Translate requirements/bug into explicit acceptance criteria.
2. Write or update failing tests first.
3. Implement minimal code changes to pass tests.
4. Refactor safely while keeping tests green.
5. Add regression tests for discovered edge cases.

## Required Coverage
- Vitest: domain logic, utilities, component behavior, API client behavior.
- Playwright: critical e2e flows (auth, key user journeys, destructive actions).
- Contract checks: typed API boundaries and schema assumptions.

## Reliability Rules
- Keep tests deterministic; avoid real external dependencies.
- Use mocks/stubs/fixtures for third-party APIs.
- Fail fast on flaky tests and stabilize before merge.

## Output Format
- Test plan mapped to acceptance criteria.
- List of added/updated tests.
- Final pass/fail status and known gaps.
