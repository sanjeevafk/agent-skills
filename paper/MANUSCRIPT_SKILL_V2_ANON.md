# Measuring the Floor Before Claiming the Null: Agent Skill-File Delivery Formats in an LLM-Judged Coding Benchmark


## Abstract

A report of "no significant difference" in an LLM-judged software engineering benchmark is uninterpretable unless the reader knows what the instrument could have detected. We make the measurement floor the primary result. Across 396 blind judged runs, five delivery conditions, whose compiled variants span 0--70.8% token reduction, produced a full-arm range of only 0.68 points on a 35-point rubric. We report this as **detection-limited, not as equivalence**. The pooled within-cell test--retest floor is $\sigma = 5.37$; against the task-blocked design ($\sigma_d = 3.76$ over 17 task pairs), the exact minimum detectable effect at 80% power is 2.72 points. The observed 0.27-point gap is 10.1% of that threshold, and resolving it would require roughly 1,500 task pairs. We also audit our own prior claims: an earlier draft's floor and threshold could not be reproduced, and our first correction then applied a two-sample formula to a paired design, overstating the threshold by a factor of $\sqrt{2}$. The correction did not strengthen the conclusion; it only made it defensible. We quantify a judge slot-position bias 13 times the task-paired effect, and report that the rubric's relationship to executable correctness is unestablished at this scale ($r = +0.047$, $p = 0.473$).

**Keywords:** Reproducibility, Negative Results, Measurement Validity, LLM-as-a-Judge, Software Engineering Benchmarks, Agent Skills, Context Engineering.

---

## 1. Introduction

Agent skill files are Markdown documents loaded into a coding agent's context. They carry API conventions, architectural invariants, testing patterns, and procedural guidance. A team configuring twenty of them pays their token cost on every turn. Compression is the obvious response, but its safety is untested.

Comparisons of prompt formats report a mean difference and a $p$-value without asking whether the instrument could have detected an effect that mattered. A 0.2-point difference on a 35-point rubric is then called "no significant difference," conflating *we found nothing* with *we could not have found anything*.

We ask three questions. **RQ1:** across five delivery conditions, with compiled variants spanning 0% to 70.8% token reduction, does any measurably change output quality? **RQ2:** which structural components (examples, tables, types) account for any difference against a test--retest floor? **RQ3:** is a routing layer better than a tuned lexical baseline or than passing the whole catalogue in context?

Our answer to RQ1 is a detection-limited null, not equivalence. We make the power calculation the contribution: the floor comes from within-cell variation on byte-identical prompts, is recomputed by released code, and is converted into the sample size needed to settle the question. A positive control also fires: aggressive bulletization moved Testing & QA by $-6.32$ points, above the floor. Nothing here licenses a compression ratio for another corpus.

### 1.1 Background and Objectives

A skill file is Markdown with frontmatter and prose. It may carry structural metadata, imperative standards for concurrency or security, or syntactic anchors for interface contracts. These enter context wholesale, by retrieval, or by compilation into a reduced form. Three properties are asserted but rarely measured: token overhead, the structural necessity of body components, and the value of retrieval.

A conventional comparison reports a mean difference and a significance test. If $p > 0.05$, the standard reading is "no difference." That reading is wrong whenever the instrument lacks power to resolve a difference that would matter. For a paired design at significance $\alpha$ and power $1-\beta$, the minimum detectable effect is $\text{MDE} = (z_{1-\alpha/2} + z_{1-\beta}) \cdot \sigma_d / \sqrt{n}$, where $\sigma_d$ is the standard deviation of paired differences and $n$ the number of pairs. The denominator is $\sqrt{n}$, not $\sqrt{2/n}$: the factor $\sqrt{2}$ belongs to independent means, whereas a paired test conditions on the task with standard error $\sigma_d/\sqrt{n}$. Because this benchmark blocks on task, the pairing unit is the task. With $n-1 = 16$ degrees of freedom, the exact noncentral-$t$ value is 2.72 points (6.5% above the normal approximation 2.55). We report the exact value throughout. All quantities are recomputed by `scripts/verify_noise_floor.py` and pinned by `tests/test_noise_floor.py`.

