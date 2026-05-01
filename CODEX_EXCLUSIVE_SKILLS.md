# Codex-Exclusive Skills

This document describes the 14 skills that exist **only** in `~/.codex/skills/` and are not automatically synced to other agent environments (agents, copilot, cursor, antigravity).

## Why Are They Exclusive?

The `global-skills.sh` sync mechanism follows a **canonical roots** model:
- **Canonical**: agents, copilot, cursor, antigravity (authoritative source)
- **Dependent**: codex (isolated by design)

This separation may be intentional because:
1. **Some skills are Codex-specific** (e.g., use Codex-only APIs)
2. **Experimental phase** (skills being tested before wider rollout)
3. **Deployment strategy** (Codex gets newer skills first)

---

## All 14 Codex-Exclusive Skills

### Deployment / Platform

| Skill | Purpose |
|-------|---------|
| **cloudflare-deploy** | Deploy to Cloudflare (Workers, Pages, etc.) — Use when deploying to Cloudflare infrastructure |
| **vercel-deploy** | Deploy to Vercel — Use for Next.js/frontend deployments to Vercel |
| **render-deploy** | Deploy to Render — Use for full-stack apps on Render's platform |

### GitHub / CI-CD

| Skill | Purpose |
|-------|---------|
| **gh-address-comments** | Address GitHub PR review comments — Use `gh CLI` to respond to review feedback on current branch |
| **gh-fix-ci** | Debug failing GitHub Actions — Use to inspect CI failures, logs, and draft fixes |
| **yeet** | Quick push & PR — Stage, commit, push, and open PR with GitHub CLI in one flow |

### Browser Automation

| Skill | Purpose |
|-------|---------|
| **playwright** | Automate real browser actions — Navigate, fill forms, capture, extract data via `playwright-cli` |
| **playwright-interactive** | Interactive UI debugging — Use `js_repl` for iterative browser/Electron debugging |
| **screenshot** | System-level screenshots — Capture desktop, window, or pixel region when tool capture unavailable |

### Data & Notebooks

| Skill | Purpose |
|-------|---------|
| **jupyter-notebook** | Create/edit Jupyter notebooks — Scaffold `.ipynb` files for experiments/tutorials |

### Security Analysis

| Skill | Purpose |
|-------|---------|
| **security-best-practices** | Language-specific security reviews — Audit Python, JS/TS, Go for secure-by-default patterns |
| **security-ownership-map** | Bus factor & secure code ownership — Analyze git history to find orphaned/high-risk code |
| **security-threat-model** | Threat modeling — Enumerate trust boundaries, assets, abuse paths for a codebase |

### Monitoring

| Skill | Purpose |
|-------|---------|
| **sentry** | Sentry error monitoring — Query Sentry issues, recent errors, health metrics |

---

## Usage

### Make these skills available everywhere

```bash
# Make the script executable
chmod +x <repo-root>/codex-exclusive-skills.sh

# Add to .bashrc for convenience
echo "alias gcodex='<repo-root>/codex-exclusive-skills.sh'" >> ~/.bashrc
source ~/.bashrc
```

### See all Codex-exclusive skills with descriptions

```bash
<repo-root>/codex-exclusive-skills.sh list
# or via alias:
gcodex list
```

### Propagate ALL Codex-exclusive skills to canonical roots

```bash
<repo-root>/codex-exclusive-skills.sh propagate
```

After this runs:
- All 14 Codex-exclusive skills are copied to `~/.agents/skills`, `~/.copilot/skills`, `~/.cursor/skills`, `~/.gemini/antigravity/skills`
- Codex keeps its copy (no deletion)

### Selectively propagate specific skills

```bash
# Propagate only deployment skills
gcodex propagate --skill cloudflare-deploy --skill vercel-deploy --skill render-deploy

# Propagate security skills
gcodex propagate --skill security-best-practices --skill security-threat-model --skill security-ownership-map
```

### Remove a skill from Codex (destructive)

```bash
# Delete yeet from Codex only
gcodex remove-from-codex yeet

# Delete multiple
gcodex remove-from-codex yeet playwright render-deploy
```

### Compare Codex vs Canonical

```bash
gcodex compare
```

Output:
```
=== Codex vs Canonical Roots ===

Skills ONLY in Codex (exclusive):
     1  cloudflare-deploy
     2  gh-address-comments
     3  ...

Skills in BOTH:
     1  agent-development
     2  ci-cd-pipeline-builder
     ...

Summary:
  Codex total: 156
  Exclusive: 14
  Shared: 142
```

---

## Recommended Workflow

