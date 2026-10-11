# Judge Position-Bias Audit

The macro protocol (§7.2) randomises delivery arms across blind labels A–E
before judging. This note reports the position-bias check that the manuscript
does not currently contain.

Reproduce with:

```bash
uv run python scripts/analyze_position_bias.py          # human-readable
uv run python scripts/analyze_position_bias.py --json   # machine-readable
```

Source: `benchmarks/delivery_results_ieee.json`, 396 judged arm-instances
(17 tasks × 5 arms × runs).

## 1. The judge has a strong slot preference

Position effect = mean deviation of that label slot from the grand mean.

| slot | effect | n | mean composite |
|:--|--:|--:|--:|
| A | **+2.08** | 78 | 26.86 |
| B | +0.70 | 80 | 25.48 |
| C | −0.79 | 80 | 23.99 |
| D | **−1.58** | 80 | 23.20 |
| E | −0.37 | 78 | 24.41 |

- One-way ANOVA: **F = 4.5373, p = 0.00136**
- Kruskal–Wallis: **H = 15.82, p = 0.00328** (nonparametric, confirms it)

The A-to-D spread is **+3.66 points — 17× the 0.21-point headline effect.**
This is the single largest systematic effect anywhere in the benchmark, and it
is an artefact of the evaluation instrument rather than of any delivery
strategy.

Both the parametric and nonparametric tests reject, so this is not a
distributional fluke.

## 2. Position is balanced, so it acts as noise not as a confound

| arm | A | B | C | D | E |
|:--|--:|--:|--:|--:|--:|
| checklist | 11 | 15 | 18 | 18 | 18 |
| checklist_v2 | 18 | 12 | 18 | 17 | 15 |
| control | 13 | 15 | 20 | 16 | 15 |
| full | 16 | 19 | 13 | 16 | 14 |
| retrieved | 20 | 19 | 11 | 13 | 16 |

No arm systematically occupies a favoured slot (range 11–20 per cell, which is
what random permutation over 396 draws produces). So the permutation did its
job: position bias is *averaged into noise* rather than *confounding* an arm
with a slot. This is why the correction below barely moves anything — and it
is the reason the bias is a design weakness rather than a fatal flaw.

## 3. Correcting for position changes no conclusion

Corrected score = observed − position effect.

| arm | raw | corrected | shift |
|:--|--:|--:|--:|
| checklist (v1) | 24.54 | 24.74 | +0.20 |
| **checklist_v2** | 24.96 | 24.97 | +0.01 |
| control | 24.49 | 24.61 | +0.11 |
| **full** | 25.17 | 25.09 | −0.08 |
| retrieved | 24.73 | 24.48 | −0.25 |

**Finding 1 holds.** The headline `full − checklist_v2` gap narrows from
+0.204 to **+0.120**. Task-blocked paired test on corrected scores:
**t = 0.1901, p = 0.8516** across 17 tasks. Still no significant difference,
so "structure-preserving compilation does not degrade quality" survives.

**The economics-first premise (§8.6.A) holds.** No arm significantly beats
`control` after correction:

| arm vs control | corrected gap | Welch p |
|:--|--:|--:|
| full | +0.48 | 0.604 |
| checklist_v2 | +0.36 | 0.695 |
| checklist (v1) | +0.13 | 0.898 |
| retrieved | −0.12 | 0.892 |

**Robustness:** excluding slot A entirely (the inflated slot), `full − v2`
widens to +0.407 and the residual spread across the other four slots is +2.28 —
same conclusion under a stricter assumption.

## 4. The real limitation this exposes: statistical power

| quantity | value |
|---|---|
| SD of paired (full, v2) differences | 7.87 |
| pairs | 78 |
| **minimum detectable effect** (80% power, α = 0.05) | **2.53 points** |
| headline gap | 0.21 points |
| headline as % of MDE | **8.3%** |

This is the number the paper should lead with. The benchmark cannot resolve
differences smaller than ~2.5 points out of 35 (~7%). Every reported
"no significant difference" therefore means **"below the detection floor,"**
not **"equivalent."**

The manuscript already says as much in §7.5 ("failure to detect rather than
formal proof of equivalence"), which is to its credit. But it states the
principle without quantifying it. A reviewer asking "what effect size could
this design have detected?" currently gets no answer.

## Recommendations

1. **Report the position effects and the MDE in §9 (Threats to Validity).**
   The bias is real, significant, and larger than every treatment effect —
   concealing it invites the reviewer to find it, and finding it themselves is
   far worse than disclosing it.
2. **Balanced label assignment.** Assign arms to slots by a Latin-square-like
   scheme (each arm appears in each slot roughly equally within every task)
   rather than by free random shuffle. This removes the effect by design
   instead of correcting it post hoc.
3. **Report position-corrected means alongside raw means** in Table 1, so the
   null result is visibly robust to the instrument's own bias.
4. **State the MDE explicitly** wherever a null is reported. This is free and
   removes the most obvious reviewer objection.

None of these require new experiments. Items 1, 3 and 4 are pure reporting.

## Note on related confounds

Two other instrument-level effects are documented elsewhere and are *not*
addressed here:

- **Judge window truncation.** ~88% of macro-benchmark responses exceed the
  10,000-character judge window (§9 covers this only for the ablation harness).
- **Single-judge design.** No inter-rater agreement κ is computable, since only
  one judge model was used (paper §9, acknowledged).