## 2. Related Work

Khojah et al. evaluated 7,072 prompts across five prompt-programming techniques [1]; Schäfer et al. developed TestPilot for unit-test generation [2]; Fakhoury et al. studied test-driven interactive generation [3]; and Hou et al. survey LLM use in software engineering [4]. These compare prompt content or generation strategy, not the delivery format of a persistent skill document.

Liu et al. established that models attend most reliably to the beginning and end of long contexts [5], which motivates compression but does not establish which components are recoverable. Zhang et al. show that contexts can be evolved rather than statically authored [6]. Neither isolates delivery format while holding task, model, and token budget fixed.

Agent skills are widespread enough to mine: Destefanis et al. released a GitHub dataset [7], and ACES addresses continuous evaluation [8]. Checklist scoring [9], [10] and verifier feedback [11] are established, and Kong et al. document LLM-as-a-judge at scale [12]. We quantify one systematic judge error rather than rediscovering unreliability.

Mann et al. [13], Bailey et al. [14], and Briand et al. [15] show that software results can fail to replicate or can reverse under a different design. We add the detection threshold as a reusable artefact alongside the raw runs.

Shashank et al. propose context-aware reinforcement learning for adaptive multimodal prompt optimization [16]. Sundaravadivel et al. use a lightweight multimodal model for one-shot industrial visual anomaly detection with prompt-conditioned inference [17]. Both adapt model input, but neither varies external skill-document delivery while holding model, task, token budget, and judge fixed.

## 3. Method

### 3.1 Architecture

The study has two linked pipelines (Fig. 1). A catalogue of 557 active skills and 2,228 cold-storage playbooks is de-duplicated at cosine similarity 0.95, reducing 531 candidates to 522 routable entries. A static compiler produces the delivery arms deterministically. The macro benchmark runs five arms on 18 tasks; the routing study runs five retrieval methods on 17 scorable queries. Both feed a blind judge that sees labels A--E permuted within each task window.

```tikz
%% architecture | Benchmark and study architecture. The catalogue is de-duplicated and indexed; every delivery arm is compiled deterministically before the blind judge scores all arms of a task in one permuted window.
\begin{tikzpicture}[
  font=\small,
  bx/.style={draw, rounded corners=1.5pt, align=center,
             inner sep=3pt, line width=0.4pt},
  dbox/.style={bx, fill=black!5},
  pbox/.style={bx, fill=black!13},
  rbox/.style={bx, fill=white},
  fbox/.style={bx, fill=black!24},
  ar/.style={-{Stealth[length=1.6mm]}, line width=0.4pt},
  lbl/.style={font=\tiny, inner sep=1pt, text=black!55}
]
\node[dbox] (cat) at (0,0mm)
  {\textbf{Source catalogue}\\[1pt]
   \texttt{skills/} 557 active \quad \texttt{collections/} 2{,}228 cold};
\node[dbox] (dedup) at (-33mm,-13mm)
  {\textbf{De-duplication}\\[1pt] cosine $\geq 0.95$\\[1pt] 531 $\rightarrow$ 522};
\node[dbox] (router) at (33mm,-13mm)
  {\textbf{Router index}\\[1pt] TF-IDF + dense\\[1pt] 522 routable};
\node[pbox] (comp) at (0,-28mm)
  {\textbf{Static compiler} (deterministic)\\[2pt]
   A0 raw \textbar{} A1 v2 \textbar{} A2 no-examples\\
   A3 no-tables \textbar{} A4 no-types \textbar{} A5 v1 bullets};
\node[rbox] (bench) at (-33mm,-43mm)
  {\textbf{Delivery benchmark}\\[1pt] 5 arms $\times$ 18 tasks\\[1pt] 396 judged runs};
\node[rbox] (routing) at (33mm,-43mm)
  {\textbf{Routing study}\\[1pt] 17 scorable queries\\[1pt] 5 methods};
\node[fbox] (judge) at (0,-58mm)
  {\textbf{Blind judge}\quad(labels A--E permuted)\\[1pt]
   35-point rubric, 7 dimensions $\times$ 5 points};
\draw[ar] (cat) -- (dedup);
\draw[ar] (cat) -- (router);
\draw[ar] (dedup) -- (bench);
\draw[ar] (router) -- (routing);
\draw[ar] (comp) -- (bench);
\draw[ar] (comp) -- (routing);
\draw[ar] (bench) -- (judge);
\draw[ar] (routing) -- (judge);
\node[lbl, anchor=south west] at ($(routing.east)+(1mm,-4mm)$) {14/17 vs 8/17};
\end{tikzpicture}
```

