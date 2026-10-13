# Agent Skills Warehouse

A curated cold-storage warehouse and offline catalog of 2,700+ specialized agent skill suites across Claude Code, Google Antigravity, OpenAI Codex, OpenCode, and Pi.

## Architecture

1. **Active Runtime Tier (`canonical/`, mirrored to `~/.agents/skills/`):** Hardened suite of ~75 production skills wired into active coding agents (<2,500 prompt tokens per turn).
2. **Cold-Storage Warehouse (`skills/` & `collections/`):** 556 modular skills across 9 core engineering domains and 2,200+ specialized domain playbooks (cybersecurity, Hugging Face, bioinformatics, financial modeling, reference architectures), loaded dynamically on demand.

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

## Commands

```bash
# Search skills by keyword
uv run python scripts/search_skills.py <keyword>

# Rebuild catalog index (skills.json)
uv run python scripts/build_index.py

# Validate frontmatter YAML across all skills
uv run python scripts/check_frontmatter.py
```
