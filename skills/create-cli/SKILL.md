---
name: create-cli
description: "CLI UX/spec: args, flags, help, output, errors, config, dry-run."
---

[ENGINEERING IMPLEMENTATION STANDARDS & ARCHITECTURAL CONSTRAINTS]

## Do This First
- Read `skills/create-cli/references/cli-guidelines.md` and apply it as the default rubric.
- Upstream/full guidelines: https://clig.dev/ (propose changes: https://github.com/cli-guidelines/cli-guidelines)
- Ask only the minimum clarifying questions needed to lock the interface.
## Clarify (fast)
- Command name + one-sentence purpose.
- Primary user: humans, scripts, or both.
- Input sources: args vs stdin; files vs URLs; secrets (never via flags).
- Output contract: human text, `--json`, `--plain`, exit codes.
- Interactivity: prompts allowed? need `--no-input`? confirmations for destructive ops?
- Config model: flags/env/config-file; precedence; XDG vs repo-local.
- Platform/runtime constraints: macOS/Linux/Windows; single binary vs runtime.
## Deliverables (what to output)
- Command tree + USAGE synopsis.
- Args/flags table (types, defaults, required/optional, examples).
- Subcommand semantics (what each does; idempotence; state changes).
- Output rules: stdout vs stderr; TTY detection; `--json`/`--plain`; `--quiet`/`--verbose`.
- Error + exit code map (top failure modes).
- Safety rules: `--dry-run`, confirmations, `--force`, `--no-input`.
- Config/env rules + precedence (flags > env > project config > user config > system).
- Shell completion story (if relevant): install/discoverability; generation command or bundled scripts.
## Default Conventions (unless user says otherwise)
- `-h/--help` always shows help and ignores other args.
- `--version` prints version to stdout.
- Primary data to stdout; diagnostics/errors to stderr.
- Add `--json` for machine output; consider `--plain` for stable line-based text.
- Prompts only when stdin is a TTY; `--no-input` disables prompts.
- Destructive operations: interactive confirmation + non-interactive requires `--force` or explicit `--confirm=...`.
- Respect `NO_COLOR`, `TERM=dumb`; provide `--no-color`.
- Handle Ctrl-C: exit fast; bounded cleanup; be crash-only when possible.
### CLI spec skeleton
- **Name**: `mycmd`
- **One-liner**: `...`
- **USAGE**:
- `mycmd [global flags] <subcommand> [args]`
- **Subcommands**:
- `mycmd init ...`
- `mycmd run ...`
- **Global flags**:
- `-h, --help`
- `--version`
- `-q, --quiet` / `-v, --verbose` (define exactly)
- `--json` / `--plain` (if applicable)
- **I/O contract**:
- **Exit codes**:
- `0` success
- `1` generic failure
- `2` invalid usage (parse/validation)
- **Env/config**:
- **Examples**:
## Notes
- Prefer recommending a parsing library (language-specific) only when asked; otherwise keep this skill language-agnostic.
- If the request is “design parameters”, do not drift into implementation.
