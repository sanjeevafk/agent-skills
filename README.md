# Agent Skills Warehouse

A curated cold-storage warehouse and offline catalog of specialized agent skill
suites across **Claude Code, Google Antigravity, OpenAI Codex, OpenCode, and Pi**.

---

## 1. System Architecture: Two-Tier Model

To prevent context collapse and 20,000+ token prompt bloat while retaining deep
domain knowledge, the environment uses a strict two-tier architecture:

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
|           531 Skills & Domain Collections Offline                        |
+--------------------------------------------------------------------------+
```

1. **Active Runtime (`~/.agents/skills/`, mirrored in `canonical/`):** Exactly 75
   hardened, non-redundant production skills wired into daily coding agents.
   Consumes $<2,500$ prompt tokens per message turn.
2. **Cold Storage Warehouse (`agent-skills/`):** Comprehensive offline archive
   preserving specialized industry, scientific, security, and enterprise
   playbooks.

---

## 2. Suites & Collection Inventory

| Suite / Collection | Location | Size | Primary Attributes & Scope |
|---|---|---|---|
| **Canonical Active Suite** | `canonical/` | **75 skills** | Curated production skills for full-stack engineering, testing (`tdd`, `veriharness`, `playwright`), security (`security-audit`), design (`impeccable`, `frontend-design`, `oil-motion`, `remotion`), research (`last30days`, `orx`), architecture (`archify`, `nextjs-15-expert`), and dynamic routing (`skill-router`). |
| **Core Modular Catalog** | `skills/` | **531 skills** | Flat skill manuals indexed across 9 semantic namespaces (`web`, `workflow`, `lang`, `ai-ml`, `security`, `debug`, `devops`, `style`, `data`). |
| **Cybersecurity Suite** | `collections/cybersecurity-skills/` | **818 skills** | Threat emulation, defensive posture, and compliance playbooks mapped to MITRE ATT&CK, NIST CSF 2.0, MITRE ATLAS, and D3FEND. |
| **Upstream ECC Suite** | `collections/ecc-upstream/` | **1027 skills** | Complete upstream Everything Claude Code (ECC) ecosystem: subagents, slash commands, workflow hooks, system rules, and framework patterns. |
| **Scientific & Life Sciences** | `collections/scientific-skills/` | **119 skills** | Bioinformatics, genomics (`scanpy`, `biopython`), computational chemistry (`rdkit`, `diffdock`), and quantum computing (`qiskit`, `cirq`). |
| **Financial Services** | `collections/financial-services/` | **112 skills** | Anthropic's official financial agents and vertical plugins: private equity, investment banking, equity research, valuation, and fund administration. |
| **Enterprise Ops** | `collections/enterprise-ops/` | **42 skills** | Brand discovery, executive positioning, enterprise onboarding, and organizational workflow templates. |
| **Reference Architectures** | `collections/reference-architectures/` | **28 systems** | Production RAG (Docling, LightRAG, Mem0, Graphiti, n8n) and web scraping pipelines (Crawl4AI v2, Ottomarkdown, PydanticAI) with distilled skill playbooks. |
| **Hugging Face Suite** | `collections/huggingface-skills/` | **26 skills** | Official Hugging Face Hub workflows, CLI/MCP tooling, datasets, spaces, evaluation, and model training (TRL, Sentence Transformers, SageMaker). |
| **Agentic Design Patterns** | `collections/agentic-design-patterns/` | **21 systems** | Production agent architectures from Antonio Gulli's textbook: prompt chaining, dynamic routing, parallelization, reflection, tool use, memory tiers, MCP, guardrails, and discovery loops. |
| **Media Production** | `collections/media-production/` | **8 skills** | Algorithmic video generation (Remotion, fframes, Manim), screen capture, and media asset pipelines. |
| **Claude Agent Architectures** | `collections/claude-agent-architectures/` | **8 systems** | Distilled blueprints from `claude-cookbooks`: Chief of Staff, SRE incident responder, vulnerability detector, agent observability, specialist coordinator, production guardrails, outcome grading, and issue-to-PR pipeline. |
| **Academic Research Suite** | `collections/academic-research-skills/` | **5 modules** | End-to-end academic paper authoring pipeline, citation anti-hallucination verification, LaTeX/APA formatting, and simulated peer-review. |
| **Impeccable Design Suite** | `collections/impeccable/` | **6 skills** | Comprehensive anti-slop frontend design system, deterministic detector rules, UX critique/audit, and live browser rendering loop. |
| **Kaggle Suite** | `collections/kaggle-skills/` | **4 skills** | Official Kaggle hackathon judging workflows, standardized agent examinations, and benchmark authoring (`kbench`, `kaggle-benchmarks`). |
| **Open Code Review Suite** | `collections/open-code-review/` | **4 skills** | Alibaba's enterprise AI code review engine (`ocr`), diff-level review, full repo audits (`ocr scan`), and host-agent delegation mode. |

---

## 3. Skill Selection at Scale: Measured, Not Assumed

An earlier revision of this README advertised a planned `Julia-1` hierarchical
router at <70 ms end-to-end on commodity CPU. **That approach was built and
benchmarked, and it does not pay for itself** at this catalogue size.

Over 17 held-out queries against a 522-routable-skill catalogue:

| Approach | Top-1 | Top-5 | p50 |
|---|---:|---:|---:|
| Dense retriever | 7/17 | 11/17 | — |
| Dense + Julia-1 rerank | **5/17** | 11/17 | 401 ms |
| Lexical TF-IDF | **8/17** | 11/17 | 1.75 ms |
| Union of both shortlists | — | **14/17** | — |
| **No retrieval — whole catalogue in context** | **14/17** | — | ~18k tokens |

Shortlist recall is identical across all three retrieval methods, so coverage is
not the limit — the reranker is. It measurably *reduced* Top-1 accuracy over
dense shortlisting alone (41.2% → 29.4%), overriding a correct shortlist hit in
6 of 11 cases. Because removing retrieval entirely matches the union oracle
ceiling, **at this catalogue scale shortlisting buys nothing a single in-context
pass does not already deliver.**

Practical guidance: treat both retrieval and reranking as **optional layers to
be measured against an oracle ceiling**, not defaults to be added. The numbers
above are reproducible from `benchmarks/` via `scripts/benchmark_router.py`.

---

## 4. Quick Commands

```bash
# Rebuild the catalog index (skills.json)
uv run python scripts/build_index.py

