---
name: export
description: Export the chat conversation history to a clean Markdown (.md) file in the workspace.
disable-model-invocation: true
---

[ENGINEERING IMPLEMENTATION STANDARDS & ARCHITECTURAL CONSTRAINTS]

1. Export the current conversation transcript into a clean Markdown (`.md`) file.
2. Format role headers (`### User`, `### Assistant`), code blocks, thinking traces, and tool results cleanly in GitHub-flavored Markdown.
3. Save to `./session_export_<TIMESTAMP>.md` or a specified `.md` path.
