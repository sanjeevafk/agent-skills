# Operations & Rules Reference Guide

This document combines the instructions for managing agent skills, static reference rulesets, Codex exclusives, and trigger shortcuts.

---

## 1. Skill Triggers & Prompting Cheat Sheet

To trigger installed agent skills reliably, mention their name explicitly using this pattern:
```text
Use the <skill-name> skill for this task.
Task: <description of task>
```

### Prompt Triggers Reference
* **Code Reviews & Quality**: `code-reviewer`, `code-review-and-quality`, `pr-review-expert`
* **Refactoring**: `code-refactor`
* **Planning & Scaffolding**: `planning-and-task-breakdown`, `feature-planning`, `fullstack-feature-scaffold`
* **Testing & TDD**: `testing-loop-master`, `test-driven-development`
* **Framework Experts**: `nextjs-15-expert`, `supabase-expert`, `tailwind-radix-expert`
* **Sentry Errors**: `sentry-workflow`, `sentry-sdk-setup`
* **Git Workflows**: `git-workflow-and-versioning`, `git-pushing`
* **GSD Workflows**: `gsd-plan-phase`, `gsd-execute-phase`, `gsd-progress`, `gsd-verify-work`

---

## 2. Agent Rules Books Reference

Rules Books are static **reference files** (policies and patterns) rather than executable skills. 

### Available Rulebooks
1. `a-philosophy-of-software-design.md` — Deep modules, information hiding.
2. `clean-architecture.md` — Dependency rule, layer separation.
3. `clean-code.md` — Clean names, short functions, error patterns.
4. `code-complete.md` — Quality construction, defensive checks.
5. `designing-data-intensive-applications.md` — Consistency, partitions, scaling.
6. `domain-driven-design-distilled.md` — Bound contexts, simple aggregates.
7. `domain-driven-design.md` — Ubiquitous language, entities vs value objects.
8. `implementing-domain-driven-design.md` — Aggregates, repositories, ACLs.
9. `patterns-of-enterprise-application-architecture.md` — Persistence, transactions.
10. `refactoring.md` — Behavior-preserving structural changes.
11. `release-it.md` — Timeout, retries, circuit-breakers.
12. `the-pragmatic-programmer.md` — DRY, orthogonality, automation.
13. `working-effectively-with-legacy-code.md` — Seams, characterization tests.

### Management Commands
```bash
# Sync local rules to all agent folders (Cursor, Copilot, Gemini, etc.)
./install-rules-books.sh sync

# Check rule installation status
./install-rules-books.sh status
```

### How to Reference in Prompts
Explicitly point your agent to the local file or mention it in the prompt:
```text
Review this new module using the "clean-architecture" and "clean-code" rules.
```

---

## 3. Codex-Exclusive Skills

The directory `~/.codex/skills/` contains 14 skills that are isolated from canonical roots to serve as experimental channels or platform-specific tools.

### Exclusive Skills Matrix

| Category | Skill Name | Purpose |
|----------|------------|---------|
| **Deployment** | `cloudflare-deploy`, `vercel-deploy`, `render-deploy` | Platform deployments. |
| **GitHub** | `gh-address-comments`, `gh-fix-ci`, `yeet` | PR handling and CI debugging via GitHub CLI. |
| **Browser** | `playwright`, `playwright-interactive`, `screenshot` | Playwright browser automation and captures. |
| **Data / Sec** | `jupyter-notebook`, `security-best-practices`, `security-threat-model`, `security-ownership-map` | Notebook scaffolding and deep code/security analysis. |
| **Monitoring** | `sentry` | Querying Sentry endpoints. |

### Propagation CLI (`codex-exclusive-skills.sh`)
```bash
# Compare local Codex setup vs canonical roots
./codex-exclusive-skills.sh compare

# Propagate all exclusive skills globally
./codex-exclusive-skills.sh propagate

# Selectively propagate specific skills
./codex-exclusive-skills.sh propagate --skill vercel-deploy --skill sentry
```

---

## 4. Upstream Skills Selection (Matt Pocock Audit)

On **1 May 2026**, an audit of the `mattpocock/skills` repository was completed. Out of 22 skills, **6 unique skills** were added, while the other 16 duplicate skills were skipped:

### Added Skills
1. `caveman` (75% token reduction instructions)
2. `diagnose` (Disciplined debugging loop)
3. `grill-with-docs` (Challenging plans against domain models)
4. `qa` (File bugs conversationally)
5. `setup-matt-pocock-skills` (Config scaffolding)
6. `zoom-out` (High-level codebase views)

### Skipped Duplicates
* `tdd`, `improve-codebase-architecture`, `design-an-interface`, `write-a-skill`, `ubiquitous-language`, `migrate-to-shoehorn`, `scaffold-exercises`, `setup-pre-commit`, `git-guardrails-claude-code`, `obsidian-vault`, `edit-article`, `request-refactor-plan`, `triage`, `to-issues`, `to-prd`, `grill-me`.

---

## 5. Workspace Integration & Utilities

This repository integrates local configurations and custom tools to compile and protect multi-environment developer workflows.

### 5.1 Borrowed Workspace Skills
We borrow key high-value skills from companion repositories directly into the local `./skills` directory:
1. `create-cli` — Language-agnostic CLI specification and usability design rules (from `agent-scripts`).
2. `brain-to-docs` — Q&A-driven loop to extract vision and decisions into READMEs and ADRs (from `davidondrej-skills`).
3. `interview-style-doc-building` — Strategic document builder that updates files incrementally without generative filler (from `davidondrej-skills`).

### 5.2 Skill Compiler (`scripts/export_skills.py`)
The compilation script detects and aggregates skills under the local `./skills` directory (with optional path flags for external folders if needed).
By default, the command `./global-skills.sh export` compiles these skills into a unified target (`.agentrules`, etc.).

### 5.3 Skill Frontmatter Validator (`scripts/validate_skills.py`)
This tool checks that all markdown-based skills under the local `./skills` folder conform to quality standards before synchronization:
* Validates YAML frontmatter parsing syntax.
* Enforces that `name` and `description` are defined and are non-empty strings.
* Scans for name conflicts/collisions.

Run the validation suite via:
```bash
python3 scripts/validate_skills.py
```

### 5.4 Stale Lock & Safe Git Committer (`scripts/committer.sh`)
This helper script secures git operations against accidental broad staging and environment index locks:
* Restores broad staged changes before operation.
* Stages only the explicit file paths passed.
* Detects and removes stale `.git/index.lock` locks using the `--force` flag.

Run the committer utility via:
```bash
bash scripts/committer.sh [--force] "feat: your commit message" path/to/file1 path/to/file2
```

