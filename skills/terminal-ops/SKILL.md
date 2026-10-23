---
name: terminal-ops
description: Evidence-first repo execution workflow for ECC. Use when the user wants a command run, a repo checked, a CI failure debugged, or a narrow fix pushed with exact proof of what was executed and verified.
metadata:
  origin: ECC
---

[ENGINEERING IMPLEMENTATION STANDARDS & ARCHITECTURAL CONSTRAINTS]

## Skill Stack
- `verification-loop` for exact proving steps after changes
- `tdd-workflow` when the right fix needs regression coverage
- `security-review` when secrets, auth, or external inputs are involved
- `github-ops` when the task depends on CI runs, PR state, or release status
- `knowledge-ops` when the verified outcome needs to be captured into durable project context
## Guardrails
- prefer repo-local scripts and helpers over improvised ad hoc wrappers
### 1. Resolve the working surface
- verify
### 2. Read the failing surface first
- use any already-supplied logs or context before re-reading blindly
### 3. Keep the fix narrow
- use the smallest useful proving command first
## Output Format
```text
SURFACE
- repo
- branch
- requested mode

EVIDENCE
- failing command / diff / test

ACTION
- what changed

STATUS
- inspected / changed locally / verified locally / committed / pushed / blocked
```