### Option A: Keep Codex Isolated (Current)
- Leave `codex-exclusive-skills.sh` as a utility
- Only propagate specific skills when needed
- Codex remains an experimental channel

**Command**: Run `gcodex propagate --skill <name>` on-demand

### Option B: Consolidate (Make Codex Canonical)
- Run `gcodex propagate` once to sync all Codex skills globally
- Edit `global-skills.sh` to include Codex in `CANONICAL_ROOTS`
- From then on, `global-skills.sh sync` will keep all agents in sync

**Commands**:
```bash
gcodex propagate
# Edit global-skills.sh line 11:
# CANONICAL_ROOTS=("$ROOT_AGENTS" "$ROOT_COPILOT" "$ROOT_CURSOR" "$ROOT_ANTIGRAVITY" "$ROOT_CODEX")
```

### Option C: Selective Propagation (Recommended)
- Keep Codex as the testing ground
- Propagate skills to all agents only after they're proven
- Use `gcodex propagate --skill <name>` to promote skills

**Commands**:
```bash
# Test a skill in Codex for a while...
gcodex list

# When ready, promote to all agents:
gcodex propagate --skill security-threat-model

# Run normal sync to keep canonical in sync:
global-skills sync
```

---

## Integration with global-skills.sh

After running `gcodex propagate`, the skills are in all canonical roots. To keep them there:

```bash
# Modify global-skills.sh to include Codex in canonical discovery:
sed -i 's/CANONICAL_ROOTS=(.*$/CANONICAL_ROOTS=("$ROOT_AGENTS" "$ROOT_COPILOT" "$ROOT_CURSOR" "$ROOT_ANTIGRAVITY" "$ROOT_CODEX")/' \
  global-skills
```

Or manually edit `~/.../agent-skills/global-skills.sh` line 11.

---

## Monitoring

Check status of Codex vs canonical:

```bash
echo "=== Current Status ==="
echo "Agents: $(ls ~/.agents/skills | wc -l)"
echo "Copilot: $(ls ~/.copilot/skills | wc -l)"
echo "Cursor: $(ls ~/.cursor/skills | wc -l)"
echo "Antigravity: $(ls ~/.gemini/antigravity/skills | wc -l)"
echo "Codex: $(ls ~/.codex/skills | wc -l)"
echo ""
echo "Exclusive to Codex: $(<repo-root>/codex-exclusive-skills.sh list | grep '[a-z]' | wc -l)"
```

---

## FAQ

### Q: Why isn't Codex in canonical roots?

A: By design—it allows Codex to be a test channel for new/experimental skills before they're promoted.

### Q: If I propagate a skill, does `global-skills.sh sync` keep it synced?

A: **Only if** the operator add `$ROOT_CODEX` to `CANONICAL_ROOTS` in `global-skills.sh`. Otherwise, propagated skills stay static.

### Q: Can I undo a propagate?

A: Yes, manually delete from other roots or restore from backup:
```bash
global-skills backup  # create backup first
# ...later...
tar -xzf ~/.skills/backups/<snapshot><root-archive>.tar.gz -C /
global-skills sync
```

### Q: What if a Codex-exclusive skill gets overwritten when I sync with global-skills.sh?

A: It won't be touched—`sync` only copies skills from canonical roots. Codex-only skills are isolated.

### Q: Should I use these skills (are they production-ready)?

A: Yes. They're in Codex because they're either:
- Platform-specific (cloudflare-deploy, vercel-deploy, render-deploy)
- Experimental but functional (security-* suite, playwright-interactive)
- Bleeding-edge (gh-* commands, depending on latest GitHub CLI features)

Start with `--skill` propagation to test before going all-in.

---

## Script Reference

### codex-exclusive-skills.sh

```bash
# List descriptions of all Codex-exclusive skills
<repo-root>/codex-exclusive-skills.sh list

# Propagate all Codex-exclusive skills to canonical roots
<repo-root>/codex-exclusive-skills.sh propagate

# Propagate specific skills only
<repo-root>/codex-exclusive-skills.sh propagate --skill cloudflare-deploy --skill security-threat-model

# Remove skills from Codex
<repo-root>/codex-exclusive-skills.sh remove-from-codex gh-fix-ci yeet

# Compare skill distribution
<repo-root>/codex-exclusive-skills.sh compare
```

---

## Next Steps

1. **Review** the exclusive skills via `gcodex list`
2. **Decide**: Keep isolated (Option A), consolidate (Option B), or selective (Option C)?
3. **Act**: Run the appropriate command above
4. **Document**: Add the choice to team conventions in `skill-triggers.md`
