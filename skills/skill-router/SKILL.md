---
name: skill-router
description: >-
  JIT discovery and on-demand loading of 2,400+ domain playbooks from the agent-skills warehouse (<5ms).
  MANDATORY PRE-FLIGHT: Query warehouse before non-trivial domain tasks including academic paper reviews,
  pitch decks/slides, hackathons, ML tuning (TRL/SFT/DPO), security/MITRE, financial modeling,
  bioinformatics, or specialized libraries outside the active canonical set.
---

# Skill Router (Dynamic Warehouse Bridge)

The active environment maintains a minimal set of canonical core skills to preserve context memory and eliminate prompt bloat. All remaining 2,400+ domain playbooks reside in the offline **Agent Skills Warehouse** (`agent-skills`).

Use this router to dynamically discover and load any specialized warehouse skill into your working context on-demand in <5ms.

---

## 1. When to Use the Router (Pre-Flight Trigger)

**Rule:** Before guessing, reinventing workflows, or answering domain questions purely from base weights, run a quick pre-flight search across the warehouse for:
- **Academic Research & Papers:** Paper reviews (`academic-paper-reviewer`, `research-paper-writing`), conference venue fitting (TMLR, NeurIPS, ICML), literature synthesis.
- **Competitions, Hackathons & Pitches:** Hackathon project planning (`devrelay-challenges`, `hackathon-judging`, `devrelay-mlh-submissions`), pitch decks & slides (`ppt-master`, `pitch-deck-creator`).
- **AI / ML Ecosystems:** Hugging Face Hub, TRL fine-tuning (`trl-grpo`, `sft`, `dpo`), Kaggle competitions (`kbench`), vLLM/Unsloth optimization.
- **Cybersecurity & Compliance:** MITRE ATT&CK / ATLAS threat emulation, NIST compliance, red-teaming prompts, forensic artifact recovery.
- **Financial Services & Valuation:** DCF modeling, LBO transactions, 3-statement modeling, equity research, credit analysis.
- **Domain Science & Engineering:** Bioinformatics (`scanpy`, `biopython`), chemistry (`rdkit`), quantum computing (`qiskit`), high-performance systems.
- **Agent Architecture Patterns:** 21 production multi-agent patterns (prompt chaining, routing, A2A communication, guardrails).

---

## 2. Autonomous Retrieval Workflow (2 Steps)

### Step 1: Query the Warehouse (<5ms)
Run `agent-skills find` with 1-3 keywords describing the domain or task:

```bash
agent-skills find <keywords>
```

**Examples:**
```bash
agent-skills find "paper review"
agent-skills find hackathon
agent-skills find "pitch deck"
agent-skills find dcf
agent-skills find trl
```

The CLI returns matching skills ranked by BM25 relevance in $<5$ ms:
- `[ACTIVE]`: Already available in your runtime context.
- `[COLD]`: Stored in warehouse; load on demand in Step 2.

### Step 2: Load the Playbook into Context
Fetch the exact file path or print the content directly:

```bash
# Print full skill content to stdout
agent-skills show <skill-name>

# Or get the exact file path to view with read_file
agent-skills show <skill-name> -p
```

### Step 3: Execute and Release
Apply the instructions, rubrics, and templates loaded from the skill to satisfy the user's prompt. You do not need to keep the skill permanently loaded—once the task turn completes, context naturally recycles.

---

## 3. Quick Reference

| Command | Purpose |
|---|---|
| `agent-skills find <query>` | Sub-5ms FTS5 keyword search across 2,400+ skills |
| `agent-skills show <skill>` | Prints full `SKILL.md` content directly |
| `agent-skills show <skill> -p` | Prints the absolute filesystem path |
| `agent-skills list [collection]` | Lists domain collections or skills within a collection |
| `agent-skills stats` | Shows live warehouse index counts and storage stats |
