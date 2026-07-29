# Skill Delivery Strategy Experiment

> **Generated at**: `2026-07-29T03:21:03.871175+00:00`  
> **Tasks**: 3 | **Runs per strategy**: 2 | **Strategies**: 4

---

## 📊 Executive Dashboard

| Strategy | Avg Score /35 | 95% CI | Wins | Avg Latency | Avg Input Tokens | Avg Output Tokens |
|---|---|---|---|---|---|---|
| `control` | **27.0** | `[-36.53, 90.53]` | 0 | 130.48s | 86.5 | 583.5 |
| `full` | **29.0** | `[3.59, 54.41]` | 0 | 79.15s | 3095.0 | 3258.5 |
| `retrieved` | **29.0** | `[3.59, 54.41]` | 0 | 68.97s | 528.5 | 2724.0 |
| `checklist` | **34.5** | `[28.15, 40.85]` | 2 🏆 | 112.75s | 311.5 | 1562.0 |

---

## 🔬 Prompt Bloat Analysis

### Task `secure-review-hard` (Skill: `security-review`)

| Strategy | Total Tokens | Overhead Tokens | Overhead % |
|---|---|---|---|
| `control`   | 86 | 0 | 0% |
| `full` | 3216 | +3130 | +3639.5% |
| `retrieved` | 544 | +458 | +532.6% |
| `checklist` | 157 | +71 | +82.6% |

> Skill full tokens: **3123** | Retrieved target: ~15% = **468** tokens

### Task `debug-loop-hard` (Skill: `debugging-code`)

| Strategy | Total Tokens | Overhead Tokens | Overhead % |
|---|---|---|---|
| `control`   | 87 | 0 | 0% |
| `full` | 2974 | +2887 | +3318.4% |
| `retrieved` | 513 | +426 | +489.7% |
| `checklist` | 466 | +379 | +435.6% |

> Skill full tokens: **2880** | Retrieved target: ~15% = **432** tokens

### Task `tdd-plan-hard` (Skill: `tdd`)

| Strategy | Total Tokens | Overhead Tokens | Overhead % |
|---|---|---|---|
| `control`   | 79 | 0 | 0% |
| `full` | 1132 | +1053 | +1332.9% |
| `retrieved` | 209 | +130 | +164.6% |
| `checklist` | 217 | +138 | +174.7% |

> Skill full tokens: **1046** | Retrieved target: ~15% = **156** tokens


---

## 📐 Pairwise Comparisons (Welch t-test)

| Pair | t-statistic | p-value | Significant? |
|---|---|---|---|
| `control_vs_full` | -0.371 | 0.7614 | No |
| `control_vs_retrieved` | -0.371 | 0.7614 | No |
| `control_vs_checklist` | -1.493 | 0.3724 | No |
| `full_vs_retrieved` | 0.0 | 1.0 | No |
| `full_vs_checklist` | -2.668 | 0.2054 | No |
| `retrieved_vs_checklist` | -2.668 | 0.2054 | No |

---

## 🏅 Per-Skill-Category Winners

| Skill Category | Best Strategy |
|---|---|
| `security-review` | **`checklist`** |
| `debugging-code` | **`checklist`** |

---

## 💡 Final Recommendation

- **Highest average judge score**: `checklist`
- **Most first-place wins**: `checklist`
- **Lowest latency**: `retrieved`
- **Lowest prompt bloat**: `control`

### Optimal Delivery Method by Skill Category

- **security-review** → `checklist`
- **debugging-code** → `checklist`

> [!IMPORTANT]
> This experiment measures **how** skills are delivered — not whether they work.
> The optimal strategy may vary by skill category, task complexity, and model.


---

## 🧬 Per-Task Judge Explanations

### Task `secure-review-hard`

**Run 1:**
- Ranking: `checklist > full > retrieved > control`
- Analysis: A leads because it uniquely addresses the SELECT FOR UPDATE quota race condition (a real production failure mode), provides the most explicit attack-surface-to-mitigation mapping in its sanitization table, and uses a server-generated storage key pattern that eliminates filename trust entirely — all while being fully readable. B is a close second: excellent type hygiene (bigint for quotas), accurate Mermaid architecture, and comprehensive MIME + extension allowlisting, but lacks A's race condition awareness and explicit per-layer attack reasoning. D is functional and correct but relies on a library black box for sanitization and provides weaker explanatory reasoning. C would rank highly on ideas alone (the two-phase quota insight is the best conceptual contribution across all four), but its truncated output makes it unusable as a standalone answer, dropping it to last despite strong reasoning quality.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `checklist` | 35 | Response A demonstrates the strongest overall execution. The architecture diagram is precise and sequential, clearly showing middleware ordering. Critically, it addresses the SELECT FOR UPDATE race co |
  | `full` | 31 | Response B is the most visually complete — the Mermaid flowchart is accurate and shows the full middleware chain, and the TypeScript types are well-structured using bigint for quota (avoiding float pr |
  | `control` | 22 | Response C has strong conceptual reasoning — the two-phase quota strategy (Content-Length soft hint + actual size hard check) is an insightful design decision not explicitly surfaced by others. The me |
  | `retrieved` | 27 | Response D is solid and practical — it correctly calls out avoiding regex blacklists, uses sanitize-filename library + path.basename + Windows reserved name checking, and adds UUID-based stored names. |

### Task `debug-loop-hard`

**Run 1:**
- Ranking: `checklist > control > retrieved > full`
- Analysis: C ranks first due to its Phase 0 correlation ID strategy — a critical operational detail absent from all other responses that enables log joining across heterogeneous tools; it also demonstrates the clearest reproducibility discipline. D is a close second: its 7-phase structured playbook, blame-elimination framing, and unique hardening phase show the deepest coverage, but its reliance on an external linked artifact makes it less self-contained and immediately usable. A ranks third — technically precise with excellent symptom-to-diagnosis mapping and the cleanest mental model diagram, but lacks the baseline instrumentation discipline of C and the breadth of D. B ranks last primarily due to the unexplained 'dap' disclaimer (a non-sequitur that undermines credibility), a weaker architectural framing, and a baseline measurement approach that, while practical, is less rigorous than C's correlation-ID-anchored method.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `retrieved` | 31 | Response A is technically accurate across all three diagnosis layers (tcpdump, strace, distributed tracing). The mental model diagram immediately frames the bisection strategy, and the tshark filter t |
  | `full` | 27 | Response B is solid and practical — the baseline curl loop with p50/p95/p99 bucketing is a strong opener that adds real diagnostic value. tcpdump commands are correct. However, it opens with a non-seq |
  | `checklist` | 34 | Response C is the strongest overall. The 'Phase 0' baseline with correlation ID tagging before any captures is an expert-level addition that most practitioners miss — it's essential for joining tcpdum |
  | `control` | 32 | Response D is the most complete in terms of visible structure — 7 explicit phases, a fingerprint table with one-liner confirmation commands, and a hardening phase (defense-in-depth) that no other resp |

### Task `tdd-plan-hard`
