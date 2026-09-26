# Operations & Architecture Guide

> Operational manual for managing skills, command namespaces, rule compilation, and multi-agent synchronization.

---

## 1. Single Source of Truth Architecture

All capabilities are maintained under two canonical directories:
* **`skills/`**: Modular skill manuals (`SKILL.md`).
* **`rules/`**: Baseline engineering standards, 14 book rulesets, and `/learn` directives.

All command wrappers (`commands/`), index registries (`skills.json`), static vector caches (`skills_embeddings.npy`, `skills_manifest.json`), dependency graphs (`docs/DEPENDENCY_GRAPH.md`), catalog docs (`docs/SKILLS_CATALOG.md`), and multi-IDE rules (`.agentrules`, `.cursorrules`, `.windsurfrules`, `copilot-instructions.md`) are **auto-generated build artifacts**.

---

## 2. CLI Tooling Reference (`gskills`)

```bash
# Build the complete pipeline end-to-end (indexes, playbooks, commands, vector cache)
gskills build-all

# Synchronize skills across ~/.gemini, ~/.agents, ~/.cursor, ~/.copilot, ~/.codex
gskills sync

# Rebuild skills.json index & synchronize static vector embeddings (skills_embeddings.npy)
gskills index

# Route queries via two-stage dense router (<0.2 ms shortlist + Laya cross-encoder)
python3 scripts/laya_router.py "How do I secure Django REST endpoints?"

# Auto-generate namespaced (/debug/, /web/, /rule/) and flat command wrappers
gskills generate-commands

# Resolve prerequisite dependency tree & render Mermaid graph
gskills graph

# Audit skills repository for potential duplicates and alias collisions
gskills lint

# Record and view skill usage analytics
gskills telemetry report

# Export multi-client IDE rules to a project folder
gskills export --format all --output-dir ~/my-project

# Create timestamped tar.gz backups of all agent environment roots
gskills backup
```

---

## 3. Command Namespaces & Slash Commands

Skills and rules are assigned namespaced commands for instant invocation:

* **`/debug/`**: Systematic debugging, root-cause isolation (`/debug/systematic`, `/debug/root-cause`).
* **`/web/`**: Modern web stack guidance (`/web/nextjs-15-expert`, `/web/supabase-expert`, `/web/tailwind-radix-expert`).
* **`/lang/`**: Language systems & interop (`/lang/python-ts-interop-mcp-builder`).
* **`/style/`**: Coding conventions (`/style/google-style-python`, `/style/google-ts`, `/style/nasa-jpl`).
* **`/gsd/`**: Milestone & phase management (`/gsd/plan-phase`, `/gsd/execute-phase`, `/gsd/progress`).
* **`/devops/`**: Deployment & containerization (`/devops/docker-patterns`, `/devops/vercel-deploy`).
* **`/rule/`**: Explicit rule invocation (`/rule/clean-code`, `/rule/user-global-rules`, `/rule/refactoring`).

---

## 4. Two-Stage Skill Routing & Cache Synchronization

To eliminate prompt bloat and 4+ minute runtime CPU re-embedding overhead across 440 skills, the repository maintains a hybrid two-stage router:

1. **Stage 1 (Dense Vector Shortlisting):** Uses a precomputed `(440, 384)` float32 vector matrix (`skills_embeddings.npy`, 660 KB) generated via `BAAI/bge-small-en-v1.5`. Live queries execute a matrix dot product in **0.15 ms on CPU**, retrieving the top-5 candidate skills with an average pairwise similarity of 0.567 (free of vector collapse).
2. **Stage 2 (Fine Cross-Attention):** Passes the top-5 candidate definitions to Laya's non-autoregressive cross-encoder (`convaiinnovations/laya`) to select the final skill with calibrated confidence in ~2.0s on CPU (<50 ms on GPU/ONNX).
3. **Automated Cache Maintenance:** Whenever skills are added, modified, or re-indexed via `scripts/build_index.py` or `skills build-all`, `_update_embeddings_cache()` automatically re-bakes `skills_embeddings.npy` and `skills_manifest.json` in ~10 seconds.
4. **Benchmark Verification:**
   * **Level 1 (Hit-Rate & Latency):** `scripts/benchmark_router.py` verifies Top-1 (55.6%) and Top-5 (61.1%) recall against 18 IEEE task prompts.
   * **Level 2 (End-to-End Task Quality):** `scripts/run_level2_benchmark.py` evaluates code synthesis with Qwen 3.7 Flash and blind 35-point DeepSeek V4 Pro rubric judging.


---

## 5. Multi-Client Rule Exports

When opening any project in Cursor, Windsurf, Copilot, or generic LLM harnesses, compile your rules into the target repository:

```bash
# Export all rule formats (.agentrules, .cursorrules, .windsurfrules, copilot-instructions.md)
gskills export --format all --output-dir ~/my-project
```

This ensures any AI assistant touching your project automatically inherits all 388 skill guidelines and 16 core engineering book rules.
