<!-- AUTO-GENERATED FILE — DO NOT EDIT MANUALLY -->
<!-- Source of truth: skills/nasa-jpl-power-of-ten-python/SKILL.md -->
---
description: "Apply NASA JPL's \"Power of Ten\" reliability coding rules to Python and FastAPI codebases to eliminate entire categories of bugs. Use this skill whenever a user asks to review, audit, or refactor Python code for reliability, production safety, or code quality — especially for FastAPI services, background workers, or any long-running Python process. Trigger even when the user says things like \"my code has silent failures\", \"I have a memory leak\", \"improve code quality\", \"make this more robust\", or \"review this for production\"."
category: "style"
namespace: "/style/nasa-power-of-ten-python"
flat_command: "/nasa-power-of-ten-python"
---

# Command: nasa-power-of-ten-python (/style/nasa-power-of-ten-python)

> **Trigger**: Apply NASA JPL's \"Power of Ten\" reliability coding rules to Python and FastAPI codebases to eliminate entire categories of bugs. Use this skill whenever a user asks to review, audit, or refactor Python code for reliability, production safety, or code quality — especially for FastAPI services, background workers, or any long-running Python process. Trigger even when the user says things like \"my code has silent failures\", \"I have a memory leak\", \"improve code quality\", \"make this more robust\", or \"review this for production\".
> **Category**: Coding Style & Architecture Standards
> **Source Skill**: [skills/nasa-jpl-power-of-ten-python/SKILL.md](file:///home/sanjeev/Downloads/agent-skills/skills/nasa-jpl-power-of-ten-python/SKILL.md)

---

# NASA JPL Power of Ten — Python & FastAPI Reliability Rules

**Description:** A structured code-review and refactoring skill that adapts NASA's
Jet Propulsion Laboratory "Power of Ten" safety-critical coding rules to Python and
FastAPI applications. These rules eliminate whole *categories* of bugs rather than
patching them one by one.

**Category:** Code Quality | Reliability | Python Best Practices

**Skill Level:** Advanced

---

## Overview

NASA's JPL uses the Power of Ten rules (authored by Gerard Holzmann) for C programs
running on Mars rovers — software where a single bug cannot be patched after launch.
The core insight is that **rules which remove entire classes of bugs are more valuable
than rules that catch individual bugs**.

Applied to Python/FastAPI, these rules surface hidden failures, prevent resource
exhaustion, and make code dramatically easier to review and test. They are not about
risk parity with spacecraft software — they are about borrowing a proven *way of
thinking* that pays off at any scale.

---

## Core Rules (Quick Reference)

| # | Rule | NASA Intent | Python/FastAPI Translation |
|---|------|------------|---------------------------|
| 1 | Simple Control Flow | No `goto`, no recursion | No bare `except`, no exception-driven flow |
| 2 | Fixed Loop Bounds | Every loop provably terminates | All `while` loops get a `MAX_ATTEMPTS` guard |
| 3 | No Dynamic Memory After Init | No `malloc` post-startup | No unbounded list/dict growth in long-running processes |
| 4 | Small, Single-Purpose Functions | ≤ 60 lines, one responsibility | Route handlers delegate; no function does 6+ things |
| 5 | Liberal Assertions | Assert invariants explicitly | Replace `assert` with explicit `ValueError`/`raise` checks that survive `-O` |

---

## Detailed Rules

### Rule 1: Restrict to Simple Control Flow

**NASA Original Purpose:**
Eliminate `goto`, `setjmp`/`longjmp`, and recursion. When control flow is complex,
you cannot confidently trace what the program will actually do.

**Python/FastAPI Application:**
Python has no `goto`, but equivalent traps exist: deeply nested `if` blocks, unbounded
recursion, and — most commonly — using broad `except` clauses to silently swallow errors
and redirect execution. This last pattern is the Python version of `goto`: it makes the
real execution path invisible.

**❌ Violates the Rule**
```python
# Exception used as silent control flow — hides real errors
def get_user(user_id):
    try:
        return db.query(User).filter(User.id == user_id).first()
    except:
        return None
```

**✅ Follows the Rule**
```python
# Explicit control flow — None case is visible and logged
def get_user(user_id):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        logger.warning("User not found", extra={"user_id": user_id})
    return user
```

**Impact:** Removing bare `except` blocks in one codebase revealed **two production
bugs that had been silently failing for months**.

---

### Rule 2: Give All Loops a Fixed Upper Bound

**NASA Original Purpose:**
Every loop must have a provable maximum iteration count. Infinite loops can freeze
an entire system with no recovery path.

**Python/FastAPI Application:**
`while` loops without explicit termination conditions are the primary offender. Under
specific failure modes — a task flag that never flips, a queue that never drains — they
run forever, consuming CPU and memory until the process dies or the server runs out of
resources.

**❌ Violates the Rule**
```python
# No upper bound — runs forever if task_complete never becomes True
while not task_complete:
    process_next_item()
    time.sleep(1)
```

**✅ Follows the Rule**
```python
# Explicit upper bound — guaranteed to terminate; failure is logged
MAX_ATTEMPTS = 300
for attempt in range(MAX_ATTEMPTS):
    if task_complete:
        break
    process_next_item()
    time.sleep(1)
else:
    logger.error("Task did not complete within timeout")
    raise TaskTimeoutError("Exceeded maximum attempts")
```

**Impact:** Three unbounded `while` loops in background workers were found that would
have consumed all server memory under specific failure conditions.

---

### Rule 3: Do Not Use Unbounded Dynamic Data Structures

**NASA Original Purpose:**
No `malloc` after initialization. In embedded systems with fixed RAM, unbounded
allocation causes unpredictable failure.

**Python/FastAPI Application:**
The direct equivalent is any data structure that grows without limit inside a long-running
process: lists accumulating results, dicts storing per-request state, in-memory event logs.
These are invisible memory leaks.

**❌ Violates the Rule**
```python
# processed_events grows forever — memory leak in a long-running process
class EventProcessor:
    def __init__(self):
        self.processed_events = []

    def process(self, event):
        result = handle_event(event)
        self.processed_events.append(result)
        return result
```

**✅ Follows the Rule**
```python
# deque with maxlen automatically evicts old entries — bounded by design
from collections import deque

class EventProcessor:
    def __init__(self, max_history=1000):
        self.processed_events = deque(maxlen=max_history)

    def process(self, event):
        result = handle_event(event)
        self.processed_events.append(result)
        return result
```

**Impact:** This pattern was the direct root cause of a confirmed memory leak in a
long-running background process.

> **Note:** Unlike embedded systems, web apps legitimately use dynamic memory for
> request handling. This rule applies specifically to **long-lived, accumulating
> structures** — not to normal per-request allocations.

---

### Rule 4: Keep Functions Small and Single-Purpose

**NASA Original Purpose:**
No function longer than one printed page (~60 lines). A function with a single clear
responsibility is easier to verify, test, and reason about.

**Python/FastAPI Application:**
FastAPI route handlers are the most common violation. A handler that validates a user,
checks a balance, writes to the database, sends an email, and updates inventory in one
function is doing six jobs. Each additional responsibility adds a new failure mode and
a new place where error handling can be silently omitted.

**❌ Violates the Rule**
```python
# One route handler doing six distinct things — impossible to test individually
@app.post("/orders")
async def create_order(order: OrderCreate, db: AsyncSession = Depends(get_db)):
    user = await db.execute(select(User).where(User.id == order.user_id))
    user = user.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.balance < order.total:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    new_order = Order(**order.dict())
    db.add(new_order)
    user.balance -= order.total
    await db.commit()
    await send_confirmation_email(user.email, new_order.id)
    await update_inventory(order.items)
    return new_order
```

**✅ Follows the Rule**
```python
# Handler orchestrates; each delegated function has one job
@app.post("/orders")
async def create_order(order: OrderCreate, db: AsyncSession = Depends(get_db)):
    user = await get_verified_user(db, order.user_id)
    await verify_sufficient_balance(user, order.total)
    new_order = await save_order(db, order, user)
    await post_order_tasks(user, new_order, order.items)
    return new_order
```

**Impact:** Splitting four multi-responsibility route handlers revealed **two missing
error-handling paths** that were unreachable in the monolithic version.

---

### Rule 5: Use Explicit Invariant Checks (Production-Safe Assertions)

**NASA Original Purpose:**
Assert that every condition you believe to be true actually is. If an assertion fails,
something went wrong that your model of the code did not anticipate.

**Python/FastAPI Application:**
Python's built-in `assert` is **silently disabled** when running with the `-O`
(optimized) flag — making it useless for production safety checks. The correct
equivalent is explicit `if`/`raise` guards that are always active, plus Pydantic
validators at API boundaries.

**❌ Violates the Rule**
```python
# assert is disabled in production with -O — provides false confidence
def calculate_discount(amount, rate):
    assert amount > 0, "Amount must be positive"
    assert 0 <= rate <= 1, "Rate must be between 0 and 1"
    return amount * rate
```

**✅ Follows the Rule**
```python
# Explicit checks — always run, always raise, always informative
def calculate_discount(amount: float, rate: float) -> float:
    if amount <= 0:
        raise ValueError(f"Amount must be positive, got {amount}")
    if not 0 <= rate <= 1:
        raise ValueError(f"Rate must be between 0 and 1, got {rate}")
    return amount * rate
```

**Impact:** Adding explicit checks to internal utility functions caught **three cases
of incorrect data being silently passed between functions**.

---

## Usage Instructions

When applying this skill to a code review or refactoring task:

1. **Scan for Rule 1 violations first** — bare `except` clauses are the highest-yield
   target. Each one is a potential production bug hidden from logs.

2. **Audit all `while` loops** — for each one, ask: "Can this provably terminate?"
   If not, add a `MAX_ATTEMPTS` bound and an `else` clause that logs/raises.

3. **Identify long-lived data structures** — any list, dict, or set that is an instance
   variable on a class used in a background worker or daemon thread is a memory leak
   candidate. Evaluate whether `deque(maxlen=N)` or periodic eviction is appropriate.

4. **Check route handler line counts and responsibility counts** — if a handler does
   more than one logical thing (validate, persist, notify, update), propose a refactor
   that extracts each responsibility into a named function.

5. **Replace all `assert` statements in non-test code** with explicit `if`/`raise`
   guards using `ValueError`, `TypeError`, or a domain-specific exception.

6. **Do not apply Rule 3 mechanically to request-scoped code** — per-request lists and
   dicts are normal and correct. Only flag structures that accumulate across requests or
   across the lifetime of a process.

---

## Output Format

When producing a code review using this skill, structure the response as:

```
## Power of Ten Code Review

### Rule Violations Found

| Rule | Location | Severity | Description |
|------|----------|----------|-------------|
| R1   | `get_user()` line 12 | High | Bare `except` swallows all errors silently |
| R2   | `worker.py` line 47 | High | `while` loop has no termination bound |
| R3   | `EventProcessor.__init__` | Medium | Unbounded list in long-running class |

### Refactored Code

[Show before/after for each violation]

### Summary

- X violations found across Y rules
- Estimated risk: [Critical / High / Medium / Low]
- Highest-priority fix: [specific item]
```

---

## Benefits & Observed Improvements

Applying these five rules to a production FastAPI application over two weeks produced
three measurable changes:

- **More bugs found during development** — clear control flow and bounded loops made
  problems surface in testing rather than production.
- **Two real production bugs discovered** — both were hidden inside bare `except` blocks
  and had been silently failing for months before removal exposed them.
- **Faster code reviews** — single-responsibility functions are significantly easier
  to understand and review in pull requests.

---

## Limitations

Not every rule translates equally to web application context:

| Rule | Limitation |
|------|------------|
| Rule 3 (No dynamic memory) | Web apps legitimately allocate per-request. Apply only to long-lived, accumulating structures — not to normal request handling. |
| Rule 1 (No recursion) | Python has recursion depth limits built in. Most web apps don't use recursion in ways that risk stack overflow; this is low priority. |
| Rule 2 (Fixed loop bounds) | Some polling loops legitimately need to run indefinitely (e.g., event loop workers). Use timeout-based bounds rather than iteration counts in those cases. |

**The real value is not mechanical rule compliance.** It is understanding *why* each
rule exists and applying that reasoning to the actual risk profile of your system.

---

## Example Usage

### Example 1 — Code Review Request

> "Review this FastAPI background worker for reliability issues."

The agent reads the file, applies the five-rule checklist, identifies a bare `except`
on line 23 (Rule 1) and an unbounded `while True` loop on line 41 (Rule 2), produces
a formatted violation table, and shows refactored versions of both.

### Example 2 — Targeted Refactor Request

> "I have a memory leak somewhere in my event processor class."

The agent scans for long-lived instance variables (Rule 3), finds an unbounded `list`
accumulating processed events, and proposes replacing it with `deque(maxlen=1000)` with
an explanation of why this is the idiomatic fix.
