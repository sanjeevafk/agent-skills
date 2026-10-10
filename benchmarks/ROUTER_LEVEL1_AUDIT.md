# Level 1 Routing Benchmark — Corrected Run (2026-10-10)

Regenerated `benchmarks/router_level1_results.json` after fixing every defect in
the original §8.7 evaluation. **The headline conclusion reversed.**

## What was wrong before

| # | defect | evidence |
|---|---|---|
| 1 | The "TF-IDF baseline" was a hand-weighted keyword scorer (exact-name 100, substring 30, tag 20, desc 15, category 10) | `benchmark_router.py:34-59` (old) |
| 2 | Catalogue vectors embedded `f"{name}: {desc}"`, leaking skill names | `build_skill_embeddings.py:42` (old) |
| 3 | `sec-webhook-audit-ieee`'s prompt opens with the literal skill name | `tasks_ieee.json` |
| 4 | Stale cache: 440 manifest entries vs 413 indexed skills, silently searched | `laya_router.py:__init__` validated only the model string |
| 5 | Stage 2 (`laya`) was not importable; paper named `NandhaKishorM/laya`, code defaulted to `convaiinnovations/laya` | neither package installs from the project env |
| 6 | Two gold labels disagreed with the benchmark skill binding | `router_level1_results.json` vs `tasks_ieee.json` |
| 7 | Level 2 was n=1, unseeded, unrecorded | `run_level2_benchmark.py:213` |

## What changed

- **Baseline is now genuine unigram TF-IDF**, ported from the delivery harness
  (`skill_delivery_experiment.py:tfidf_score`) so it matches the macro benchmark's
  `retrieved` arm.
- **Catalogue vectors embed descriptions only**; a build-time guard now rejects
  any document using the leaky `name: description` rendering.
- **Stale-cache guard**: vector count, manifest count, and index count must agree
  or the router refuses to start.
- **Julia-1 replaces Laya as the Stage 2 decision head.** Verified locally: loads
  in ~4.2 s, decides in 78–276 ms on CPU, deterministic across repeated calls,
  correct routing on the Django probe (0.919 confidence). Julia-1 pins
  `transformers>=5.0,<5.1`, which `sentence-transformers` also accepts.
- **Gold labels canonicalised** and asserted present in the catalogue:
  `sre-node-leak-ieee` → `systematic-debugging` (its benchmark binding
  `debugging-code` is absent from disk and therefore unroutable);
  `qa-ratelimiter-tdd-ieee` → `tdd` (benchmark binding, also what the §8.4
  ablation used; the prior router's `tdd-workflow` was wrong).
- **Freebie task excluded** from the headline rate and reported separately.
- **Catalogue rebuilt from disk truth: 530 skills** (was 440 in the manifest,
  413 in `skills.json`).

## Results (17 scorable tasks; 1 freebie excluded)

| method | Top-1 | Top-5 |
|---|---:|---:|
| **TF-IDF baseline (real)** | **8/17 (47.1%)** | 11/17 (64.7%) |
| Stage 1 only (BGE-small) | 7/17 (41.2%) | 11/17 (64.7%) |
| Stage 1 + Julia-1 rerank | **2/17 (11.8%)** | 11/17 (64.7%) |

Latency: TF-IDF p50 1.71 ms; two-stage p50 516 ms (Julia-1 dominates).

## The finding

**Julia-1 reranking destroys Stage 1 accuracy: −5 tasks (7/17 → 2/17).**

In 9 of 11 cases the correct skill was already in the Stage-1 shortlist and
Julia-1 overrode it. Representative failures:

| task | gold | rank in Stage 1 | Julia-1 chose |
|---|---|---:|---|
| `qa-checkout-e2e-ieee` | `e2e-testing` | 1 | `playwright` |
| `devops-api-k8s-ieee` | `kubernetes-patterns` | 1 | `get-available-resources` |
| `sre-p99-regression-ieee` | `performance-profiler` | 1 | `nasa-power-of-ten-python` |
| `sec-amm-pool-ieee` | `defi-amm-security` | 1 | `deal-screening` |

Two contributing causes, both measured:

1. **Option truncation.** Julia-1 enforces a 48-token limit per option. Skill
   descriptions average 42 words (median 35, max 124), so a deterministic clip
   ladder was required; 17 of 18 routes were clipped (10 at 32 words, 6 at 24,
   1 at 18), retaining ~79% of description text. The model frequently receives
   fragments rather than the discriminating content.
2. **Near-duplicate catalogue entries.** `e2e-testing` is described as
   "Playwright E2E testing patterns, Page Object Model…" while `playwright`
   covers the same ground. These are genuinely ambiguous, and the vendor's own
   card warns that "ambiguous wording… can also cause mistakes."

## Consequences for the manuscript

The prior §8.7 claims — 55.6% Top-1, 61.1% Top-5 for the two-stage router, and
0.0% for the "TF-IDF baseline" — are **both withdrawn**. The 55.6% figure came
from a run whose baseline was rigged and whose vectors leaked skill names. The
0.0% figure came from a scorer that cannot score anything correctly by
construction.

Honest replacements: real TF-IDF 47.1% / 64.7%; Stage-1-only dense retrieval
41.2% / 64.7%; adding Julia-1 reranking **reduces** Top-1 to 11.8%.

## What this does and does not establish

- It **does not** show Julia-1 is unsuitable for routing in general. It shows a
  144M decision model, fed clipped descriptions from a catalogue containing
  near-duplicates, degrades a competent dense retriever on these 17 queries.
- Retrieval recall (Top-5) is unchanged at 11/17, so **Stage 1 is the
  bottleneck**; reranking cannot recover what shortlisting missed.
- n=17 is small. The −5 delta is consistent and directionally clear but a
  per-task sign test would not reach significance; it should be reported as a
  measured regression, not a precise effect size.

## Open items

1. **Level 2 was not re-run.** The old n=1 head-to-head (24.67 vs 23.00) used the
   withdrawn router and cannot be kept. Re-running it now would test a pipeline
   shown to be worse than its own Stage 1, so it should be dropped rather than
   re-run unless the truncations are fixed first.
2. **Truncation fix**, if Julia-1 is to be retained: compress descriptions to a
   discriminative summary (embedding-free) rather than word-clipping, and verify
   the option budget empirically per option.
3. **Julia-1 routing remains available** as a baseline for a held-out study with
   ~200 non-benchmark queries and a de-duplicated catalogue.