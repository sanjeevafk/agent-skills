# Agent Skills Warehouse

A curated cold-storage warehouse and offline catalog of 2,140+ specialized agent skill suites across Claude Code, Google Antigravity, OpenAI Codex, OpenCode, and Pi.

## Architecture

1. **Active Runtime Tier (`canonical/`, mirrored to `~/.agents/skills/`):** Streamlined set of **16 core daily drivers** (<1,200 prompt tokens per turn) including `agent-reach`, `skill-router`, `code-review`, `systematic-debugging`, `tdd`, `humanizer`, and `bro`.
2. **Cold-Storage Warehouse (`collections/` & `skills/`):** **2,125 specialized domain playbooks** across **28 domain collections** (LLM security & red-teaming, Golang, Rust, design systems, cybersecurity, Hugging Face, bioinformatics, financial modeling), retrievable JIT in <0.5 ms.

## Recent Upgrades & Ingestions

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
* **Warehouse Skill:** Available on-demand via [`canonical/skill-evals`](canonical/skill-evals) and [`skills/skill-evals`](skills/skill-evals).

## Research Benchmark

This repository serves as the artifact and benchmark testbed for the empirical software engineering paper:

> **Measuring the Floor Before Claiming the Null: Agent Skill-File Delivery Formats in an LLM-Judged Coding Benchmark** (SANER 2027 RENE track submission)

### Key Findings

- **Detection-limited null:** Evaluated five skill-file delivery strategies across 396 blind judged runs (18-task engineering benchmark; Qwen 3.7 Flash generating, DeepSeek V4 Pro judging a 35-point rubric) and 87 ablations. Total spread across arms is 0.68 points.
- **Noise floor:** Test-retest noise floor is **sigma = 5.37** (pooled within-cell across all 396 runs).
- **Power analysis:** Task-blocked paired SD is **sigma_d = 3.76** (17 task pairs), setting the minimum detectable effect at **MDE = 2.72 points** (80% power, alpha = 0.05). The observed 0.275-point difference is only 10.1% of the detection threshold. Distinguishing these strategies would require ~1,500 task pairs.
- **Position bias:** Significant slot-position bias in the judging window (spread = 3.63 points, A minus D, within-window permutation p = 0.000014, sign test p = 0.000186) exceeds the treatment effect by 13x.

### Authoritative Figures

| Metric | Value | Verification Script |
|:--|--:|:--|
| Noise floor sigma | **5.37** | `scripts/verify_noise_floor.py` |
| Task-paired SD sigma_d | **3.76** (17 pairs) | `scripts/verify_noise_floor.py` |
| MDE (80% power, exact noncentral t) | **2.72** | `scripts/verify_noise_floor.py` |
| Observed difference vs MDE | **10.1%** | `scripts/verify_noise_floor.py` |
| Required task pairs | **1,473** | `scripts/verify_noise_floor.py` |
| Window-centred position spread | **3.63** (p < 0.00005) | `scripts/analyze_position_blocks.py` |
| Position spread sign test (A > D) | 52/73 (p = 0.000186) | `scripts/analyze_position_blocks.py` |
| Position bias vs treatment effect | **13x** | `scripts/analyze_position_blocks.py` |

### Reproducing Results

```bash
uv run python scripts/verify_noise_floor.py        # Recompute sigma, sigma_d, MDE
uv run pytest tests/ -q                            # Run full claim-integrity test suite
uv run python scripts/analyze_position_blocks.py   # Run block-aware position bias analysis
uv run python scripts/verify_compiled_artifacts.py # Verify compiled checklist reproducibility
uv run python scripts/measure_tokens_real.py --check # Tokenizer-measured compression check
```

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
