# Agent Rules Books Setup

This document explains how to install, manage, and use `agent-rules-books`—a collection of 13 engineering guidelines and decision frameworks.

## What Are Agent Rules Books?

Agent rules books are **reference documentation** that guide agents in making architectural and implementation decisions. They're NOT executable skills—they're engineering policies and best practices.

**Examples:**
- Clean Code: Principles for readable, maintainable code
- Domain-Driven Design: Modeling patterns for complex domains
- Release It!: Production reliability principles
- Refactoring: Safe code transformation techniques

**Key traits:**
- NOT triggered via slash-commands
- Used as **context/guidelines** in agent decision-making
- Can be referenced when designing solutions
- Embedded into agent instructions and prompts

---

## All 13 Available Rules

1. **a-philosophy-of-software-design.md** — Shallow vs. deep modules, information hiding, module depth
2. **clean-architecture.md** — Dependency rule, clean architecture layers, separation of concerns
3. **clean-code.md** — Naming, functions, error handling, tests, code quality
4. **code-complete.md** — Construction quality, defensive coding, data clarity
5. **designing-data-intensive-applications.md** — Data consistency, events, replay safety, partitioning
6. **domain-driven-design-distilled.md** — Practical DDD without ceremony, bounded contexts, aggregates
7. **domain-driven-design.md** — Deep modeling, ubiquitous language, entities vs. value objects
8. **implementing-domain-driven-design.md** — Aggregate boundaries, repositories, anti-corruption layers
9. **patterns-of-enterprise-application-architecture.md** — Business logic patterns, persistence, transaction boundaries
10. **refactoring.md** — Safe refactoring steps, preserving behavior, known transformations
11. **release-it.md** — Production readiness, timeouts, retries, circuit breakers, observability
12. **the-pragmatic-programmer.md** — DRY, orthogonality, automation, feedback loops
13. **working-effectively-with-legacy-code.md** — Seams, safe refactoring, characterization tests

---

## Installation

### One-time install to canonical root

```bash
chmod +x <repo-root>/install-rules-books.sh
<repo-root>/install-rules-books.sh install
```

This downloads agent-rules-books from GitHub to `~/.agents/agent-rules-books/`.

### Install and sync to all agent environments

```bash
<repo-root>/install-rules-books.sh install --sync
```

Installs rules to:
- `~/.agents/agent-rules-books/`
- `~/.copilot/agent-rules-books/`
- `~/.cursor/agent-rules-books/`
- `~/.gemini/antigravity/agent-rules-books/`
- `~/.codex/agent-rules-books/`

### Sync existing rules to other agents (after update)

```bash
<repo-root>/install-rules-books.sh sync
```

---

## Usage: How to Use Agent Rules Books

### They're NOT Slash-Commands

You **cannot** invoke rules via `/rule clean-code` or similar. Instead, they're used in three ways:

---

## Method 1: Reference During Problem-Solving

When solving design problems, explicitly tell agents to consult the rules:

```
I'm refactoring a legacy method with 300 lines of mixed concerns.

Use the "working-effectively-with-legacy-code" and "refactoring" rules to:
1. Create safe characterization tests
2. Break dependencies using seams
3. Extract responsibilities one at a time
4. Ensure behavior is preserved

Constraint: No step should require >5 files to change.
```

The agent reads those rules from `~/.agents/agent-rules-books/`, applies the principles, and crafts the approach.

---

## Method 2: Request Domain Model Review

For architecture and design decisions:

```
Design a domain model for an e-commerce system using:
- "domain-driven-design" for ubiquitous language and bounded contexts
- "implementing-domain-driven-design" for aggregate boundaries
- "clean-architecture" for dependency rule enforcement

Output: Domain diagram + core entities + aggregate roots.
```

---

## Method 3: Production Readiness Checklist

Before deploying services:

```
Review this new microservice for production readiness using "release-it" rules.

Checklist:
- Timeouts on all external calls?
- Retries with backoff?
- Circuit breaker patterns?
- Load shedding under stress?
- Monitoring/observability?
- Graceful degradation?
```

---

## Where Rules Live and How Agents Access Them

### In Agents' Context/Instructions

When the operator install rules, they become available as **reference context**. Agents can:

1. **Be configured** to load rules into their instruction context:
   ```bash
   # In ~/.copilot/instructions/ or ~/.cursor/instructions/:
   # Add @~/.agents/agent-rules-books/clean-code.md
   ```

2. **Be invoked manually** by referencing the file:
   ```
   Use these rules: @~/.agents/agent-rules-books/clean-architecture.md
   ```

