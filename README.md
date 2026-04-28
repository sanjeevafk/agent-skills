# Global Skills Setup Guide

This guide explains how to use your global multi-agent skills setup.

It works across these agent environments:

- `~/.agents/skills`
- `~/.copilot/skills`
- `~/.cursor/skills`
- `~/.gemini/antigravity/skills`
- `~/.codex/skills`

## 1) Script Location

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
