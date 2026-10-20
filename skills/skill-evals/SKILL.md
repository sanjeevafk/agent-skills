---
name: skill-evals
description: Multi-arm evaluation harness and pre-activation quality linter for AI agent skills to quantitatively measure adherence, effect, and token economy before deployment.
license: MIT
metadata:
  repo: https://github.com/sanjeevafk/agent-skill-evals
tools: Bash, Read, Write
---

# Skill Evals & Pre-Activation Quality Linter

A quantitative, multi-arm evaluation harness and pre-activation quality gate for AI agent skills (`SKILL.md`). Built on the research principles of Sergii Makarevych (2026) and the Poteto Verification Playbooks.

## When to Activate

- Testing any new or modified `SKILL.md` before promoting it to the active runtime context.
- Benchmarking candidate skills against a length control arm to isolate prompt-length placebo gains.
- Running pre-activation linting to enforce directive density ($\ge 1.5\text{ directives/KB}$) and detect conversational fluff.
- Bulk auditing an active skill inventory to eliminate prompt bloaters and security vulnerabilities.

## Core Directives

- **Lint Before Evaluating:** Always execute `python3 ~/.agents/scripts/lint_skill.py <path>` as Stage 0 to abort early on low-density prose or security issues.
- **Run the 3-Arm Trial:** Execute `python3 ~/.agents/scripts/eval_skill.py <skill_name> --prompt "<task>"` across Baseline (Arm A), Candidate (Arm B), and Length Control (Arm C).
- **Apply the Decision Matrix:**
  - *Adherence < 70%:* Reject with `REWRITE TEXT`. The agent cannot parse or execute the instructions.
  - *Arm B $\le$ Arm C:* Reject with `DROP IDEA (FOLKLORE)`. The skill delivers no causal lift beyond length expansion.
  - *Arm B $>$ Arm C $>$ Arm A:* Accept with `SHIP & PIN`. The skill demonstrates verified causal improvement.
- **Audit Suite Inventory:** Periodically sweep `~/.gemini/config/skills` with `python3 ~/.agents/scripts/audit_suite.py` to identify context bloaters (> 20 KB) and demote them to warehouse cold storage.

## Repository

The complete standalone evaluation harness, linter CLI, and test suite are maintained in [**`sanjeevafk/agent-skill-evals`**](https://github.com/sanjeevafk/agent-skill-evals).
