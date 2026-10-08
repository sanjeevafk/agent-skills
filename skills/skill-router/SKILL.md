---
name: skill-router
description: >-
  Dynamically discover, retrieve, and load specialized domain skills from the offline cold-storage
  agent-skills warehouse (2,000+ playbooks) when a user request requires capabilities outside the
  active canonical set. Use whenever the task involves financial modeling (DCF, LBO, M&A), Hugging Face Hub/TRL,
  Kaggle competitions/judging, fframes video, academic paper drafting, cybersecurity MITRE playbooks,
  C++ DOD optimization, bioinformatics, or agentic design patterns.
---

# Skill Router (Dynamic Warehouse Bridge)

The active environment maintains exactly 76 canonical production skills to preserve context memory and eliminate prompt bloat. All remaining 2,000+ domain skills reside in the offline **Agent Skills Warehouse** (`agent-skills`).

Use this router to dynamically discover and load any specialized warehouse skill into your working context on-demand.

---

## 1. When to Use the Router

Trigger this router whenever the user asks for a capability outside the 76 canonical engineering skills, including:
- **Financial Services & Valuation:** DCF modeling, LBO transactions, 3-statement modeling, equity research, credit analysis, pitch decks.
- **AI / Machine Learning Ecosystems:** Hugging Face Hub, TRL fine-tuning (SFT, DPO, GRPO), Kaggle benchmarks/judging (`kbench`), Gradio apps.
- **Media & Creative:** `fframes-video` (GPU Skia/Rust/SVG rendering), Fal.ai media pipelines, VideoDB indexing.
- **Cybersecurity & Compliance:** MITRE ATT&CK / ATLAS threat emulation, NIST CSF 2.0 compliance, red-teaming prompts, forensic disk acquisition.
- **Agent Architecture Patterns:** 21 production patterns (prompt chaining, routing, A2A communication, HITL, memory persistence, guardrails).
- **Domain Science & Engineering:** Bioinformatics (`scanpy`, `biopython`), computational chemistry (`rdkit`), quantum computing (`qiskit`), C++ data-oriented design.

---

## 2. Autonomous Retrieval Workflow

When a domain-specific request arrives, follow this 2-step retrieval loop:

### Step 1: Find the relevant skill
Run `agent-skills find` with 1-3 keywords describing the domain:

```bash
agent-skills find <keywords>
```

**Examples:**
```bash
agent-skills find dcf
agent-skills find "lbo model"
agent-skills find fframes
agent-skills find trl
agent-skills find "prompt chaining"
```

The CLI returns matching skills ranked by relevance in $<5$ ms, indicating `[ACTIVE]` (already in memory) or `[COLD]` (in warehouse storage).

### Step 2: Load the playbook into context
Once identified, fetch the full skill content or file path:

```bash
# Print full skill content directly to stdout
agent-skills show <skill-name>

# Or get the exact file path to view with file tools
agent-skills show <skill-name> --path-only
```

**Examples:**
```bash
agent-skills show dcf-model
agent-skills show fframes-video
agent-skills show pattern-prompt-chaining
```

### Step 3: Execute the task
Apply the instructions, templates, and patterns loaded from the skill to satisfy the user's prompt. You do not need to keep the skill permanently loaded; once the task turn finishes, context naturally recycles.

---

## 3. Useful Router Commands

| Command | Purpose |
|---|---|
| `agent-skills find <query>` | Sub-5ms FTS5 keyword search across all 2,000+ skills |
| `agent-skills show <skill>` | Prints full `SKILL.md` content directly |
| `agent-skills show <skill> -p` | Prints only the absolute filesystem path |
| `agent-skills list [collection]` | Lists all domain collections or skills within one collection |
| `agent-skills stats` | Shows live warehouse index counts and storage stats |
| `agent-skills index --force` | Re-indexes the warehouse database |
