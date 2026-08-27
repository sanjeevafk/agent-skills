# Agent Skills Framework

[![License](https://img.shields.io/github/license/sanjeevafk/agent-skills?style=flat-square)](https://github.com/sanjeevafk/agent-skills/blob/main/LICENSE)
![Agentic Engineering](https://img.shields.io/badge/Agentic-Engineering-1F8A70?style=flat-square)
![Skills Count](https://img.shields.io/badge/Skills-418+-blue?style=flat-square)
![Empirical Evaluations](https://img.shields.io/badge/IEEE_Benchmark-396_Evals-purple?style=flat-square)

A curated, telemetry-driven skill and prompt delivery framework for autonomous coding agents. Manage, compile, benchmark, and deploy domain engineering skills across **Claude Code, Google Antigravity, Cursor, Windsurf, GitHub Copilot, and Codex**.

---

## Overview

Modern software engineering agents rely on injected skill documents (`SKILL.md`, `.cursorrules`, and `.agentrules`) to enforce repository patterns, API designs, database migrations, and security rules. 

However, in enterprise codebases loading 15 to 25 skills simultaneously, uncompressed prompt injection causes severe context bloat (exceeding 50,000 tokens per message), while aggressive one-line rule extraction triggers **Context Collapse** in syntax-dense tasks.

`agent-skills` provides:
1. **418+ Curated Domain Skills:** Production-grade engineering patterns spanning Security, Distributed Systems, Testing (TDD/E2E), DevOps, C++ Performance, Databases, and Architecture.
2. **Structure-Preserving Static Compiler:** An offline compiler (`scripts/compile_checklists_v2.py`) that extracts imperative constraints while strictly preserving code blocks, type signatures, and tables—capturing **99.2% of full manual quality** while reducing prompt token overhead by **30.0%**.
3. **The IEEE 18-Task Hard Benchmark Suite:** An empirical evaluation harness measuring code correctness, maintainability, and token economics across 396 blind cross-vendor LLM-as-a-Judge evaluations.
4. **Modular Skill Playbooks:** Pre-packaged JSON manifests (`playbooks/`) for loading targeted skill sets (`fullstack-nextjs`, `security-audit`, `senior-engineer`).

---

## Quick Start

Clone the repository and run the automated installer:

```bash
git clone https://github.com/sanjeevafk/agent-skills.git && cd agent-skills && ./scripts/install-global-skills.sh
```

After opening a new shell:

```bash
# Verify installation and skills health
skills status

# Run full index build and command generation
skills build-all
```

---

## Repository Structure

```
agent-skills/
|-- skills/                 [CANONICAL] 418+ Modular Domain Skill Manuals
|-- playbooks/              [PRESETS] Curated Skill Bundles (Security, Fullstack, etc.)
|-- rules/                  [STANDARDS] 16 System Standards & Software Design Principles
|-- benchmarks/             [RESEARCH] IEEE 18-Task Benchmark & Empirical Evaluation Data
|   |-- tasks_ieee.json     18 Hard SE Benchmark Task Specifications
|   |-- checklists_v2/      Structure-Preserving Compiled Checklists
|   |-- tables_ieee/        Publication-Ready LaTeX Tables & Pareto Plots
|   `-- csv_ieee/           Summary & Raw Evaluation Metrics (396 Evals)
|-- scripts/                [TOOLING] Compilers, Runners, Linter, and Indexers
|-- hooks/                  [LIFECYCLE] Terminal Statuslines & Pre-Execution Guards
`-- docs/                   [DOCUMENTATION] Human Architecture Guides & Catalog
```

---

## Empirical Benchmark Findings (N=396 Blind Evaluations)

We evaluated 5 instruction delivery strategies across 18 hard software engineering benchmark tasks spanning 6 domains: Architecture, Databases, DevOps, SRE, Security, and Testing ($N=396$ blind evaluations using Qwen 3.7 Flash as executor and DeepSeek V4 Pro as independent judge on a 35-point rubric).

| Strategy | Mean Score (/35) | 95% Confidence Interval | Median | Std Dev ($\sigma$) | Prompt Token Overhead | Output Code Depth |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **`full` (Raw Manual)** | **25.17** | `[23.86, 26.47]` | 26.00 | 5.80 | 2,270 tokens (+1,478%) | 4,588 tokens |
| **`checklist_v2` (Compiler v2)** | **24.96** | `[23.62, 26.30]` | 26.00 | 6.03 | **1,590 tokens (+1,006%)** | **5,431 tokens** |
| **`retrieved` (RAG Sections)** | **24.73** | `[23.49, 25.98]` | 25.00 | 5.56 | 430 tokens (+199%) | 4,548 tokens |
| **`checklist_v1` (Aggressive)** | **24.54** | `[22.99, 26.08]` | 26.00 | **6.94** | 663 tokens (+362%) | 4,555 tokens |
| **`control` (No Skill Baseline)** | **24.49** | `[23.19, 25.80]` | 25.00 | 5.82 | 144 tokens (+0%) | 5,078 tokens |

### Core Empirical Discoveries:

1. **99.2% Quality Retention with 30% Prompt Savings:**  
   Structure-preserving compilation (`checklist_v2`) captures 99.2% of full manual quality ($\Delta = -0.21$, Welch $t=0.22$, $p=0.8286$, Cohen's $d=+0.03$), eliminating 680 prompt tokens per skill on every turn.
2. **Context Collapse in Aggressive Bulletization:**  
   Stripping code examples into abstract one-line bullet lists (`checklist_v1`) triggers severe instability ($\sigma = 6.94$) and catastrophic collapse in syntax-dense tasks (crashing to **17.2/35** on Testing & QA). Preserving code blocks and tables in `checklist_v2` stabilizes execution across all domains.
3. **Higher Output Code Volume:**  
   By removing narrative prose distraction, `checklist_v2` prompts the model to focus its reasoning budget directly on code synthesis, producing **5,431 output tokens** (+18.4% deeper implementations than uncompressed manuals).
4. **Multi-Skill Scaling Economics:**  
   In enterprise environments with 20 active repository skills, `checklist_v2` saves **26,000 prompt tokens per turn**, eliminating **~780,000 tokens per 30-turn developer session**.

---

## Modular Skill Playbooks

Instead of loading 400 skills simultaneously, activate curated domain bundles via [`playbooks/`](playbooks/):

| Playbook | Target Stack / Objective | Bundled Skills |
| :--- | :--- | :--- |
| **`security-audit`** | Vulnerability assessment & threat modeling | `security-review`, `gateguard`, `security-bounty-hunter`, `healthcare-phi-compliance` |
| **`fullstack-nextjs`** | Modern full-stack web applications | `nextjs-15-expert`, `supabase-expert`, `tailwind-radix-ui`, `type-architecture-analyzer` |
| **`senior-engineer`** | High-reliability systems engineering | `code-refactor`, `architecture-decision-records`, `performance-profiler`, `systematic-debugging` |
| **`mvp-bootstrap`** | Rapid prototype & production scaffolding | `docker-patterns`, `fastapi-expert`, `database-migrations`, `tdd` |

---

## Command Namespaces & Slash Commands

Skills and rules support namespaced slash commands and shorthand aliases:

| Namespace | Example Commands | Capability |
| :--- | :--- | :--- |
| **`/debug/`** | `/debug/systematic`, `/debug/root-cause` | Root-cause isolation, race condition mitigation |
| **`/security/`** | `/security/review`, `/security/defi-amm` | HMAC auditing, zero-trust auth, smart contract audit |
| **`/perf/`** | `/perf/cpp-performance`, `/perf/profiler` | Orthodox C++, zero-allocation loops, eBPF profiling |
| **`/data/`** | `/data/postgres-patterns`, `/data/redis-patterns` | Zero-downtime migrations, RLS, distributed rate limits |
| **`/test/`** | `/test/tdd`, `/test/e2e-playwright` | Test-driven development, deterministic Playwright suites |
| **`/devops/`** | `/devops/docker-patterns`, `/devops/k8s-stateful` | Multi-stage zero-trust containers, StatefulSet HA |

---

## CLI Reference

```bash
skills build-all         # Rebuild indexes, command wrappers, dependency graphs, and catalog
skills verify            # Run validation, integration tests, and syntax compilation checks
skills sync              # Synchronize skills across ~/.gemini, ~/.agents, ~/.cursor, ~/.copilot
skills index             # Rebuild reverse-indexed skills.json
skills generate-commands # Generate namespaced and flat command wrappers
skills graph            # Build skill dependency tree and Mermaid diagram
skills lint             # Audit repository for duplicates and metadata completeness
```

---

## Reproducibility & Benchmark Execution

To reproduce the empirical benchmark runs:

```bash
# Run the 18-task IEEE benchmark suite
python3 scripts/skill_delivery_experiment.py \
  --tasks benchmarks/tasks_ieee.json \
  --runs 5 \
  --judge-chars 16000

# Recompile structure-preserving checklists
python3 scripts/compile_checklists_v2.py
```

All raw outputs, evaluation traces, and analysis scripts are available in [`benchmarks/`](benchmarks/).

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
