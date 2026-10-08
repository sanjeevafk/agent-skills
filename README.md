# Agent Skills Warehouse

A curated cold-storage warehouse and offline catalog of specialized agent skill suites across **Claude Code, Google Antigravity, OpenAI Codex, OpenCode, and Pi**.

---

## 1. System Architecture: Two-Tier Model

To prevent context collapse and 20,000+ token prompt bloat while retaining deep domain knowledge, the environment uses a strict two-tier architecture:

```
+--------------------------------------------------------------------------+
|                       ACTIVE RUNTIME (~/.agents/skills)                  |
|          75 Canonical Skills -- Linked across all 5 Agent Harnesses      |
|           Zero Context Bloat -- 100% Frontier LLM Attention Recall       |
+--------------------------------------------------------------------------+
                                     ^
                                     |  Promoted on demand
                                     v
+--------------------------------------------------------------------------+
|                     COLD STORAGE WAREHOUSE (agent-skills)                |
|           1,700+ Specialized Skills & Domain Collections Offline         |
|      Planned 60ms Local Hierarchical Routing via Julia-1 (No Cloud Tokens) |
+--------------------------------------------------------------------------+
```

1. **Active Runtime (`~/.agents/skills/`, mirrored in `canonical/`):** Exactly 75 hardened, non-redundant production skills wired into daily coding agents. Consumes $<2,500$ prompt tokens per message turn.
2. **Cold Storage Warehouse (`agent-skills/`):** Comprehensive offline archive preserving specialized industry, scientific, security, and enterprise playbooks.

---

## 2. Present Suites & Collection Inventory

| Suite / Collection | Location | Size | Primary Attributes & Scope |
|---|---|---|---|
| **Canonical Active Suite** | `canonical/` | **76 skills** | Curated production skills for full-stack engineering, testing (`tdd`, `veriharness`, `playwright`), security (`security-audit`), design (`impeccable`, `frontend-design`, `oil-motion`, `remotion`), research (`last30days`, `orx`), and architecture (`archify`, `nextjs-15-expert`). |
| **Core Modular Catalog** | `skills/` | **413 skills** | Flat skill manuals indexed across 9 semantic namespaces (`web`, `workflow`, `lang`, `ai-ml`, `security`, `debug`, `devops`, `style`, `data`). |
| **Cybersecurity Suite** | `collections/cybersecurity-skills/` | **818 skills** | Threat emulation, defensive posture, and compliance playbooks mapped to MITRE ATT&CK, NIST CSF 2.0, MITRE ATLAS, and D3FEND. |
| **Upstream ECC Suite** | `collections/ecc-upstream/` | **293 skills** | Complete upstream Everything Claude Code (ECC) ecosystem: subagents, slash commands, workflow hooks, system rules, and framework patterns. |
| **Scientific & Life Sciences** | `collections/scientific-skills/` | **117 skills** | Bioinformatics, genomics (`scanpy`, `biopython`), computational chemistry (`rdkit`, `diffdock`), and quantum computing (`qiskit`, `cirq`). |
| **Academic Research Suite** | `collections/academic-research-skills/` | **5 modules** | End-to-end academic paper authoring pipeline, citation anti-hallucination verification, LaTeX/APA formatting, and simulated peer-review. |
| **Enterprise Ops** | `collections/enterprise-ops/` | **39 skills** | Brand discovery, executive positioning, enterprise onboarding, and organizational workflow templates. |
| **Media Production** | `collections/media-production/` | **9 skills** | Algorithmic video generation, Manim explainers, and media asset pipelines. |
| **Reference Architectures** | `collections/reference-architectures/` | **28 systems** | Production RAG (Docling, LightRAG, Mem0, Graphiti, n8n) and web scraping pipelines (Crawl4AI v2, Ottomarkdown, PydanticAI) with distilled skill playbooks. |
| **Kaggle Suite** | `collections/kaggle-skills/` | **3 skills** | Official Kaggle hackathon judging workflows, standardized agent examinations, and benchmark authoring (`kbench`, `kaggle-benchmarks`). |
| **Hugging Face Suite** | `collections/huggingface-skills/` | **25 skills** | Official Hugging Face Hub workflows, CLI/MCP tooling, datasets, spaces, evaluation, and model training (TRL, Sentence Transformers, SageMaker). |
| **Impeccable Design Suite** | `collections/impeccable/` | **24 commands** | Comprehensive anti-slop frontend design system, 59 deterministic detector rules, UX critique/audit, and live browser rendering loop. |
| **Open Code Review Suite** | `collections/open-code-review/` | **2 skills** | Alibaba's enterprise AI code review engine (`ocr`), diff-level review, full repo audits (`ocr scan`), and host-agent delegation mode. |

---

## 3. Planned Routing: Local Decision Modeling

Rather than loading large skill catalogs into frontier prompts or relying on lossy vector embeddings (which yield a ~39% retrieval miss rate), the planned router uses **`SupersonicLabs/Julia-1`** (a 144.3M open-weights non-generative decision model based on `mmBERT-small`):

- **Hierarchical Tree Routing:** Evaluates prompts in two rapid stages ($\le 20$ candidates each):
  1. *Stage 1 (Domain level):* Classifies the query into 1 of the 9 catalog namespaces (~35 ms).
  2. *Stage 2 (Skill level):* Evaluates the candidates within that namespace (~35 ms).
- **Latency & Footprint:** Runs in **$<70$ ms end-to-end on commodity CPU** with a 550 MB FP32 memory footprint.
- **Zero Cloud Cost:** 100% offline, zero cloud tokens spent, and deep cross-attention decision accuracy.

---

## 4. Quick Commands

```bash
# Rebuild the catalog index (skills.json)
uv run python scripts/build_index.py

# Check status of canonical skills
ls -la canonical/
```
