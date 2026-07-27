<!-- AUTO-GENERATED FILE — DO NOT EDIT MANUALLY -->
<!-- Source of truth: skills/gsd-note/SKILL.md -->
---
description: "Zero-friction idea capture. Append, list, or promote notes to todos."
category: "gsd"
namespace: "/gsd/note"
flat_command: "/gsd-note"
---

# Command: gsd-note (/gsd/note)

> **Trigger**: Zero-friction idea capture. Append, list, or promote notes to todos.
> **Category**: GSD Project Management
> **Source Skill**: [skills/gsd-note/SKILL.md](file:///home/sanjeev/Downloads/agent-skills/skills/gsd-note/SKILL.md)

---

<objective>
Zero-friction idea capture — one Write call, one confirmation line.

Three subcommands:
- **append** (default): Save a timestamped note file. No questions, no formatting.
- **list**: Show all notes from project and global scopes.
- **promote**: Convert a note into a structured todo.

Runs inline — no Task, no AskUserQuestion, no Bash.
</objective>

<execution_context>
@~/.copilot/get-shit-done/workflows/note.md
@~/.copilot/get-shit-done/references/ui-brand.md
</execution_context>

<context>
$ARGUMENTS
</context>

<process>
Execute the note workflow from @~/.copilot/get-shit-done/workflows/note.md end-to-end.
Capture the note, list notes, or promote to todo — depending on arguments.
</process>
