# Performance by Design: A C++ Guide

This document is a practical guide for writing native code that starts
close to the desired performance shape instead of requiring a long cleanup pass
after the prototype works.

The short version:

```
Design hot paths as C-style code so costs, data flow, and algorithmic shape remain explicit.
Use C++ only where it gives real safety, clarity, or compile-time structure.
Do not rely on the compiler to erase bad data structures, allocations, copies,
string formatting, dynamic dispatch, or bad algorithmic complexity.
```

This is not an argument for rewriting the codebase in C. C++ gives useful tools:
namespaces, references, `nullptr`, `enum class`, `constexpr`, small template
specialization families, RAII at ownership boundaries, and operator overloads
for the public symbolic API. Those are worth keeping.

This is close in spirit to Branimir Karadžić's
[Orthodox C++](https://bkaradzic.github.io/posts/orthodoxc%2B%2B/) and the
broader C-like C++ mindset, but it is not a mechanical adoption of any external
style guide. The rule is practical: keep the C++ features that make our code
safer or clearer, reject the ones that hide work, and prove performance with
benchmarks.

The rule is narrower and more important:

```
The public API may be expressive.
The internal implementation must be explicit.
```

In systems such as parametric CAD and computational geometry, evaluation paths
are not isolated utility code. Symbolic values, nonlinear solving, profile CSG,
selection, measurement layout, document export, meshing, and future simulation
all compose. Through composition, even a "minor" routine can run inside a solver
inner loop or CSG retry step, or become a browser interaction or export
bottleneck. Treat every routine as potentially performance-sensitive.
Measurement determines where to spend optimization effort, not where disciplined
design begins.

## Why This Document Exists

One early profile CSG implementation proved semantics: profile graphs, generated
boundaries, provenance, tolerance diagnostics, selection, export, and several
boolean cases. That work was useful. It also accumulated prototype-grade C++:

```
std::vector<std::vector<SplitPoint>> split_points;
std::vector<SplitPoint> unique;
Segment fragment = segment;
std::ostringstream out;
std::string topology_id = ...;
```

That style made the implementation easy to extend locally, but expensive to
make fast later. It created several classes of avoidable cost:

* quadratic all-pairs intersection before broadphase pruning;
* nested heap allocations;
* per-fragment allocation and deep copies;
* strings and provenance carried through numeric topology passes;
* resampling during split instead of preserving analytic intervals;
* repeated sorting and deduplication of tiny heap-backed vectors;
* runtime kind branching inside inner loops;
* hidden deep copies of objects containing containers, strings, optional heavy
  payloads, symbolic values, and provenance records.

In one measured case study, targeted rewrites moved the gold scripting-layer
DXF fixtures from:

```
constrained_mounting_plate    18.766 ms  ->  10.054 ms
dense_drill_pattern         3381.881 ms  ->  16.481 ms  (~205x faster)
stepped_boolean_bracket       31.516 ms  ->  10.048 ms
```

In that case study, the three-fixture total went from `3432.163 ms` to
`36.583 ms` in one repeat-5 sample. That is about `94x` faster overall, with one
fixture crossing a `200x` movement. The measurements come from the same gold
DXF workflow.

This is serious. A `2x` improvement might be ordinary tuning. A `10x`
improvement usually means the algorithm or data layout was wrong. A `100x` to
`200x` improvement is not "C++ got optimized"; it is proof that the original
architecture was doing the wrong work. That gap is larger than the ordinary
performance difference people expect between native C++ and Python for many
real workloads. In other words, writing native C++ in a heap-heavy,
object-heavy, string-heavy style can erase the advantage of choosing C++ in the
first place.

Bad C++ can be slower than Python for the operation the user actually cares
about. That does not mean Python loops are faster than native loops. It means a
pure-Python implementation can beat C++ code that repeatedly allocates, formats
strings, walks hash tables, copies rich objects, misses caches, and runs the
wrong algorithmic shape. Language choice does not rescue bad architecture.

The lesson is uncomfortable but important: prototype-grade C++ can be slow
enough that the language choice stops mattering. The winning change was not one
clever intrinsic or one compiler flag. It was removing avoidable work: fewer
containers, fewer allocations, fewer copies, less string/provenance traffic in
numeric loops, better pruning, and data shaped around the computation.

That improvement proves the original shape was wrong. It would have been
cheaper to build the fast shape first.

The purpose of this guide is to make that first implementation style more
repeatable.

## What Would Have Been Cheaper

Within the same case study, the dense drill fixture did not become about `205x`
faster because of a single magic trick. It moved because many pieces of
prototype C++ were removed or reshaped:

* all-pairs work was pruned before expensive routines where possible;
* rich copied Segment objects were replaced or bypassed in hot paths;
* nested scratch vectors were moved toward flat retained buffers;
* source/provenance strings were moved out of topology identity and hot
  comparison paths;
* small ID lookups moved to specialized ID tables instead of generic maps;
* repeated temporary allocation was replaced with retained scratch storage;
* diagnostic formatting stopped being paid on the success path;
* exact end-to-end gold benchmarks made regressions visible.

The important point is not that every individual change was large. Many were
small and some were rejected after benchmarking. The large speedup came from
the accumulated removal of avoidable work from a path that ran many times.

A later CSG slice from the same case study is a useful example of how to choose
the right level of attack. The split-heavy edge-notch gold fixture still took
about `24.894 ms` after many local CSG cleanups. A local in-place
segment-reversal cleanup was tested and rejected because it did not move the
gold run. The real win was one level higher: `difference(base, *cutters)` was
still executing as many sequential binary booleans even when the cutters were
independent. Batching those independent cutters into one multi-loop cutter
region moved the focused edge-notch benchmark from roughly `28-29 ms` to
`5.633 ms`, and the gold fixture from `24.894 ms` to `10.887 ms`.

The lesson is direct: when the profile says a phase is being repeated, first
ask whether the whole phase can be removed, batched, or reordered under a clear
invariant. Only tune the local loop after the algorithmic shape is right.

Writing the fast shape first would have meant:

1) Lower user-facing geometry into compact numeric arrays before boolean work.
2) Keep names, provenance, Python-visible dictionaries, and diagnostic strings
   in cold side tables.
