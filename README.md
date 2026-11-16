# Agent Skills Warehouse

A curated cold-storage warehouse and offline catalog of 2,330+ specialized agent skill suites across Claude Code, Google Antigravity, OpenAI Codex, OpenCode, and Pi.

## Quick Start

Binary media (images, audio, video) is kept out of git and published as release assets. After cloning, run `python3 scripts/fetch_media.py` once to restore it (checksums in `media.lock`). Search, indexing and skill text work without it.

```bash
./bin/agent-skills find "red teaming"   # keyword search (SQLite FTS5, BM25)
./bin/agent-skills show <skill>         # print a skill's content or path
./bin/agent-skills list                 # list collections
./bin/agent-skills stats                # index statistics
./bin/agent-skills index --force       # rebuild the search index
```

## Architecture

1. **On-Demand Router (`skills/skill-router` + `./bin/agent-skills`):** Single active entry point that discovers and loads specialized skills JIT in <0.5 ms without bloating the system prompt.
2. **Warehouse Storage (`collections/` & `skills/`):** **2,300+ specialized domain playbooks** across **34 domain collections** (LLM fine-tuning & MLOps, red-teaming & security, Golang, Rust, design systems, bioinformatics, financial modeling). Identical skills in `skills/` symlink to `collections/`.

## Recent Upgrades & Ingestions

- **NousResearch Hermes Agent Suite (`collections/hermes-agent`):** Ingested 175 novel, production-tested MLOps, LLM fine-tuning (`axolotl`, `accelerate`, `vllm`, `unsloth`, `peft`), multi-agent arbitration (`agent-merge-conflict-arbiter`, `adversarial-ux-test`), recursive knowledge vaults (`llm-wiki`), and domain research playbooks (`arxiv`, `grounded-citations`, `bioinformatics`, `evm`, `solana`), de-duplicating 35 overlaps.
- **`be-ambitious` Task Elevation (`skills/be-ambitious` & `canonical/be-ambitious`):** Autonomous and flagged (`--depth`, `--altitude`, `--range`, `--all`) meta-skill elevating prompts across Altitude (durable systems), Depth (primary sources, expert tools, outside judge), and Range (noun-to-verb, adversarial red teaming). Inspired by Felix Rieseberg's essay [How to Be More Ambitious: A Tutorial for Humans with Models](https://felixrieseberg.com/how-to-be-more-ambitious-a-tutorial-for-humans-with-models/) and DannyMac180's [`be-ambitious`](https://github.com/DannyMac180/skills/tree/main/be-ambitious).
- **Promptfoo Red-Teaming & Evals Suite (`collections/ai-evals-promptfoo`):** Ingested first-party agent skills from Promptfoo for non-adversarial eval suites, target provider setups, threat mapping, and redteam vulnerability scans.
- **Golang Production Skills (`collections/golang-skills`):** Ingested 46 Go playbooks by Samuel Berthe (`samber/cc-skills-golang`) covering concurrency, DI, and performance.
- **BeautifulRust Idiomatic Suite (`collections/rust-skills`):** Ingested Rust guidelines distilled from Google, Microsoft, and official API conventions.
- **Design & UI-to-Motion Systems (`collections/design-skills`):** Ingested landing page architecture and showcase motion design playbooks from `elayadesign`.
- **Web Security SAST (`collections/web-security`):** Ingested Song Jianyang's 14-layer static XSS SAST audit skill (`songjianyang/xss-audit`).
- **Media Production Additions (`collections/media-production`):** Added `openscreen-demo` for screen recording, zooming, and demo video production via OpenScreen MCP.
- **English-First Purge & Hardening:** Pruned 1,400+ translation duplicates across 14 language subdirectories to enforce English-first catalog integrity.
- **Search Engine Optimization (`bin/agent-skills`):** Upgraded SQLite FTS5 engine to weighted BM25 (`bm25(skills_fts, 10.0, 2.0, 1.0, 0.0)`) with exact-match bonus and sub-millisecond retrieval (<0.5 ms).
- **Active Runtime Streamlining:** Pruned 52+ redundant/niche skills to cold storage, leaving a focused 16-skill active core and saving ~3,000 prompt tokens per turn.
- **English Anti-Slop Standard:** Deployed official 60.5k-star English [`blader/humanizer`](https://github.com/blader/humanizer) v3.1.0 into active runtime.
- **Harness Scripts Preserved:** Archived skill evaluation and linting harnesses to `bin/eval_harness/`.

## Skill Evaluation & Quality Gates

All skills in this warehouse are evaluated and pre-screened using the 3-arm evaluation harness and pre-activation quality linter in [**`sanjeevafk/agent-skill-evals`**](https://github.com/sanjeevafk/agent-skill-evals).

* **Linter & Density Gate:** Enforces directive density (>= 1.5 directives/KB), spec formatting, and security checks via `skill-lint`.
* **3-Arm Empirical Evaluation:** Benchmarks candidate skills against Baseline (Arm A) and Length Control (Arm C) via `skill-eval`.
* **Audit Suite:** Sweeps active directories for context bloaters via `skill-audit`.
* **NVIDIA SkillEvaluator CI (Tier 1, Advisory):** Runs no-LLM static, security (`SkillSpector`, `Gitleaks`, `Semgrep`, `bandit`), PII/Unicode, and cross-harness compatibility checks on changed `skills/**` and `collections/**` in PRs via [`.github/workflows/skill-checks.yml`](.github/workflows/skill-checks.yml).
* **Warehouse Skill:** Available on-demand via [`skills/skill-evals`](skills/skill-evals).

## Skill Discovery & Search Architecture

Skill retrieval is powered by a high-precision **Weighted BM25 search engine** ([`scripts/search_skills.py`](scripts/search_skills.py)):
* **Zero Overhead:** 100% local, sub-millisecond retrieval (<0.3ms) with zero model/API calls or vector databases.
* **Token Normalization:** Automatically splits and indexes `camelCase`, `snake_case`, and `kebab-case` code identifiers.
* **Field Weighting:** Prioritized field scoring (Name: 3.0, Tags: 2.0, Description: 1.0) with Robertson-Spärck Jones IDF and document length normalization ($k_1=1.2, b=0.75$).

## Commands

```bash
# High-speed FTS5 search (<0.5ms) across 2,100+ skills
agent-skills find <query>

# Print full skill content or file path
agent-skills show <skill-name>
agent-skills show <skill-name> -p

# Rebuild catalog SQLite FTS5 index
agent-skills index --force

# Inspect warehouse statistics
agent-skills stats

# Search skills via legacy Weighted BM25 Python script
uv run python scripts/search_skills.py <query>
```
