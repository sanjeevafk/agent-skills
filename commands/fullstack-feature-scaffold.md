<!-- AUTO-GENERATED FILE — DO NOT EDIT MANUALLY -->
<!-- Source of truth: skills/fullstack-feature-scaffold/SKILL.md -->
---
description: "Scaffold end-to-end features across Next.js frontend, API layer, Supabase schema/policies, and tests."
category: "security"
namespace: "/security/fullstack-feature-scaffold"
flat_command: "/fullstack-feature-scaffold"
---

# Command: fullstack-feature-scaffold (/security/fullstack-feature-scaffold)

> **Trigger**: Scaffold end-to-end features across Next.js frontend, API layer, Supabase schema/policies, and tests.
> **Category**: Security, Compliance & Hardening
> **Source Skill**: [skills/fullstack-feature-scaffold/SKILL.md](file:///home/sanjeev/Downloads/agent-skills/skills/fullstack-feature-scaffold/SKILL.md)

---

# Full-Stack Feature Scaffold (Next.js + Supabase)

## Objective
Create a production-ready feature scaffold from schema to UI with secure defaults and tests.

## Scaffold Workflow
1. Requirement breakdown and acceptance criteria.
2. Supabase schema + migration + RLS policies.
3. Server-side API/action layer with validation.
4. Typed frontend data hooks/components.
5. UI states: loading, empty, error, success.
6. Vitest + Playwright coverage.

## Generated Artifacts
- Migration SQL and policy definitions.
- Typed domain models and API contracts.
- Route/module skeletons in Next.js App Router.
- Test files and fixtures.

## Guardrails
- No service role key in client code.
- No untyped API boundaries.
- Every mutation path requires authz checks.
- Include rollback notes for schema changes.

## Output Format
- Folder/file scaffold map.
- Step-by-step implementation plan.
- Validation and rollout checklist.
