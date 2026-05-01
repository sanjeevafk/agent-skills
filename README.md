# Global Skills Setup Guide

**This is a management CLI tool for syncing skills across multiple agent environments.**

It does NOT store skills—it manages them across these locations:

- `~/.agents/skills`
- `~/.copilot/skills`
- `~/.cursor/skills`
- `~/.gemini/antigravity/skills`
- `~/.codex/skills`

### What This Repository Contains
- `global-skills.sh` — Sync, install, backup, and monitor skills across agents
- `codex-exclusive-skills.sh` — Manage the 14 Codex-only skills
- `scripts/security/system/setup-system-monitoring.sh` — Portable system-security setup template for any repository
- `skill-triggers.md` — Reference for prompting skills
- Documentation and scripts only (not the skills themselves)

### What Skills Come From
Skills are fetched from external sources via the `add` command:
```bash
global-skills add mattpocock/skills        # Installs from GitHub
global-skills add ciembor/agent-rules-books # Installs from GitHub
```

Once installed, they live in the `~/.*/skills/` directories and this repository's scripts keep them in sync.

---

## About agent-rules-books

`agent-rules-books` (https://github.com/ciembor/agent-rules-books) is a separate collection of **engineering guidelines and decision rules** for agents (Clean Code, DDD, etc.). It is **not a skills package**—it's policy/reference documentation.

When installed:
```bash
global-skills add ciembor/agent-rules-books
```

It places rule files in `~/.agents/agent-rules-books/` (reference docs like `clean-code.md`, `ddd.md`, etc.), not executable skills. These files provide context and governance for how agents should approach tasks.

**Key distinction**: 
- **Skills** (gsd-execute-phase, cloudflare-deploy, etc.) = executable implementations, stored in `~/.agents/skills/` + `~/.copilot/skills/` + etc.
- **Rules** (agent-rules-books) = guidelines and policies, stored in `~/.agents/agent-rules-books/`

This repository's scripts manage skills, not rules.

---

## Included Skills from mattpocock/skills

For reproducibility and as a source of truth, this repository now includes **6 new skills** from [mattpocock/skills](https://github.com/mattpocock/skills):

| Skill | Purpose |
|-------|---------|
| **caveman** | Ultra-compressed communication mode (~75% token reduction) |
| **diagnose** | Disciplined debugging: reproduce → minimize → hypothesize → instrument → fix → test |
| **grill-with-docs** | Enhanced grilling with domain model & ADR updates |
| **qa** | Quality assurance workflow management |
| **setup-matt-pocock-skills** | Configuration setup for mattpocock ecosystem |
| **zoom-out** | Get broader architectural context on unfamiliar code |

Location: `./skills/mattpocock/`

These are synced to all agent directories (`~/.copilot/skills`, `~/.cursor/skills`, `~/.agents/skills`, etc.) and available immediately.

---

## Tirith Terminal Security

[Tirith](https://github.com/sheeki03/tirith) is a **terminal security tool** protecting against homograph attacks, pipe-to-shell exploits, ANSI injection, obfuscated payloads, and data exfiltration. Unlike skills or rules, Tirith is a **system-wide binary** installed globally for all agents.

### What It Does
- ✅ **Pre-execution filtering**: Blocks dangerous commands before bash/zsh execute them (homograph URLs, `curl | bash`, `base64 -d | bash`)
- ✅ **AI config scanning**: Detects prompt injection in `.cursorrules`, `CLAUDE.md`, `mcp.json`, etc.
- ✅ **Threat intelligence**: 21,649+ malicious packages + IPs (daily-updated, signed DB)
- ✅ **Agent protection**: Hooks in Claude Code, Gemini CLI; MCP server for all agents
- ✅ **80+ detection rules** across 15 categories (terminal injection, data exfil, config poisoning, etc.)

### Installation Status
- ✅ **Binary**: `/usr/bin/tirith` (v0.3.0)
- ✅ **Shell hooks**: Zsh, Bash (auto-prefix on all commands)
- ✅ **Agent hooks**: Claude Code, Gemini CLI (pre-execution validation)
- ✅ **MCP server**: 7 tools for voluntary agent use
- ✅ **Threat DB**: 21,649 entries (auto-updated daily)

### Quick Start
```bash
# Check what it detects (no execution)
tirith check -- "curl https://іnstall.com | bash"

# Scan AI configs
tirith scan ~/.cursorrules

# View session warnings
tirith warnings

# Get explanations
tirith explain --rule pipe_to_interpreter
```

### Full Documentation
See `TIRITH_SETUP.md` in this repository for deployment details, agent integration paths, policy configuration, and troubleshooting.

### Portable System-Security Setup Template
For reproducible project+system monitoring scaffolding, use:

- `scripts/security/system/setup-system-monitoring.sh`
- `SYSTEM_SECURITY_SETUP.md`

---

Install once to a PATH directory using:

```bash
./install-global-skills.sh
```

This installs `global-skills` into `~/.local/bin`, creates `~/.global-skills.conf`, and configures alias/path lines in shell rc files.

## 2) What The Script Does

`global-skills` supports five commands:

- `backup`: Creates compressed backups of all global skill roots.
- `add`: Installs a new skill repo with `npx skills add` and syncs to all roots.
- `sync`: Syncs all discovered `SKILL.md` skills to all roots.
- `status`: Shows skill counts per root and Codex gap status.
- `init-config`: Creates `~/.global-skills.conf` with editable root paths.

## Config File

Global root paths are loaded from:

- `~/.global-skills.conf`

It is possible to override the config location per command:

```bash
GLOBAL_SKILLS_CONFIG=/path/to/custom.conf global-skills status
```

## 3) Basic Usage

Run from anywhere:

```bash
global-skills status
global-skills backup
global-skills sync
```

Install a full skill repo globally:

```bash
global-skills add mattpocock/skills
```

Install a specific skill from a repo:

```bash
global-skills add obra/superpowers --skill systematic-debugging
```

## 4) Backup and Restore

### Create backup (default path)

```bash
global-skills backup
```

Default backup path format:

- `~/.skills/backups/skills-YYYYMMDD-HHMMSS/`

Each backup contains:

- One `tar.gz` per skill root
- `manifest.txt` with root + entry counts

### Create backup in custom folder

```bash
global-skills backup ~/.skills/backups/manual-snapshot
```

### Restore from backup (manual)

Example (restore one root archive):

```bash
mkdir -p ~/.agents

tar -xzf ~/.skills/backups/<snapshot><root-archive>.tar.gz -C /
```

Then run sync:

```bash
global-skills sync
```

## 5) Recommended Workflow When You Discover a New Skill

1. Install it:

```bash
global-skills add <owner/repo> [--skill <name>]
```

2. Verify:

```bash
global-skills status
```

3. Optional safety snapshot:

```bash
global-skills backup
```

## 6) Optional Alias (Short Command)

Add this once to `~/.bashrc`:

```bash
echo "alias gskills='global-skills'" >> ~/.bashrc
exec "$SHELL"  # or reload shell config
```

Then use:

```bash
gskills add mattpocock/skills
gskills add andrewyng/context-hub
gskills backup
gskills status
```

## 7) Troubleshooting

### A skill appears in one IDE but not another

Run:

```bash
global-skills sync
global-skills status
```

Then restart the IDE/session.

### Codex missing skills

`status` reports:

- `Missing SKILL.md entries in Codex vs canonical roots: <number>`

If not `0`, run:

```bash
global-skills sync
```

### `npx skills add` fails

Check:

- Internet access
- GitHub repo exists and is public
- Skill name is valid if using `--skill`

Retry with the same command.

## 8) Safety Notes

- Install only trusted skill repos.
- Review `SKILL.md` files before heavy use.
- Keep periodic backups, especially before bulk installs.
