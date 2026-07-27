<!-- AUTO-GENERATED FILE — DO NOT EDIT MANUALLY -->
<!-- Source of truth: skills/gsd-update/SKILL.md -->
---
description: "Update GSD to latest version with changelog display"
category: "gsd"
namespace: "/gsd/update"
flat_command: "/gsd-update"
---

# Command: gsd-update (/gsd/update)

> **Trigger**: Update GSD to latest version with changelog display
> **Category**: GSD Project Management
> **Source Skill**: [skills/gsd-update/SKILL.md](file:///home/sanjeev/Downloads/agent-skills/skills/gsd-update/SKILL.md)

---

<objective>
Check for GSD updates, install if available, and display what changed.

Routes to the update workflow which handles:
- Version detection (local vs global installation)
- npm version checking
- Changelog fetching and display
- User confirmation with clean install warning
- Update execution and cache clearing
- Restart reminder
</objective>

<execution_context>
@~/.copilot/get-shit-done/workflows/update.md
</execution_context>

<process>
**Follow the update workflow** from `@~/.copilot/get-shit-done/workflows/update.md`.

The workflow handles all logic including:
1. Installed version detection (local/global)
2. Latest version checking via npm
3. Version comparison
4. Changelog fetching and extraction
5. Clean install warning display
6. User confirmation
7. Update execution
8. Cache clearing
</process>
