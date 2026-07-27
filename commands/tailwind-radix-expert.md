<!-- AUTO-GENERATED FILE — DO NOT EDIT MANUALLY -->
<!-- Source of truth: skills/tailwind-radix-expert/SKILL.md -->
---
description: "Build accessible, consistent UI using Tailwind CSS and Radix/shadcn patterns."
category: "web"
namespace: "/web/tailwind-radix-expert"
flat_command: "/tailwind-radix-expert"
---

# Command: tailwind-radix-expert (/web/tailwind-radix-expert)

> **Trigger**: Build accessible, consistent UI using Tailwind CSS and Radix/shadcn patterns.
> **Category**: Web & Frontend Development
> **Source Skill**: [skills/tailwind-radix-expert/SKILL.md](file:///home/sanjeev/Downloads/agent-skills/skills/tailwind-radix-expert/SKILL.md)

---

# Tailwind + Radix Expert

## Objective
Create polished, accessible, and maintainable interfaces with strong design consistency.

## Design Rules
1. Use semantic tokens (CSS variables) for theming.
2. Preserve accessibility behavior from Radix primitives.
3. Ensure visible focus states and keyboard navigation.
4. Keep class composition readable and reusable.
5. Validate mobile and desktop responsiveness.

## Component Conventions
- Separate behavior from presentation.
- Build composable primitives before page-level composition.
- Prevent style drift by reusing tokenized utilities.

## Quality Gates
- A11y: labels, roles, focus, contrast.
- Layout: no overflow or clipping at common breakpoints.
- Interaction: consistent hover/active/disabled states.

## Output Format
- Component API and composition plan.
- Styling tokens/utilities used.
- Accessibility and responsive validation checklist.