### 3.2 Delivery strategies

`control` injects no skill content. `full` injects the verbatim `SKILL.md`. `retrieved` selects a subset of `full` under a fixed retrieval budget; the selected text is verbatim, but the prompt is smaller because it contains fewer skills (430 vs 2,270 mean tokens). `checklist_v2` is structure-preserving compilation at 28.6% reduction. `checklist` is aggressive bulletization at 70.8% reduction. Mean prompt sizes are 144, 2,270, 430, 1,590, and 663 tokens.

### 3.3 Blind protocol and attrition

Arms are permuted across labels A--E, so the judge cannot infer treatment from position. The protocol schedules up to five runs per task--arm cell across 18 tasks and five arms: 450 planned instances. The archive holds 450 response files; 25 belong to `db-ratelimit-redis-ieee`, which was generated but never judged, leaving 425 scheduled attempts across 17 judged tasks. Of those, 396 produced a judged record and 29 did not.

Of the 54 lost attempts, **48 are executor failures**: retained 23-character records of the form `[exit=5 latency=1.67s]`, meaning termination with a non-zero status in under two seconds. All 25 dropped-task attempts are of this kind; the other 23 are scattered across the 17 judged tasks. **Six further attempts generated a full-length response** (19.7k to 36.0k characters) with no judged record, so the loss was downstream. Of 425 retained files, 348 exceed the judging cap and 77 do not; of 396 judgments, 342 come from truncated responses and 54 from responses under the cap.

### 3.4 Rubric and instrumentation

A 35-point rubric scores seven five-point dimensions: correctness, completeness, maintainability, architecture, security, reasoning quality, and instruction adherence. Generation uses `qwen/qwen3.7-flash`; one model, `deepseek/deepseek-v4-pro`, judges blind to condition. The Python compiler is cross-validated against a Rust version across all six modes: 120/120 byte-identical. Both compiled arms regenerate 18/18 artefacts against run-time manifests, and a recovered source must match its SHA-256 hash.

All token figures use `cl100k_base`. The same files give 28.56%, 28.47%, and 29.05% reduction with `cl100k_base`, `o200k_base`, and `p50k_base`. The old `len//4` heuristic gave 30.41%, overstating reduction by 1.85 pp. Across three tokenizers the figure varies by 0.58 pp, so compression is stable; the estimator was wrong. Per skill this is 2,071 to 1,479 tokens, saving 591 per skill per turn.

```figurewide
fig_v2_design.pdf | fig:design | Design and attrition. (a) Five delivery arms and their prompt-token reduction. (b) Compression under the character heuristic and three BPE tokenizers. (c) The reconciled 450-425-396 account, including 25 dropped-task attempts, 23 scattered executor stubs, and six full-length responses with no judged record.
```

### 3.5 Analytical Scaling Model

