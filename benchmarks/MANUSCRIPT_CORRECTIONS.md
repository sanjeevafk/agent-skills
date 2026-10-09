# Manuscript Corrections Log

Editorial pass applied to `paper/MANUSCRIPT.md` on 2026-10-09.

`paper/` is git-ignored (unpublished manuscript, third-party PDFs), so these
edits are **not** in the artifact repository's history. This file records what
changed and the evidence behind each correction, so reviewers and future
authors can audit them.

Every numeric correction below was re-verified against the archived data before
being applied. Nothing was changed on the basis of a draft note.

## A. Claims that overstated the evidence

### A1. Headline reframed from "30% savings at no quality cost" to a
###     detection-limited null

**Was:** "structure-preserving static compilation achieved a mean score within
0.21 points of uncompressed manuals … while reducing prompt overhead by 30.0%."

**Now:** the central result is stated as a null with an informative asymmetry,
in the abstract, Finding 1, §10, and Finding 4.

**Why:** the claim "no quality cost" requires ruling out degradation below the
detection threshold. With a measured test-retest floor of σ = 6.09 on
byte-identical prompts, the minimum detectable effect at 80% power is ≈ 2.53
points on the 35-point rubric (7.2%). The 0.21-point gap is 8.3% of that floor,
and resolving it directly would need roughly 3,700 paired runs. "No significant
difference" here means *below threshold*, not *equivalent*.

The paper already said this in §7.5 in principle but never quantified it. The
defensible claim — "format effects below ~7% of the rubric are not observable
in this design" — is stronger and is now stated explicitly.

### A2. Abstract shortened from ~805 to 236 words

IEEE limits abstracts to roughly 250 words. The previous abstract was
non-compliant by a factor of three. Rewritten around the null + TDD
asymmetry rather than the compression win.

### A3. `r = +0.616` construct-validity claim removed

**Was (§9 and abstract):** "in self-contained tasks, syntax compilation aligns
strongly and statistically significantly with the judge's Correctness subscore
(e.g. `sec-django-hardening`: r = +0.616, p = 0.001)."

**Now:** the pooled null (Pearson r = +0.047, p = 0.473) is presented as the
only reproducible construct-validity figure, and the paper states explicitly
that per-task subgroup correlations are not independently recomputable from the
artifact because the per-run `syntax_rate` records were never persisted.

**Why:** `scripts/run_execution_calibration.py` rebuilt `calibration_records`
in memory and wrote only a Markdown report; no machine-readable calibration
JSON exists in the repository. Worse, lines 616 and 689 of that script embedded
`r = +0.616, p = 0.001` and `r = +0.344, p = 0.108` as **literal text inside
f-strings** — adjacent to genuinely interpolated values such as `{pear_r:.3f}`.
Re-running the calibration therefore reproduced the same claim regardless of
what the data actually showed.

**Also fixed:** the generator now interpolates the two largest computed
subgroup correlations instead of hardcoding them, and states that per-task
values are not persisted.

### A4. "Wins" and "Rank Points" columns removed from Table 1

These came from the judge's free-text `ranking` field, not from the scores, and
were never defined in the paper. Recomputed: across the 80 judgement records
carrying a ranking, the judge's top-ranked arm was not its own highest-scoring
arm in **10 cases (12.5%)**. Under that measure `checklist_v2` received the
*fewest* top rankings (10) while holding the second-highest mean, and
`checklist_v1` received the *most* (18) while holding the lowest mean — an
ordering that inverts the score column printed beside it.

Replaced with a note recording that the ranking field was collected, found
unreliable, and deliberately discarded.

## B. Numeric corrections

| location | was | now | verified by |
|---|---|---|---|
| §8.4 header | N = 66 scored runs | **N = 69** | 69 records in `ablation_results.json` (a1=12, a2=21, a3=18, a4=18) |
| §8.4 A2 paired test | mean diff **+1.53**, t = **+0.67** | **−1.53**, t = **−0.67** | mean of the paper's own six listed deltas (2.00, 2.00, −8.50, −9.00, 2.00, 2.33) = −1.5283; SD 5.598 → t = −0.6688 |
| abstract + §9 judge-window pilot | mean gap **+0.83** | **−0.83** | `judge_window_pilot.json`: 6 paired outputs, diffs (24k − 10k) = [−3, −7, +1, +1, −5, +8], mean −0.8333, p = 0.7201 |

Both sign errors were direction-only: magnitudes and p-values were already
correct. Neither changes a conclusion, but both would be caught by a careful
reviewer and would cast doubt on the surrounding numbers.

## C. Threats to Validity — two subsections added

### C1. Judge Position Bias and Statistical Power

Discloses a bias the manuscript never tested. Per-slot mean deviations from the
grand mean: A +2.08, B +0.70, C −0.79, D −1.58, E −0.37. One-way ANOVA
F = 4.5373, p = 0.00136; Kruskal–Wallis H = 15.82, p = 0.00328. The A-to-D
spread of +3.66 points is ~17× the headline treatment effect and is the largest
systematic effect in the benchmark.

Position is close to balanced across arms (11–20 runs per arm-slot cell), which
is what the random permutation was designed to achieve, so the bias averages
into noise rather than confounding an arm with a slot. Correcting for it leaves
every conclusion intact (`full` − `checklist_v2` narrows +0.204 → +0.120, paired
t = 0.1901, p = 0.8516; no arm beats `control`, all Welch p > 0.6; excluding
slot A widens the gap to +0.407).

Reproduce with `uv run python scripts/analyze_position_bias.py`. Full write-up
in `POSITION_BIAS_AUDIT.md`. Pinned by `TestJudgePositionBias` in
`tests/test_paper_claims.py`.

### C2. Statistical Power

States the minimum detectable effect (≈ 2.53 points at 80% power, from SD 7.87
on 78 paired comparisons) and which findings survive it: TDD tracer-bullet
removal (Δ = −8.50) clears the 6.09 floor; the `checklist_v1` Testing & QA drop
(Δ = −6.32, n = 11) clears it only marginally.

## D. Compiler provenance (§7.1)

Corrected in the previous commit. Summary:

- The "abstract syntax tree (AST)" characterisation was wrong — the
  implementation is a line-oriented section parser. Prose now says
  "section-and-element structure", and Algorithm 1's pseudocode variable was
  renamed `AST` → `TREE` so it no longer contradicts the prose.
- §7.1 now names `crates/skills-compiler` and states that all five delivery
  arms and all ablation conditions come from it.
- The test count was corrected from "13 unit tests" to 14 A4-specific tests,
  with a breakdown of behavioural guards versus known-gap characterisation
  tests.

## Not changed, still open

- **`checklist_v2` confound.** The arm is the only one carrying an extra
  `[INSTRUCTION]` directive, which plausibly explains its higher output-token
  volume. Not addressed by any edit here — it needs a re-run, not a rewrite.
- **"Sub-second skill routing"** in §8.7 contradicts the paper's own measured
  2.08 s end-to-end (cross-encoder p50 = 1.95 s). The §8.7-A naive baseline
  ("4.5 minutes" for 440 passes) is ~3.2× faster than the measured per-pass
  cost. Needs a wording fix.
- **Token figures** throughout are `len(text) // 4` character estimates rather
  than real tokenizer output. The 680-token and 30.0% numbers inherit the
  approximation and should be described as estimates.
- **`skills/tdd/SKILL.md` and `skills/debugging-code/`** remain unrestored, so
  2 of 18 artifacts do not reproduce and two tests are `xfail`.