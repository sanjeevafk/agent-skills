---
name: cpp-performance
description: High-performance C++ engineering standards focusing on Orthodox C++, zero-allocation hot paths, data-oriented design (DOD), cache-conscious layout, and algorithmic pruning.
---

# Performance by Design: A C++ Guide

This skill provides practical engineering standards for writing native C++ code that starts close to the desired performance shape instead of requiring a long cleanup pass after the prototype works.

## Core Principle

```
Design hot paths as C-style code so costs, data flow, and algorithmic shape remain explicit.
Use C++ only where it gives real safety, clarity, or compile-time structure.
Do not rely on the compiler to erase bad data structures, allocations, copies,
string formatting, dynamic dispatch, or bad algorithmic complexity.
```

This is not an argument for rewriting codebases in pure C. C++ provides essential tools: namespaces, references, `nullptr`, `enum class`, `constexpr`, small template specialization families, RAII at ownership boundaries, and operator overloads for public symbolic APIs. Those are worth keeping.

This adheres to the [Orthodox C++](https://bkaradzic.github.io/posts/orthodoxc%2B%2B/) philosophy: keep the C++ features that make code safer or clearer, reject the ones that hide work, and prove performance with benchmarks.

```
The public API may be expressive.
The internal implementation must be explicit.
```

---

## Why Performance-First Architecture Matters

Prototype-grade C++ that leans heavily on standard containers, nested vectors, and heap allocations accumulates severe avoidable overhead:
- Quadratic all-pairs intersection before broadphase pruning;
- Nested heap allocations (`std::vector<std::vector<T>>`);
- Per-fragment allocation and deep copies;
- Strings and provenance carried through numeric topology passes;
- Repeated sorting and deduplication of tiny heap-backed vectors;
- Runtime kind branching and dynamic dispatch inside inner loops;
- Hidden deep copies of objects containing containers, strings, optional payloads, and symbolic values.

Writing native C++ in a heap-heavy, object-heavy, string-heavy style can erase the advantage of choosing C++ in the first place. Bad C++ can be slower than optimized high-level languages when it repeatedly allocates, formats strings, walks hash tables, copies rich objects, and misses caches.

---

## The Most Common Agent Failure Mode

Agents tend to write "canonical modern C++" because it looks safe, idiomatic, and locally correct:

```cpp
std::vector<T> out;
std::unordered_map<Key, Value> map;
std::string name;
std::optional<Metadata> metadata;
std::function<void(...)> callback;
std::ostringstream message;
```

These are convenient default tools for tests, scripts, bindings, and cold API glue. They are the **wrong default** for code that performs the underlying computation in hot loops.

---

## The Compiler Will Not Fix Structural Bloat

The compiler optimizes simple functions, inlines code, and folds constants, but it cannot fix architectural bloat. Specifically, the compiler cannot remove:
- Heap allocation required by container growth;
- Allocator bookkeeping and memory fragmentation;
- Cache misses caused by pointer-heavy object graphs;
- Branchy runtime dispatch selected by stored kinds or virtual calls;
- String formatting in inner loops;
- Hash-table probes with unpredictable memory access;
- Deep copies that are semantically observable;
- Poor broadphase or $O(n^2)$ pair generation when the algorithm asked for every pair.

---

## Designing the Computation First

Before writing native subsystems, establish:
1. **What is the hot loop?** How many times can it run per user action?
2. **What data does the hot loop actually need?** What data is only needed for diagnostics, API identity, selection, or export?
3. **Where is memory allocated?** Can a single workspace be retained and reused between evaluations?
4. **What benchmark will catch a regression?**

Public objects exist for UX and ergonomics (`Profile`, `Boundary`, `Solution`). Hot internal records exist strictly for computation (`HotSegment[]`, `PairCandidate[]`, `SplitPoint[]`).

---

## Hot Data vs. Cold Data

- **Hot Data (Minimal numeric state needed by the algorithm):**
  - Kind tags, numeric coordinates, parameter intervals, orientation, tolerance, integer source IDs, loop IDs, compact topology keys.
- **Cold Data (Everything needed later):**
  - Strings, debug paths, names, symbolic handles, Python objects, rich provenance lists, sample buffers, human-readable IDs.

Hot records must carry **integer handles into cold tables**, never cold payloads.

### Anti-Pattern (Heavy Object in Hot Path):
```cpp
struct Segment {
    SegmentKind kind;
    NumPoint a;
    NumPoint b;
    SymbolicPoint sa;
    SymbolicPoint sb;
    std::vector<SourceRef> a_sources;
    std::vector<SourceRef> b_sources;
    std::vector<FragmentSourceProvenance> provenance;
    std::optional<ParametricCurveSegment> parametric;
    std::vector<NumPoint> parametric_samples;
    std::string topology_id;
};
```

### Production Pattern (Flat POD Record):
```cpp
struct HotSegment {
    uint32_t source_id;
    uint32_t loop_id;
    uint32_t first_cold_ref;
    uint16_t kind;
    uint16_t flags;
    double p0[2];
    double p1[2];
    double data[4];
    double t0;
    double t1;
    double tolerance;
};
```

---

## Ownership & Allocation Discipline

### Rules:
1. **Allocate Once & Reuse:** Allocate one retained workspace per evaluation context. Do not allocate inside inner loops.
2. **Flat Retained Buffers:** Use flat contiguous buffers for candidates, split points, and fragments. Clear + reuse capacity instead of construct + destroy.
3. **POD Records:** Hot records must be POD or trivial to copy.
4. **Strings & Diagnostics:** Strings are for humans and logs. Keep strings, provenance, and message formatting completely off the success execution path.
5. **Runtime Dispatch:** Prefer explicit enum tags + switch statements or specialized template kernels over virtual calls or `std::function` in hot loops.

---

## Summary Engineering Checklist

1. [ ] **Public API may be expressive; internal hot paths must be explicit.**
2. [ ] **Separate hot numeric data from cold identity/diagnostic tables.**
3. [ ] **Use POD-like records and integer handles in inner loops.**
4. [ ] **Allocate retained workspaces; eliminate per-call heap containers.**
5. [ ] **Prune and batch algorithms before micro-tuning.**
6. [ ] **Keep strings, provenance, and formatting off the success path.**
7. [ ] **Measure and guard performance with gold end-to-end fixtures.**
