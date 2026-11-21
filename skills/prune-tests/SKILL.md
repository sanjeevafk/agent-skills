---
name: prune-tests
description: >
  Prune every test that guards no actual behavior: tests that depend on the past (asserting deleted code stays gone),
  tests that depend on nothing (tautological mocks, browser/framework guarantees, type-system redundancies), and
  tests that depend on implementation details (asserting private state, mirrors source logic). Deletes production
  code and artificial seams that existed solely to serve those tests.
  USE WHEN: /prune-tests, "prune tests", "clean up tests", "delete zombie tests", "test bloat", or optimizing CI test suite.
---

# Prune Tests: Eliminate Tests That Guard No Behavior

Prune every test that does not guard real, observable behavior.

---

## 1. Core Evaluation: What Does Each Test Depend On?

Keep a test **only** if it depends on intended, user- or caller-observable behavior:
- It must change **only** when that behavior intentionally changes.
- It must fail **only** when that behavior regresses.
- If another test already guards the same behavior, prune the duplicate copy.

### Prune tests that depend on:

### A. The Past
* **What it does**: Asserts that removed or refactored code stays gone.
* **Why it's useless**: Bringing old code back would be an intentional architectural decision, never an accidental regression.
* **Examples**:
  * Asserting a deprecated flag or legacy module is absent from its old import path.
  * Checking `existsSync("src/legacy/exporter.ts") === false`.

### B. Nothing (Tautologies & Framework Guarantees)
* **What it does**: No conceivable defect in production code could make it fail, or it asserts invariants already guaranteed by the platform or compiler.
* **Examples**:
  * Testing the browser or runtime (e.g. verifying a `<button>` renders or DOM `click` fires).
  * Mocks that verify the mock: stubbing a service to return `X`, then asserting that the function returns `X`.
  * Asserting compile-time invariants that the type system (TypeScript, Rust, Go) already guarantees without running.

### C. The Implementation (Change Detectors)
* **What it does**: Breaks whenever the internal code structure changes, even when outward behavior remains 100% identical.
* **Examples**:
  * The test's expected value is computed using the identical algorithmic formula as the function itself (tautology: `price - price * 0.2`).
  * Asserting private variables, internal helper call counts (`expect(myService._items.length).toBe(1)`), or intermediate state.

---

## 2. The Pruning & Deletion Protocol

1. **Delete**:
   * Prune every test file or test block identified in categories A, B, or C.
2. **Rewrite (Only when behavior is real)**:
   * Where a test touches genuine caller behavior but asserts private state, rewrite it against the public contract (e.g., assert `cart.total()` instead of `cart._items.length`).
3. **Delete Test-Only Production Code & Seams**:
   * Inspect production files for artificial seams, methods, and export flags created solely for testing (e.g., `_resetCacheForTests()`, `_getInternalState()`, public getters on private state).
   * **Delete them completely from the production source.**

---

## 3. What Done Looks Like

- [ ] Every remaining test is strictly anchored to intended, caller-observable behavior.
- [ ] Every remaining test fails on a regression, and *only* on a regression.
- [ ] Zero tests assert that legacy or deleted code remains absent.
- [ ] Zero duplicate tests guard the same invariant.
- [ ] Zero production code or artificial seams exist solely to service tests.

---

## 4. Concrete Examples

```diff
--- a/pricing.test.ts
+++ b/pricing.test.ts
@@ Rewritten: the expected value repeated the code's logic @@
 test("applies the discount", () => {
-  const price = 100;
-  expect(applyDiscount(price, 0.2)).toBe(price - price * 0.2);
+  expect(applyDiscount(100, 0.2)).toBe(80);
 });

--- a/cart.test.ts
+++ b/cart.test.ts
@@ Rewritten against caller-facing contract instead of private state @@
 test("adds an item to the cart", () => {
   const cart = new Cart();
   cart.add(book);
-  expect(cart._items.length).toBe(1);
+  expect(cart.total()).toBe(book.price);
 });

@@ Deleted: checkout.test.ts already guards this exact total @@
-test("total includes tax", () => {
-  expect(cartTotal([book], { tax: 0.1 })).toBe(11);
-});

--- a/export.test.ts
+++ b/export.test.ts
@@ Deleted: guards code that no longer exists @@
-test("legacy exporter is gone", () => {
-  expect(existsSync("src/export/legacy.ts")).toBe(false);
-});

--- a/session.test.ts
+++ b/session.test.ts
@@ Deleted: test and test-only production helper @@
-test("clears the cache", () => {
-  _resetCacheForTests();
-  expect(_getCacheSize()).toBe(0);
-});

--- a/session.ts
+++ b/session.ts
@@ Deleted production code that only existed for tests @@
-export function _resetCacheForTests() { cache.clear(); }
-export function _getCacheSize() { return cache.size; }
```
