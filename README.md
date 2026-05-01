# Global Skills Setup Guide

**This is a management CLI tool for syncing skills across multiple agent environments.**

It does NOT store skills—it manages them across these locations:

- `~/.agents/skills`
- `~/.copilot/skills`
- `~/.cursor/skills`
- `~/.gemini/antigravity/skills`
- `~/.codex/skills`

### What This Repo Contains
- `global-skills.sh` — Sync, install, backup, and monitor skills across agents
- `codex-exclusive-skills.sh` — Manage the 14 Codex-only skills
- `skill-triggers.md` — Reference for prompting skills
- Documentation and scripts only (not the skills themselves)

### What Skills Come From
Skills are fetched from external sources via the `add` command:
```bash
~/Downloads/global-skills.sh add mattpocock/skills        # Installs from GitHub
~/Downloads/global-skills.sh add ciembor/agent-rules-books # Installs from GitHub
```

Once installed, they live in the `~/.*/skills/` directories and this repo's scripts keep them in sync.

---

## About agent-rules-books

`agent-rules-books` (https://github.com/ciembor/agent-rules-books) is a separate collection of **engineering guidelines and decision rules** for agents (Clean Code, DDD, etc.). It is **not a skills package**—it's policy/reference documentation.

When installed:
```bash
~/Downloads/global-skills.sh add ciembor/agent-rules-books
```

It places rule files in `~/.agents/agent-rules-books/` (reference docs like `clean-code.md`, `ddd.md`, etc.), not executable skills. These files provide context and governance for how agents should approach tasks.

**Key distinction**: 
- **Skills** (gsd-execute-phase, cloudflare-deploy, etc.) = executable implementations, stored in `~/.agents/skills/` + `~/.copilot/skills/` + etc.
- **Rules** (agent-rules-books) = guidelines and policies, stored in `~/.agents/agent-rules-books/`

This repo's scripts manage skills, not rules.

---

## Included Skills from mattpocock/skills

For reproducibility and as a source of truth, this repo now includes **6 new skills** from [mattpocock/skills](https://github.com/mattpocock/skills):

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

Your helper script is intended to live in Downloads (outside project repos):

- `~/Downloads/global-skills.sh`

This keeps your project clean and gives you one reusable command for any repo.

## 2) What The Script Does

`global-skills.sh` supports four commands:

- `backup`: Creates compressed backups of all global skill roots.
- `add`: Installs a new skill repo with `npx skills add` and syncs to all roots.
- `sync`: Syncs all discovered `SKILL.md` skills to all roots.
- `status`: Shows skill counts per root and Codex gap status.

## 3) Basic Usage

Run from anywhere:

```bash
~/Downloads/global-skills.sh status
~/Downloads/global-skills.sh backup
~/Downloads/global-skills.sh sync
```

Install a full skill repo globally:

```bash
~/Downloads/global-skills.sh add mattpocock/skills
```

Install a specific skill from a repo:

```bash
~/Downloads/global-skills.sh add obra/superpowers --skill systematic-debugging
```

## 4) Backup and Restore

### Create backup (default path)

```bash
~/Downloads/global-skills.sh backup
```

Default backup path format:

- `~/.skills/backups/skills-YYYYMMDD-HHMMSS/`

Each backup contains:

- One `tar.gz` per skill root
- `manifest.txt` with root + entry counts

### Create backup in custom folder

```bash
~/Downloads/global-skills.sh backup ~/.skills/backups/manual-snapshot
```

### Restore from backup (manual)

Example (restore one root archive):

```bash
mkdir -p ~/.agents

tar -xzf ~/.skills/backups/<snapshot>/home_sanjeev_.agents_skills.tar.gz -C /
```

Then run sync:

```bash
~/Downloads/global-skills.sh sync
```

## 5) Recommended Workflow When You Discover a New Skill

1. Install it:

```bash
~/Downloads/global-skills.sh add <owner/repo> [--skill <name>]
```

2. Verify:

```bash
~/Downloads/global-skills.sh status
```

3. Optional safety snapshot:

```bash
~/Downloads/global-skills.sh backup
```

## 6) Optional Alias (Short Command)

Add this once to `~/.bashrc`:

```bash
echo "alias gskills='~/Downloads/global-skills.sh'" >> ~/.bashrc
source ~/.bashrc
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
~/Downloads/global-skills.sh sync
~/Downloads/global-skills.sh status
```

Then restart the IDE/session.

### Codex missing skills

`status` reports:

- `Missing SKILL.md entries in Codex vs canonical roots: <number>`

If not `0`, run:

```bash
~/Downloads/global-skills.sh sync
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