Let $K$ denote active skills loaded per turn, $T_{\text{manual}}$ average uncompressed skill length, and $T_{\text{v2}}$ compiled length. The per-turn saving is $\Delta_{\text{turn}} = K \cdot (T_{\text{manual}} - T_{\text{v2}}) = K \cdot 591$ tokens. For $S$ turns, $\Delta_{\text{session}} = S \cdot K \cdot 591$; at $K = 20$ and $S = 30$ this yields 354,600 tokens per session. This is arithmetic on measured lengths, not an inference from judge scores, so it does not inherit the detection limit. But the quality assumption that compressed delivery is acceptable rests on Section IV-B, which is detection-limited.

## 4. Results

### 4.1 The noise floor

Every run inside a task--arm cell used a byte-identical prompt. Pooling within-cell variation across all 396 runs isolates judge and generation stochasticity from any treatment effect: $\sigma = 5.37$ points, computed over 85 cells with 311 degrees of freedom; per-cell standard deviations range from 0.00 to 11.73. This is the instrument's resolution limit, recomputed by `scripts/verify_noise_floor.py` rather than asserted.

Against the task-blocked design ($\sigma_d = 3.76$ over 17 task pairs), the exact minimum detectable effect is 2.72 points (7.8% of the scale) at 80% power and $\alpha = 0.05$; the normal approximation gives 2.55. Every "no significant difference" below means *below the detection threshold*, not equivalence.

### 4.2 RQ1: Delivery format does not measurably change quality

The five arm means are `full` 25.17 ($n = 78$), `checklist_v2` 24.96 ($n = 80$), `retrieved` 24.73 ($n = 79$), `checklist` 24.54 ($n = 80$), and `control` 24.49 ($n = 79$). The full range is **0.68 points** (Fig. 3). Because the design blocks on task, the `full`--`checklist_v2` difference is paired: $+0.275$, with $t = 0.3011$, $p = 0.7672$ over 17 task pairs. The observed difference is 10.1% of the MDE. No arm significantly exceeds `control` (all Welch $p > 0.6$). This is a detection-limited null, not equivalence: the benchmark cannot distinguish the arms. Table I reports the per-arm prompt sizes and mean scores.

| Arm | Prompt tokens | Mean score (n) |
|---|---|---|
| `control` | 144 | 24.49 (79) |
| `full` | 2,270 | 25.17 (78) |
| `retrieved` | 430 | 24.73 (79) |
| `checklist_v2` | 1,590 | 24.96 (80) |
| `checklist` | 663 | 24.54 (80) |

Table: tab:arms | Per-arm prompt size and judge score. Prompt sizes are means under `cl100k_base`; n is the number of judged runs.

```figurewide
fig_v2_results.pdf | fig:results | Results against the floor. (a) Arm means with 95% confidence intervals; the shaded span is the minimum detectable difference. (b) Domain-level differences from the full manual, including the Testing & QA drop. (c) Component ablations. (d) The failed n = 15 replication.
```

### 4.3 The one component that clears the floor

Aggressive bulletization (the `checklist` arm, 70.8% compression) is the single intervention that clears the noise floor: on Testing & QA, `full` scores 23.50 and `checklist` 17.18, a difference of $-6.32$. It rests on $n = 11$ pairs, roughly one noise-floor unit. The milder `checklist_v2` arm does not show the drop, which constrains any mechanism claim: it is not compression per se that harms these tasks, but compression aggressive enough to remove syntactic anchors.

### 4.4 Component ablations

Mean scores are A1 v2 balanced 19.75 ($n = 4$), A2 no examples 18.58 ($n = 6$), A3 no tables 16.83 ($n = 6$), and A4 no types 21.50 ($n = 6$). Ten of twelve true interventions move scores by at most $\pm 6$ points, within the noise floor. A4 scores highest, inconsistent with a simple "syntax carries the signal" account. The cells are small ($n = 3$), so we report this without a mechanism.

### 4.5 A replication failure we report rather than bury

