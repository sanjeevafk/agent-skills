---
name: be-ambitious
description: >
  Elevate tasks and prompts into their highest-leverage versions across Altitude (durable systems),
  Depth (raw materials, expert tools, external judge), and Range (noun-to-verb shift, adversarial red-team).
  Autonomously triages the right dimension for the task, or accepts explicit modes (--depth, --altitude, --range, --all).
  USE WHEN: /be-ambitious, "be ambitious", "make this prompt deeper", "raise the bar on this task",
  "what would an expert do here", "think bigger/deeper about this", or during high-stakes architecture/planning.
---

# Be Ambitious: Full-Spectrum Task Elevation

Adapted and expanded from Felix Rieseberg's [*How to Be More Ambitious: A Tutorial for Humans with Models*](https://felixrieseberg.com/how-to-be-more-ambitious-a-tutorial-for-humans-with-models/) and DannyMac180's [`be-ambitious`](https://github.com/DannyMac180/skills/tree/main/be-ambitious):

> Most AI interactions fail not from model limitations, but from human self-censorship—settling for task execution rather than outcome mastery.
> True ambition is not scope creep; it is elevating the caliber of execution across **Altitude**, **Depth**, and **Range**.

---

## 1. Input & Mode Resolution

The task is whatever follows `/be-ambitious`. If empty, use the user's most recent request.

### Mode Triage (Autonomous vs. Explicit)
If an explicit flag is passed (`--depth`, `--altitude`, `--range`, `--all`), enforce that specific lens.
Otherwise, **autonomously select the highest-leverage lens** based on task characteristics and state the choice in one line:

* **Depth (`--depth`):** For algorithms, tricky bugs, performance tuning, data analysis, or refactoring.
  * *Constraint: Deeper, not bigger.* Refuse feature bloat or scope expansion. Demand raw materials, named instruments, and an external judge.
* **Altitude (`--altitude`):** For manual chores, one-off scripts, recurring reports, or infrastructure patches.
  * *Constraint: System over task.* Ask "What is the goal beyond the goal?" Turn a disposable answer into a durable, self-healing loop or harness.
* **Range (`--range`):** For security audits, architectural design, PRDs, policy design, or trade-off reviews.
  * *Constraint: Active mechanics & adversarial red teams.* Convert passive nouns to verbs; assemble complementary disciplines without shallow roleplay.
* **Full Spectrum (`--all`):** For major greenfield projects, zero-to-one initiatives, or mission-critical systems.

---

## 2. The 3-Dimensional Elevation Engine

```
[User Task]
    │
    ├── 1. Noun-to-Verb Shift (Range)   ──> Transform passive assets into active causal dynamics
    ├── 2. Goal Beyond the Goal (Altitude) ──> Identify outcome & durable automation
    ├── 3. Primary Raw Material (Depth)  ──> Bypass summaries; point to raw sources & traces
    ├── 4. Named Domain Instruments (Depth) ──> Force field-specific tools & algorithms
    ├── 5. Adversarial Red Team (Range)  ──> Bring in hostile / forensic audit perspectives
    └── 6. Outside Ground Truth (Depth)  ──> Independent judge (tests, benchmarks, metrics)
    │
    ▼
[Rewritten Prompt: Production-grade, zero fluff]
```

### Phase A: The Noun-to-Verb Shift (IDEO / Tom Kelley)
Models become passive when handed nouns (*"a security report"*, *"a review deck"*, *"a cache wrapper"*).
Immediately translate nouns into active causal verbs:
* *Not:* "Build an analytics dashboard."
* *Instead:* "Surfacing latency regressions under 99th-percentile load and isolating upstream database deadlocks within 30 seconds."

### Phase B: Altitude (The Goal Beyond the Goal)
Answer:
1. **The Ultimate Outcome:** What decision or action does this task serve?
2. **Durable Infrastructure:** How does this stop being a human-in-the-loop chore? What test harness, CI check, or monitor prevents this from ever breaking or needing manual intervention again?

### Phase C: Depth (Rawness, Instruments, Outside Judge)
Answer:
1. **Top Professional Moves:** What 2-3 tactical moves separate a world-class practitioner from a competent worker here (e.g., base-rate checks, reproducing before patching, invariant proofs)?
2. **The Rawest Source Material:** Bypass digested summaries, reports, or secondhand tickets. What primary data must the model start from (e.g., raw SQLite WAL logs, eBPF flamegraphs, pcap packets, SEC 10-K filings)?
3. **Specific Methods & Named Tools:** Concrete tools the best in the industry use (e.g., Z3 theorem prover, Polars, Valgrind, IDA/Ghidra, Playwright 2x Retina, loudnorm EBU R128).
4. **The Audacious Target:** Set an aggressive performance or quality bar (e.g., 200ms latency, zero-copy, <1% false-positive rate) and assert that it is fully achievable.
5. **The Outside Judge:** An external verification mechanism independent of both the model and the user. What automated benchmark, test suite, or measurement determines a PASS vs. FAIL?

### Phase D: Range (Assembling the Heist Crew)
Identify 2 complementary or adversarial disciplines that must review the work (e.g., a forensic accountant, a distributed systems SRE, a security red-teamer, a typography/motion designer).
*Constraint: Demand their actual investigative methods, checklists, and edge-case probes—never shallow conversational roleplay.*

---

## 3. Output Format

Format the output strictly as:

```markdown
### 🎯 Ambition Vector: [Autonomous Choice: Depth / Altitude / Range / Full Spectrum]
*Brief 1-sentence rationale for why this lens unlocks highest leverage.*

---

### 🔍 Tactical Breakdown
* **Active Dynamic (Noun → Verb):** [What mechanics are being executed]
* **Rawest Primary Material:** [Exact datasets, logs, or source files]
* **Named Domain Instruments:** [Specific frameworks, profilers, algorithms]
* **The Outside Judge:** [Deterministic pass/fail check, benchmark, or test suite]
* *(If Altitude)* **Durable System:** [How this becomes an automated asset]
* *(If Range)* **Adversarial / Red Team Probe:** [Hostile edge-case or auditor question]

---

### 📝 Rewritten Prompt
```[language if applicable, or plain text]
[Drop-in prompt ready to copy and run, written in the user's voice with the exact technical specifications, raw sources, and verification criteria established above.]
```

---
*Run this prompt now? (yes / tweak)*
```

Stop immediately after the rewrite. **Do not execute the prompt** until the user explicitly confirms.