3) Use integer topology/source keys during computation.
4) Allocate one retained workspace for split points, pair candidates,
   fragments, classification scratch, and validation scratch.
5) Add broadphase before pair intersections.
6) Write specialized line/arc/parametric kernels instead of carrying rich
   generic objects through every pair.
7) Attach provenance only after topology survives filtering and assembly.
8) Put gold end-to-end fixtures in place before optimizing so every slice has a
   guardrail.

That is the expected first-pass shape for similar implementations. A correctness
prototype that intentionally violates it must be labeled temporary and have a
rewrite plan. Otherwise it will become production debt.

## The Most Common Agent Failure Mode

Agents tend to write "canonical modern C++" because it looks safe, idiomatic,
and locally correct:

```
std::vector<T> out;
std::unordered_map<Key, Value> map;
std::string name;
std::optional<Metadata> metadata;
std::function<void(...)> callback;
std::ostringstream message;
```

These are convenient default tools, and for tests, scripts, bindings, and cold
API glue they can be fine. They are the wrong default for code that performs
the underlying computation.

The failure pattern is usually:

1) Implement a feature with rich objects because that is locally easy.
2) Put everything needed by any consumer into one record.
3) Use standard containers because they make ownership easy.
4) Use strings because they are human-readable and stable.
5) Add correctness tests.
6) Extend the feature repeatedly.
7) Discover that the "small" path is now called thousands of times.
8) Benchmark and find that the cost is allocation, copying, lookup, formatting,
   and topology shape, not the actual math.
9) Spend multiple iterations undoing the original data model.

That is what happened in parts of the codebase. Do not repeat it.

## The Compiler Will Not Fix This

The "zero-overhead abstraction" phrase is often misused. The compiler can
inline simple functions, remove dead stores, fold constants, and optimize
obvious loops. It cannot turn an unsuitable architecture into a good one.

The compiler generally cannot remove:

* heap allocation required by container growth;
* allocator bookkeeping;
* cache misses caused by pointer-heavy object graphs;
* branchy runtime dispatch selected by stored kinds or virtual calls;
* string formatting;
* hash-table probes with unpredictable memory access;
* deep copies that are semantically observable;
* poor broadphase or no broadphase;
* O(n²) pair generation when the algorithm asked for every pair;
* debug-build overhead from layered templates and standard-library iterators;
* compile-time cost from abstraction stacks.

Even when optimized builds recover some overhead, debug builds remain important.
The codebase is developed, tested, debugged, and benchmarked in local debug builds.
Slow debug builds reduce iteration speed and hide algorithmic thinking behind
toolchain patience.

Design for explicit work. Then let the compiler optimize that.

## Design The Computation First

Before writing a new native subsystem, answer these questions:

```
What is the hot loop?
How many times can it run per user action?
Can it run inside nonlinear solve retries?
Can it run once per segment, pair, residual, sample, cell, or element?
What data does the hot loop actually need?
What data is only needed for diagnostics, API identity, selection, or export?
Where is memory allocated?
Can the same workspace be reused between evaluations?
What is the expected tiny, medium, large, and pathological size?
What benchmark will catch a regression?
```

Do this before choosing public-facing class shapes or standard containers.

The public object model can remain ergonomic:

```
Circle
Rectangle
Profile
Boundary
Solution
Selection
Document
```