An earlier version reported a syntax-collapse effect: stripping TDD tracer-bullet code from a `tdd` skill reduced a payment-state-machine task by $\Delta = -8.50$ at $n = 6$, and we called it replicated. We re-ran that cell at $n = 15$ per arm with a matched control. The balanced arm scored 22.53 (SD 5.11); the no-examples arm scored 26.07 (SD 7.37). The effect **reverses**: $\Delta = -3.53$, Welch $t = -1.525$, $p = 0.14$. The pooled SD of 6.34 reproduces the noise floor closely, so the instrument behaved as documented; the effect did not. We withdraw the claim.

### 4.6 Position bias is 13 times the treatment effect

The blind protocol permutes arms across labels A--E, yet the judge has a strong slot preference. Mean deviations from the grand mean are A $+2.08$ ($n = 78$), B $+0.70$ ($n = 80$), C $-0.79$ ($n = 80$), D $-1.58$ ($n = 80$), and E $-0.37$ ($n = 78$). A pooled one-way ANOVA over 396 rows ignores that the five labels share a task, a judge call, and that window's idiosyncrasy. An earlier draft reported exactly that, $F = 4.5373$, $p = 0.00136$, and we withdraw it.

Treating the window as the block gives a stronger result. Removing each window's own mean and permuting position labels **within** each window -- the randomisation the protocol performed -- gives a spread of 3.63 with $p < 0.00005$. A descriptive ANOVA on window-centred scores gives $F = 7.1794$, $p = 0.000014$, but its within-window residuals sum to zero, so we do not treat that $p$ as valid. A sign test agrees: of the 78 windows that scored both A and D, five tied, leaving 73 informative windows, of which A wins 52. We report the one-sided binomial $p = 0.000186$; the two-sided value is $p = 0.000371$.

A Friedman test on within-window ranks gives $H = 4.843$, $p = 0.304$ -- not significant. The judge favours slots without systematically reordering arms inside a window; mean rank at A is 3.69 against a neutral 3.0. The bias inflates and deflates absolute scores but does not decide comparisons on its own. The A-to-D spread is 13 times the headline effect (3.63/0.275 = 13.2; pooled 3.66/0.275 = 13.3). Correcting for position leaves the nulls intact: `full`--`checklist_v2` narrows to $+0.120$ ($p = 0.8516$), no arm beats `control`, and excluding slot A widens the gap to $+0.407$.

```figurewide
fig_v2_position.pdf | fig:position | Judge position bias. (a) Mean score deviation by judging slot, with the A-to-D spread. (b) Analysis variants on a log $p$-value axis. The within-window permutation is the inferential test; the pooled ANOVA is withdrawn, and the rank test is not significant.
```

### 4.7 RQ3: Routing does not earn its cost

Seventeen scorable queries (one prompt-leak query excluded) used an identical catalogue. Keyword TF-IDF reaches 8/17 Top-1 and 11/17 Top-5 at 1.51 ms p50. Dense BGE-small reaches 7/17 and 11/17 at 47 ms. Dense plus a Julia-1 reranker reaches 5/17 and 11/17 at 391 ms. **Top-5 recall is identical across all three**: no reranker can recover a skill the shortlist never surfaced, so Stage 1 recall is binding.

Within one system class, the reranker is harmful: it drops Top-1 from 7/17 to 5/17 and, over a union shortlist with a 14/17 ceiling, realises only 5/17, discarding nine recoverable tasks. Direct in-context choice over all 522 routable skills solves 14/17, but that is not like-for-like: direct choice uses a remote frontier generator, while every retrieval arm uses local 33M/144M models, so the gap measures system class.

```figurewide
fig_v2_retrieval.pdf | fig:retrieval | Retrieval and the correction record. (a) Top-1 and Top-5 recall. (b) p50 retrieval latency on a log axis. (c) Withdrawn estimates beside their recomputed values; the paired design halves the threshold relative to the two-sample form.
```

## 5. Discussion

### 5.1 What We Could Not Reproduce

Our most important negative result concerns our own earlier draft; it is why we trust the remaining numbers.

#### 5.1.1 A headline statistic that no code could produce

