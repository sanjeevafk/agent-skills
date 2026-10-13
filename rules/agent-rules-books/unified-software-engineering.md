# Unified Software Engineering Agent Rules

## Core Operating Stance
Working code is not automatically clean or production-ready. Optimize for the whole result: local reasoning, explicit boundaries, and safe evolution over local cleverness or dogmatic layers.

---

### 1. Macro Architecture & Boundaries (Clean Arch, Ousterhout, PEAA)
- **Deep Modules Over Shallow Layers**: Prefer a small, stable interface hiding substantial complexity over multi-layer pass-through wrappers. If a layer merely renames or forwards calls, eliminate it.
- **Dependency Rule**: Source code dependencies point inward toward policy. Domain logic must never directly import ORM models, HTTP payloads, framework types, or external SDKs.
- **Match Architecture to Complexity**: Do not default to enterprise ceremony everywhere. Use straightforward Transaction Scripts for simple CRUD; reserve Domain Models and Hexagonal/Clean ports for complex business policies.
- **Pull Complexity Downward**: The lower module owning the detail should absorb edge cases, normalization, and mechanics instead of forcing callers to coordinate them.

### 2. Domain & Data Integrity (DDD, Kleppmann)
- **One Source of Truth Per Fact**: Never duplicate authoritative state across multiple stores without an explicit coordination or reconciliation contract.
- **Ubiquitous Language**: Model around explicit domain vocabulary. When business terms diverge across teams or features, establish separate Bounded Contexts with explicit translation adapters.
- **Protect Invariants Locally**: Keep business invariants inside rich entities/aggregates. Caches, search indexes, and read views are secondary derived data that must be rebuildable.
- **Idempotency & Replay Safety**: Queued jobs, event consumers, and retried write paths must be idempotent. Never assume exactly-once delivery.

### 3. Code Construction & Local Reasoning (Clean Code, Code Complete, Pragmatic Programmer)
- **Design for Local Reasoning**: A reader must understand a code path without holding hidden global state or jumping across dozens of trivial 2-line helpers.
- **Single Abstraction Level**: Separate setup, input validation, core computation, and external side effects into distinct, visible phases.
- **Boundary Defense**: Validate data at trust boundaries (HTTP, CLI, queues). Use assertions/types for programmer invariants inside the boundary. Make impossible states unrepresentable.
- **Commands vs. Queries**: Functions that return a value should not introduce hidden mutations. Keep side effects explicit.
- **Comments for Intent Only**: Use comments strictly for rationale, constraints, invariants, or upstream quirks. If code requires narration to be understood, refactor names and structure instead.

### 4. Safe Evolution & Legacy Code (Fowler Refactoring, Feathers)
- **Control Before Elegance**: In legacy code without test coverage, your first job is safety, not an aesthetic rewrite. Create seams (wrap, sprout, extract) to make changes testable.
- **Characterize Before Changing**: When legacy behavior is uncertain, write characterization tests to capture existing behavior before altering logic.
- **Separate Refactoring from Behavioral Changes**: Never bundle structural cleanup and functional feature changes into the same unverified edit.
- **Targeted Refactoring**: Fix only the smell that directly blocks your current task. Stop once the path is safe; do not refactor indefinitely.

### 5. Production Reality & Resilience (Release It!)
- **Every Dependency Can Fail**: Never issue un-bounded network, database, or external calls. Enforce explicit timeouts by default.
- **Fail Fast & Isolate**: Use circuit breakers, bulkheads, and fallback paths so downstream outages do not cascade.
- **Bounded Backoff**: Retries must have maximum caps and exponential backoff with jitter to prevent retry storms.
- **Design for Overload**: Admission limits, rate limits, queue backpressure, and load shedding are core architecture requirements, not post-launch hotfixes.

---

## Agent Verification Checklist (Run Before Submitting Diff)
1. **Locality**: Can a developer understand this change reading only the modified function/module?
2. **Depth**: Did I solve complexity by pulling it downward, or did I merely add a shallow helper/wrapper?
3. **Purity**: Did framework/vendor details leak into the core domain?
4. **Resilience**: Are there timeouts on I/O, idempotency on writes, and bounded limits on loops/queues?
5. **Safety**: If touching legacy code, did I characterize behavior and verify tests before and after?
