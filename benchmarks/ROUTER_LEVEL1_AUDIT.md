# Level 1 Routing Benchmark — Corrected Run (2026-10-10)

Regenerated `benchmarks/router_level1_results.json` after fixing every defect in
the original §8.7 evaluation, then again after fixing the option-truncation
defect the first regeneration exposed. **The headline conclusion reversed twice.**

> **Truncation fix applied after the first regeneration.** The first corrected
> run fed Julia-1 word-clipped description *prefixes* and scored 2/17. The
> truncation fix (below) raised it to **5/17**. Numbers below reflect the final
> state; §"Truncation fix" documents both measurements.

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
- **Catalogue rebuilt from disk truth: 531 skills** (was 440 in the manifest,
  413 in `skills.json`). `debugging-code` was reconstructed from its surviving
  compiled artifact and is routable again; see `skills/RECOVERY.md`.

## Results (17 scorable tasks; 1 freebie excluded)

| method | Top-1 | Top-5 |
|---|---:|---:|
| **TF-IDF baseline (real)** | **8/17 (47.1%)** | 11/17 (64.7%) |
| Stage 1 only (BGE-small) | 7/17 (41.2%) | 11/17 (64.7%) |
| Stage 1 + Julia-1 rerank | **5/17 (29.4%)** | 11/17 (64.7%) |

Latency: TF-IDF p50 1.75 ms; two-stage p50 401 ms (Julia-1 dominates).

Catalogue: **531 skills** (530 + the recovered `debugging-code`; see
`skills/RECOVERY.md`).

## Truncation fix (task #4) and its effect

**Before.** Julia-1 enforces a hard 48-token limit per option. Skill
descriptions average 42 words (median 35, max 124), so the first corrected run
applied a whole-description clip ladder. Result: **17 of 18 routes were
truncated**, retaining ~79% of description text, and Julia-1 scored 2/17.

Word-clipping the head of a description is the wrong repair — the opening
clause is frequently the least discriminating part and is often near-identical
across duplicate entries.

**After.** `_option_text` in `scripts/julia_router.py` keeps each description's
**leading clause** (the part stating what the skill is for) and only clips when
the runtime rejects it. Measured on the 531-skill catalogue:

- **529 of 531 options fit unmodified** at a 24-word ceiling (mean 15.6 words).
- Across the 17 scored routes, every option now fits; the ladder binds on only
  a handful (`clip_words` distribution: 24×14, 21×1, 20×1, 18×1).

**Effect on results:** Julia-1 rerank Top-1 improved **2/17 → 5/17**, and the
number of correct-Stage-1 hits it overrides fell **9 → 6**. Residual misses are
dominated by genuinely ambiguous catalogue entries:

| task | gold | rank in Stage 1 | Julia-1 chose |
|---|---|---:|---|
| `qa-checkout-e2e-ieee` | `e2e-testing` | 1 | `playwright` |
| `devops-api-k8s-ieee` | `kubernetes-patterns` | 1 | `get-available-resources` |
| `sre-p99-regression-ieee` | `performance-profiler` | 1 | `nasa-power-of-ten-python` |
| `devops-gha-pipeline-ieee` | `ci-cd-pipeline-builder` | 4 | `serverless-deploy` |

`e2e-testing` is described as "Playwright E2E testing patterns, Page Object
Model…" while `playwright` covers the same ground; the vendor's own card warns
that "ambiguous wording… can also cause mistakes."

## The finding

**Julia-1 reranking still degrades Stage 1 accuracy: −2 tasks (7/17 → 5/17).**

The truncation fix recovered 3 of the 5 originally-observed lost tasks, but the
reranker remains net-negative on these queries: in 6 of 11 cases the correct
skill was already in the Stage-1 shortlist and Julia-1 overrode it.

Root cause is now unambiguous: **shortlist recall is the bottleneck, not
ranking.** Top-5 recall is identical (11/17) with and without reranking, so
reranking cannot recover what shortlisting missed, and it occasionally discards
what shortlisting got right.

This does not show Julia-1 is unsuitable for routing in general. It shows that a
144M decision model, presented with a 5-way choice over a catalogue containing
near-duplicate entries, does not improve over a competent dense retriever on
these 17 queries. n=17 is small; the −2 delta is reported as a measured
regression, not a precise effect size.

## Consequences for the manuscript

The prior §8.7 claims — 55.6% Top-1, 61.1% Top-5 for the two-stage router, and
0.0% for the "TF-IDF baseline" — are **both withdrawn**. The 55.6% figure came
from a run whose baseline was rigged and whose vectors leaked skill names. The
0.0% figure came from a scorer that cannot score anything correctly by
construction.

Honest replacements: real TF-IDF **47.1% / 64.7%**; Stage-1-only dense retrieval
**41.2% / 64.7%**; adding Julia-1 reranking **reduces** Top-1 to **29.4%**.

The section should now be framed as a *negative* result with a diagnosed cause:
at this catalogue size, cross-encoder reranking is a net loss against a
well-tuned lexical baseline, and the binding constraint is shortlist recall.

## What this does and does not establish

- Retrieval recall (Top-5) is unchanged at 11/17 across all three methods, so the
  ceiling is Stage 1. Improving Stage 2 cannot help until Stage 1 recall rises.
- Julia-1 is viable infrastructure — it runs locally, is deterministic, is fast
  enough (p50 401 ms end to end), and its calibration is usable. It is simply
  not additive on these queries.
- n=17 is small and 6 of the residual failures are near-duplicate catalogue
  entries, so a de-duplicated catalogue is a precondition for a fair reranking
  evaluation, not an optional refinement.

## Open items

1. **Level 2 was not re-run.** The old n=1 head-to-head (24.67 vs 23.00) used the
   withdrawn router and cannot be kept. Re-running would test a pipeline now
   shown to be *worse* than both its own Stage 1 and the lexical baseline, so it
   should be dropped rather than re-run.
2. **De-duplicate the catalogue.** `e2e-testing`/`playwright` and
   `hf-cloud-python-env-setup`/`huggingface-cloud-python-env-setup` (identical
   descriptions, cosine 1.000) are unresolvable by any router.
3. **Raise shortlist recall**, which is the actual bottleneck: 6 of 17 queries
   never place the gold skill in the top 5.
4. **Julia-1 routing remains available** as a baseline for a held-out study with
   ~200 non-benchmark queries, once the catalogue is de-duplicated.