An earlier version reported $\sigma = 6.09$, $\sigma_d = 7.87$ over 78 pairs, and MDE 2.53 from 42 runs on byte-identical prompts. None is reproducible: no 42-run grouping exists, the `full`--`checklist_v2` contrast has 17 pairs, and 6.09/7.87 appear only in prose and a docstring. The raw SD of all 396 scores (6.03) folds task difficulty into judge noise; conditioning on the task--arm cell (Fig. 5c) gives $\sigma = 5.37$, $\sigma_d = 3.76$, exact MDE 2.72, a 10.1% gap, and about 1,473 pairs for 80% power. Only $t = 0.3011$ and $p = 0.7672$ were correct before.

#### 5.1.2 A second error, in our own correction

Our first correction made the opposite error. It said the correction *strengthened* the null because MDE rose from 2.53 to 3.61, shrinking the gap. That 3.61 applied the two-sample form $\text{MDE} = (z_{1-\alpha/2} + z_{1-\beta}) \cdot \sigma_d \sqrt{2/n}$ to a paired design. The factor belongs to independent means; the paired standard error is $\sigma_d/\sqrt{n}$, so the two-sample form overstates the threshold by exactly $\sqrt{2}$. The correct paired normal value is 2.55 and the exact noncentral-$t$ value is 2.72; recomputing the old draft under the paired method gives 2.50, so the increase to 3.61 was an artefact. The gap is 10.1% of the exact threshold, not the 7.6% we claimed. The null is unchanged, but the correction did not strengthen it. `tests/test_noise_floor.py` now asserts that the MDE at the required sample size reproduces the observed gap.

#### 5.1.3 Other claims we cannot fully reproduce

Subgroup correlations (for example $r = +0.616$, $p = 0.001$) depended on `syntax_rate` records never persisted; the two largest values were literal script text. A subgroup $r = +0.207$ on 44 runs has the same provenance and is unreplicated. Character-heuristic token figures are superseded by Section III-D.

#### 5.1.4 What is reproducible

The remainder is recomputable and enforced: CI re-derives the floor, $\sigma_d$, and MDE from `delivery_results_ieee.json`; both compiled arms regenerate 18/18 artefacts against SHA-256; compression fails CI on source drift or a reduction move above 0.5 pp.

### 5.2 Threats to Validity

#### 5.2.1 Statistical conclusion validity

The MDE is 2.72 points, the observed 0.27-point gap is 10.1% of it, and resolving it needs about 1,500 task pairs; every null in Section IV is below threshold. Multiple comparisons are uncorrected, and a single judge precludes inter-rater agreement. Between-run SDs (5.56--6.94) mix task difficulty; the within-cell $\sigma = 5.37$ is cleaner. Position bias is 13 times the task-paired effect; correcting leaves conclusions intact, but the floor belongs to this judge and protocol. Attrition is not random by arm, though the 5--7 run spread cannot plausibly produce the result.

#### 5.2.2 Construct validity

A post-hoc calibration across 238 executable runs found a weak correlation between execution pass rate and judge score ($r = +0.047$, $p = 0.473$), dominated by 194 environmental failures (missing browser drivers, Redis daemons, TypeScript resolution), not code quality. We do not claim the rubric is invalid, but its link to executable correctness is unestablished at this scale. The $r = +0.207$ subgroup is unreplicated. The benchmark asks for prose, not a testable repository state, the deepest limit on a judge score.

#### 5.2.3 Internal validity

The executor runs with repository filesystem context, and traces show repo exploration rather than closed-book synthesis. If it can read skill content from the working tree, `control` is not skill-free, biasing toward the null and plausibly contributing to the failed replication in Section IV-E. We did not isolate the executor and cannot bound the effect. The `checklist_v2` arm also carried an extra `[INSTRUCTION]` directive, explaining its higher output-token volume; we withdrew the volume claim, and `tests/test_paper_claims.py` asserts the matched-control result.

#### 5.2.4 External validity