# Validate that every SKILL.md frontmatter block parses
uv run python scripts/check_frontmatter.py

# Compile every skill with frontmatter preserved (dry run)
uv run python scripts/compile_and_deploy.py --dry-run

# Check status of canonical skills
ls -la canonical/
```

Compile a single skill programmatically:

```python
import sys; sys.path.insert(0, "scripts")
import skills_compiler as sc

text, metrics = sc.compile_skill(
    open("skills/tdd/SKILL.md").read(),
    sc.checklist_v2("testing"),          # domain-aware code-block budget
)
print(metrics["token_reduction_percentage"])
```

---

## 5. Licensing

**This repository ships no single blanket license, and should not acquire one
without scoping it.**

| Content | Terms |
|---|---|
| `scripts/`, `canonical/`, and skills authored for this repository | *no license granted yet* |
| `collections/` (15,070 files) | **retain their upstream licenses** — Apache-2.0, MIT, and CC BY-NC 4.0 are all present |
| Any path shipping its own `LICENSE` (`skills/archify`, `skills/bro`, `skills/oil-motion`, `skills/attention-span`, …) | governed by that file |

Before adding a root `LICENSE`, three things need settling:

1. **`skills/attention-span/` is AGPL-3.0.** AGPL is copyleft and cannot be
   relicensed MIT by the author for anyone who already received it under those
   terms. Its own LICENSE file correctly isolates it.
2. **`collections/academic-research-skills/` is CC BY-NC 4.0** (© Cheng-I Wu).
   Non-commercial terms are incompatible with a permissive repository license,
   so that path must retain its own.
3. **`skills/archify/node_modules/` — 4,172 vendored files are committed.** This
   is a dependency tree carrying dozens of third-party licenses; it should be
   git-ignored and installed on demand rather than vendored.

The recommended arrangement is **MIT for authored work with an explicit scope
clause** excluding `collections/` and any path carrying its own `LICENSE`,
accompanied by a `THIRD_PARTY_NOTICES.md` recording each vendored collection's
provenance and terms. No root `LICENSE` has been added — that decision is
outstanding.