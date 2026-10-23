---
name: veriharness
description: Multi-rollout verification harness for high-stakes tasks based on Google Research's VeriHarness protocol ("Same model. Better evidence."). Generates independent candidate rollouts, resolves disagreements against disk evidence, actively challenges shared consensus, and delivers evidence-backed repairs to eliminate model blind spots.
---

# VeriHarness: Scaling Multi-Rollout Verification

Based on Google Research's **VeriHarness** methodology (*Zhang, Lee, et al., arXiv:2610.00972*).
Use this skill for complex bugs, critical architectural refactoring, algorithmic code, high-stakes schema migrations, or tasks where single-rollout execution is prone to hallucination, premature assumptions, or silent edge-case failures.

---

## Core Epistemology

1. **Agreement is NOT evidence.** Rollouts from the same model share training distributions, prompts, and blind spots. A majority is not proof; a unanimous majority can be completely wrong while a minority rollout is right.
2. **Same model, better evidence.** The verifier is not a smarter judge—its sole advantage comes from the pool structure and evidence actively extracted from the environment (files, git history, command probes, recomputed quantities).
3. **Trajectories are testimony, not deliverables.** Rollout reasoning and logs explain *what* was attempted, but they are subjective claims. Corroborate every claim against disk ground truth.
4. **No check, no verdict.** Never pick a solution because it is articulate, idiomatic, or cleanly written. Every judgment must cite a deterministic check. If a point cannot be verified, state it as open.

---

## 4-Phase Verification Architecture

```
Task Spec + Inputs
       │
       ├──► Candidate Rollout A (Isolated) ──┐
       └──► Candidate Rollout B (Isolated) ──┼──► Phase 1: Disagreement Resolver  ──► ledger_elim.json
                                             │    (Test divergences with probes)
                                             │
                                             └──► Phase 2: Consensus Challenger   ──► ledger_fals.json
                                                  (Actively break shared beliefs)
                                                                │
                                                                ▼
                                                  Phase 3: Adjudication
                                                  (Select base, plan surgical work)
                                                                │
                                                                ▼
                                                  Phase 4: Evidence-Backed Delivery
                                                  (Patch, test suite, audit record)
```

---

## Phase 1: Generate Independent Candidate Rollouts

Spawn 2 independent subagents (or generate 2 isolated draft approaches in separate worktrees/branches) with identical input constraints:
- **Rollout A (Direct & Idiomatic):** Focuses on standard idiomatic design, minimal changes, and direct execution.
- **Rollout B (Defensive & Invariant-Centric):** Focuses on failure modes, defensive boundaries, edge cases, and minimal shared state.

Each rollout must output:
1. Exact modified file paths and function signatures.
2. Load-bearing assumptions (schema shapes, types, error codes).
3. Deliverables and test results.

---

## Phase 2: Disagreement Resolution (Discrimination)

Compare Rollout A and Rollout B to identify where they diverge (different APIs, conflicting schema assumptions, divergent edge handling).

**Rules of Engagement:**
- Work the disagreements that separate the candidates most for the least effort.
- Settle each disagreement by **external evidence**: check definitions in source files, read git history, run a typecheck, or recompute a value.
- Conventions come from the codebase, not model preference: pre-existing repository patterns, database schemas, and documentation outrank personal style.
- Record findings in `ledger_elim.json`:
  ```json
  [
    {
      "disagreement": "Whether User.created_at is UTC datetime or integer epoch",
      "rollout_a": "datetime with tzinfo=UTC",
      "rollout_b": "int unix epoch",
      "probe": "Inspect schema definition in backend/models/user.py line 34",
      "evidence": "models/user.py explicitly declares 'created_at = Column(DateTime(timezone=True))'",
      "eliminated": "Rollout B assumption"
    }
  ]
  ```

---

## Phase 3: Consensus Falsification (Breaking What They Share)

Where both rollouts agree, their agreement is not evidence. Actively seek to **falsify** the shared consensus.

**Order of Attacks:**
1. **Delivery contract first:** Verify file names, counts, export signatures, and CLI arguments against the prompt. (Entire rollout pools frequently miss contract details together).
2. **Recompute load-bearing figures:** Recompute numbers, sizes, and limits directly from raw inputs—never trust a candidate's intermediate calculation.
3. **Challenge shared readings:** When a prompt is ambiguous, rollouts often agree only because they took the same intuitive reading. Formulate the alternative reading and probe the repo for which was intended.
4. **Unanimous omission:** Check the specification for requirements, error cases, or cleanup obligations that *neither* rollout handled.

Record findings in `ledger_fals.json`:
```json
[
  {
    "consensus_claim": "Both rollouts assumed Redis connection pool timeout is configured in seconds",
    "falsification_probe": "Check config/cache.py settings and redis client initialization",
    "evidence": "cache.py passes timeout to client expecting milliseconds (timeout=3000)",
    "status": "falsified",
    "correction": "Pass 3000ms instead of 3s to prevent immediate timeout under load"
  }
]
```

---

## Phase 4: Adjudication & Evidence-Backed Repair

Act as the lead adjudicator synthesizing both ledgers:

1. **Select Base:**
   - Choose the rollout with fewer eliminated claims as `base`.
   - If both are fundamentally flawed or violated core requirements, set `base: "none"` and construct from task inputs.
2. **Synthesize Repair Plan (`work[]`):**
   - Incorporate winning elements, edge cases, and helper functions from the rejected rollout.
   - Apply fixes for every falsified consensus claim identified in Phase 3.
   - List any unresolved ambiguities as `open[]`.
3. **Execute & Verify:**
   - Apply the surgical patch.
   - Execute the project's verification suite (`pytest`, `pnpm test`, `cargo test`, or local `verify.sh`).
   - Deliver the final artifact alongside an audit summary:

```markdown
### VeriHarness Verification Audit
- **Selected Base:** Rollout A (idiomatic implementation)
- **Eliminated Rollout Claims:** 2 (Rollout B epoch timestamp assumption; Rollout B unneeded dependency)
- **Falsified Consensus Claims:** 1 (Redis timeout unit in ms corrected)
- **Omissions Recovered:** Handled HTTP 429 backoff that neither rollout initially implemented
- **Verification Gate:** 18/18 tests passing
```
