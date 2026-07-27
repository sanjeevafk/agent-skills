# Engineering Principles & Architecture Standards

> Canonical reference for architectural standards, coding invariants, and software engineering book rules.

---

## 1. Core Philosophy

1. **Single Source of Truth**: `skills/` and `rules/` are canonical. All commands, indexes, dependency graphs, and IDE exports are derived build artifacts.
2. **Explicit > Clever**: Code readability, maintainability, and clear type boundaries take priority over clever shortcuts.
3. **Information Hiding & Deep Modules**: Simple, clean interfaces hiding internal complexity (*A Philosophy of Software Design*).
4. **Separation of Concerns**: Strict boundary enforcement between UI, Business Domain, and Infrastructure layers (*Clean Architecture*).
5. **Defend Boundaries**: Validate all external inputs at system entry points; enforce strict typing inside domain boundaries (*Code Complete*).
6. **Zero-Defect Verification**: Never declare work complete without empirical CLI test passing evidence (*TDD* & *Verification Loop*).

---

## 2. Incorporated Software Engineering Standards (14 Books)

The framework enforces guidelines derived from 14 software engineering classics:

| Book Standard | Primary Architectural Mandate |
| :--- | :--- |
| **Clean Code** (Martin) | Short, single-responsibility functions; meaningful names; explicit error handling. |
| **Clean Architecture** (Martin) | The Dependency Rule: Outer layers depend on inner domain; domain never imports infrastructure. |
| **Refactoring** (Fowler) | Small, behavior-preserving structural changes backed by deterministic tests. |
| **The Pragmatic Programmer** (Hunt & Thomas) | DRY principle, orthogonality, automation, and explicit contract design. |
| **Designing Data-Intensive Applications** (Kleppmann) | Concurrency control, idempotency, data isolation levels, and partition safety. |
| **A Philosophy of Software Design** (Ousterhout) | Deep modules, hiding implementation details, reducing cognitive complexity. |
| **Domain-Driven Design** (Evans, Vernon) | Ubiquitous language, bounded contexts, entities vs value objects, aggregate boundaries. |
| **Code Complete** (McConnell) | Defensive programming, input sanitization, assertions, and boundary checks. |
| **Working Effectively with Legacy Code** (Feathers) | Establishing characterization tests and dependency seams before modifying legacy logic. |
| **Release It!** (Nygard) | Production stability patterns: Timeouts, Circuit Breakers, Bulkheads, and Graceful Degradation. |
| **PofEAA** (Fowler) | Domain Model, Data Mapper, Repository, and Unit of Work patterns for enterprise applications. |

---

## 3. Technology Guidelines

### TypeScript
* Strict mode enabled (`strict: true`).
* Disallow `any` except at explicitly documented external boundary adaptors.
* Discriminated unions for domain state modeling.
* Immutability preferred (`readonly`).

### Python
* Complete type annotations on all function signatures (`mypy` clean).
* Dataclasses or Pydantic models over raw untyped dictionaries.
* Explicit context managers (`with`) for resource management.

### Database (Postgres & Supabase)
* Row Level Security (RLS) policies mandatory on every user-facing table.
* Parameterized queries mandatory (zero string concatenation for SQL).
* Reversible, migration-safe DDL schemas.

### Production Reliability & Resilience
* Wrap all external API and network boundaries with explicit timeout and retry limits.
* Implement fallback degradation paths for external dependency outages.