3. **Be mentioned by name** (if agent tooling supports it):
   ```
   Use the Clean Code rules to review this function.
   ```

---

## Integration with Global Skills Setup

Unlike skills (which are executable and need syncing with `global-skills.sh`), rules are **static reference documents** that can optionally be replicated.

**Use this for managing rules:**
```bash
<repo-root>/install-rules-books.sh install --sync
```

**Use this for managing skills:**
```bash
<repo-root>/global-skills.sh add mattpocock/skills
<repo-root>/global-skills.sh sync
```

---

## Checking Status

### Are rules installed?

```bash
<repo-root>/install-rules-books.sh status
```

Output:
```
=== agent-rules-books Installation Status ===

✓ $HOME/.agents/agent-rules-books (13 rules)
✓ $HOME/.copilot/agent-rules-books (13 rules)
✓ $HOME/.cursor/agent-rules-books (13 rules)
✓ $HOME/.gemini/antigravity/agent-rules-books (13 rules)
✓ $HOME/.codex/agent-rules-books (13 rules)
```

### List available rules

```bash
<repo-root>/install-rules-books.sh list
```

---

## Best Practices

### 1. Reference Specific Rules, Not All

Bad:
```
Review my code.
```

Good:
```
Review my code using "clean-code" rules. Focus on: naming clarity, function size, separation of concerns.
```

---

### 2. Combine Complementary Rules

For complex decisions, layer rules:

```
Design a new service using these rules:
1. "clean-architecture" for external boundaries
2. "domain-driven-design" for core modeling
3. "release-it" for production patterns
4. "designing-data-intensive-applications" for data consistency
```

---

### 3. Use During Code Review

Structural reviews:
```
Review this PR against "clean-architecture" and "clean-code" rules.
Report violations with severity: blocker | major | minor.
```

---

### 4. Use for Refactoring Guidance

Pre-refactor discussion:
```
Before refactoring, consult "refactoring" rules:
- Is current behavior characterized by tests?
- Can we create a seam without modifying core logic?
- What's the smallest safe transformation?
```

---

## Updating Rules

Rules are tracked in git (if the operator installed with the script). To get the latest:

```bash
# Manual update (if installed directly)
cd ~/.agents/agent-rules-books
git pull origin main

# Re-sync to other agents
<repo-root>/install-rules-books.sh sync
```

---

## FAQ

### Q: Can I create custom rules?

A: Yes. Add `.md` files to `~/.agents/agent-rules-books/` in the same format (sections for "When to use", "Decision rules", "Trigger rules", "Final checklist").

```bash
# Create custom rule
cat > ~/.agents/agent-rules-books/my-team-practices.md << 'EOF'
# My Team Practices

## When to use
[the guidance here]

## Decision rules
- rule 1
- rule 2

## Trigger rules
- when X happens, use this rule

## Final checklist
- [ ] Verified
EOF

# Sync to other agents
<repo-root>/install-rules-books.sh sync
```

---

### Q: Are these rules binding or advisory?

A: **Advisory**. They're patterns and principles agents should consider, not hard constraints. Some rules may conflict with project-specific policies—always layer project rules on top of these.

---

### Q: Why aren't these skills?

A: Because they're not executable operations—they're decision frameworks. Skills automate tasks; rules guide thinking.

---

### Q: Can I disable rules for a specific agent?

A: Yes, delete them from that agent's directory:
```bash
rm -rf ~/.cursor/agent-rules-books
```

Then re-sync if needed:
```bash
<repo-root>/install-rules-books.sh sync
```

---

## Script Reference

```bash
# Install to canonical root only
<repo-root>/install-rules-books.sh install

# Install and sync to all agents
<repo-root>/install-rules-books.sh install --sync

# Sync existing rules to all agents (after updates)
<repo-root>/install-rules-books.sh sync

# Check installation status
<repo-root>/install-rules-books.sh status

# List all available rules
<repo-root>/install-rules-books.sh list
```

---

## Quick Start

```bash
# 1. Install and sync
<repo-root>/install-rules-books.sh install --sync

# 2. Verify
<repo-root>/install-rules-books.sh status

# 3. List available
<repo-root>/install-rules-books.sh list

# 4. Use in prompts (reference specific rules when asking agents for decisions)
```

Example prompt after setup:
```
Use "clean-code" and "code-complete" rules to review this function for:
- Naming clarity
- Parameter count
- Error handling
- Defensive programming
```

The agent will consult those rules and apply them to the codebase.