The implementation should lower those objects into compact arrays and side
tables:

```
HotSegment[]
HotVertex[]
HotLoop[]
PairCandidate[]
SplitPoint[]
FragmentRecord[]
ColdSourceTable
ColdDiagnosticTable
```

The conversion boundary is deliberate. Public objects exist for UX. Hot records
exist for computation.

## Hot Data And Cold Data

Hot data is the minimum numeric state needed by the algorithm:

```
kind tags
numeric coordinates
parameter interval endpoints
orientation
tolerance
source integer ids
loop ids
compact topology keys
```

Cold data is everything needed later:

```
strings
debug paths
names
symbolic Value handles
Python objects
rich provenance lists
docstrings
sample buffers
human-readable topology ids
selection descriptions
```

The hot record should carry integer handles into cold tables, not cold payloads.

Bad shape:

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

Better shape:

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

The second record is not the final exact record. It shows the direction:
copy-cheap numeric fields in the hot path, rich information elsewhere.

## Ownership Rules

Hot records should usually be POD or close to POD. A record that is repeatedly
copied, sorted, filtered, or stored in scratch buffers must be cheap to move
and preferably trivial to copy.

Prefer:

* value types with fixed-size fields;
* integer handles;
* indices into retained workspaces;
* plain arrays or `std::vector` of POD records when ownership is clear and the
  container lives outside the innermost loop.

Avoid in hot paths:

* nested `std::vector`;
* `std::string`;
* `std::unordered_map` / `std::map` for tiny sets that could be linear or hashed
  with a specialized table;
* `std::optional` wrapping heavy objects;
* `std::function`;
* polymorphic base pointers when the set of kinds is closed and known;
* objects that own other containers by value and therefore deep-copy on
  assignment.

RAII is still useful at ownership boundaries: arenas, workspaces, file handles,
Python object holders, and document-level resources. It is not a reason to make
every intermediate fragment a rich owning object.

## Allocation Discipline

Default rule:

```
Allocate once (or once per evaluation) and reuse.
Do not allocate inside the inner loop unless measurement proves it is free.
```

Practical patterns:

* One retained workspace per evaluation context.
* Flat buffers for candidates, split points, fragments, and classification
  results.
* Clear + reuse instead of construct + destroy.
* Reserve capacity from expected size when the upper bound is known.
* Prefer index-based references over pointer-rich graphs when the lifetime is
  the workspace lifetime.

If a routine needs temporary storage, prefer a caller-provided scratch buffer
or a workspace member over a local `std::vector` that grows every call.

## Algorithmic Shape Before Micro-Optimization

When a path is slow, first ask:

1. Is the work necessary?
2. Can independent work be batched?
3. Can expensive work be pruned before it runs?
4. Is the data already in the right form, or is conversion repeated?
5. Is a higher-level rewrite available (multi-boolean instead of sequential
   binary, analytic intervals instead of resampling, etc.)?

Only after the shape is right should local loop tuning, inlining, or specialized
kernels be the focus.

A local optimization that does not move the end-to-end gold benchmark is usually
not the right place to spend time yet.

## Strings And Diagnostics

Strings are for humans, logs, export, and Python-facing identity. They are not
for topology identity or hot comparison keys.

Prefer:

* integer source ids;
* compact topology keys;
* side tables that map ids to human-readable strings only when needed.

Do not format diagnostic messages on the success path. Format them when a
failure or explicit diagnostic request actually occurs.

## Runtime Dispatch

Closed sets of geometric kinds (line, arc, circle, parametric, …) should prefer
explicit tags + switch or specialized kernels over virtual calls or
`std::function` in hot loops.

If the set is open and truly extensible by plugins, virtual dispatch may be
justified at a coarser boundary. Keep it out of the innermost numeric kernels
when possible.

## Measurement

Gold end-to-end fixtures are the primary guardrail. Microbenchmarks are useful
for isolating a kernel, but the decision to keep a change is driven by the gold
runs that represent real user workflows.

When measuring:

* Use the same fixtures before and after.
* Prefer repeat runs and report stable statistics.
* Watch both optimized and debug builds; debug iteration speed matters.
* Reject changes that improve a microbench but do not move (or regress) the
  gold path.

## Summary Rules

1. Public API may be expressive; internal hot path must be explicit.
2. Separate hot numeric data from cold identity/diagnostic data.
3. Prefer POD-ish records and integer handles in inner loops.
4. Allocate retained workspaces; avoid per-call nested containers.
5. Fix algorithmic shape (pruning, batching, lowering) before micro-tuning.
6. Keep strings, provenance, and formatting off the success path.
7. Measure with gold end-to-end fixtures.
8. Treat every routine as potentially performance-sensitive until measurement
   says otherwise.

Write code that makes the work visible. Then benchmark it.
