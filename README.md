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

Clone the repository and run the installation script. The installer will copy the `global-skills` utility to your `~/.local/bin`, write a configuration file, add standard aliases/PATH values to your shell config, and **automatically import and sync all curated repository skills** into your agent environments:

```bash
git clone https://github.com/sanjeevafk/agent-skills.git && cd agent-skills && ./scripts/install-global-skills.sh
```

After opening a new shell:

```bash
global-skills status
# or
gskills status
```

## What This Repository Contains

- `scripts/global-skills.sh` — Sync, install, backup, monitor, and **export** skills across agents
- `scripts/install-global-skills.sh` — Installer for PATH-based setup + config bootstrapping
- `scripts/codex-exclusive-skills.sh` — Manage Codex-only skills and optionally propagate
- `scripts/export_skills.py` — Compile skills into `.cursorrules`, `.windsurfrules`, or `copilot-instructions.md`
- `scripts/convert_html_guide.py` — Convert upstream HTML style guides to agent-readable Markdown
- `scripts/security/system/setup-system-monitoring.sh` — Portable system-security setup template
- `.github/workflows/sync-styleguides.yml` — Weekly auto-sync of Google Style Guides from upstream
- `docs/skill-triggers.md` — Reference for prompting skills
- `docs/` — Setup and operational documentation
- `exports/` — Auto-generated client-specific rule files (do not edit manually)

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
global-skills export --format all
global-skills export --format cursor --include google-style-python,google-style-typescript
global-skills export --format copilot --output-dir ~/my-project
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

## Included Curated Skills

The repository includes a highly curated set of specialized skills:

### Engineering & Reliability
- `google-eng-practices` — Codifies Google's Code Health philosophy for reviewers and authors
- `nasa-jpl-power-of-ten-python` — Adapts NASA's safety-critical coding rules for Python/FastAPI

### Google Style Guides (Language-Specific)
- `google-style-common` — Cross-language principles: naming philosophy, comment standards
- `google-style-python` — Full Python style guide with Review and Writing modes
- `google-style-typescript` — TypeScript-specific rules (types, enums, visibility, `any` avoidance)
- `google-style-javascript` — JavaScript rules (ES modules, JSDoc, `const`/`let`, arrow functions)
- `google-style-go` — Go guide across three layers: rules, best practices, and decisions
- `google-style-java` — Java guide (2-space indent, K&R braces, Javadoc, import ordering)
- `google-style-cpp` — C++ guide (no exceptions, smart pointers, naming, header hygiene)

### Type & Architecture
- `type-architecture-analyzer` — Expert TypeScript type system design and refactoring

### Matt Pocock Skills
Selected from [mattpocock/skills](https://github.com/mattpocock/skills):
- `caveman`
- `diagnose`
- `grill-with-docs`
- `qa`
- `setup-matt-pocock-skills`
- `zoom-out`

Location: `./skills/`

## Exporting Skills to Other Clients

Compile all local skills into formats consumable by Cursor, Copilot, and Windsurf:

```bash
# Export all formats at once
global-skills export --format all

# Export only for Cursor, into a specific project
global-skills export --format cursor --output-dir ~/my-project

# Export a subset of skills
global-skills export --format copilot --include google-style-python,google-style-typescript,google-eng-practices
```

Or run the script directly:

```bash
python3 scripts/export_skills.py --format all --skills-dir ./skills --output-dir ./exports
python3 scripts/export_skills.py --list   # see all available skills
```

Output files:

| Format | File |
|---|---|
| Cursor | `.cursorrules` |
| GitHub Copilot | `.github/copilot-instructions.md` |
| Windsurf | `.windsurfrules` |

## Upstream Style Guide Sync

Google Style Guides in `skills/google-style-*/references/full_guide.md` are kept
in sync with [google/styleguide](https://github.com/google/styleguide) via a
weekly GitHub Action (`.github/workflows/sync-styleguides.yml`).

To trigger a manual sync:
1. Go to **Actions → Sync Google Style Guides → Run workflow**
2. Optionally specify which guides: `js,ts,cpp,java,go`

The workflow opens a PR with diffs if upstream guides have changed. `quick_reference.md`
files are **not** auto-updated — manual review is required when core rules change.

## Related Docs

- `docs/.agent.md` — Contributor guide and workspace governance model
- `docs/ENGINEERING_PRINCIPLES.md` — Engineering principles and response style standards
- `docs/AGENT_RULES_BOOKS_SETUP.md`
- `docs/CODEX_EXCLUSIVE_SKILLS.md`
- `docs/MATTPOCOCK_SKILLS_SELECTION.md`
- `docs/SYSTEM_SECURITY_SETUP.md`
- `docs/TIRITH_SETUP.md`
- `docs/skill-triggers.md`

## Workspace Governance & Model Harness Framework

This repository **experiments with** a model harness approach — systematic governance and resource management designed to improve non-frontier AI code generation.

### Components

1. **Engineering Principles** (`docs/ENGINEERING_PRINCIPLES.md`)
   - Lightweight reference (500 tokens vs 35K for full rule books)
   - File-type-specific loading instead of global pollution
   - Core philosophy, decision trees, and tech-specific patterns

2. **Contributor Guide** (`docs/.agent.md`)
   - Quality standards for skill contributions
   - Response style enforcement (no emojis, clear formatting)  
   - Skill discovery optimization through precise when-to-use descriptions

3. **Security Harness** (`scripts/security/`, `docs/TIRITH_SETUP.md`)
   - Pre-deploy vulnerability scanning
   - Supply chain integrity checks
   - Code pattern auditing

### Honest Assessment: Partial Implementation

**What the setup accomplishes:**

- Token efficiency: 80-93% reduction in overhead rules (35K → 2K per session)
- Consistency: Canonical rules enforced across all agents
- Governance: Clear quality standards and security practices
- Structure: Reproducible across multiple agent environments (Copilot, Cursor, Claude)

**What's actually unproven:**

- No baseline metrics for code quality (before/after)
- No A/B testing framework to measure improvement
- No model-agnostic validation across different LLMs
- No performance benchmarks (error rates, hallucination patterns)
- No automated feedback loops to validate harness effectiveness
- No regression detection if governance changes degrade performance

**Claims we CANNOT make:**

We cannot claim this helps non-frontier models "punch above their weight" without data. The setup has good structure and efficiency, but we lack:
1. Comparative testing (same task with/without harness)
2. Baseline measurements (code quality metrics before deployment)
3. Model variance analysis (does it help Haiku vs Sonnet vs others differently?)
4. Ablation studies (which components actually matter?)

### What This Actually Is

A **governance and efficiency framework** that:
- Reduces token waste (proven: 35K → 2K)
- Establishes clear quality standards (process-level, not outcome-level)
- Scales across multiple agent contexts (infrastructure win)

**Not yet:** A validated model harness with measured impact on code generation quality.

### To Become a Robust Harness

Would need:
1. Baseline test suite (measure code quality without harness)
2. A/B testing framework (same prompts, measure delta)
3. Model-specific profiling (how does it impact different models?)
4. Automated metrics (error patterns, hallucination rate, code coverage)
5. Regression gates (changes must improve or hold metrics)

---

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT. See [LICENSE](LICENSE).