Eighteen tasks across six domains is a small base. The one domain-level effect rests on $n = 11$ pairs and is a hypothesis. Nothing generalises to non-English skills or repository-modification tasks.

The judge saw each response truncated at 10,000 characters. Of the 425 retained response files for the 17 tasks that ran, **348 (81.9%) exceeded the cap**. Of the **396 recorded judgments**, **342 (86.4%) were produced from a truncated response**, since 54 come from responses under the limit. The median response was 18.6k characters, and similar rates across arms show truncation was not label-specific. Truncation ceilings discrimination, so the null is conservative; the reported $\sigma$ is also measured under truncation, so an untruncated instrument would plausibly show a wider floor and larger MDE. We cannot size that conservatism.

The direct-choice comparison spans system classes, and the routing study is in-domain: 18 engineering queries with overlapping terminology, Top-5 recall of 64.7% across 522 skills, and two catalogue entries with byte-identical descriptions that no retriever can resolve.

#### 5.2.5 Reproducibility of the statistics in this paper

Until Section V-A, three statistics supporting Section IV-A existed only as prose; they are now CI-gated and pinned. We did not run a fresh-generation replication of the floor: a test--retest floor is interpretable only against the process producing the scores, so a fresh measurement would characterise a different executor, possibly judge, and differ for reasons unrelated to the archived results. Whether the floor generalises remains open.

### 5.3 Implications for Practice and Research

The reusable result is the floor: estimate within-cell variation, pair on the blocked unit, and state effects against detection. The observed 0.27-point gap is an order of magnitude below resolution, and resolving it requires roughly 1,500 task pairs rather than 17. The position result changes study design: because slot identity is confounded with treatment, permuting labels and analysing within windows is not optional.

Adaptive prompt optimization and lightweight multimodal inference point toward cheaper model inputs [16], [17]. Our result does not contradict that direction: external skill-document delivery differences must be resolved before a format is declared safe. Making a statistic executable is necessary but not sufficient: scripts can repeat conceptual errors, so tests must pin the exact design invariants.

## 6. Conclusion and Future Work

Across 396 blind judged runs and 87 ablations, no delivery strategy we tested measurably changed output quality, and the benchmark could not have resolved a difference of the size observed. The primary contribution is the floor: $\sigma = 5.37$, $\sigma_d = 3.76$ over 17 task pairs, exact MDE 2.72, and a judge position bias 13 times the task-paired effect, all recomputed by a CI-gated script. "No significant difference" here means "underpowered," not "equivalent."

Three practical conclusions survive. Moderate compression showed no measurable decline, but the result rests on 17 tasks in one corpus. Aggressive extraction produced a preliminary warning in Testing & QA ($-6.32$, $n = 11$) requiring replication. A reranking layer made retrieval worse, and direct catalogue choice beat all retrievers, though that comparison spans system classes. We also withdraw three earlier claims -- an output-volume advantage explained by a confound, a router accuracy figure with a mis-specified baseline, and a syntax-collapse effect that failed to replicate at $n = 15$ -- and three irreproducible statistics in Section V-A.

### 6.1 Future Work

An adequately powered replication is the first requirement: roughly 1,500 task pairs would resolve the observed 0.27-point gap at 80% power. That replication should isolate the executor, add a second judge, re-score without the 10,000-character truncation, and test whether Stage 1 retrieval improvements close the 14/17 ceiling. Extending the corpus beyond English prose and a single catalogue would test external validity.

## Acknowledgment

The authors thank the institution for providing facilities and the maintainers of the open-source tools used in this study.

## References

