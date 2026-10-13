# Agent Skills Warehouse

A curated cold-storage warehouse and offline catalog of 2,700+ specialized agent skill suites across **Claude Code, Google Antigravity, OpenAI Codex, OpenCode, and Pi**, designed to prevent prompt bloat and context collapse in daily agent sessions.

---

## 1. What This Repository Is

To preserve frontier LLM attention and eliminate 20,000+ token per-turn overhead, the environment uses a strict two-tier architecture:

1. **Active Runtime Tier (`canonical/`, mirrored to `~/.agents/skills/`):** A minimal, hardened suite of ~75 production skills wired into active coding agents (<2,500 prompt tokens per turn).
2. **Cold-Storage Warehouse (`skills/` & `collections/`):** An offline repository housing **556 modular skills** across 9 core engineering domains and **2,200+ specialized domain playbooks** (cybersecurity MITRE/NIST, Hugging Face, bioinformatics, financial modeling, and reference architectures), bridged dynamically on-demand via `skill-router`.

---

## 2. Accompanying Research Paper

This repository is the artifact and benchmark testbed for an empirical software engineering paper submitted to the **SANER 2027 Reproducibility Studies and Negative Results (RENE) track**:

> **Measuring the Floor Before Claiming the Null: Agent Skill-File Delivery Formats in an LLM-Judged Coding Benchmark**

### What the study found

The study compared five skill-file delivery strategies across 396 blind judged runs on an 18-task engineering benchmark (Qwen 3.7 Flash generating, DeepSeek V4 Pro judging a 35-point rubric), plus 87 ablation runs.

**The headline result is a detection-limited null.** No delivery strategy measurably changed output quality: the entire five-arm range is 0.68 points on a 35-point rubric. Rather than report that as "no significant difference," the paper measures the instrument first. The test-retest floor, pooled within-cell across all 396 runs, is **σ = 5.37**; against the task-blocked design actually used (σ_d = 3.76 over 17 task pairs) the minimum detectable effect at 80% power is **2.72 points**. The observed 0.27-point gap is **10.1% of that threshold**, so the benchmark cannot distinguish these arms — which is a statement about measurement power, not evidence of equivalence. Closing the question would take roughly 1,500 task pairs rather than 17.

One component does clear the floor: aggressive rule bulletization (70.8% compression) drops the Testing & QA domain by −6.32 points at n = 11. We report this as a **preliminary warning requiring replication**, not a finding.

### Claims this repository has withdrawn

Three earlier results from our own work were withdrawn after re-analysis, and the corrections are recorded in [`benchmarks/MANUSCRIPT_CORRECTIONS.md`](benchmarks/MANUSCRIPT_CORRECTIONS.md):

- **A syntax-collapse effect** (Δ = −8.50, n = 6) **reversed sign** when re-run at n = 15 with a matched control. An earlier version of this README presented it as a finding; that was wrong.
- **An output-volume advantage** for `checklist_v2`, which a stray `[INSTRUCTION]` directive explains by ~82%.
- **A router-accuracy figure** whose baseline was a mis-specified hand-weighted scorer.

### Claims this repository could not reproduce

The paper's own headline power analysis was wrong until audited, and we report that too. An earlier draft quoted σ = 6.09 from "42 runs on byte-identical prompts", σ_d = 7.87 over "78 pairs", and an MDE of 2.53. **No run subset of size 42 exists in the archive and no code produced any of those figures.** Our first correction then introduced a *second* error, applying the two-sample MDE formula (which carries a √2 factor for independent means) to a paired design. Both errors, and the invariants that now prevent them, are documented in §7 of the paper and enforced by tests.

### Reproducing the reported numbers

```bash
uv run python scripts/verify_noise_floor.py    # sigma, sigma_d, MDE, required n
uv run pytest tests/ -q                        # claim-integrity suite, 67 tests
uv run python scripts/verify_compiled_artifacts.py   # 18/18 byte-identical
uv run python scripts/measure_tokens_real.py --check # tokenizer-measured compression
```

Compression figures are measured with real BPE tokenizers, not a character heuristic: the cl100k_base reduction is **28.56%**, not the 30.41% the old `len//4` estimate produced.

## 3. Quick Commands

```bash
# Search skills by keyword
uv run python scripts/search_skills.py <keyword>

# Rebuild catalog index (skills.json)
uv run python scripts/build_index.py

# Validate SKILL.md frontmatter blocks
uv run python scripts/check_frontmatter.py

# Run compiler verification on benchmarks
uv run python scripts/verify_compiled_artifacts.py
```
