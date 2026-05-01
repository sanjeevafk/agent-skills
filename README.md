# Agent Skills Toolkit

[![License](https://img.shields.io/github/license/sanjeevafk/agent-skills?style=flat-square)](https://github.com/sanjeevafk/agent-skills/blob/main/LICENSE)
![Agentic Engineering](https://img.shields.io/badge/Agentic-Engineering-1F8A70?style=flat-square)

Manage and sync skills across multiple AI agent environments from one source of truth.

If copying skill folders between five different directories is annoying: ⭐ star this repo.

## Why Use This?

Compared to raw `npx skills add`, desktop apps, or manual copying:

- One command syncs all configured agent skill roots.
- Config-driven roots (`~/.global-skills.conf`) make the setup portable and customizable.
- Repeatable backup/sync workflow with predictable structure.
- Supports curated + reproducible team conventions from version control.

## Installation (One-Liner)

```bash
git clone https://github.com/sanjeevafk/agent-skills.git && cd agent-skills && ./install-global-skills.sh
```

After opening a new shell:

```bash
global-skills status
# or
gskills status
```

## What This Repository Contains

- `global-skills.sh` — Sync, install, backup, and monitor skills across agents
- `install-global-skills.sh` — Installer for PATH-based setup + config bootstrapping
- `codex-exclusive-skills.sh` — Manage Codex-only skills and optionally propagate
- `scripts/security/system/setup-system-monitoring.sh` — Portable system-security setup template
- `docs/skill-triggers.md` — Reference for prompting skills
- `docs/` — Setup and operational documentation

## Config File

Global root paths are loaded from:

- `~/.global-skills.conf`

Initialize default config:

```bash
global-skills init-config
```

Override config file location for a command:

```bash
GLOBAL_SKILLS_CONFIG=/path/to/custom.conf global-skills status
```

## Commands

```bash
global-skills status
global-skills sync
global-skills backup
global-skills add mattpocock/skills
global-skills add obra/superpowers --skill systematic-debugging
```

## Recommended Skill Combinations

### Minimal Viable Setup

- `global-skills add mattpocock/skills --skill caveman --skill diagnose --skill zoom-out`
- `global-skills sync`

### Security-First Setup

- `global-skills add mattpocock/skills --skill qa --skill diagnose`
- Use repository security template: `scripts/security/system/setup-system-monitoring.sh`
- Pair with docs: `docs/SYSTEM_SECURITY_SETUP.md` and `docs/TIRITH_SETUP.md`

### Senior Engineer Mode

- `global-skills add mattpocock/skills --skill grill-with-docs --skill qa --skill diagnose --skill zoom-out`
- Use `docs/skill-triggers.md` for repeatable prompt structure
- Keep periodic backups: `global-skills backup`

## Included Matt Pocock Skills

The repository includes these curated skills from [mattpocock/skills](https://github.com/mattpocock/skills):

- `caveman`
- `diagnose`
- `grill-with-docs`
- `qa`
- `setup-matt-pocock-skills`
- `zoom-out`

Location: `./skills/mattpocock/`

## Related Docs

- `docs/AGENT_RULES_BOOKS_SETUP.md`
- `docs/CODEX_EXCLUSIVE_SKILLS.md`
- `docs/MATTPOCOCK_SKILLS_SELECTION.md`
- `docs/SYSTEM_SECURITY_SETUP.md`
- `docs/TIRITH_SETUP.md`
- `docs/skill-triggers.md`

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT. See [LICENSE](LICENSE).