1. R. Khojah, F. G. de Oliveira Neto, M. Mohamad, and P. Leitner, "The Impact of Prompt Programming on Function-Level Code Generation," *IEEE Transactions on Software Engineering*, vol. 51, no. 8, pp. 2381--2395, 2025. DOI: 10.1109/TSE.2025.3587794.
2. M. Schäfer, S. Nadi, A. Eghbali, and F. Tip, "An Empirical Evaluation of Using Large Language Models for Automated Unit Test Generation," *IEEE Transactions on Software Engineering*, vol. 50, no. 1, pp. 85--105, 2024. DOI: 10.1109/TSE.2023.3334955.
3. S. Fakhoury, A. Naik, G. Sakkas, C. Chakraborty, and S. Lahiri, "LLM-Based Test-Driven Interactive Code Generation: User Study and Empirical Evaluation," *IEEE Transactions on Software Engineering*, vol. 50, no. 8, pp. 2254--2268, 2024. DOI: 10.1109/TSE.2024.3411200.
4. X. Hou et al., "Large Language Models for Software Engineering: A Systematic Literature Review," *ACM Transactions on Software Engineering and Methodology (TOSEM)*, vol. 33, no. 8, 2024. DOI: 10.1145/3695988.
5. N. F. Liu et al., "Lost in the Middle: How Language Models Use Long Contexts," *Transactions of the Association for Computational Linguistics (TACL)*, vol. 12, pp. 157--173, 2023.
6. Q. Zhang et al., "Agentic Context Engineering: Evolving Contexts for Self-Improving Language Models," *arXiv preprint arXiv:2510.04618*, 2025.
7. G. Destefanis, D. Graziotin, M. Vaccargiu, and M. Ortu, "GitSkills: A Dataset of Agent Skills on GitHub," *arXiv preprint arXiv:2608.10906*, 2026.
8. NVIDIA Research and SkillEvaluator Team, "Evaluating Skills, Not Just Agents: Agentic Continuous Evaluation of Skills (ACES)," *arXiv preprint arXiv:2608.20614*, 2026.
9. D. Cook et al., "TICKing All the Boxes: Generated Checklists Improve LLM Evaluation and Generation," *arXiv preprint arXiv:2410.03608*, 2024.
10. Y. Zhou and X. Tan, "AutoChecklist: Composable Pipelines for Checklist Generation and Scoring with LLM-as-a-Judge," in *Proceedings of ACL*, 2026.
11. J. Kwok et al., "LLM-as-a-Verifier: Fine-Grained Feedback for Agents," *arXiv preprint arXiv:2607.05391*, 2026.
12. E. Y. Kong et al., "The Lifecycle of LLM-as-a-Judge for Large-Scale Recommendation Explanations," *arXiv preprint arXiv:2608.18300*, 2026.
13. M. Mann, E. Keeling, and V. Ioannidis, "On the Reproducibility Crisis in Computer Science," *Communications of the ACM*, vol. 62, no. 12, pp. 65--70, 2019. DOI: 10.1145/3148149.
14. J. J. Bailey, M. D. Meschniak, J. C. Sutton, and R. E. Taylor, "The Replication Crisis for Empirical Software Engineering Research," in *Proc. ESEC/FSE*, 2019, pp. 1--4. DOI: 10.1145/3331595.3331596.
15. L. C. Briand, J. L. Elbaz, F. Khendek, and E. Ammann, "Differential and Case-Based Evaluation of Software Design Quality Measures," in *Proc. Int. Workshop on Empirical Assessment of Software Engineering Methods and Tools (ESEM)*, 1999, pp. 30--37. DOI: 10.1145/302405.302629.
16. R. Shashank, R. Shreeshanth, M. Rajagopal, G. Karthi, and A. Rajakrishnammal, "A Context-Aware Reinforcement Learning Framework for Adaptive Multimodal Prompt Optimization," *Research Square preprint*, 2026. DOI: 10.21203/rs.3.rs-9637361/v1.
17. P. Sundaravadivel, R. Augustian Isaac, U. Kumaran, and G. Priyanga, "Lightweight multimodal large language model enabling efficient one shot industrial visual anomaly detection," *Discover Artificial Intelligence*, vol. 6, no. 1, Art. no. 483, 2026. DOI: 10.1007/s44163-026-01252-w.
