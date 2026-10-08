# Agentic Design Patterns Collection

Distilled architectural patterns and production playbooks from Antonio Gulli's *"Agentic Design Patterns: A Hands-On Guide to Building Intelligent Systems"*.

## Pattern Catalog (21 Architecture Skills)

### 1. Core Foundational Patterns (Ch 1-7)
- [`pattern-prompt-chaining`](./pattern-prompt-chaining/SKILL.md): Sequential task decomposition & intermediate validation.
- [`pattern-routing`](./pattern-routing/SKILL.md): Intent-based dynamic routing to specialized models & tools.
- [`pattern-parallelization`](./pattern-parallelization/SKILL.md): Concurrent fan-out/gather & voting ensembles.
- [`pattern-reflection`](./pattern-reflection/SKILL.md): Iterative self-critique and refinement loops.
- [`pattern-tool-use`](./pattern-tool-use/SKILL.md): Deterministic execution interfaces & sandboxed tools.
- [`pattern-planning`](./pattern-planning/SKILL.md): Strategic task decomposition & dynamic replanning.
- [`pattern-multi-agent-collaboration`](./pattern-multi-agent-collaboration/SKILL.md): Hierarchical lead-worker & peer collaboration.

### 2. Advanced Patterns (Ch 8-11)
- [`pattern-memory-management`](./pattern-memory-management/SKILL.md): Tiered working context, sliding windows & persistent state.
- [`pattern-dynamic-adaptation`](./pattern-dynamic-adaptation/SKILL.md): Self-optimizing prompts & feedback assimilation.
- [`pattern-model-context-protocol`](./pattern-model-context-protocol/SKILL.md): Standardized FastMCP client-server architecture.
- [`pattern-goal-setting-monitoring`](./pattern-goal-setting-monitoring/SKILL.md): Milestone tracking & quantifiable goal verification.

### 3. Production Patterns (Ch 12-14)
- [`pattern-exception-handling`](./pattern-exception-handling/SKILL.md): Multi-tiered fallbacks, circuit breakers & backoff retries.
- [`pattern-human-in-the-loop`](./pattern-human-in-the-loop/SKILL.md): Risk-tiered approval gates & interactive pause/resume.
- [`pattern-knowledge-retrieval-rag`](./pattern-knowledge-retrieval-rag/SKILL.md): Hybrid search, cross-encoder reranking & citation grounding.

### 4. Enterprise Patterns (Ch 15-21)
- [`pattern-inter-agent-communication`](./pattern-inter-agent-communication/SKILL.md): A2A protocol, Agent Cards discovery & JSON-RPC envelopes.
- [`pattern-resource-optimization`](./pattern-resource-optimization/SKILL.md): Prompt caching, model cascades & token budgeting.
- [`pattern-reasoning-engines`](./pattern-reasoning-engines/SKILL.md): Chain-of-Thought, Tree of Thoughts & execution verifiers.
- [`pattern-guardrails-safety`](./pattern-guardrails-safety/SKILL.md): Multi-stage input/output sanitization & injection defense.
- [`pattern-evaluation-monitoring`](./pattern-evaluation-monitoring/SKILL.md): LLM-as-a-Judge rubrics & regression testing.
- [`pattern-prioritization`](./pattern-prioritization/SKILL.md): Dynamic impact-urgency scoring & DAG resolution.
- [`pattern-exploration-discovery`](./pattern-exploration-discovery/SKILL.md): Hypothesis generation & autonomous discovery loops.
