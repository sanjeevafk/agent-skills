# Skill Delivery Experiment — IEEE Run

> **Generated**: `2026-08-26T14:18:02.017208+00:00`  
> **Tasks**: 18 | **Runs per strategy**: 5 | **Strategies**: 5  
> **Executor**: `agy-default` | **Judge**: `cmd:deepseek/deepseek-v4-pro` | **Seed**: 20260824

---

## 📊 Executive Dashboard

| Strategy | Avg Score /35 | 95% CI | Median | Std | Wins | Avg Latency | Avg In Tok | Avg Out Tok |
|---|---|---|---|---|---|---|---|---|
| `control` | **24.49** | `[23.19, 25.8]` | 25.0 | 5.82 | 16 | 46.41s | 143.77 | 5078.22 |
| `full` | **25.17** | `[23.86, 26.47]` | 26.0 | 5.8 | 21 🏆 | 51.55s | 2269.79 | 4588.35 |
| `retrieved` | **24.73** | `[23.49, 25.98]` | 25.0 | 5.56 | 15 | 44.44s | 429.68 | 4548.23 |
| `checklist` | **24.54** | `[22.99, 26.08]` | 26.0 | 6.94 | 18 | 52.25s | 663.46 | 4554.54 |
| `checklist_v2` | **24.96** | `[23.62, 26.3]` | 26.0 | 6.03 | 10 | 52.27s | 1590.09 | 5431.07 |

---

## 🔬 Normality Diagnostics (Shapiro–Wilk on judge scores)

| Strategy | W | p | n | Verdict |
|---|---|---|---|---|
| `control` | 0.97631 | 0.14868 | 79 | normal (p>0.05) |
| `full` | 0.9547 | 0.00741 | 78 | **non-normal** (parametric tests cautious) |
| `retrieved` | 0.97163 | 0.07538 | 79 | normal (p>0.05) |
| `checklist` | 0.93687 | 0.00066 | 80 | **non-normal** (parametric tests cautious) |
| `checklist_v2` | 0.96921 | 0.05053 | 80 | normal (p>0.05) |

---

## 📐 Pairwise Comparisons (Welch t + Mann–Whitney U + Cohen's d, Holm-corrected)

| Pair | t | p (Welch) | U | p (MW) | Cohen's d | Holm p | Significant? |
|---|---|---|---|---|---|---|---|
| `checklist_vs_checklist_v2` | -0.41361 | 0.67973 | 3156.5 | 0.88314 | -0.065 | 1.0 | No |
| `control_vs_checklist` | -0.04317 | 0.96562 | 3019.0 | 0.6278 | -0.007 | 1.0 | No |
| `control_vs_checklist_v2` | -0.49866 | 0.61872 | 2951.0 | 0.47184 | -0.079 | 1.0 | No |
| `control_vs_full` | -0.7254 | 0.4693 | 2816.0 | 0.35208 | -0.116 | 1.0 | No |
| `control_vs_retrieved` | -0.26548 | 0.79099 | 3023.5 | 0.73676 | -0.042 | 1.0 | No |
| `full_vs_checklist` | 0.61915 | 0.53674 | 3193.5 | 0.79923 | 0.098 | 1.0 | No |
| `full_vs_checklist_v2` | 0.21691 | 0.82856 | 3163.0 | 0.8823 | 0.034 | 1.0 | No |
| `full_vs_retrieved` | 0.47682 | 0.63417 | 3227.0 | 0.60885 | 0.076 | 1.0 | No |
| `retrieved_vs_checklist` | 0.19741 | 0.84377 | 3088.5 | 0.80643 | 0.031 | 1.0 | No |
| `retrieved_vs_checklist_v2` | -0.24825 | 0.80427 | 3069.0 | 0.7548 | -0.039 | 1.0 | No |

---

## 🌍 Per-Domain Analysis (RQ4)

| Domain | control | full | retrieved | checklist | checklist_v2 | Δ (chk−full) | Kruskal–Wallis p |
|---|---|---|---|---|---|---|---|
| Architecture & Refactoring | 27.8 | 27.86 | 25.57 | 26.33 | 25.27 | -1.53 | 0.4247 |
| Databases & Persistence | 21.89 | 22.56 | 26.22 | 24.67 | 24.22 | 2.11 | 0.43412 |
| DevOps & Cloud | 21.4 | 25.4 | 21.4 | 24.13 | 23.47 | -1.27 | 0.22143 |
| SRE & Debugging | 24.67 | 26.6 | 25.6 | 25.67 | 25.27 | -0.93 | 0.95395 |
| Security & Auditing | 27.27 | 23.67 | 26.53 | 27.33 | 27.67 | 3.66 | 0.13206 |
| Testing & QA | 22.1 | 23.5 | 23.36 | 17.18 | 23.09 | -6.32 | 0.09763 |

---

## 📈 RQ3: Skill Size vs Quality Delta (checklist − full)

- Pearson r: `0.4634` (p=0.06101)
- Spearman ρ: `0.6058` (p=0.00996)
- n tasks: 17

| Task | Skill | Bytes | Δ (chk−full) |
|---|---|---|---|
| `sec-webhook-audit-ieee` | `security-review` | 12493 | 2.8 |
| `sec-amm-pool-ieee` | `defi-amm-security` | 5315 | 6.2 |
| `sec-django-hardening-ieee` | `django-security` | 17172 | 2.0 |
| `sre-node-leak-ieee` | `debugging-code` | 11613 | -1.6 |
| `sre-flaky-ci-ieee` | `systematic-debugging` | 9884 | -0.4 |
| `sre-p99-regression-ieee` | `performance-profiler` | 5078 | -0.8 |
| `qa-ratelimiter-tdd-ieee` | `tdd` | 4211 | -5.6 |
| `qa-checkout-e2e-ieee` | `e2e-testing` | 8077 | 1.0 |
| `qa-dashboard-browserqa-ieee` | `browser-qa` | 3727 | -12.17 |
| `arch-godclass-refactor-ieee` | `code-refactor` | 3358 | -2.4 |
| `arch-adr-scaling-ieee` | `architecture-decision-records` | 7131 | 0.65 |
| `arch-form-statemachine-types-ieee` | `type-architecture-analyzer` | 6172 | -3.6 |
| `devops-ml-docker-ieee` | `docker-patterns` | 8263 | -4.0 |
| `devops-api-k8s-ieee` | `kubernetes-patterns` | 19987 | 1.8 |
| `devops-gha-pipeline-ieee` | `ci-cd-pipeline-builder` | 4756 | -1.6 |
| `db-analytics-query-ieee` | `postgres-patterns` | 3820 | -0.6 |
| `db-zerodowntime-rename-ieee` | `database-migrations` | 11851 | 5.5 |

---

## ⚖️ Judge Usage & Cost Accounting

- Judge calls: 82 | prompt tokens: 0 | completion tokens: 0
- Model: `deepseek/deepseek-v4-pro` via `cmd`

---

## 💡 Final Recommendation

- **Highest average judge score**: `full`
- **Most first-place wins**: `full`
- **Lowest latency**: `retrieved`
- **Lowest prompt bloat**: `control`

> [!WARNING]
> 2 judge evaluations failed and are queued in `pending_judges`. Run `python3 scripts/skill_delivery_experiment.py --judge-only` (after limits reset) to score them without re-executing. Stats above EXCLUDE queued runs until recovered.

---

## 🧬 Per-Task Judge Explanations

### Task `sec-webhook-audit-ieee` (domain: Security & Auditing)

**Run 1:**
- Ranking: `checklist > checklist_v2 > retrieved > control > full`
- Analysis: E and C are the strongest because they both correctly order the vulnerabilities, produce concrete, working HMAC/ledger implementations, and never leak errors; E separates itself from C by depth (11 findings with CWE mappings) and broader hardening, while C is cleaner and more focused. D is a close third with a real asyncpg solution but loses to C/E because of a hex-vs-bytes signature comparison bug and a success-on-failure response that undermines reliability. B and A fall behind on executability: B leaves the ledger as NotImplementedError pseudocode, and A's core HMAC logic never actually uses the secret, making it cryptographically broken despite otherwise sound prose.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `full` | 22 | Solid vulnerability ordering and good prose, but the core HMAC code is wrong: compute_signature hashes the raw body WITHOUT using the secret (h.update(raw_body) only), so it is not HMAC at all and is  |
  | `control` | 26 | Correctly identifies the key issues with accurate HMAC usage and a sensible processing order (content-type, raw body, HMAC, atomic ledger, parse). However, the implementation is largely pseudocode: Ev |
  | `checklist_v2` | 32 | Best prioritization (correctly flags the in-memory dict as the top-severity financial-loss issue, then signature-after-parse, then rotation). Implementation is concrete and correct: real HMAC, persist |
  | `retrieved` | 27 | Strong, runnable PostgreSQL/asyncpg implementation with correct atomic UPSERT and good error handling, but it contains a real signature-verification bug: SecretRing.verify compares hmac.compare_digest |
  | `checklist` | 33 | Most thorough and technically sophisticated response: 11 clearly ranked vulnerabilities with CWE references and a summary table, plus a comprehensive hardened implementation. Strong on correctness (ra |

**Run 2:**
- Ranking: `control > checklist_v2 > full > retrieved > checklist`
- Analysis: D and A both demonstrate expert-level command of the domain, but D is more concrete and catches subtle correctness/security issues (timing side-channels, key-ring races, deprecated APIs) with fully working code, whereas A leans on production-grade Postgres/Redis architecture but leaves its idempotency layer as pseudocode and has a minor severity-ordering slip. C and B are comparable mid-tier responses that each carry one central bug — C breaks replay dedup (missing IntegrityError handling) while B breaks the primary HMAC function (missing key argument), with C edging out B because it gets the fundamental signature check right and calibrates severity better. E trails significantly because it reintroduces the in-memory ledger, orders dedup before authentication, and mishandles a missing key, effectively failing several of the task's explicit security requirements.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `checklist_v2` | 31 | Thorough (8 vulns) with production-grade architecture (PostgreSQL, advisory locks, multi-secret, Redis rate limiting, timestamp skew, PII redaction). Slight severity-ordering inconsistency (a 'High' i |
  | `retrieved` | 21 | Covers 6 core vulnerabilities and uses the correct ON CONFLICT DO NOTHING idiom for idempotency, but the central verify_hmac function is broken (hmac.new called without a key, plus dead 'provided_byte |
  | `full` | 22 | Good severity ordering and a correct HMAC-on-raw-bytes implementation, but the replay dedup is broken: record_event_id uses a bare INSERT plus rowcount instead of catching sqlite3.IntegrityError, so d |
  | `control` | 34 | Most thorough (10 vulns) and technically sharp, catching subtle issues (timing side-channel, key-ring concurrency, deprecated asyncio.get_event_loop, sensitive logging). Code is correct and concrete w |
  | `checklist` | 14 | Under-weights the race condition (MEDIUM) and error leakage (LOW) despite both being core requirements. Multiple serious flaws: the ReplayLedger falls back to the exact in-memory dict being fixed (and |

**Run 3:**
- Ranking: `checklist_v2 > control > retrieved > full > checklist`
- Analysis: A and E are clearly the strongest: both identify the full vulnerability set (including concurrency-safe idempotency and constant-time secret iteration) and back it with correct, complete code. They separate only on polish — A is slightly more systematic in mapping each fix to its vulnerability and demonstrates expiry in the ring, while E adds rate-limiting/dependency-wiring scope. B and D are mid-tier: both write plausible code but each leaves a real defect (B's check-then-insert race, D's unfixed timing side-channel and connection leak). C ranks last because its replay ledger is stubbed out, its HMAC helper is malformed, and it performs replay checks before authentication.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `checklist_v2` | 35 | Identifies 10 vulnerabilities in clean severity order with 'attack surface' and 'fix' for each, and the corrected implementation correctly remediates all of them (raw-bytes-first HMAC, persistent SQLi |
  | `retrieved` | 26 | Solid 7-vulnerability analysis and reasonably structured SQLAlchemy/PostgreSQL implementation with compare_digest and rotation fallback. However, the idempotency fix is flawed: check_idempotency (SELE |
  | `checklist` | 16 | Analysis is reasonable and correctly flags constant-time comparison, but the implementation is not production-grade: the replay ledger is entirely NotImplementedError stubs (so requirements 2 and 3 ar |
  | `full` | 24 | Good 7-vulnerability analysis and its replay mechanism is actually correct (atomic INSERT + IntegrityError detection). But it contradicts its own findings: verify_hmac breaks early on a matching secre |
  | `control` | 35 | Also enumerates 10 vulnerabilities with a table for the top issue and adds rate limiting and dependency-wiring concerns. Implementation is correct: atomic SQLite INSERT via PRIMARY KEY, locked SecretR |

**Run 4:**
- Ranking: `checklist > full > checklist_v2 > control > retrieved`
- Analysis: A is the clear leader: it covers every required property and adds genuinely relevant hardening (key expiry, constant-time iteration, masking, locking) with correct atomic dedup. E is solid but narrower and has subtle idempotency-state and rotation gaps. B and D are close, but B edges ahead because it correctly enforces atomic idempotency (the explicit core requirement) even though it has a runtime NameError and a timing leak, while D's otherwise-strong reasoning is undermined by an INSERT that never actually deduplicates; C ranks last because both its atomicity and its event-claiming logic are broken despite enumerating many issues.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `checklist` | 34 | Most thorough and technically sound. Correctly verifies HMAC before parsing, uses SQLite INSERT OR IGNORE for atomic dedup, adds key versioning with expiry, and catches subtle issues (timing side-chan |
  | `checklist_v2` | 24 | Correctly implements atomic idempotency via UniqueViolation catch and a persistent ledger, which is the single most important requirement. But the module has a NameError (config variables call _env_or |
  | `retrieved` | 19 | Enumerates several relevant vulnerabilities but the idempotency is broken: the SQL has no ON CONFLICT despite the comment claiming it does, record_event returns rowcount==1 unconditionally, and the ha |
  | `control` | 23 | Strong, systematic reasoning and good coverage (key-id rotation, clock skew, content-type, TOCTOU). However, the core idempotency is defective: the INSERT lacks ON CONFLICT despite the docstring, so d |
  | `full` | 28 | Clean and correctly ordered. Uses streaming body read with a size cap, verifies HMAC on raw bytes, and achieves atomic idempotency by catching IntegrityError on a UNIQUE-constrained insert. Minor gaps |

**Run 5:**
- Ranking: `retrieved > checklist_v2 > checklist > control > full`
- Analysis: A and D are the strongest, with A winning on production architecture (Postgres vs D's SQLite) and a cleaner, directly-on-task response, while D wins on analytical exhaustiveness. E is architecturally strong (Postgres+Redis) but has a subtle idempotency-signal gap and less rigorous reasoning than D. B is solid but undercuts the core concurrency requirement with a knowingly non-atomic fallback, and C ranks last because its 'corrected' HMAC verification is functionally broken and never actually compares the supplied signature.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `retrieved` | 34 | Technically sound, correctly ordered vuln list with a production-grade Postgres/async SQLAlchemy solution, key-ring rotation, constant-time compare, and advisory-lock awareness. Minor gaps: mislabels  |
  | `control` | 29 | Strong 8-item analysis and clean Redis SET NX idempotency. However, the dev in-memory fallback is explicitly non-atomic, and the claim-before-process design can permanently drop events whose processin |
  | `full` | 18 | Vulnerability list is mostly reasonable, but the corrected code's HMAC verification is fundamentally broken: the incoming signature is never compared, and computed_base is built with the raw body as k |
  | `checklist_v2` | 32 | Most exhaustive and technically precise analysis (13+ items, referencing actual repo files), with lock-guarded SecretRing and a persistent ledger. Slightly sprawling and uses SQLite (even WAL/singleto |
  | `checklist` | 31 | Comprehensive 9-item review (including rate limiting and timestamp windowing) with production-grade Postgres+Redis. Idempotency uses ON CONFLICT upsert without clearly returning a first-vs-duplicate s |

### Task `sec-amm-pool-ieee` (domain: Security & Auditing)

**Run 1:**
- Ranking: `checklist_v2 > retrieved > checklist > control > full`
- Analysis: E and D are the strongest because both correctly separate the manipulation vectors and implement internal-reserve accounting with slippage bounds; E edges out D on precision by cleanly distinguishing donation inflation from first-depositor inflation and explicitly tracking _totalAssets. A and B are comprehensive but marred by imprecise attack mechanics (A's incorrect reentrancy loop, B's impossible mid-transaction MEV observation) and weaker architectural clarity. C ranks last because its 'hardened' swap reintroduces the CEI violation (sends output before receiving input) and omits output-reserve settlement, so the proposed fix is itself broken.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `checklist` | 26 | Most complete enumeration (11 paths + full risk table + implementation), but several attack mechanics are imprecise or wrong — the reentrancy 'each recursion credits more B against unchanged reserves' |
  | `control` | 23 | Good concrete math for donation-driven price manipulation, and it names the five interlocking flaws cleanly. But Rank 3 is conceptually muddled (MEV bots cannot observe mid-transaction state between t |
  | `full` | 18 | Analysis is concise and correctly names the vectors, but the 'hardened' swap is fundamentally broken: it transfers tokenOut to the user before pulling tokenIn (reintroducing the reentrancy/ordering fl |
  | `retrieved` | 28 | Clean, mostly correct attack paths with a sound hardened approach (internal reserves, TWAP reference, slippage, deposit-single-asset with actual-tokens-received). Minor deductions for the unverifiable |
  | `checklist_v2` | 30 | Best precision and adherence: clearly distinguishes donation-inflation from first-depositor inflation, correctly tracks `_totalAssets` separately from balanceOf, enforces CEI plus nonReentrant/Pausabl |

**Run 2:**
- Ranking: `retrieved > control > checklist > full > checklist_v2`
- Analysis: A ranks first because it is the only response that both accurately enumerates/ranks the attacks and fully demonstrates a correctly ordered, slippage-bound swap with consistent imports, though its fee/reserve accounting has a subtle mismatch. D is second for the strongest conceptual rigor and the correct MIN_LIQUIDITY fix, but loses ground to A on numeric example accuracy and truncating before the swap. B, C, and E follow: B is broad but misstates the oracle swap mechanics and has a constructor error; C shows the swap correctly yet bungles its central worked example and imports; E has scattered correct math but is riddled with compile errors and never reaches the swap function.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `retrieved` | 29 | Covers all required attacks, ranks them clearly, and demonstrably provides a full hardened swap with correct CEI ordering, on-chain slippage bound, deadline, reentrancy guard, and internal reserve acc |
  | `checklist` | 24 | Broad enumeration (7 attack paths) with a clear ranking table and good intent (recoverTokens, collectFees, TWAP helper). However, the core oracle spot-price manipulation walkthrough has the swap direc |
  | `full` | 20 | Does show a hardened swap with the right ordering (compute -> check slippage -> transfer in -> update reserves -> transfer out). But the primary donation-inflation scenario has numerically incorrect/s |
  | `control` | 26 | Most thorough conceptual analysis, clearly identifies balance-based pricing as the root cause, correctly uses the canonical MIN_LIQUIDITY lock, and covers first-depositor inflation, reentrancy, sandwi |
  | `checklist_v2` | 19 | Some math is right (oracle-manipulation example and the swap-output helper are correct), but the first-depositor inflation example is muddled, and the code contains multiple compile-breaking issues: u |

**Run 3:**
- Ranking: `checklist > retrieved > control > checklist_v2 > full`
- Analysis: E is best because it is the only response whose hardened code keeps reserve accounting exactly consistent with actual received tokens and fees, while still delivering precise vulnerability reasoning and full instruction adherence; A ranks just behind on the strength of its exhaustive attack taxonomy but its implementation is less rigorous on reserve accounting and TWAP. The lower-ranked responses differ mainly in code quality rather than vulnerability identification: C has a defensible design but a token-routing/ordering inconsistency, B is architecturally muddled with undefined state and contradictory reserve logic, and D is last because its fee accounting corrupts the constant-product invariant despite otherwise correct ordering.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `retrieved` | 29 | Best enumeration and clear ranking; hardened code uses internal reserves and CEI but reserves lack a precise delta-based accounting path and the TWAP implementation is nominal, so architecture/securit |
  | `checklist_v2` | 22 | Correctly names the core vulns but the code is inconsistent (undefined _reserve map, confusing tokenA/tokenB vs quoteToken/outputToken, contradictory reserve mutations), hurting correctness, maintaina |
  | `control` | 26 | Solid structured analysis and a defensible implementation, but tokenIn as an arbitrary address contradicts the two-token design, and updating reserves before pulling input tokens is a partial CEI/orde |
  | `full` | 23 | Covers the required paths but has a critical fee-accounting bug (reserveIn += amountIn while only amountInAfterFee enters the invariant) and a muddled price-impact guard, undermining correctness and s |
  | `checklist` | 33 | Strongest technical execution: precise delta-based reserve accounting, correct fee deduction via mulDown, explicit anti-donation sweeps, and clear CEI/security rationale; slightly less complete only b |

**Run 4:**
- Ranking: `checklist > control > retrieved > full > checklist_v2`
- Analysis: B edges out A primarily because B uses the exact constant-product formula with deadline/TWAP support and a cleaner severity ranking, while A relies on a linearized approximation and lacks a deadline. D is a solid audit but its implementation is undermined by a nonsensical slippage require and arithmetic errors in its worked example, placing it below A and B. C and E both enumerate the paths correctly but ship broken code: C's nonReentrantLP modifier and deposit math are non-functional, while E's computeAmountOut and helper libraries fail to compile and misprice swaps, making E the weakest deliverable despite its strong attack enumeration.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `control` | 30 | Covers all required attack paths with a clean ranking and a usable swap. Internal reserves, CEI ordering, MIN_LIQUIDITY, and slippage check are all correct. Minor deductions: the swap uses a linearize |
  | `checklist` | 34 | Strongest technical submission. Uses the exact constant-product formula (reserveOut - mulDiv(reserveOut, amountInAfterFee, reserveIn + amountInAfterFee)), has deadline, recipient, internal reserves, a |
  | `full` | 21 | Enumerates all paths and the core swap has reasonable CEI/slippage/internal-reserve structure, but the code is broken: the custom nonReentrantLP modifier calls an undefined reentered() function, and t |
  | `retrieved` | 25 | Good narrative coverage and ranking, adding an overflow concern. Swap architecture (CEI, deadline, internal reserves, nonReentrant) is sound. However, the swap contains a copy-paste require that compa |
  | `checklist_v2` | 21 | Best enumeration (adds missing emergency pause) and solid reasoning structure, but the implementation is non-compiling and mathematically wrong: .sqrt() is not a native uint256 method, IERC20 has no . |

**Run 5:**
- Ranking: `full > checklist_v2 > control > retrieved > checklist`
- Analysis: B edges out D on slightly more accurate first-depositor framing and a cleaner deposit-delta measurement, though both are strong, correct, and complete implementations. A is close but its analysis conflates donation and oracle manipulation and mischaracterizes first-depositor inflation; C has the best reasoning yet fails the implementation deliverable, while E provides code but weakens security with a non-protective placeholder TWAP and redundant reserve state.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `control` | 26 | Covers all requested attack paths and delivers a clean, well-structured hardened contract (internal reserves, MINIMUM_LIQUIDITY, amountOutMin, fee-before-calc, ReentrancyGuard). But reasoning is muddl |
  | `full` | 28 | Strong, balanced answer. Attack enumeration and ranking are mostly accurate (donation inflation, CEI/reentrancy, flash-loan spot manipulation, slippage, first-depositor), and the implementation is sol |
  | `retrieved` | 23 | By far the best threat analysis: seven distinct paths, CVSS scores, concrete scenarios, and a clear threat-model table. The problem is that the hardened implementation is truncated almost immediately  |
  | `checklist_v2` | 28 | Systematic and correct: enumerates five vulnerabilities with clear exploit mechanics, ranks them, and provides a substantial hardened contract (internal reserves, TWAP + sqrtPriceLimitX96, CEI orderin |
  | `checklist` | 24 | Detailed exploit sequences and a complete implementation, but undermined by a fake oracle: _getTwapPrice() just computes a ratio from the internal reserves rather than reading an actual external TWAP, |

### Task `sec-django-hardening-ieee` (domain: Security & Auditing)

**Run 1:**
- Ranking: `checklist > full > retrieved > checklist_v2 > control`
- Analysis: E ranks first because it is the only response that verifiably addresses all four required issues with correct CWE mappings and complete, runnable fixes, especially the serializer allowlisting requirement. D is second for the deepest and most correct SQL-injection analysis (allowlisting structural elements), but it is truncated before the serializer issue and contains a demonstration typo. A is solid on Issues 1-2 but mislabels a CWE, while C and B trail on completeness and maintainability (B's dynamic import and dict-key hacks, C's redundant raw-query fallback).

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `retrieved` | 28 | Issues 1 and 2 are fully and correctly demonstrated with solid fixes (parameterization + validation + ORM alternative; object-level permission classes + queryset scoping). However, Issue 2 mislabels C |
  | `control` | 25 | Issue 1 is the most thorough of the set (parameterized params dict, sort/order allowlist, date/status/number validation, comparison table). But the Issue 2 fix is cut off mid-solution and Issues 3-4 a |
  | `checklist_v2` | 26 | CWEs (89, 284/639, 798) are defensible, and Issues 1-2 have complete, ORM-first fixes with permission classes and queryset scoping. But it introduces redundancy (raw fallback + ORM) and a fragile `use |
  | `full` | 28 | Technically the strongest SQL-injection treatment: it correctly distinguishes structural elements (table/column/operator) that cannot be parameterized and protects them with allowlists, adds a query-l |
  | `checklist` | 30 | The only response that fully and correctly covers all four issues with the right CWEs (89, 284/862, 798, 915) and complete fixes, including `.gitignore`, `.env.example`, serializer field allowlisting, |

**Run 2:**
- Ranking: `retrieved > checklist_v2 > checklist > control > full`
- Analysis: B ranks first for being the most balanced and production-idiomatic: it prefers the ORM, covers SQL injection, object-level authorization, and secrets cleanly, and reaches further into the required issues than A/D/E. A is nearly as strong and actually deeper on visible defense-in-depth, but its over-engineered query-builder abstraction and earlier truncation undercut its practicality. D distinguishes itself with the best SQL-injection teaching (allowlisting identifiers vs parameterizing values) but loses ground on correctness of the exploit demo and Django-idiomatic fit, while C is solid but slightly muddled in its mixed ORM/raw-SQL retrieve method and E trails on a minor exploit inaccuracy and an off-task framing.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `checklist_v2` | 31 | Highest technical rigor on the visible issues: correct CWE-89/284, solid parameterized query builder with date validation and status allowlist, and a clean dedicated permissions module with tenant iso |
  | `retrieved` | 30 | Most balanced and practical: correct CWEs (89, 284/862, 798), clean ORM-first SQL fix with a clear parameterized raw-SQL alternative, owner/tenant permissions, and environment-variable secrets. Reache |
  | `checklist` | 29 | Accurate CWEs (89, 862, 798/321), correct named-placeholder parameterization, composite permission classes, and a good dotenv/_get_env secrets helper. Reaches Issue 3. The retrieve method mixes ORM qu |
  | `control` | 29 | Best treatment of the identifier-vs-value distinction (allowlisting structural columns while parameterizing values), which is the key SQL-injection insight. Strong authz diagram. However, it relies on |
  | `full` | 26 | Good allowlist + tenant validation + parameterized queries and a sensible owner-or-admin model method, but the tenant_slug '; DROP TABLE' exploit is inaccurate for a single-statement driver, and the p |

**Run 3:**
- Ranking: `checklist > retrieved > checklist_v2 > full > control`
- Analysis: B ranks first because it is the most correct and idiomatic, emphasizing queryset-scoped tenant isolation and clean env-var secrets without introducing bugs. E and C both cover three issues, but E edges out C because C's CombinedObjectPermissions inheritance bug silently drops the owner check on writes, whereas E keeps tenant scoping and ownership checks coherent. A and D trail because they are truncated earliest — A also contains internal serializer/permission inconsistencies, and D covers only the SQL-injection issue, leaving the other three required fixes unaddressed.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `full` | 19 | Strong SQL-injection section with a group_by whitelist and both ORM and parameterized-raw fixes, and decent object-level permission classes. But it is truncated early (never reaches secrets or the sta |
  | `checklist` | 28 | Cleanest and most idiomatic response: correct CWE-89 with ORM + enum whitelist, strong object-level fix centered on get_queryset() scoping (the key multi-tenant defense), and solid env-var/dotenv secr |
  | `checklist_v2` | 24 | Well-structured with named-parameter SQL, get_queryset tenant scoping, and django-environ secrets. However, CombinedObjectPermissions has a real authorization bug: multiple-inheritance MRO means IsTen |
  | `control` | 20 | Issue 1 is correct and clean (named placeholders + status whitelist + ORM alternative), but the response is cut off after SQL injection, covering only one of the four required vulnerabilities and none |
  | `retrieved` | 26 | Solid across SQL injection (column whitelist + parameterized values), object-level authorization (permission classes, queryset scoping, and CurrentTenantMiddleware), and secrets management. A few mino |

**Run 4:**
- Ranking: `full > checklist_v2 > control > retrieved > checklist`
- Analysis: C leads by being the only response to reach secrets management with a proper django-environ fix while still correctly covering SQL injection and object-level authorization. B is the strongest on the two issues it does cover (tenant-scoped reads, identifier allowlisting, throttling) but never reaches issues 3–4, whereas C's broader coverage and standard hardening win out. A is clean and correct for issues 1–2 but stops early and drags in a tangential CWE-918; E covers a third issue but carries real defects (fail-open permission, bad int() parsing, non-multi-tenant TENANT_ID check), and D ranks last due to a buggy, over-engineered tenant resolver. Across all five responses, the clearest shared gap is that none visibly addresses the fourth required fix: serializer field allowlisting for the mass-assignment-prone staff flag.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `control` | 25 | Correctly names CWE-89 and CWE-285, gives clear exploits and clean parameterized-query + ORM fixes, and provides reasonable permission classes. However it stops after issues 1–2, never reaches secrets |
  | `checklist_v2` | 26 | Most rigorous on the first two issues: tenant-scoped reads AND writes, an identifier allowlist with pg_sql.Identifier, throttling, and membership-based authorization. Loses points because it stops bef |
  | `full` | 28 | Gets furthest: covers SQL injection, server-side object authorization, and begins secrets management with a correct django-environ/env.db/.gitignore/fail-loudly pattern. A minor dead-code duplicate SA |
  | `checklist` | 20 | Covers SQL injection and object authorization with correct CWE mapping and a fail-closed fallback, but the _resolve_tenant_id dotted-path resolver is buggy and over-engineered, and the response stops  |
  | `retrieved` | 21 | Reaches issue 3 (CWE-798/312) but with notable flaws: fail-open TenantObjectPermission (returns True when tenant_id is absent), invalid int() parsing for limit/offset, and a single global TENANT_ID ch |

**Run 5:**
- Ranking: `checklist > checklist_v2 > retrieved > control > full`
- Analysis: A edges out C because it uniquely solves the identifier-injection half of the SQL bug via a filter-field allowlist, the most technically correct defense for f-string-built filters, while C's completeness is signalled but its SQL fix only parameterizes values. C, D, and E are all strong and differentiated mainly by architecture and secrets depth: C's TenantOwned mixin is the cleanest multi-tenant model, D's secrets management is the most deployment-ready, and E offers a solid mixin plus loud-failing secret loading. B ranks last because its manual has_object_permission call in an APIView is less idiomatic and its SQL hardening overlooks identifier injection, despite being functionally correct.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `checklist` | 34 | Technically the strongest on the SQL issue: it correctly distinguishes identifier injection from value injection and allowlists the filter_field while parameterizing values, which the other responses  |
  | `full` | 30 | Correct parameterization and object-level permission code, but the class-based view manually calls has_object_permission in a non-idiomatic way instead of relying on DRF's viewset/permission integrati |
  | `checklist_v2` | 34 | The only response whose executive summary explicitly names all four issues including CWE-915 (mass assignment), signaling full coverage. Uses a TenantOwned mixin, scope_queryset, and instance-level te |
  | `retrieved` | 32 | Correct and production-minded, especially the secrets section (systemd drop-ins, AWS Secrets Manager CLI examples, per-environment security headers). Object auth via is_owner + check_object_permission |
  | `control` | 32 | Clean ObjectPermissionRequiredMixin and viewset scoping, plus a _get_secret helper that fails loudly on missing env vars. Strong SQL defense (whitelisted columns, no SELECT *, safe defaults, error han |

### Task `sre-node-leak-ieee` (domain: SRE & Debugging)

**Run 1:**
- Ranking: `control > checklist_v2 > full > retrieved > checklist`
- Analysis: E and B are clearly the top two: both are complete and technically sound, but E edges ahead by explicitly addressing the OOM-during-capture risk and using the cleaner `v8.getHeapSnapshot()`/`--expose-gc` API, while B's memory-backed emptyDir for snapshots is a subtle self-defeating choice. D and A are mid-tier with a shared Phase-1 flaw — D's inspector approach is conceptually right but its `takeSnapshot` method call is wrong, whereas A's SIGUSR1 claim is more fundamentally incorrect — so D ranks slightly above A. C trails all others because it invents non-existent Node APIs (`process.forceGC`, `process.setMinTickBeforeForceGC`) and fabricates a capture path that would not yield a usable heap snapshot.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `retrieved` | 24 | Covers all requested areas with clear phases and solid fixes, but Phase 1 has a fundamental error: it claims SIGUSR1 triggers a heap snapshot (it actually starts the inspector debugger) and invents `- |
  | `checklist_v2` | 33 | Very strong, methodical plan. Correctly uses `--heapsnapshot-signal=SIGUSR1`, adds a three-snapshot comparison, clean instrumentation, grep-based code audit, and bounded/streaming fixes. Minor issues: |
  | `checklist` | 15 | Least reliable response. Contains fabricated Node.js APIs (`process.forceGC`, `process.setMinTickBeforeForceGC`) and a confused SIGUSR2/inspector-curl capture path that won't produce a valid snapshot. |
  | `full` | 25 | Good production-security judgment (correctly warns against `--inspect` and uses a programmatic inspector session), and the conceptual capture approach is valid. However, the snapshot code is wrong: it |
  | `control` | 34 | Best response. Correctly uses `--expose-gc` and `v8.getHeapSnapshot()`, explicitly flags the critical RSS-doubling risk during capture, and gives a genuinely production-safe cadence. Retainer-chain an |

**Run 2:**
- Ranking: `full > checklist > retrieved > control > checklist_v2`
- Analysis: C and E are the strongest because they combine mostly-correct technical guidance with clear, usable retainer-chain reasoning and good Buffer-analysis; C edges out E on cleaner instrumentation and retainer illustration, while E has the better Buffer section but a few more broken APIs and a misleading listener counter. A is solid and safe but undermined by incorrect Node APIs (`v8.takeHeapSnapshot`, the fake debug endpoint), and B falls below it because it invents numerous flags/APIs and its code is over-engineered and buggy. D ranks last due to actively harmful `--max-old-space-size` advice, buggy code, and the thinnest Buffer/retainer analysis.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `retrieved` | 24 | Covers every requested section and gives strong root-cause/fix direction, but many concrete specifics are wrong: `v8.takeHeapSnapshot` is not a real API (it's `v8.writeHeapSnapshot`), the `curl http:/ |
  | `control` | 18 | Very verbose and conceptually broad, but littered with invented/incorrect mechanisms: `--trace-allocations`, `--async-stack-traces`, `process._v8debug.TakeHeapSnapshot`, `v8.takeHeapSnapshot()`, and m |
  | `full` | 28 | Strong, structured answer with accurate retainer-chain illustrations and solid conceptual correctness. Cleanest and most usable guidance overall. Minor errors keep it from a 5: `process.memoryHelpers` |
  | `checklist_v2` | 16 | Contains actively harmful advice: recommending `--max-old-space-size=2048` when the heap is already ~3.5GB would crash the process rather than aid diagnosis, and `--gc-interval 1000` is not a standard |
  | `checklist` | 28 | Very systematic and clearly follows the requested step-by-step structure. Uses the correct `--heapsnapshot-signal=SIGUSR2` flag, gives an accurate Buffer/response-logging retainer chain, and its Buffe |

**Run 3:**
- Ranking: `checklist > retrieved > control > full > checklist_v2`
- Analysis: D ranks first because its capture method is technically grounded (correct signal flag and real heapdump package) and it adds a probability-ranked root-cause list with a clean leak-pattern table, with only minor command-name slips. B is a close second for its systematic symptom table and rich emitter/buffer pattern enumeration, but loses ground on fabricated v8 capture APIs and the wrong default signal. C and A both repeat incorrect v8.writeHeapSnapshot usage and unreliable diagnostics, while E falls last because it confidently fabricates V8 APIs and npm tooling that would actively mislead a debugging effort.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `full` | 18 | Attempts all four phases but is truncated mid-Phase-4, so the plan is incomplete. Contains fabricated flags (--heapsnapshot-nofile-limit), muddled inspector pseudo-code, and half-finished snippets. Th |
  | `retrieved` | 26 | Strong conceptual coverage with an excellent symptom table and four emitter + two buffer leak patterns. However, the core capture APIs are wrong: v8.writeHeapSnapshot() does not return a Buffer, and w |
  | `control` | 23 | Covers all requested areas with a clean structure and good security posture (internal-only route, network policy). But it repeats the wrong writeHeapSnapshot signature (passing a stream), uses SIGUSR1 |
  | `checklist` | 26 | Most grounded response: uses --heapsnapshot-signal=SIGUSR1 correctly, real heapdump package, --expose-gc for forced-GC confirmation, and a sound probability-ranked root-cause list with a clean leak-pa |
  | `checklist_v2` | 17 | Extremely verbose and structurally complete, but the core V8 APIs are fabricated (v8.takeHeapSnapshot, v8.getHeapCodeAndSourceMaps) and it invents npm packages (inspector-diff, lttng). JSON.stringify- |

**Run 4:**
- Ranking: `retrieved > control > checklist_v2 > full > checklist`
- Analysis: A is the clear winner because it combines correct Node 20 mechanics (built-in --heapsnapshot-signal), accurate retainer-chain interpretation, and clean, production-sensible fixes with only minor flag/API sloppiness. B and D are comparable in completeness, but B's listener instrumentation is more fundamentally broken (dead process.emit call, wrong weakref require, wrong emitter-internals model) while D's flaws are narrower (no-flag SIGUSR2 and a misnamed v8 API), so D edges slightly in correctness yet B has richer coverage. E and C trail: E provides good root-cause content but too many wrong concrete commands/APIs, and C is weakest because it recommends deprecated tooling and includes broken code alongside its otherwise valid fixes.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `retrieved` | 31 | Most technically accurate: correctly uses Node 20 built-in --heapsnapshot-signal/SIGUSR2, gives a sound retainer-chain reading, and offers valid root causes (on/off pairing, once(), response-body capt |
  | `control` | 25 | Covers every requested phase in depth, but its instrumentation is error-prone: process.emit('heapsnapshot') does nothing, require('weakref') is wrong in Node 20 (globals already exist), and the EventE |
  | `checklist` | 18 | Recommends deprecated heapdump and legacy v8-profiler-node8 when Node has a built-in flag, includes a broken rotation snippet, and a v8Profiler .pipe() API that doesn't exist. The listener patch spams |
  | `checklist_v2` | 27 | A measured, well-structured plan with sound root causes and a correct Node 20 AbortController/signal fix. However, it claims kill -SIGUSR2 triggers a snapshot without starting with the flag, and inven |
  | `full` | 25 | Complete and addresses all four required areas, but contains multiple false specifics: kill -USR1 doesn't write heap snapshots, the CDP path /devtools/browser/capture-screenshot is a browser (not Node |

**Run 5:**
- Ranking: `checklist > full > checklist_v2 > retrieved > control`
- Analysis: A and D are the clear top tier: both are complete and conceptually correct, but A more accurately flags the stop-the-world pause inherent in snapshots while D understates it as 'non-blocking/zero latency,' and A is slightly more disciplined about protecting endpoints. Both A and D contain API-level errors (A's writeHeapSnapshot options/SIGUSR1/heapdiff; D's v8.takeHeapSnapshot and the blocking contradiction), so they are close, with A edging out D on safety-critical accuracy. E and B are weaker because their capture/instrumentation code is riddled with fabricated or invalid Node APIs (`--inspect-pid`, `process._handleSymbols`, `curl /snapshot/gc`, `InspectProfiler`) even though their conceptual reasoning and fixes are reasonable; E ranks above B for its cleaner structure and threshold table. C is last by a wide margin because it fails to provide any plan at all.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `checklist` | 28 | Thoroughly covers all four required parts and correctly emphasizes the critical point that heap snapshots pause JS execution (a multi-second stop-the-world pause). However, several concrete APIs are w |
  | `retrieved` | 22 | Conceptually sound (comparison view, retainer chains, .once vs .on, unbounded arrays) but the implementation is unreliable: `curl http://localhost:9229/snapshot/gc` is not a real inspector endpoint, ` |
  | `control` | 7 | Does not produce the requested plan at all. It only states that no codebase exploration is needed and that it could produce a plan directly, delivering no diagnosis steps, no capture/diff procedure, n |
  | `full` | 27 | Very complete and clean, with the correct `--heapsnapshot-signal=SIGUSR2` flag, good retainer-chain tracing, AsyncLocalStorage coverage, and well-structured listener/Buffer leak patterns with clean fi |
  | `checklist_v2` | 22 | Well-structured with a useful detection-thresholds table and clean root-cause/fix sections, and `writeHeapSnapshot` is used correctly in places. But it contains several broken constructs: `--inspect-p |

### Task `sre-flaky-ci-ieee` (domain: SRE & Debugging)

**Run 1:**
- Ranking: `checklist_v2 > full > checklist > control > retrieved`
- Analysis: A and D both fully satisfy the brief with ranked hypotheses, forced reproduction, and deterministic fixes, with A edging ahead via more aggressive stress-running (CPU saturation, xdist, hash-seed subprocess loops). E is complete and correct but less concrete on stress reproduction. C has good structure yet includes invalid code (post-start PYTHONHASHSEED, non-existent asyncio/marker APIs), and B falls last because its timestamp reproduction is self-consistent (can't fail), its async repro is structurally broken, and its fixes section is truncated.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `checklist_v2` | 33 | Most thorough and technically sound. Ranked hypotheses with a clean likelihood table; reproductions concretely force TZ variation, CPU saturation + xdist, and PYTHONHASHSEED cycling. Fixes use zoneinf |
  | `retrieved` | 20 | Hypothesis ranking is good, but the reproduction code is self-contradictory: the timestamp repro formats the same naive datetime on both sides so it can never differ, and the async repro mixes time.sl |
  | `control` | 24 | Covers all three tests with sensible fixes (freezegun, bounded poll loop, sorted iteration), but contains real errors: setting PYTHONHASHSEED via monkeypatch.setenv after interpreter start has no effe |
  | `full` | 31 | Strong, disciplined answer with codebase-pattern comparison and complete fixes (freezegun, asyncio.wait_for, sorted/semantic assertions). Reproduction scripts are clear, though the async repro does no |
  | `checklist` | 30 | Complete, clean, and free of bugs; uses time_machine for freezing, asyncio.wait_for plus bounded retry for polling, and sorted/keyed access for ordering. Slightly weaker on the 'stress-running' requir |

**Run 2:**
- Ranking: `retrieved > control > checklist > checklist_v2 > full`
- Analysis: A ranks first because it is the only fully complete response: all three tests are correctly diagnosed, reproduced, and fixed with clean, standard deterministic patterns and no truncation. D follows closely with superior architectural reasoning (injectable clock) and strong stress-oriented reproductions but is slightly cut off and marginally over-engineered. C, E, and B all truncate near the end; C is cleaner and more directly aligned with the prompt, E is more elaborate but less precise per test, and B is weakest due to its stray artifacts and missing final fix.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `retrieved` | 33 | Correctly identifies all three root causes (timezone/boundary race, fixed-sleep timing race, set hash randomization) and prescribes accurate, standard fixes (freezegun, asyncio.wait_for, sorted). Full |
  | `full` | 26 | Root causes are correctly diagnosed with per-test ranked hypothesis tables and sound Test 1 fix (freezegun with absolute instant). However, the response is truncated mid-Fix 2 and Fix 3 is missing, an |
  | `checklist` | 27 | Strong systematic structure (root cause → pattern → reproduction → fix) and correct fixes including event-driven and bounded-backoff async options plus sorted() ordering. Slightly truncated at the end |
  | `control` | 31 | Excellent diagnosis and the strongest architectural thinking: introduces an injectable Clock abstraction separating production time from test time, alongside freezegun, wait_for/events, and sorted().  |
  | `checklist_v2` | 29 | Very thorough with data-flow traces, a shared 'environmental non-determinism' framing, and an elaborate executable reproduction harness (temp files + subprocess pytest with varying TZ/PYTHONHASHSEED a |

**Run 3:**
- Ranking: `retrieved > checklist_v2 > checklist > control > full`
- Analysis: C and B are clearly the strongest and nearly tied, but C wins on instruction adherence because its reproduction scripts explicitly demonstrate all three required mechanisms — forcing ordering (PYTHONHASHSEED, 100x runs), freezing time (subprocess TZ + freezegun), and stress-running (100x/50x iterations) — and its hypothesis table maps each hypothesis to a concrete falsification step. D is solid but ranks third because its broken async reproduction is technically invalid and one reasoning claim is speculative. E and A trail due to reproduction bugs: E has undefined symbols in its scripts while A misuses time.sleep in an async test (deterministic failure, not flake) and truncates its third fix, so A finishes last.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `full` | 25 | Strong hypothesis ranking (confidence stars) and a clear CI-vs-local explanation, plus correct freezegun/wait_for fixes. However, the broken async reproduction uses time.sleep(2) inside an async test, |
  | `checklist_v2` | 32 | Excellent, runnable self-contained reproduction harness with a --repro flag and stress-test instructions. Correctly uses await asyncio.sleep(2) to model the flake (unlike A/D), and offers multiple wel |
  | `retrieved` | 33 | Best-aligned with the prompt. The ranked hypothesis table includes an actionable 'How to Test' column (PYTHONHASHSEED=0, TZ variants, stress with workers), and the three reproduction scripts each expl |
  | `checklist` | 30 | Thorough and complete: per-test hypothesis formation, subprocess/TZ and taskset load reproduction, and multiple fix options including sorted() and @pytest.mark.parametrize. However, the broken async r |
  | `control` | 26 | Good structure and correct core async reproduction (await asyncio.sleep), with a valuable parametrized boundary-timestamp test. But the code contains concrete errors: undefined format_timestamp and __ |

**Run 4:**
- Ranking: `full > retrieved > checklist > control > checklist_v2`
- Analysis: A and B are the clear leaders: A is the most complete and best aligned to the explicit 'minimal reproduction + forced conditions + deterministic fixes' instructions, while B has the cleanest and most technically correct fixes but a slightly thinner reproduction. C is strong and correct but lacks a unified stress harness and faithful timestamp reproducer, placing it third. E and D both suffer from concrete code defects, but D's over-engineered, hand-rolled infrastructure (broken freeze_time, sync poll for async, set-order helper that doesn't actually fix nondeterminism) is more damaging than E's isolated undefined-variable/fake-import bugs, so D falls to last.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `full` | 30 | Strong overall: explicit ranked hypothesis table, a full minimal reproduction script that forces all three failure modes, stress-run commands (PYTHONHASHSEED, freezegun, CPU load), and deterministic f |
  | `retrieved` | 32 | Cleanest and most technically correct fixes: freezegun plus aware-datetime comparison, asyncio.wait_for/Event, and sorted()/list. Excellent observation table and justified hypothesis ranking. Reproduc |
  | `checklist` | 29 | Very clear root-cause traces and percentage-ranked hypotheses; fixes (freezegun/patch, robust_poller with deadline, sorted/list) are correct and idiomatic. Reproduction snippets exist for each failure |
  | `checklist_v2` | 19 | Highly verbose and 'production-grade' in appearance, but the hand-rolled _FrozenTime is actively broken (inverted naive/aware condition, `datetime.datetime` AttributeError, fragile sys.modules patchin |
  | `control` | 26 | Comprehensive with evidence summary, ranked hypotheses, stress harness, and remediation checklist. However, the async fix references an undefined `retries` variable and imports a non-existent `pytest_ |

**Run 5:**
- Ranking: `checklist_v2 > full > control > retrieved > checklist`
- Analysis: E and C lead because they explicitly neutralize timezone (not just freeze time) and use correct async primitives, with E adding reusable helpers and a falsifiability-focused hypothesis table. B is close but trips on a frozen-timestamp assertion bug and inconsistent hypothesis percentages; A and D trail mainly on timezone completeness and truncated Fix 3 sections, with A also muddling its repro code and D under-addressing timezone while mixing time.sleep into async waits.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `retrieved` | 29 | Strong hypothesis tables with likelihoods and a real stress/repro harness that forces all three failure modes (hash seed, worker delay, time boundary). But the reproduction code is muddled (e.g., a bo |
  | `control` | 32 | Tightly organized, fully addresses all three tests plus environment-level guards (TZ, PYTHONHASHSEED), and gives clean production-side clock injection. Minor correctness issues: the frozen timestamp a |
  | `full` | 34 | Excellent, explicit timezone handling (datetime.now(timezone.utc), offset-aware freeze), crisp likelihood reasoning that maps each symptom to exactly one root cause, and clean before/after code for al |
  | `checklist` | 28 | Good conceptual framing and useful order-independent assertion guidance (membership vs. position), but the timestamp fix leans on freeze_time without explicitly neutralizing timezone, the async fix st |
  | `checklist_v2` | 35 | Best overall: falsifiable hypothesis ranking, explicit timezone-neutral fixtures plus a parametrized timezone math test, a reusable await_condition helper with proper asyncio primitives and diagnostic |

### Task `sre-p99-regression-ieee` (domain: SRE & Debugging)

**Run 1:**
- Ranking: `checklist > full > checklist_v2 > retrieved > control`
- Analysis: C and A are the top two: C wins on reasoning depth (correctly identifying pool saturation as the dominant mechanism) and adds load-testing, while A has the strongest flame-graph interpretation and decision tree. D is solid and clean but narrower, and B is undermined by a Flask-in-FastAPI error and an undefined variable. E ranks last due to a syntactically invalid SQLAlchemy event listener and broken pool subclass code. All responses are truncated before the required batching/indexing/pool-tuning fixes, so none fully satisfies that portion of the prompt.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `full` | 27 | Strong, accurate diagnosis with a clear decision tree and the best flame-graph reading section. Covers query tracing, pool metrics, continuous profiler, and DB-side pg_stat_statements. Minor SQLAlchem |
  | `retrieved` | 24 | Good ranked hypotheses and a useful cause-distinguishing matrix, but code quality drags it down: imports Flask in a FastAPI context, uses an undefined total_request_ms, and misuses the pool API. Trunc |
  | `checklist` | 28 | Best diagnostic reasoning — correctly notes that a nearly-flat p50 strongly implicates pool saturation as the dominant mechanism, likely triggered by N+1. Accurate, detailed py-spy flags and adds k6 l |
  | `checklist_v2` | 26 | Well-structured, correct N+1 detection toolkit with a sensible heuristic score and dedup-savings estimate. Clean dataclass-based design. More focused than the others but truncated earlier, so it reach |
  | `control` | 20 | Has a decent diagnostic tree and lock-contention SQL, but multiple concrete code bugs undermine correctness: the event.listens_for target is the invalid string 'text Compiled SQL', and the Instrumente |

**Run 2:**
- Ranking: `full > checklist > control > checklist_v2 > retrieved`
- Analysis: D leads because it best answers the core diagnostic question — how to distinguish N+1, pool saturation, and lock contention — with a precise decision matrix and concrete SQL, and it prioritizes the highest-value instrument first. A and B are both comprehensive and provide solid instrumentation code, but A is undermined by a concurrency bug in its per-request listener registration and B by DB-side code signature errors; B gains ground from its pg_stat_statements coverage while A's timing approach is more reliable. C covers similar ground but with broken/confused code, and E stands apart as a summary of a deliverable rather than the deliverable itself, offering no actionable design content.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `checklist` | 27 | Strong signal analysis and full instrumentation code (SQLAlchemy query tracing, pool metrics, py-spy, OpenTelemetry) plus a decision matrix. However, the query-tracking middleware registers/removes pr |
  | `control` | 27 | Covers the full scope and uniquely goes deep into DB-side instrumentation (pg_stat_statements, pg_stat_activity lock queries) with a useful thresholds table and call-stack capture. Some code issues (u |
  | `checklist_v2` | 21 | Provides profiler scripts and pool metrics, but the query tracer contains a non-functional placeholder (`_noop` listening on a logger parent) and the `_QueryCountTrackingMixin` monkey-patching logic i |
  | `full` | 29 | Best diagnostic differentiation: the decision matrix explicitly separates N+1, pool saturation, and lock contention using query-duration patterns, queries-per-request distribution, and P95-vs-P99 rela |
  | `retrieved` | 15 | This is only a meta-summary claiming a document was created; it lists the required elements (hypotheses, instruments, distinguishing tests, flame graph guide, ranked fixes) but supplies none of the ac |

**Run 3:**
- Ranking: `control > retrieved > full > checklist_v2 > checklist`
- Analysis: A leads on diagnostic reasoning depth and signal interpretation, but its code contains more real bugs (invalid method calls, non-existent imports) than B's cleaner, more balanced delivery with clearer flame-graph guidance. C nearly matches B on differentiation rigor but has asyncio/API errors and a missing fixes section; D and E trail because D's pool-metrics logic is inverted (undermining the saturation-vs-N+1 call) and E relies on risky monkey-patching with inaccurate pool introspection. Overall the group converges on the correct root cause, with separation driven primarily by code correctness and maintainability rather than conceptual understanding.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `control` | 28 | Strongest diagnostic reasoning: the signal-analysis table mapping each metric (p50/p99/CPU/mem/connections) to what it rules out is excellent, and the three-pattern comparison is crisp. Instruments (p |
  | `retrieved` | 27 | Well-structured and balanced. The distinction table plus a concrete `classify_latency_regression` heuristic (overhead ratio vs query count) is practical, and the ASCII flame-graph examples (N+1 wide r |
  | `full` | 26 | Excellent, detailed differentiation matrix (9 signals) and a clear step-by-step decision flow for distinguishing N+1 from pool saturation and lock contention. Symptom analysis correctly keys on flat C |
  | `checklist_v2` | 25 | Provides a useful layered instrumentation diagram and, uniquely, concrete PostgreSQL diagnostic queries (pg_stat_activity state distribution, pg_stat_statements, lock waits, N+1 frequency) which are i |
  | `checklist` | 20 | Good hypothesis tree (N+1, pool exhaustion, missing index) and a reasonable N+1 scoring heuristic, but the implementation approach is the weakest: monkey-patching `database.pool.execute` is fragile an |

**Run 4:**
- Ranking: `control > full > checklist > retrieved > checklist_v2`
- Analysis: Response D ranks highest because it gives the sharpest, most actionable discrimination of N+1 vs pool saturation vs lock contention with a concrete classification test and profile-grep checklist, while staying technically sound and fully addressing the ranked-fix requirement. Response B is the most complete breadth-wise but falls behind D on a couple of hard technical errors (wrong pg_stat_statements columns, broken lock JOIN) and a less rigorous decision framework. E, A, and C all show strong investigative instincts and reasonable instruments but each has truncation or concrete correctness bugs: E has invalid pg_locks SQL and non-existent SQLAlchemy wait events, A truncates the flame-graph and fixes sections, and C has the most API-level mistakes in its code samples, making it the weakest of the five.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `retrieved` | 27 | Strong, accurate opening symptom analysis with a clear hypothesis-vs-signal table. Instruments are mostly correct and well-chosen (py-spy, SQLAlchemy events, pool checkout/checkin metrics). Minor issu |
  | `full` | 28 | Most complete: explicitly covers continuous profiler, query tracing (pg_stat_statements + log_min_duration_statement), pool metrics, cache hit rate, access logs, the three-way distinction, flame-graph |
  | `checklist_v2` | 26 | Well-structured hypothesis matrix and instrumentation plan (py-spy + scalene alternative, PG server-side logging, app tracer, middleware, Prometheus pool metrics). But several concrete bugs lower corr |
  | `control` | 30 | Best reasoning quality: concise, decisive signal interpretation and the most rigorous decision matrix for separating N+1 vs pool saturation vs lock contention, plus a concrete classification test and  |
  | `checklist` | 26 | Comprehensive hypothesis matrix and instrumentation (SQL tracer, pool hooks, py-spy, lock diagnostics), with a good explicit ranking of fixes. However, several errors reduce the score: the pg_locks SQ |

**Run 5:**
- Ranking: `checklist > full > control > checklist_v2 > retrieved`
- Analysis: D ranks first because it is the most correct and rigorously structured (contextvars tracing, k6 load testing, protected debug endpoint, explicit decision flow), whereas the others carry more concrete code defects or thinner instrumentation. E edges out B on correctness and clarity of the async tracing/decision matrix, despite B's stronger profiler-selection reasoning; C and A trail because C uses thread-local state in an async service and A relies on a broken, async-unsafe cProfile middleware. The responses differ primarily in whether they ground their diagnosis in working async-safe instrumentation and whether they actually complete the requested fix ranking.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `retrieved` | 17 | Reasonable diagnostic framing and good flame-graph/lock-detection material, but the 'continuous profiler' is a cProfile middleware that (a) is fundamentally wrong for async FastAPI and (b) never calls |
  | `control` | 19 | Strong on instrument selection (correctly prefers py-spy over cProfile with an overhead rationale, uses OTel/SQLAlchemy spans) and trace-signature reasoning. However the code misuses SQLAlchemy intern |
  | `checklist_v2` | 18 | Covers pool metrics, query tracing, profiler, DB-side slow-query/EXPLAIN, and a clear N+1-vs-saturation-vs-lock table. A key correctness flaw is using threading.current_thread for route tagging in an  |
  | `checklist` | 25 | Most systematic and correct: phased instrumentation, contextvars-based per-request query telemetry, k6 load test for hard before/after numbers, and an explicit decision flow distinguishing the three c |
  | `full` | 20 | Clear symptom/decision matrix and correct contextvars-based async query tracing, plus a useful async task inspector. The pool-metrics code is broken (accesses prometheus-client internals and nonexiste |

### Task `qa-ratelimiter-tdd-ieee` (domain: Testing & QA)

**Run 1:**
- Ranking: `full > checklist > retrieved > control > checklist_v2`
- Analysis: A is strongest because it actually executes the requested three red/green/refactor cycles with explicit 'what improved' notes and covers every required test seam, despite minor unit and rigor flaws. C ranks second as a coherent, correct-but-synchronous solution that misses the coroutine requirement. B and E share a similar weakness: both attempt the distributed/async abstraction the task wants but ship buggy, contradictory code and muddled narratives, with B's backend logic actually broken and E's backend never persisting pruning. D ranks last because it combines a sync-only design, private-clock patching, an append-before-check bug, and self-acknowledged non-red tests, making it the least rigorous and least faithful to the prompt.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `full` | 24 | Delivers the ordered test list, a first failing test, minimal pass, and three labeled red/green/refactor cycles with stated improvements. Covers boundary, rollover, clock injection, concurrency (async |
  | `retrieved` | 16 | Has the right conceptual ingredients (Clock protocol, RateLimitBackend ABC, async interface), but the implementation is broken: InMemoryBackend prunes with `t > now` (keeps only future timestamps), us |
  | `checklist` | 19 | Clean synchronous in-memory implementation whose sliding-window pruning is correct, with a sensible unittest-style red/green/refactor flow. However it is fully synchronous, so it misses the required a |
  | `checklist_v2` | 14 | Synchronous `is_allowed` with clock patched through a private staticmethod (`limiter._clock = ...`), an initial append-before-check bug, and repeated admissions that the tests are not truly red. No lo |
  | `control` | 16 | Uses async and a backend ABC with clock injection, which is closest in spirit to the spec, but the backend never persists pruning (stale timestamps accumulate) and get-then-add is not atomic, so it is |

**Run 2:**
- Ranking: `full > control > checklist_v2 > retrieved > checklist`
- Analysis: D ranks first for overall structure, test coverage, thread safety, and explicit refactor steps despite being synchronous; E edges out A because it genuinely states what each refactor improved, whereas A omits refactors entirely and makes a misleading distributed-safety claim. C has the best distributed-safe store abstraction but is dragged down by a self-contradictory pre/post-increment semantics error, and B sits last because its reasoning is muddled and the walkthrough repeatedly revises itself.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `checklist_v2` | 20 | Sliding-window deque logic and clock injection are correct, and the 28-item ordered test list is the most comprehensive. However, the response never shows an explicit refactor step (a hard requirement |
  | `checklist` | 19 | The final sliding-window list implementation is correct and it does include ABC/dataclass abstractions plus explicit refactor steps. But the walkthrough is muddled — it repeatedly revises its own test |
  | `retrieved` | 20 | The RateLimitStore Protocol with an atomic increment_and_count operation is the strongest genuinely distributed-safe interface across all responses. However, the author gets confused about whether the |
  | `full` | 23 | Most structured and complete response: a 20-item test list, modular package layout, threading.Lock for thread safety, and explicit refactor steps. The main misses are that the interface is synchronous |
  | `control` | 21 | The deque-based sliding window and pop-undo logic are correct, and the refactor sections are the clearest in the set, explicitly stating what each refactor improved. But there is no distributed-safe i |

**Run 3:**
- Ranking: `control > checklist > checklist_v2 > full > retrieved`
- Analysis: E ranks first because its code is correct, its refactor rationale is explicit, and it follows the strict red-green-refactor discipline most faithfully, despite stopping short of actually implementing concurrency. A and B both cover more ground but are undermined differently: A by a confused, self-correcting narrative and incomplete test list, B by a test fixture that would error at runtime (`advance` passed to and called on a RateLimiter that lacks it). D and C trail because each has a real core-logic defect — D appends before enforcing the limit (unbounded bucket growth) and C's WindowState references undefined attributes, making its code non-runnable as written.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `checklist` | 20 | Sliding-window logic (deque + cutoff prune) is essentially correct, and the red-green-refactor structure is present. But the narrative is littered with visible self-correction ('But wait…', 'Let me re |
  | `checklist_v2` | 21 | Offers the most complete surface: design-decision table, full 9-test suite, and three cycles including a genuine asyncio concurrency test with per-key locks. However the test harness is broken — the f |
  | `retrieved` | 16 | Shows a 6-test plan and the deliberate `>` vs `>=` bug is a nice TDD touch, but the core code is broken: the initial WindowState dataclass defines only `key` and `entries` yet its methods reference `s |
  | `full` | 20 | Presents a clean AllowResult-based contract and a solid prioritized test list with an async interface. But the GREEN implementation appends the timestamp *before* checking the limit, so rejected reque |
  | `control` | 25 | Cleanest and most disciplined of the set: ordered 9-test inventory across three increments before code, correct sliding-window logic, and a refactor table explicitly stating what each change improved. |

**Run 4:**
- Ranking: `checklist_v2 > full > retrieved > control > checklist`
- Analysis: C is the strongest because it delivers a genuinely correct sliding-window implementation with clean, substantive refactors and proper clock injection, even though it doesn't reach the concurrency/distributed-safe requirements before truncation. A is close on algorithm correctness but loses ground on muddled reasoning, a hacky clock, and a double clock-read; E is correct in the single-threaded case but its concurrency test is non-functional. B falls below A and E because it substitutes a fixed-window counter for the required sliding window and mislabels it 'equivalent,' a direct violation of the central instruction; D ranks last due to pervasive contradictions, an inconsistent clock contract, and near-total lack of completed cycles.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `full` | 21 | Implements a correct sliding-window (timestamp list → deque with stale eviction) with injectable clock. Covers boundary, rollover, and starts key isolation. However the reasoning is muddled (the autho |
  | `control` | 18 | Fails the core requirement: it implements a fixed-window counter and argues it is 'equivalent to a 1-slot sliding window,' which is false (fixed windows allow boundary bursts that sliding windows prev |
  | `checklist_v2` | 26 | Cleanest and most correct sliding-window implementation: deque-based pruning with a correct `<= cutoff` boundary, count-guard before append (rejected requests not stored), and clean injectable `now` c |
  | `checklist` | 16 | Extremely messy and self-contradictory. The clock contract flips several times, there is a dataclass mismatch (`InjClock(start=...)` vs `now_val`), and the `allow()` docstring says it both returns Tru |
  | `retrieved` | 19 | Single-threaded sliding-window logic is correct (list filtering with a correct cutoff), and it shows five cycles with boundary/rollover coverage. But the 'concurrent acquisition' test is broken: it us |

**Run 5:**
- Ranking: `full > checklist_v2 > retrieved > control > checklist`
- Analysis: E ranks first because it is the only response that actually demonstrates three distinct, minimally-incremental red-green-refactor cycles with clear refactor rationale, even though its coroutine test is broken and its 'distributed-safe interface' is unsubstantiated. A is second on the strength of its correct distributed-safe storage abstraction and async/coroutine-oriented design, but it is truncated after a single cycle and therefore fails the explicit 'three increments' requirement. B and C trail because B substitutes threads for coroutines and front-loads the full implementation (defeating strict TDD), while C is truncated and contains a concrete off-by-window test bug; D is last as a non-deliverable.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `checklist_v2` | 21 | Best architecture: explicit IRateLimiterStorage distributed-safe interface, async clock, and per-key asyncio locks match the coroutine/interface requirements directly. However the response is truncate |
  | `retrieved` | 18 | Most complete in raw cycle count (four iterations) and the synchronous sliding-window logic is correct, but it uses threads/threading.Barrier instead of the required coroutines, provides no distribute |
  | `control` | 16 | Has a proper RateLimitInterface ABC and async methods, but the response is truncated before the concurrency increment and contains a concrete bug: test T1.3 uses timestamps [0..49] with window_seconds |
  | `checklist` | 7 | Not a real answer. It contains no ordered test list, no failing test, no code, and no refactor steps — only a self-congratulatory summary claiming the deliverable is already complete while offering to |
  | `full` | 21 | Delivers the most genuine TDD demonstration: three full red-green-refactor cycles with truly minimal implementations (Cycle 1 always-allows, Cycle 2 adds the counter, Cycle 3 adds pruning + clock) and |

### Task `qa-checkout-e2e-ieee` (domain: Testing & QA)

**Run 1:**
- Ranking: `control > retrieved > full > checklist > checklist_v2`
- Analysis: E ranks first because it is the only response that fully delivers the named quarantine-policy requirement alongside real per-worker data isolation and networkidle-free waits, at the cost of some type-level bugs. B is close behind with the cleanest, most compilable auth and API-stub code, but loses ground due to a duplicate-key compile error, hardcoded credentials, and a truncated (missing) quarantine policy. A and C each nail one dimension (A: reasoning and trace-on-first-retry; C: page-object wait helpers) but leave core code broken or missing, while D is clearly worst because its route-interception code contains fatal syntax errors that prevent it from running.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `full` | 20 | Good reasoning and clean directory layout, and it is the only response using trace:'on-first-retry' correctly. But the auth fixture is substantively broken: workerIsolatedCookieName is a no-op (so no  |
  | `retrieved` | 23 | Cleanest and most correct auth (storageState + seed script) and route-interception code, with a clear Base->Auth->Api->Checkout fixture hierarchy and workerPrefix-based isolation. However, the config  |
  | `checklist` | 18 | Solid BasePage with typed locators and useful custom wait helpers (waitForVisible/Detached/OptimisticUpdate), and no hardcoded credentials. But 'preserveWhitespace: true' is an invalid Playwright opti |
  | `checklist_v2` | 13 | Contains fatal syntax errors ('await page.route \'url\', handler' missing parentheses) repeated across the stub service, a placeholder throw in performFreshLogin, an undefined custom toBeOK matcher, a |
  | `control` | 26 | Most complete response and the only one to explicitly specify a quarantine policy (dedicated serial project + quarantine-manifest with maxFlake/audit fields). Strong per-worker isolation via nonce/uid |

**Run 2:**
- Ranking: `retrieved > checklist > checklist_v2 > control > full`
- Analysis: D edges out C and B because it combines a correct on-retry trace mode, a clean local/CI project split, and working per-worker isolation, whereas C's storageState is effectively shared across workers and its artifact mode is wrong, and B — despite the best code quality — never shows the config or quarantine policy the task explicitly requested. A and E rank last because they introduce hard correctness failures: A ships invalid Playwright config keys/modes plus non-deterministic Math.random fixtures, and E has a circular-duplicate fixture plus an incorrect fulfillment API and no quarantine handling.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `control` | 21 | Covers config, global setup, and fixture hierarchy, but the config uses invalid Playwright keys (`videos`, `tracesDir`) and an invalid trace value (`'retry'` — not a real mode). Global setup calls `wa |
  | `checklist_v2` | 27 | Highest-quality code shown: fully typed domain model, genuinely deterministic fixtures (no Date.now/random in stub data), behavior-driven payment stub, and an explicit no-waitForTimeout policy. Howeve |
  | `checklist` | 24 | Best quarantine implementation (dedicated serial project with `fullyParallel: false`, `retries: 0`) and an excellent root-cause table. But `getWorkerStoragePath()` is evaluated once at config load usi |
  | `retrieved` | 25 | Cleanest defensible config with a local/CI two-project split, correct `trace: 'on-first-retry'`, solid typed domain types, and per-worker `TEST_WORKER_INDEX` isolation. Weaknesses: video is `'retain-o |
  | `full` | 20 | Has a plausible structure and `workerInfo.parallelIndex % totalAccounts` mapping, but contains a serious bug: the base fixture defines `stubbedContext` twice (the second depends on itself, a circular  |

### Task `qa-dashboard-browserqa-ieee` (domain: Testing & QA)

**Run 2:**
- Ranking: `retrieved > checklist_v2 > checklist`
- Analysis: B beats C on code correctness and maintainability: B's smoke crawl is cleaner and functional, while C contains multiple concrete bugs (un-abortable Request in the mutation guard, inverted error filter, ev.type() on a plain object, fabricated navigator.metrics) that would break at runtime. C's security concept is strong on paper but non-functional, negating its apparent edge. D is clearly last because it only summarizes what it claims to have delivered elsewhere rather than producing any actual plan, rules, or exit criteria, so it fails instruction adherence outright. All three are truncated, but B and C at least deliver real, executable scaffolding for the early stages.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `retrieved` | 25 | Correctly identifies the workspace has no dashboard and delivers real Playwright code. Smoke-crawl code is mostly sound, though the INP 'approximation' via navigation timing is technically wrong and p |
  | `checklist_v2` | 22 | Good environment discovery and a genuinely valuable concept (mutation guard). But the code has real defects: page.on('request') gives a Request, which has no abort() method, so the guard cannot actual |
  | `checklist` | 12 | Delivers no actual plan, rules, code, or exit criteria — only a summary claiming the full spec 'has been delivered in the previous response.' It lists stage titles but produces none of the required su |

**Run 3:**
- Ranking: `full > retrieved > checklist_v2 > control > checklist`
- Analysis: C and E are the clear top two for full coverage and strong blast-radius/exit-criteria reasoning, with C edging out E on strict adherence to the flat 0.1% threshold and an explicit verdict matrix, while E offers richer accessibility and dark-mode detail. A ranks third because its blast-radius and baseline work is excellent but its Core Web Vitals code contains scope/measurement bugs, and it trails on runnable-correctness. B and D sit lowest due to structural test bugs (nested `test()` in B, a tautological assertion and failed-request detection gap in D) and missing security/accessibility/exit criteria.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `checklist_v2` | 27 | Strong blast-radius table and baseline strategy, plus a useful env-guard script. But the Core Web Vitals snippet is buggy: CLS is never actually observed, and `cls`/`inpValues`/`avgInp` are referenced |
  | `control` | 21 | The smoke-crawl code is solid (response.ok() + requestfailed handling) and filter tests are reasonable, but the 'reset on all viewports' test is structurally broken — it uses an invalid Playwright sig |
  | `full` | 34 | Comprehensive and technically sound. Covers all four phases, a detailed forbidden-action blast-radius table with an opt-in mutation rule, dark-mode baseline strategy, masking, 0.1% threshold, and a cl |
  | `checklist` | 20 | Python smoke crawl is mostly valid but failed-request detection misses `requestfailed` events (status 0 is never >= 400), so real network failures slip through. The drill-down assertion is tautologica |
  | `retrieved` | 33 | Excellent plan with deep chart-ARIA, focus-order, reduced-motion, and dark-mode contrast specifics, plus a strong never-click/allowed table and concrete exit gate. The per-element tolerance tiers (0.0 |

**Run 4:**
- Ranking: `checklist_v2 > control > retrieved > full > checklist`
- Analysis: A ranks first because it is the only response that fully addresses all seven required sections with dedicated, concrete content (including both the blast-radius rules and the dark-mode dual-baseline strategy that several others omit or truncate). C and E are strong on technical depth and architecture, but both truncate before delivering the dark-mode baseline and exit criteria, with E additionally missing any explicit blast-radius rules. B and D trail because B stops at the interaction phase with no visual/a11y/dark-mode/exit sections, and D fails outright by producing no plan at all — only a clarifying question.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `checklist_v2` | 34 | Explicitly covers every requested component — smoke crawl (console errors, failed requests, CWV), interaction tests, visual regression with masking and 0.1% threshold, accessibility (contrast, focus o |
  | `full` | 23 | Produces solid, runnable Playwright code for smoke and interaction phases with strong blast-radius rules, but truncates during Phase 2 and never delivers visual regression, accessibility, dark-mode ba |
  | `control` | 31 | Highly detailed and technically precise: pinned viewport/DPR config, per-stage pass/fail, mask selectors, 0.1% threshold, and a thorough ARIA role table including tooltip/aria-describedby. Falls short |
  | `checklist` | 8 | Does not deliver a QA plan at all. The response is a meta-question asking whether the user wants a plan extended, referencing a previous answer and a skill checklist. It produces no actual content add |
  | `retrieved` | 28 | Presents a clean six-phase architecture with good code (masking, contrast extraction, pixel-diff) and explicitly names dark-mode baseline and sign-off phases, but truncates before Phase 5/6 and provid |

**Run 5:**
- Ranking: `retrieved > full > checklist_v2 > checklist > control`
- Analysis: C wins on completeness and instruction adherence because it explicitly and cleanly delivers every requested deliverable — blast radius, dark-mode baseline, exit criteria, and a genuinely detailed accessibility pass — whereas A and D are slightly less explicit on accessibility and visual-regression detail. A and D are close seconds, with A cleaner in code structure and D stronger on security/blast-radius YAML, but both trail C on end-to-end sign-off clarity. B is thorough on interaction/visual depth yet omits a dedicated blast-radius section and drifts into repo context, while E is structurally sound but marred by small code inaccuracies that lower its correctness and maintainability.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `full` | 29 | Strong, well-structured plan with a clear scope table, six detailed blast-radius rules (no-production, read-only, opt-in mutator, redaction, rate-limiting), a sound light/dark baseline strategy, and a |
  | `control` | 26 | The most granular on smoke/interaction/visual detail (filter matrix, drill-down depth rules, masking registry, baseline matrix), and technically accurate overall. However it lacks a dedicated 'what ne |
  | `retrieved` | 34 | The most complete and instruction-adherent response: explicit blast-radius table, four clean phases matching the task's four passes, dark-mode baseline strategy, per-phase exit criteria, and a verdict |
  | `checklist_v2` | 29 | Excellent security posture via a YAML blast-radius config (immutable pages, credential rotation, redaction, dry-run mutation policy) and a clear 'no baseline = inconclusive' rule. Concrete, runnable-s |
  | `checklist` | 26 | Has an explicit no-click-zone table and a nice cross-device parity angle (mobile bottom-sheet vs desktop popover) that others lack. But code quality is weaker: `pageerror` is mislabeled as unhandled-p |

### Task `arch-godclass-refactor-ieee` (domain: Architecture & Refactoring)

**Run 1:**
- Ranking: `full > control > retrieved > checklist_v2 > checklist`
- Analysis: B is the strongest because it alone delivers all five required deliverables — characterization harness, a persistence-first seam order with rationale, commit-by-commit strangler steps, target boundaries, and per-commit preservation checks — in a coherent order. A and C both reach characterization plus a seam order but truncate before the strangler/target phases; A's persistence-first rationale better matches the 'scattered SQL' pain than C's pricing-first choice. E covers characterization and target boundaries but omits the seam order and strangler steps entirely, while D never gets past characterization tests.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `control` | 23 | Strong on the dependency-map/static analysis and the persistence-first seam rationale (correctly motivated by scattered SQL). However, the characterization code has real fixture bugs (undefined tmp_pa |
  | `full` | 32 | The only response that delivers all five requested deliverables end-to-end: golden-master capture (SQL interceptor, fake SMTP, audit), a persistence-first seam order with clear rationale, eight increm |
  | `retrieved` | 24 | Solid characterization harness (SQLCaptureHook, MailStub) and a defensible seam extraction order, but chooses pricing-first rather than persistence-first, which is less aligned with the 'direct SQL sc |
  | `checklist` | 19 | Good intuition on characterization-first and strong prod-safety discipline (staging mirror, 'NEVER prod'), but it stops after the golden-master phase. It never delivers the seam extraction order, stra |
  | `checklist_v2` | 24 | Clean, reusable harness (QueryLog, EmailSnapshot) and a well-reasoned 'harness over mocks' argument, plus a decent target module layout. But it omits the explicit seam extraction order and the increme |

**Run 2:**
- Ranking: `control > full > checklist > checklist_v2 > retrieved`
- Analysis: C and A are the strongest because they pair rigorous golden-master mechanics (interceptor + DB-state hash/snapshot) with an explicit, justified persistence-first seam order and per-commit verification; C edges out A on SQL-capture depth while A matches it on the commit-by-commit proof table. D is nearly as good but chooses a different email-first seam order and is slightly lighter on capture details. E adds a genuinely useful AST inventory but is undermined by broken code and over-aggressive sanitization, while B is weakest because its MagicMock-based 'golden master' records calls rather than proving preserved behavior and leaves many tests as placeholders.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `full` | 33 | Sound plan: row-level DB state hashing plus email capture, clear persistence-first seam rationale, explicit commit table mapping every step to a verification hook, and concrete module boundaries. Secu |
  | `retrieved` | 23 | Heavily code-focused but the golden master relies on MagicMock db.execute that records calls instead of verifying real DB state; several tests are placeholders ('pass', print-to-bootstrap, 'record act |
  | `control` | 33 | Most rigorous SQL capture: query interceptor (SQL + params + rowcount) AND pre/post DB state snapshots, plus a clean email interceptor, golden file format, and verify_matches_golden helper. Explicit ' |
  | `checklist` | 32 | Strongest 'reasons to change' module boundaries and a clear, well-argued (though different) seam order: observability wrappers first, then email, then persistence, then validation/pricing/tax. Slightl |
  | `checklist_v2` | 26 | Valuable unique Phase 0 AST-based signature/SQL/field inventory, and clear SQL/email snapshot tests, but contains invalid Python ('self | FunctionDef'), fragile MagicMock patching, and sanitization th |

**Run 3:**
- Ranking: `checklist > retrieved > checklist_v2 > full > control`
- Analysis: B ranks first because it delivers all four requested components — characterization tests, a reasoned seam extraction order, incremental strangler steps, and module boundaries — with explicit per-commit verification. E is technically superior on architecture (pure-logic-first seam order) and correctness (asserting domain state over raw SQL), but it truncates before the strangler steps. C and D both stop before the seam/strangler sections, with C adding an explicit three-gate preservation check while D offers the most rigorous DB checksum and SMTP capture; A is verbose on test infrastructure but has a code typo and omits the seam/module plan entirely.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `control` | 20 | Detailed golden-master/interceptor code, but it is verbose, contains a code typo ('existists=False'), and is truncated before the seam extraction order, strangler steps, and module boundaries — three  |
  | `checklist` | 28 | Most complete response: covers characterization tests, a full seam extraction order with rationale, incremental strangler steps with shippability/verification notes, and target module boundaries. The  |
  | `checklist_v2` | 23 | Solid characterization harness (SQL recorder, email capture, audit stub) and an explicit three-gate behavior-preservation mechanism (golden master, dead-SQL grep, frozen API signature). However, it tr |
  | `full` | 22 | The most rigorous characterization section — database snapshots with per-row checksums, a fake SMTP transport, and audit-log capture. But it truncates before the seam extraction, strangler steps, and  |
  | `retrieved` | 30 | Technically the strongest on architecture and reasoning: correctly recommends asserting resulting domain state rather than raw SQL, and chooses pure/deterministic logic (Validator → Pricing/Tax) first |

**Run 4:**
- Ranking: `retrieved > control > full > checklist_v2 > checklist`
- Analysis: All five correctly identify persistence/repository as the first seam, but they diverge on sequencing: A, D, and E extract pricing/tax (pure logic) before email/audit (side effects), while B uniquely elevates email to second place — defensible but less canonical. A and D are the most complete across all five deliverables, whereas B and E are deeper on characterization and reasoning but truncated on strangler steps and target boundaries. C is context-aware and competent but falls behind on architecture and maintainability (notably the SQLite-replay risk).

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `retrieved` | 32 | Canonical and technically sound: persistence-first, then pure logic (pricing/tax), then side effects (email/audit). Justifies each seam with 'why first/second'. Characterization covers API mapping, SQ |
  | `control` | 31 | Superb characterization (captures return values, DB rows, emails, audit, exceptions) and a strong 'why NOT this order' section. Ports/adapters naming (OrderPersistencePort, EmailGateway) is the most p |
  | `checklist` | 25 | Correctly flags the repo lacks OrderService, then delivers a solid two-tier characterization with SQL normalization and email/audit fakes. Weaker on architecture: no explicit layering, and the 'replay |
  | `full` | 30 | The most complete and explicit across all five deliverables: a full strangler-step table with per-step verification, a detailed domain/infrastructure/application target with explicit dependency rules, |
  | `checklist_v2` | 29 | Highest reasoning quality: correctly argues SQL/SMTP are implementation, not the observable contract, and explains why the migration is not parallelizable. Protocol-based interfaces are clean. However |

**Run 5:**
- Ranking: `checklist > checklist_v2 > full > control > retrieved`
- Analysis: A edges out the field on technical correctness and discipline — it gives the most concrete, runnable SQL-snapshot options (DB-level logging plus connection proxy), explicit email/audit capture, and a rigorous per-commit proof gate while transparently flagging that no OrderService exists in the repo. C is the most complete on paper (full golden-file generator, hash+payload snapshots) but slips on a subtle correctness bug in its example script and a vaguer SQL capture, so it ranks just below A. B and D are both strong and fully compliant, differing mainly in seam ordering (pure-logic-first vs. highest-coupling-first) and depth of SQL mechanics; B's interface-first ABC tables and commit checklist give it a slight edge over D's more narrative style. E is practical and safe but the least rigorous in snapshot mechanics, using hard-coded assertions rather than true serialized snapshots, which weakens its golden-master credibility and places it last.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `checklist` | 32 | Most technically correct and disciplined answer. Correctly notes there is no OrderService in the repo and proceeds against the described scenario, avoiding fabrication. Nails every requested element:  |
  | `full` | 31 | Strong, well-structured response that fully addresses every part of the prompt. The commit-guard checklist, snapshot schema, and interface-first ABC extraction are clear and actionable. SQL and email  |
  | `checklist_v2` | 31 | Very complete, with the most detailed golden-file generation script and a concrete hash+payload DB snapshot. Dependency-depth ordering is well justified and interface-first with dataclasses is clean.  |
  | `control` | 30 | Excellent reasoning quality, with the clearest statement of the golden-master philosophy (record what happens now, even if it's wrong) and the strongest rationale for extracting persistence first (hig |
  | `retrieved` | 29 | Clear, practical, and immediately applicable, with a helpful test-selection matrix and concrete Java interface sketches. Correctly orders database first and supports it with a convincing blast-radius  |

### Task `arch-adr-scaling-ieee` (domain: Architecture & Refactoring)

**Run 1:**
- Ranking: `control > retrieved > checklist > full > checklist_v2`
- Analysis: C and A are the strongest: both are fully decision-grade with quantified forcing factors and four alternatives, but C is cleaner (table + diagram, no duplicate Decision heading) while A adds monitoring metrics yet repeats the Decision section. B has the richest narrative and strangler-pattern reasoning but is verbose and does not clearly surface its reversal triggers, whereas D is equally complete and quantified but wraps a clean ADR in extra meta-commentary. E falls clearly last because it omits the mandatory Alternatives Considered section, so it never weighs the rewrite or extraction options against each other.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `retrieved` | 33 | Thorough, quantified forcing factors, four real alternatives (including the chosen notification extraction), concrete positive/negative consequences, plus monitoring metrics and five reversal triggers |
  | `full` | 30 | Strong strangler-pattern recommendation with vivid, concrete incident context and deep trade-off analysis. However it reads more like an essay than a decision-grade ADR, and while it references 'Rever |
  | `control` | 34 | Cleanest, most decision-grade response. Quantified forcing factors with non-negotiable constraints, a concrete decision table plus ASCII architecture diagram, four well-formatted alternatives, clear c |
  | `checklist` | 32 | The ADR itself is complete and decision-grade with quantified reversal triggers and references. Sound 'sidecar process, not service' framing. Slightly undermined by the surrounding meta-commentary ('D |
  | `checklist_v2` | 21 | The core decision (monolith retained, notifications extracted as a sidecar process via LISTEN/NOTIFY) is reasonable and the reversal-trigger table is useful, but the response omits the required 'Alter |

**Run 2:**
- Ranking: `control > checklist > full > retrieved > checklist_v2`
- Analysis: A and C are the strongest: both deliver every required ADR element with quantified forcing factors and thorough alternative analysis, with A edging out C on polish (references, tables) and concision. E is complete and solid but slightly shallower. D and B both fail key requirements — B omits the mandatory alternatives and consequences sections entirely, while D is truncated and opens with an unexplained error apology — so they rank last, with D above B because it at least attempts the emphasized alternatives and consequences.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `control` | 34 | Fully decision-grade ADR with status, quantified forcing factors, clear decision, exactly three alternatives including notification-only extraction, positive/negative consequences, concrete reversal t |
  | `checklist_v2` | 21 | Decision and implementation specifics are sound, but it omits the explicitly required 'Alternatives Considered' section entirely and has no positive/negative consequences split (only Risks). Ends with |
  | `checklist` | 33 | Complete ADR with status, context, decision, four alternatives (including notification-only), positive/negative consequences, and reversal triggers. Deep, well-justified rejection of each alternative; |
  | `retrieved` | 22 | Covers decision, context, alternatives, and consequences, but the reversal triggers section is truncated mid-sentence and it opens with a spurious/hallucinated apology about file creation that was nev |
  | `full` | 31 | Complete, well-structured ADR with context, decision, three alternatives (including notification-only), consequences, risks, and reversal triggers. Concrete figures and mitigations; architecture reaso |

**Run 3:**
- Ranking: `full > checklist > control > checklist_v2 > retrieved`
- Analysis: A and B are the strongest because both are complete, decision-grade, internally consistent, and pair concrete forcing factors with tightly-scoped, measurable reversal triggers. E is nearly as complete and architecturally sharp but loses points for verbosity, invented-looking precision metrics, and a confusing AND/OR reversal-trigger structure. C is solid but undercut by DB-boundary contradictions and sprawl, while D trails mainly because it is truncated and incomplete, followed closely by a few weaker consequences.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `full` | 34 | Technically sound and tightly structured. Reaches the right decision, gives 4 alternatives including the required notification extraction, and separates consequences from risks with concrete, measurab |
  | `checklist` | 34 | Excellent. Strong problem framing (scaling-boundary vs capacity), 4 well-argued alternatives, clear chosen path, and implementation notes that make it actionable. Reversal triggers are concrete (team  |
  | `checklist_v2` | 28 | All required sections are present with quantified context and 5 reversal triggers. However, it contains internal inconsistencies (notification service 'owns its schema' yet writes flow 'through the mo |
  | `retrieved` | 23 | Correct direction and reasonable alternatives, but the response is truncated mid-sentence during the reversal-triggers section, so it fails to fully meet the instruction. Some consequences ('moral haz |
  | `control` | 31 | Very complete with a strong architecture rationale (event sourcing, materialized views, Go/Node choice) and an explicit risks/mitigation table plus JWT/TLS handling. Slightly over-verbose and introduc |

**Run 4:**
- Ranking: `control > checklist_v2 > full > checklist > retrieved`
- Analysis: C ranks first because it is the most complete, concrete, and cleanly decision-grade — correct status, explicit 'extract notifications' alternative, and hard quantitative evidence with no preamble noise. A and B are both strong architecturally but lose ground on instruction adherence (A omits extraction as an enumerated alternative and adds preamble; B prematurely marks the decision 'accepted'). D drops for its mislabeled 'sidecar' framing, while E falls to last because truncation leaves the required reversal triggers and full consequences missing.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `checklist_v2` | 32 | Technically excellent: shared-DB anti-pattern is named and mitigated (schema namespaces, LISTEN/NOTIFY, async messaging), forcing factors are quantified (40% threads vs 8% value, 3x QoQ), and reversal |
  | `full` | 32 | Complete and sound: lists extraction as an explicit alternative, provides event-sourcing/CDC design, risks, and reversal triggers. The architecture reasoning (dedicated schema, API boundary, async com |
  | `control` | 34 | Strongest overall: cleanly written with no preamble, status 'Proposed' is correct, includes 4 alternatives with extraction explicitly marked as chosen, and uses the most concrete forcing factors (supp |
  | `checklist` | 30 | Complete structure with all required sections and adds useful 'what becomes easier/harder' analysis plus compliance-aware reversal triggers (PCI/HIPAA), earning a security edge. However, the 'sidecar  |
  | `retrieved` | 29 | Architecturally strong and detailed (LISTEN/NOTIFY, RabbitMQ, private gem repo, 9-week scoped effort) with a rigorous forcing-factors table. But the response is truncated mid-'Negative' consequences,  |

**Run 5:**
- Ranking: `checklist > control > checklist_v2`
- Analysis: B and C reach the same sound decision (extract only notifications) and are both strong, but B is cleaner and more decision-grade while C is more thorough yet slightly verbose and essay-like. D is clearly weakest: its 'vertical scaling' recommendation is architecturally muddled and fails to fully satisfy the core requirement that the notification module scale independently, whereas B and C directly solve that forcing factor with a strangler extraction.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `checklist` | 33 | Technically sound with concrete forcing factors (35% queue depth, 12k WS connections, ~$500K rewrite cost). All required ADR sections present plus non-goals and references. Strangler-pattern decision  |
  | `control` | 28 | Most complete response — comparison matrix, appendices, sourced metrics, and a strong problem statement. Reasoning is excellent. Minor correctness concern: Event Sourcing + CQRS is arguably over-engin |
  | `checklist_v2` | 21 | All sections present with a diagram and measurable triggers, but the core decision is muddled: title claims 'vertical scaling' while the body proposes horizontal pod replicas, and keeping notification |

### Task `arch-form-statemachine-types-ieee` (domain: Architecture & Refactoring)

**Run 1:**
- Ranking: `full > control > checklist_v2 > checklist > retrieved`
- Analysis: B ranks first because it is the only response with a genuinely correct compile-time proof — a type-level `ValidTransition` map that yields `never` for the two invalid transitions — even though it is truncated. C is the most complete and readable, but its `assertUnreachable` exhaustiveness check is technically broken because `action` is never narrowed to `never`. A is clean and uses sound branded IDs but has a data-type mismatch and is truncated; D falls to last because it reintroduces non-null assertions and an unsafe `as unknown as UserId` cast (the exact anti-patterns the task targets), while E is slightly above D since it avoids those casts but has hard type errors and a reducer that ignores current state.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `checklist_v2` | 27 | Solid structure: correct branded IDs, discriminated unions per step, and an event reducer. But the `const _exhaustive: never = event` checks in partial switches are not actually narrowed to `never` (t |
  | `full` | 31 | The only response with a genuinely correct compile-time proof: a type-level `ValidTransition<From, E>` map that resolves invalid (step, event) pairs to `never`, directly demonstrating both bad transit |
  | `control` | 30 | Complete, clean, and the clearest presentation with concrete proof examples for both invalid transitions. Branded IDs and per-step unions are correct with no unsafe casts. However, the `assertUnreacha |
  | `retrieved` | 19 | Good phase+step architecture and branded IDs, but it reintroduces the exact anti-patterns the task says to eliminate: non-null assertions (`state.payment!`, `state.userId!`, `state.confirmation!`) and |
  | `checklist` | 21 | Correct branded IDs, step-label literals, and a reducer whose `switch (action.type)` is genuinely exhaustive. But the reducer ignores the current step entirely, so it does not actually make invalid (s |

**Run 2:**
- Ranking: `control > checklist_v2 > retrieved > checklist > full`
- Analysis: C and D stand out because they treat the invalid transitions as a type-design problem (removing GO_BACK and requiring AddressFormData/ShippingInfo on the relevant event or state), which is exactly the 'unrepresentable at compile time' proof the prompt demands; C is conceptually the strongest but has code-level compile errors, while D is slightly weaker conceptually yet more runnable. A, B, and E all still enforce the dirty/back-after-payment invariants through runtime guards, throws, or `dirty` booleans, so they demonstrate exhaustive switches and branded IDs without actually eliminating the two bug classes at the type level.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `retrieved` | 24 | Comprehensive structure with branded IDs, per-phase/per-step discriminated unions, and never-exhaustiveness in every reducer. However, the two target transitions are still prevented by runtime guards  |
  | `checklist` | 22 | Rich attempt: brand utility, per-step data, DirtyKeys mapped/conditional type, and nested exhaustive switches. But it leans on `as WizardState['dirty']`, `satisfies Omit<WizardState,'dirty'>`, and `_e |
  | `control` | 30 | Best conceptual match to the prompt: it removes GO_BACK from the event set entirely and makes MOVE_TO_PAYMENT require `address: AddressFormData`, so both invalid transitions are genuinely unrepresenta |
  | `checklist_v2` | 27 | Solid, likely-compilable implementation: unique-symbol branded IDs, per-step union where later steps require earlier data as required (not optional) fields, string-tagged events, and a switch with tra |
  | `full` | 19 | Clear narrative and branded IDs, but it keeps a `stepDirty: boolean` on every step state, so 'dirty' is always representable and the dirty transition is blocked only by a runtime `throw`. Back-navigat |

**Run 3:**
- Ranking: `control > retrieved > full > checklist_v2 > checklist`
- Analysis: A and B are the strongest, both delivering complete before/after models with correct branded IDs and discriminated unions; A edges out B because it avoids `as` casts in the transition logic and frames transitions as compile-time unrepresentability, whereas B falls back to a runtime `if (state.dirty) return null` guard that does not satisfy the 'prove at compile time' requirement. D distinguishes itself with an explicit `from`/`to` transition graph but ships a broken never-check (asserting `never` on a variable that is still the full union), while C relies on runtime guards and pervasive casts plus unused helper types. E ranks last because its heavy `as WizardState` casts and placeholder values erase type safety, and its state machine still allows back-navigation after payment, directly contradicting one of the two invalid transitions that were supposed to be made unrepresentable.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `control` | 24 | Most exhaustive enumeration of all required pieces (branded IDs, per-step unions, events, phase-based reducer, never-check) and avoids `as`/`any` in the transition logic. However, it maintains two par |
  | `retrieved` | 22 | Clean, readable before/after with correct unique-symbol branding and a coherent step-discriminated union. But the generic `WizardAction<Next>` is collapsed when used, and — critically — 'submitting wh |
  | `checklist_v2` | 17 | Covers all sections but the design is runtime-guard driven (`if (state.step.kind !== ...) throw`), uses many `as` casts (e.g. `merged as PersonalInfoData`), declares unused unique symbols while actual |
  | `full` | 20 | Has a genuinely interesting idea — encoding transitions via `from`/`to` literal-number fields — and clean branded IDs. But the exhaustiveness check is technically broken: it switches on the string ``  |
  | `checklist` | 15 | Uses `as WizardState`/`as StepAddress`/`as OrderId` casts on nearly every return plus placeholder values (`"" as StepId`), which defeats the whole point of the exercise. The `completedSteps` tuple ide |

**Run 4:**
- Ranking: `retrieved > checklist_v2 > checklist > full > control`
- Analysis: A leads because it most faithfully renders the requested pattern — correct branding, per-step discriminated unions, and explicit no-back-actions — despite a BaseState `step: never` compile bug; B is close but its @ts-expect-error proofs are mechanically wrong and its reducer is over-verbose. D falls behind because `Partial` never distinguishes dirty from complete and the reducer silently no-ops instead of proving transitions unrepresentable, while E and C are weaker on correctness — E through typos and a generic-interface (not true union) design, and C through a fundamentally invalid `unique symbol` brand type plus runtime throws instead of compile-time guarantees.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `retrieved` | 27 | Cleanest overall structure with correct branding, per-step data requirements, and a discriminated union keyed on `step`. However, `BaseState` declaring `step: never` then overriding it in derived inte |
  | `checklist_v2` | 24 | Correct branding and a thorough before/after. The @ts-expect-error 'proof' is flawed because it marks reachable, valid action cases as unreachable (unused-directive compile errors), and the state-firs |
  | `control` | 16 | The branded-type helper `T & { __brand: unique symbol & { _: B } }` is invalid TypeScript (a bare `unique symbol` cannot be used as a type reference), and `const uid: UserId = "user-42"` is wrongly la |
  | `checklist` | 21 | Branding is correct (`K & { __brand: T }` with `typeof UserId`), but the state uses `Partial<T>` everywhere, so 'dirty' vs 'complete' is never actually modeled — undermining the central 'submit while  |
  | `full` | 17 | Ambitious type-level metaprogramming but riddled with typos and self-corrections: `ToStep<'profile:submit'>>` (double bracket) and `AllowedFromEvents` vs `AllowedFromSteps` naming mismatch, plus a red |

**Run 5:**
- Ranking: `full > checklist_v2 > retrieved > control > checklist`
- Analysis: D ranks first because its parameterized conditional action type `Action<S>` is the only design that truly makes invalid transitions unrepresentable at compile time, despite several implementation bugs; A is second as the most complete and cleanly explained answer, though its `submittable` boolean flags are a weaker encoding and its proof is truncated. E, C, and B all fall back to runtime `throw` guards (and B additionally over-engineers broken, unused type utilities), so they fail the central 'prove unrepresentable at compile time' requirement; C also introduces a raw-card-number PCI security regression and demonstrably non-compiling `never` assignments, while B's `UnreachableUnion` and `WithFields` helpers are internally incoherent.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `checklist_v2` | 28 | Solid, well-commented before/after with branded IDs (factory + validation), per-step discriminated unions, and event-driven transitions. Minor correctness issues: StepToken is declared as both a `cons |
  | `checklist` | 18 | Covers all requested elements but with serious type-level flaws: `WithFields`/`HasAllKeys` are broken, unused abstractions; `Brand` uses `__brand` while separately declaring unused unique symbols; `Un |
  | `control` | 19 | Branded IDs and discriminated unions are on the right track, but the exhaustiveness proof is incorrect: `const _exhaustiveCheck: never = state.step` assigns a string-literal union to `never` and would |
  | `full` | 28 | The conditional action type `Action<S extends WizardState>` is the strongest architectural approach and is the only response that genuinely makes invalid transitions unrepresentable (e.g., no `go-back |
  | `retrieved` | 21 | Readable predicate-guard style with branded IDs, per-step unions, and PCI-safe `cardToken`. But the core requirement is not met: the transition function relies on `throw new Error` runtime guards, so  |

### Task `devops-ml-docker-ieee` (domain: DevOps & Cloud)

**Run 1:**
- Ranking: `full > checklist > checklist_v2 > control > retrieved`
- Analysis: B leads because it produces a coherent, mostly-buildable multi-stage image with correct non-root ownership and an actual hash-pinning mechanism, even if the hash value is a placeholder. A has the strongest architecture/cache reasoning but loses points for a false hash claim, a likely-invalid apt pin, and harmful .dist-info deletion. E is clean and buildable yet drops the mandatory pinned-hash requirement, while C and D are technically broken — C via shell/`--require-hashes` misuse and D via a nonexistent base image, musl-vs-manylinux torch incompatibility, and a non-functional scratch final stage.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `checklist` | 26 | Strong resolver/runtime separation and clear cache-ordering rationale, but the 'pinned hash' claim is false (no --hash/--require-hashes appears), apt pins curl=8.5.0-2/tini=0.19.0-3 likely don't exist |
  | `full` | 27 | Clean multi-stage with proper non-root ownership (chowns the venv too), healthcheck, dockerignore, and runtime-only secrets. The hash pinning mechanism is present (--require-hashes and --hash placehol |
  | `control` | 18 | Attempts all requirements but is broken in practice: process substitution `<( ... )` fails under /bin/sh, `pip freeze` output is passed to `--require-hashes` (which is not a hash file), and there is c |
  | `retrieved` | 12 | Fatal design errors: `python:${ALPINE_VERSION}-slim` resolves to a nonexistent `python:3.20-slim`, the final stage uses `FROM scratch` while copying arbitrary Alpine /usr/lib and /bin (no libc loader  |
  | `checklist_v2` | 25 | Most complete set of deliverables (Dockerfile, requirements, dockerignore, multiple compose files, env example) and the Dockerfile is largely buildable, but it completely omits pinned hashes (a core r |

**Run 2:**
- Ranking: `checklist > full > retrieved > checklist_v2 > control`
- Analysis: E is the most complete and technically sound response, with correct hash pinning, clean wheels isolation, and no critical defects. B has a strong, well-reasoned architecture but is undermined by a runtime-breaking PYTHONPATH omission and the wrong OpenMP package, while D runs but fails its own claim of pinned hashes and isolates torch poorly. C and A are the weakest: C uses a nonexistent torch-cpu package with invalid hash syntax, and A contains invalid self-referencing COPY plus a non-root pip install that would fail outright.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `control` | 19 | Provides all the artifacts but is technically broken: the `COPY --from=wheels /wheels /app/wheels` self-references the stage being built (invalid), installing pip packages as `USER appuser` into root- |
  | `full` | 26 | Clean, well-structured response that hits nearly every requirement and reasons clearly. However, it has two runtime-critical bugs: `pip install --prefix=/build/.local` puts site-packages on a path Pyt |
  | `checklist_v2` | 21 | Covers the deliverables and gives a detailed justification table, but key details are wrong: it installs a nonexistent `torch-cpu` package name (correct is `torch==...+cpu` from the pytorch CPU index) |
  | `retrieved` | 21 | The direct torch install (`torch==2.6.0+cpu` from the extra-index) would actually run, but the response misleadingly claims hash pinning while the Dockerfile never passes `--require-hashes` or `--hash |
  | `checklist` | 30 | The strongest and most coherent solution: correct CPU-only torch index, `--require-hashes`/`--hash` pinning, clean three-stage wheels isolation, non-root user with `--chown`, sensible /healthz HEALTHC |

**Run 3:**
- Ranking: `full > checklist > retrieved > control > checklist_v2`
- Analysis: B is best because it combines a clean, idiomatic wheel-builder/dep-installer/runtime split with correct cache-first layer ordering and thorough reasoning, whereas A's --prefix approach is more fragile and duplicates the torch install. E is architecturally sound but is undercut by a broken shell-variable HEALTHCHECK in exec form and weaker adherence to the hash-pinning requirement. C contains outright correctness failures (source-building torch, conflicting port/healthcheck, truncated output), and D provides no deliverable at all, placing them clearly at the bottom.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `checklist` | 27 | Meets most structural requirements (multi-stage, non-root with chown, HEALTHCHECK, .dockerignore, no secret ENV) and has excellent justifications. However, the 'pinned hashes' requirement is only reco |
  | `full` | 32 | Cleanest and most idiomatic design: dedicated wheel-builder stage with pip wheel/pip download, cache-optimized layer ordering (torch first), non-root user created before copies, sensible HEALTHCHECK,  |
  | `control` | 15 | Multiple real errors: 'pip wheel --no-binary :all:' would attempt a torch source build (impractical/incompatible with manylinux wheels), the fallback pip install has invalid/conflicting syntax, and th |
  | `checklist_v2` | 8 | Provides no Dockerfile, no .dockerignore, and no justification. It only references a 'previous response' that is not actually present, so it fails to deliver any of the requested artifacts or analysis |
  | `retrieved` | 29 | Solid, conventional multi-stage build with clean wheel isolation, non-root user, good .dockerignore, and strong security posture. However, the HEALTHCHECK uses exec form with a shell variable (${PORT: |

**Run 4:**
- Ranking: `full > checklist_v2 > control > checklist > retrieved`
- Analysis: E and D are clearly the strongest: both use a glibc base that is actually compatible with PyTorch CPU wheels, implement proper multi-stage isolation, non-root users, and solid .dockerignore/secret handling. E edges out D on maintainability and reasoning because D invents a non-existent `ziphint` tool and contradicts its own 'source last' cache rule in the actual file, whereas E is internally consistent with no fabricated commands. A, C, and B each contain at least one build-breaking flaw — A's frozen.txt reinstall lacks the PyTorch index URL, C's `--no-binary :all:` forces a source build and references requirements.txt before copying it, and B is fatally undermined by Alpine/musl incompatibility, malformed wheel URLs, and gosu misuse — with the common shared weakness that none of the five responses actually implements true hash pinning despite the requirement.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `control` | 22 | Solid multi-stage structure and cache-ordering rationale, but contains a build-breaking bug: `pip freeze > frozen.txt` emits `torch==2.4.1+cpu`, then `pip install -r frozen.txt` runs without the PyTor |
  | `retrieved` | 15 | Several fatal technical errors make this image unbootable: Alpine (musl) has no official PyTorch CPU wheels, so `pip install` of torch fails or forces a source build; the wheel URL is malformed (`cp31 |
  | `checklist` | 15 | Uses a correct glibc base and non-root user, but `pip wheel --no-binary :all:` forces source compilation of torch (impractical and effectively broken), and the runtime `pip install -r requirements.txt |
  | `checklist_v2` | 25 | Best security posture overall (read_only, cap_drop, no-new-privileges, non-root, no secrets) and a correct glibc base with a three-stage split. However, it fails to pin hashes (only version pins), inv |
  | `full` | 26 | Cleanest, most coherent implementation: correct glibc base with an explicit, accurate warning against Alpine/musl, proper source-last layer ordering, no fabricated tools, and a strong secret-managemen |

**Run 5:**
- Ranking: `full > control > checklist > retrieved > checklist_v2`
- Analysis: A ranks first because it delivers the cleanest, most coherent multi-stage architecture with the correct Debian base, non-root ownership, and clear layer justifications, despite a silent wheel-build failure (`|| true`) and hash pinning that is referenced rather than enforced. D is a close second with stronger hash/secret details but is held back by a missing runtime `curl` and an install command that never actually enforces the hashes it advertises. E's fragile venv-copy approach, C's missing hashes plus redundant runtime re-install, and B's fatal Alpine/musl incompatibility with PyTorch put them progressively lower.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `full` | 26 | Strong multi-stage split (base/build/runtime), correct Debian slim base for torch, non-root with chmod 555, sensible HEALTHCHECK, good layer ordering and thorough .dockerignore/compose. Weakened by `| |
  | `checklist_v2` | 21 | Covers all requirements structurally and justifies layers well, but the runtime uses `python:3.12-alpine3.20`, and PyTorch ships no musl wheels, so `pip install torch` cannot work without a source com |
  | `retrieved` | 18 | Correct Debian base, non-root, and HEALTHCHECK, but misses pinned hashes entirely, has a `grep -ivv` typo in the fragile torch extraction, and re-runs `pip install -r requirements.txt` in the runtime  |
  | `control` | 26 | Good Debian multi-stage design with pinned hashes shown, BuildKit secret mounts, non-root, and sensible healthcheck values. However, the runtime HEALTHCHECK calls `curl` but curl is only installed in  |
  | `checklist` | 19 | Uses a viable Debian base, non-root, tini, and a working healthcheck, but the venv `site-packages` copy with hand-set PYTHONPATH/LD_LIBRARY_PATH is brittle, copied `bin/*` scripts retain `/opt/venv/bi |

### Task `devops-api-k8s-ieee` (domain: DevOps & Cloud)

**Run 1:**
- Ranking: `retrieved > checklist > checklist_v2 > full > control`
- Analysis: B and C are the clear leaders and near-tied: B has the most correct and best-reasoned probe handoff (200s/45s/15s) with exemplary averageValue math, while C has the strongest architecture/security via the Secrets Store CSI driver and better p99 CPU headroom (250m/1000m vs B's 100m/250m). B edges ahead overall because its probe thresholds are safer and its reasoning is more precise, though C's only real flaws are overly aggressive liveness/readiness windows and a minor selectPolicy comment. A is solid but incomplete (truncated HPA and a missing preStop despite referencing one), D is weakened by a TCP-only startup probe and slow detection, and E is the weakest due to ':latest', the 58s preStop sleep, and readiness threshold 1.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `checklist_v2` | 27 | Probe arithmetic is sound (80s startup, 15s liveness, 15s readiness), resources (250m/1000m) and rolling update (maxUnavailable 0) are correct, and the drain/probe explanation is clear. However the HP |
  | `retrieved` | 33 | All three required manifests are complete and technically correct: HPA v2 with CPU (60%) + custom Pods metric, full scaleUp/scaleDown behavior, PDB minAvailable 2, correct rolling update, and the star |
  | `checklist` | 32 | Best secret-store fidelity: uses the Secrets Store CSI driver with a full SecretProviderClass, which is the literal 'cluster secret store mounted as files' requirement. Architecture and security are t |
  | `full` | 26 | Complete enough (Deployment, ServiceAccount, HPA, PDB, drain explanation), with good hardening (seccomp, non-root, read-only FS). The main correctness gap is the startup probe being a tcpSocket check, |
  | `control` | 22 | Several anti-patterns undermine it: image tag ':latest', a 58s preStop sleep (delays every rollout termination), readiness failureThreshold: 1 (single probe failure drops the pod from endpoints, flapp |

**Run 2:**
- Ranking: `full > retrieved > checklist_v2 > checklist > control`
- Analysis: The key differentiators are secret handling, manifest correctness, and drain-sequence accuracy. A wins by using the CSI secrets-store driver (the only true 'cluster secret store' answer) with clean probe arithmetic and an accurate termination narrative, while D is a close second but errs on preStop/SIGTERM ordering and uses native Secrets. E and C both contain one fatal manifest defect (E's unreachable initContainer curl vs C's duplicate volumes key and 300s/self-contradictory startup explanation), and B ranks last because it directly violates the 'files not env' requirement with a secretKeyRef env var and uses :latest plus only 2x CPU headroom.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `full` | 34 | Strongest overall: CSI secret-store driver mounted as files (best match for 'cluster secret store'), clean probe separation with correct startup-vs-liveness reasoning (initialDelay 0), 3x CPU headroom |
  | `control` | 23 | Direct instruction violation: DB_PASSWORD is injected via secretKeyRef into an env var despite the explicit 'files not env' requirement, and it mixes native Secrets with env rather than a cluster secr |
  | `checklist` | 26 | Good security posture (seccomp, projected secret files, GOMAXPROCS) and correct intent, but a structural YAML defect (duplicate 'volumes:' key) and a self-contradictory startup explanation: it claims  |
  | `retrieved` | 29 | Solid manifests with 4x CPU headroom (best p99 margin), 40s startup budget with real safety margin, and both minAvailable and maxUnavailable PDB variants. Uses native Secret files rather than a cluste |
  | `checklist_v2` | 27 | Clean manifests, good probe separation, proper PDB, and valuable Go shutdown code (srv.Shutdown). However, a fatal architectural bug: the cache-warmup initContainer curls localhost:8080/warm, but init |

**Run 3:**
- Ranking: `checklist_v2 > checklist > control > retrieved > full`
- Analysis: A and B are clearly the top two: both deliver production-grade manifests with correct probe arithmetic and graceful-drain reasoning, with A edging ahead on metric correctness (Pods vs External for queue depth), image digest pinning, and broader RBAC/ConfigMap/anti-affinity coverage, while B edges ahead on fully visible deliverable completeness. D is strong on the secrets-store implementation but undermined by a :latest tag, a missing securityContext, and an incorrect PDB equivalence claim, while E falls behind due to a critical preStop deadlock that breaks graceful drain. C is non-functional, delivering no actual manifests or explanations.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `checklist_v2` | 33 | Strongest technical content: correct Pods-type custom metric (not External), digest-pinned image, anti-affinity, ConfigMap/RBAC separation, emptyDir cache/tmp, and correct probe arithmetic. Slightly m |
  | `checklist` | 33 | Delivers all three manifests in full plus a clear probe-arithmetic table and termination sequence. Security is excellent (readOnlyRootFilesystem, drop ALL, runAsNonRoot, no SA token). Minor correctnes |
  | `full` | 7 | Not a real answer — it is a continuation/confirmation artifact that claims the solution was already delivered but shows no manifests, no arithmetic, and no drain sequence. Fails every substantive requ |
  | `control` | 25 | Best secrets approach (CSI Secrets Store driver + SecretProviderClass directly matching 'cluster secret store mounted as files'). But it uses a :latest image, models per-replica queue depth as an Exte |
  | `retrieved` | 22 | Has good pieces (immutable image, Pods metric type, minAvailable: 2 PDB, file-mounted secrets, strong hardening). But the preStop hook deadlocks: it waits for the Go process to exit before SIGTERM is  |

**Run 4:**
- Ranking: `checklist_v2 > full > retrieved > checklist > control`
- Analysis: The decisive split is the rolling-update strategy: E, A, and D use maxSurge:1 + maxUnavailable:0 (correct, zero-downtime), while B and C use maxSurge:0 + maxUnavailable:0, which Kubernetes rejects and would deadlock deploys — a fatal correctness failure. Among the correct three, E edges out A on security (explicit non-root UID, sealed-secrets note, anti-affinity) and completeness, and A edges out D via CSI secret mounting and full HPA behavior tuning; D is solid but thinner on behavior config and preStop. B ranks above C because C compounds the same strategy bug with ':latest', deprecated alpha annotations, no securityContext, and arithmetic errors.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `full` | 33 | Correct maxSurge:1/maxUnavailable:0 strategy, valid autoscaling/v2 HPA with CPU + External queue-depth metric, valid PDB, correct probe arithmetic (startup 200s covers 20s warmup with headroom, livene |
  | `checklist` | 21 | Fatal error: maxSurge:0 + maxUnavailable:0 is rejected by the API server (may not both be 0) and would block any rolling update, contradicting the zero-downtime claim. Also places selectPolicy at beha |
  | `control` | 19 | Same fatal maxSurge:0 + maxUnavailable:0 deadlock as B. Adds image ':latest' (non-immutable), mixes deprecated autoscaling alpha annotations with the v2 spec (confusing/redundant), references an undef |
  | `retrieved` | 28 | Correct maxSurge:1/maxUnavailable:0, valid probes (50s/30s/10s), valid HPA (CPU + Pods queue-depth) and PDB. Solid security (non-root, read-only fs, drop ALL, no SA token). Falls short of A/E by omitt |
  | `checklist_v2` | 34 | Best overall. Correct maxUnavailable:0/maxSurge:1, valid autoscaling/v2 HPA with CPU + Pods queue-depth and stabilization tuning, valid PDB. Most thorough: adds Service, ConfigMap, pod anti-affinity,  |

**Run 5:**
- Ranking: `full > checklist > checklist_v2 > control > retrieved`
- Analysis: A edges out C because it pairs a correct maxUnavailable:0 drain with a more conservative 45s grace period, minReadySeconds, a fuller HPA (behavior policies plus a memory metric), and the most thorough probe arithmetic, even though C is stronger on the explicit preStop hook. C clearly beats B on the zero-drop requirement because B's maxUnavailable:1 and missing preStop undercut the drain guarantee that C nails with preStop + maxUnavailable:0. B remains above D and E on overall cleanliness and completeness despite its drain weakness, while D's factual RBAC/ConfigMap confusion and E's invalid probe field plus throttling-prone CPU sizing push them to the bottom.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `full` | 35 | Correct maxUnavailable:0 + terminationGracePeriodSeconds:45 for zero-drop drain; probes use distinct /healthz (startup+liveness) and /readyz paths with a 180s startup budget that clearly covers the 20 |
  | `checklist_v2` | 29 | Most comprehensive artifact set (adds Ingress, ConfigMap, anti-affinity, RBAC) and strong probe arithmetic with a timing diagram. However, rollingUpdate uses maxUnavailable:1 instead of 0, which weake |
  | `checklist` | 32 | Best drain execution: maxUnavailable:0 combined with an explicit preStop sleep 5 to allow endpoint propagation before draining, plus a Go /readyz snippet showing correct warmup gating. Probes, HPA (CP |
  | `control` | 25 | Gets the core drain strategy right (maxUnavailable:0, terminationGracePeriodSeconds:45) and offers the best resource sizing for throttling avoidance (500m/1G requests/limits). CSI SecretProviderClass  |
  | `retrieved` | 24 | Strong security (seccomp RuntimeDefault, non-root, readOnlyRootFilesystem, projected volumes for file-mounted secrets) and maxUnavailable:0 + terminationGracePeriodSeconds:60. But it includes an inval |

### Task `devops-gha-pipeline-ieee` (domain: DevOps & Cloud)

**Run 1:**
- Ranking: `control > checklist_v2 > retrieved > full > checklist`
- Analysis: A ranks first because its lockfile-based cache-key design is the most accurate and thoroughly justified and its path-filtered CI matrix is largely correct, despite a sharding/coverage error and a useless build-cache key. C and D are close behind on structure and intent, but C's fundamental `changed_apps` output bug and D's `has_packages`/`--filter=[HEAD~1]` bugs break the path-filtering core, with C's clearer multi-file scope edging out D. B falls to fourth due to the `pull_request_target` security/correctness flaw, and E is clearly worst because it produces no actual workflow or explanation at all.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `control` | 23 | Best cache-key reasoning of the set (three-tier lookup, lockfile-only primary key, rationale for build cache). Path-filtering outputs and per-app Node 20/22 x shard-4 matrix are sound. Correctness dro |
  | `full` | 13 | Uses `pull_request_target` with a default `checkout`, which both fails to test the PR's actual code and exposes a privilege-boundary anti-pattern. Test job is not path-filtered, `download-artifact` is |
  | `checklist_v2` | 20 | Cleanest scope signaling (explicitly lists ci/deploy/release/CODEOWNERS) and solid cache-key explanation, but the core path-filtering is broken: it references a `changed_apps` JSON output that dorny/p |
  | `retrieved` | 18 | Thoughtful Turbo-based per-app/per-lib path filtering, but several bugs undermine it: `has_packages` is referenced without being emitted, the test command uses `--filter=[HEAD~1]` (ignoring the path-f |
  | `checklist` | 7 | Not an answer: it merely asserts that a prior response was complete and restates the requirements. It delivers no YAML, no cache-key design, and no OIDC trust configuration, so it fails every substant |

**Run 2:**
- Ranking: `checklist > full > retrieved > checklist_v2 > control`
- Analysis: D and E are clearly the strongest, delivering valid, maintainable YAML with correct path filters, lockfile-keyed caching, and a correct Node 20/22 x 4-shard test matrix, whereas A and C contain broken GitHub Actions expressions that would fail to run. B has the best cache-key reasoning but pairs it with brittle, buggy change detection. All five responses are truncated before fully delivering the preview-environment, OIDC-gated production deploy, SBOM/attestation, and merge-queue requirements, so no response fully satisfies the complete task.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `checklist_v2` | 14 | Uses dorny/paths-filter correctly and sketches a staged job graph, but the YAML contains invalid expressions: hashFiles in top-level env, impossible output indexing (outputs[format(...)]), needs.*.res |
  | `retrieved` | 15 | Cache-key design explanation is the strongest and most detailed across responses (lockfile hash, store, per-package build). However the change-detection shell script is convoluted and buggy, uses a no |
  | `control` | 12 | Correctly observes the target repo is not a TS monorepo and supplies generic templates, but the delivered YAML is heavily broken: `needs.*.result`, `contains(github.event.head_commit.modified, ...)`,  |
  | `checklist` | 24 | Cleanest and most syntactically valid YAML: correct dorny filters, cache keys on lockfile hash, proper Node 20/22 x shard 1-4 test matrix, integration tests with services, and a well-structured job gr |
  | `full` | 23 | Valid, maintainable YAML using paths-filter, lockfile-hash caching, Turborepo, and a correct Node 20/22 x 4-shard matrix. The architecture overview names all required components (preview, OIDC, SBOM,  |

**Run 3:**
- Ranking: `full > checklist > control > checklist_v2 > retrieved`
- Analysis: E and B are the clear leaders because they actually produce workflow YAML and explain the cache/OIDC design, with E edging out B on security depth and a correct, concrete trust policy despite a small hashFiles bug. C is directionally reasonable but undermined by a probably-broken fromJSON/paths-filter assumption and missing deploy/OIDC/release content. D only asserts completeness without showing any files, and A provides nothing but placeholders, placing both at the bottom for failing the deliverable requirement.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `retrieved` | 7 | Delivers no YAML, no cache-key explanation, and no OIDC trust config. It only claims the work is done and lists placeholders. Fails every substantive requirement of the task. |
  | `checklist` | 30 | Strong, concrete multi-file design with real path filters, a Node/shard matrix, merge_queue, and a verify-checklist status sink. Slightly flawed by caching node_modules alongside the pnpm store, an ov |
  | `control` | 22 | Provides real YAML and a thoughtful path-filtered matrix, but relies on dorny/paths-filter emitting JSON arrays (fromJSON on outputs that are normally booleans), which is likely broken. Deploy, OIDC,  |
  | `checklist_v2` | 16 | Only a bulleted summary asserting the solution is complete. No YAML, no cache-key design, and no OIDC trust policy are actually shown. The conceptual coverage is decent, but it does not deliver the re |
  | `full` | 30 | Delivers real workflow YAML plus detailed, accurate cache-key and OIDC trust-policy explanations. The environment-gated STS trust policy and least-privilege role setup are correct and concrete. Minor  |

**Run 4:**
- Ranking: `control > retrieved > checklist_v2 > checklist > full`
- Analysis: D leads on the most demanding criteria — OIDC trust configuration, deploy gating, SBOM/attestation, and merge-queue enforcement — and reasons through the full lifecycle, while A delivers the cleanest, most-correct CI YAML and the clearest lockfile-keyed cache explanation. C's cache-key philosophy is sound but its matrix expressions are syntactically broken, E's build-cache keying is circular and not lockfile-based, and B combines a deprecated `set-output` pattern with a malformed build matrix, leaving it least correct.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `retrieved` | 26 | Cleanest, most-parseable visible YAML with a clear three-tier cache table keyed on the lockfile and per-app build isolation. Main flaw is `continue-on-error: true` on the test job without an aggregati |
  | `full` | 19 | Scope-detection via git diff is functional and the Node 20/22 x 4-shard test matrix is correct, but the response uses the deprecated `::set-output` command and the build matrix contains a malformed/ga |
  | `checklist_v2` | 21 | Strong cache-key philosophy (three namespaces with lockfile hash and progressive restore keys) and a logical lint/build/test/type-check structure. However, the workspace matrix uses a garbled `fromJSO |
  | `control` | 30 | The strongest treatment of the hardest requirements: OIDC trust-chain conditions (audience, environment tag, ref match), preview vs production role separation, SBOM + cosign/SLSA attestation, and merg |
  | `checklist` | 22 | Includes a preview workflow with OIDC (`id-token: write` + `aws-actions/configure-aws-credentials`) and a per-app CI structure, but the build cache keys on `github.sha`/`hashFiles('.cache/**')` rather |

**Run 5:**
- Ranking: `checklist_v2 > retrieved > full > checklist > control`
- Analysis: C wins on reasoning quality and instruction adherence because it actually delivers the explicitly requested cache-key and OIDC trust explanations at depth, with GCP+ AWS conditional IAM policies, while most others truncate before those sections. A beats E on security (safe pull_request trigger vs pull_request_target) despite E's better maintainability, and B/D trail because their matrices are fragile and they either mishandle fork safety or under-address the OIDC/release/merge-queue deliverables.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `retrieved` | 24 | Solid CI structure and a clear cache-key table, but has real YAML/expression errors (strsplit is not a valid GitHub expression function, awkward '1/4' shard values) and the path filter only distinguis |
  | `checklist` | 18 | Per-app path filtering is good, but using pull_request_target with a head.sha checkout is a serious fork-safety vulnerability, the matrix is overloaded with a 'cond' dimension and object-based exclude |
  | `checklist_v2` | 31 | Clearly the strongest explanation: a two-layer cache-key derivation with worked examples, and a complete OIDC trust configuration for both GCP and AWS with conditional bindings and branch/env gates. S |
  | `control` | 20 | Correctly notices the repo is not a TS monorepo, and has a reasonable cache-key explanation, but the test matrix uses a 'cond' field plus object-based excludes that are likely invalid in GitHub Action |
  | `full` | 24 | The reusable-workflow split is the most maintainable and maps cleanly to per-app builds/tests, and it explicitly attempts preview, release, and merge-queue wiring. But it also uses pull_request_target |

### Task `db-analytics-query-ieee` (domain: Databases & Persistence)

**Run 1:**
- Ranking: `retrieved > control > checklist > full > checklist_v2`
- Analysis: E is the most technically sound — it reconstructs the actual plan with concrete numbers, tunes autovacuum correctly, and models the window partition so the composite index truly avoids the sort — but it cuts off before the rewritten query. A covers every requested deliverable yet is undermined by invalid SQL (REFRESH TABLE, an index hint, a Chinese-character identifier), while C is complete and clean but trips on the '9,600 partitions' arithmetic and partitions by user_id (so its index does not actually eliminate the sort). B's rewrite misplaces LIMIT before ranking and gives a wavering partitioning verdict, and D is a non-answer with no technical substance.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `control` | 25 | Complete coverage of all five deliverables with a clear index decision tree and correct column-order reasoning. However, it contains invalid SQL (REFRESH TABLE events, a Chinese-character identifier i |
  | `full` | 23 | Gets the composite index and stats fixes roughly right and addresses every section, but the rewritten query is logically flawed (LIMIT inside the CTE truncates before ranking, and PARTITION BY user_id |
  | `checklist` | 24 | Complete with a clean final query and correct 'probably not yet' partitioning verdict, but it contains a clear math error (9,600 monthly partitions), presents an invalid WHERE-window query before self |
  | `checklist_v2` | 9 | A stub/meta response with no actual technical content — only bullet-point claims that everything was already covered. Fails every substantive requirement of the task. |
  | `retrieved` | 26 | Most rigorous and technically accurate diagnosis: reconstructs a realistic EXPLAIN ANALYZE with concrete figures, correctly tunes autovacuum_analyze_scale_factor and SET STATISTICS, and models the win |

**Run 2:**
- Ranking: `checklist_v2 > retrieved > control > checklist > full`
- Analysis: A, B, and C all deliver legitimate, technically sound answers, but they differ mainly in depth and emphasis: A is the most comprehensive (adding work_mem/parallelism config and keyset pagination), B is the cleanest and best-organized with a phased execution plan, and C contributes the strongest single diagnostic idea (multivariate MCV statistics) but over-commits to partitioning and leaves the rewritten query incomplete. D and E are not real answers — both claim completeness or defer further without ever producing the requested node-by-node analysis, index strategy, estimate fix, partitioning decision, or rewritten query, which is why they collapse to 1s and rank last.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `checklist_v2` | 32 | Most complete answer: node-by-node table, composite/partial/covering index rationale with correct column-order logic, conditional partitioning verdict, estimate fixes, config tuning (work_mem for the  |
  | `retrieved` | 28 | Clean, well-structured answer covering every requested section with a strong CTE/materialization table and phased execution order. Solid three-layer estimate fix and balanced partitioning stance. Slig |
  | `control` | 26 | Strong diagnosis with a concrete annotated EXPLAIN ANALYZE and a valuable `CREATE STATISTICS (mcv)` addition for correlated columns, plus partition automation script. Partitioning verdict leans too ab |
  | `checklist` | 7 | Non-answer: merely asserts the response is complete and lists what it 'covered' without providing any diagnosis, index strategy, estimate fix, partitioning decision, or rewritten query. Fails every su |
  | `full` | 7 | Non-answer that offers to elaborate on an analysis that was never actually delivered. No technical content whatsoever, so it fails the task on all criteria regardless of its polite framing. |

**Run 3:**
- Ranking: `control > checklist_v2 > full > checklist > retrieved`
- Analysis: B edges out A because it nails the two most subtle points—PG12+ CTE inlining semantics and CREATE STATISTICS (mcv) for correlated tenant_id/event_type estimates—even though A is more complete overall. D and C both make an invalid partial-index mistake (NOW() vs subquery) and miss or misuse a key detail: D omits extended statistics while C states CTE behavior backwards, so D ranks just ahead of C. E falls last because, despite good structure, it contains multiple fabricated PostgreSQL syntax constructs and gets the default CTE materialization behavior exactly wrong.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `checklist_v2` | 29 | Very thorough node-by-node causal chain and strong composite-index reasoning. Minor technical issues: the query uses a plain CTE while the explanation implies materialization (PG12+ defaults to inlini |
  | `control` | 28 | Strongest on the two trickiest points: correctly states PG12+ CTE inlining semantics and correctly prescribes CREATE STATISTICS (mcv) for correlated equality predicates. The rewrite changes RANK to RO |
  | `checklist` | 24 | Gets extended statistics right and parameterizes the query, but contains two clear factual errors: a partial index predicate using a subquery (not allowed in PostgreSQL) and a backwards claim that CTE |
  | `full` | 27 | Correct composite index, correct CTE materialization semantics, and good partitioning decision framework with parameterized query. Flaws: the partial index uses NOW() (non-immutable, disallowed in ind |
  | `retrieved` | 20 | Covers every requested topic and the core index order is right, but it is factually wrong on the materialization question: it says CTEs are optimization fences by default in PG12+, and it cites non-ex |

**Run 4:**
- Ranking: `full > checklist_v2 > checklist > retrieved > control`
- Analysis: B ranks first because its index, estimate fix, partitioning verdict, and rewritten query are all correct and coherent, with no SQL errors and a clear CTE-materialization explanation. C is a close second on technical accuracy and reasoning but risks missing the explicitly required rewritten query. E and A are both complete but flawed — E by incorrect extended-statistics syntax and a convoluted lateral query, A by invalid `WHERE RANK() <= 10` SQL and muddled join-before-ranking logic — while D trails because it reverses the equality/range column order in its primary index and prematurely advocates monthly partitioning over index/statistics fixes.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `retrieved` | 26 | Covers every requested point thoroughly (node-by-node plan, composite/partial/covering index rationale, stats, partitioning, rewritten query, materialized view). However the rewritten query is invalid |
  | `full` | 32 | Strongest and most technically sound response. Correct composite+INCLUDE index `(tenant_id, event_type, created_at DESC) INCLUDE (user_id)` with proper equality-first-then-range ordering, correct esti |
  | `checklist_v2` | 28 | Excellent, clean index strategy (composite vs single vs partial vs covering with a cost/benefit discussion), correct column ordering, solid statistics fix with a useful monitoring query, and a well-re |
  | `control` | 18 | Contains a key indexing error: the 'primary fix' recommends `(tenant_id, created_at)` with `event_type` relegated to INCLUDE, which puts the range column ahead of an equality column and forces a scan  |
  | `checklist` | 27 | Complete and insightful — correct index `(tenant_id, event_type, created_at DESC)`, correct column-order reasoning, good partial/covering coverage, and it uniquely offers the LATERAL + LIMIT top-N pat |

**Run 5:**
- Ranking: `checklist > retrieved > full > checklist_v2 > control`
- Analysis: A leads because it is the only response that fully and accurately delivers every requested artifact — node-by-node diagnosis, the three index shapes with correct column-order reasoning, the estimate fix, a reasoned partitioning call, and a correct MATERIALIZED CTE rewrite — with minimal errors. C edges B by being tighter and adding concrete autovacuum/extended-statistics tuning, while B has slightly more filler and a few imprecise claims. E and D fall to the bottom mainly because both truncate before finishing the required query rewrite; D also changes the join key in its example, while E commits worse correctness failures (a fabricated hyperloglog statistic detail, incorrect cardinality math, and a semantics-changing DISTINCT ON rewrite).

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `checklist` | 32 | Strongest overall. Covers all five explicit requirements (node-by-node plan, composite/partial/covering index with column-order rationale, stats fix, partitioning decision, CTE/materialization rewrite |
  | `full` | 28 | Complete and largely correct, addressing all requirements with a clear priority-ordered fix list. Good partial/covering tradeoff discussion and pg_partman-based partitioning. Minor correctness issues: |
  | `retrieved` | 28 | Accurate and complete, with a clean node-by-node diagnosis and strong autovacuum tuning (scale_factor=0, threshold=50k) plus extended MCV statistics. Composite/covering/partial index reasoning is corr |
  | `control` | 18 | Truncated before delivering the rewritten query — a core, explicitly-requested deliverable — so it fails a key instruction. The node-by-node walk and index column-order rules are good, but the example |
  | `checklist_v2` | 19 | Most architecturally complete index strategy (covering composite, partial, secondary, FK index all correctly reasoned), but undermined by serious correctness problems: it fabricates 'compressed hyperl |

### Task `db-zerodowntime-rename-ieee` (domain: Databases & Persistence)

**Run 1:**
- Ranking: `retrieved > checklist > checklist_v2 > full > control`
- Analysis: C wins because its backfill actually commits per batch from a client script and correctly handles lock/statement timeouts, avoiding the invalid COMMIT-inside-DO-block error that undermines A, D, and E. A and D are close: A has the most nuanced trigger and lock reasoning but a hard SQL error and a lock-type mistake, while D has the best index-rebuild strategy and accurate lock table but a silent row-skipping backfill bug that runs as one long transaction. B and E trail due to divergent-trigger logic and fragile or incomplete backfill implementations.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `checklist` | 24 | Strongest trigger design (IS DISTINCT FROM plus NULL-recovery clause) and thoughtful lock/backfill discussion, but contains hard errors: COMMIT and SET LOCAL inside a PL/pgSQL DO block are illegal, AD |
  | `full` | 18 | Good risk framing, partial unique index, and correctly notes CREATE INDEX CONCURRENTLY cannot run in a transaction. However the trigger only copies when primary_email IS NULL, so post-backfill email u |
  | `retrieved` | 26 | The most operationally correct backfill: a Python script that commits each batch outside the DB, sets lock_timeout/statement_timeout, tracks a resumable offset, and handles lock-timeout retries. Lock  |
  | `checklist_v2` | 25 | Best structure, explicit assumptions, and the clearest index lifecycle (partial unique -> concurrent full -> rename). Lock table is accurate. But the backfill runs the entire DO block as one transacti |
  | `control` | 16 | Good pre-flight phase and a correct lock table, plus it names the single-UPDATE hazard. But the trigger WHEN clause references OLD on an INSERT trigger (invalid), the CTID-based resumable backfill is  |

**Run 2:**
- Ranking: `checklist > checklist_v2 > full > retrieved > control`
- Analysis: B ranks first because it sequences the read-flip only after all 8 replicas run the new code, uses sound lock semantics and a reusable stored-procedure backfill, and treats DROP COLUMN's ACCESS EXCLUSIVE honestly. A and C are both comprehensive but undermined by fundamental errors — A's backfill/verify SQL is outright broken and C mislabels several lock modes — while E adds cursor/trigger bugs on top of a thin index strategy. D is weakest because its AFTER-trigger design is non-functional and its 'deploy before triggers' sequencing contradicts the dual-write invariant, making the safest path unclear.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `checklist_v2` | 26 | Very thorough: pre-flight, monitoring table, utility functions, and explicit per-stage rollback. But concrete SQL bugs (invalid `RETURNING count(*) INTO v_ct` with a second `GET DIAGNOSTICS`; `batch_s |
  | `checklist` | 32 | Cleanest and most architecturally sound: explicit expand → backfill → flip (gated on all replicas) → contract, with two rolling app deploys and a dual-write trigger safety net. Correctly identifies th |
  | `full` | 26 | Good five-phase expand-contract framing and an explicit explanation of why RENAME fails. Backfill stored procedure with progress table is maintainable. But several lock claims are wrong (`ADD COLUMN`  |
  | `control` | 19 | Includes a real threat model and a progress table with pessimistic `locked_until` claiming, which is a good backfill idea. But the core is broken: AFTER triggers that mutate NEW are no-ops (should be  |
  | `retrieved` | 24 | Reasonable pre-flight, expand, dual-write, bounded-batch Python backfill, and rollback coverage. Correct that ADD COLUMN takes ACCESS EXCLUSIVE briefly. But `CREATE TRIGGER` is mislabeled as RowExclus |

**Run 3:**
- Ranking: `retrieved > checklist_v2 > checklist > full > control`
- Analysis: A edges out B because its lock-behavior table is accurate (B invents 'ACCESS MODIFIED') and its backfill is a cleaner bounded id-range loop, despite A's minor index-comment syntax bug. D and C are close but both have broken backfills: C's `COMMIT` inside a DO block fails outright, while D's `last_good_pk += v_count` silently skips rows; D ranks slightly higher for its correct lock table and advisory-lock design. E is clearly worst because it violates the central bounded-batch requirement with a single massive UPDATE, misstates ADD COLUMN locking, and includes a dangerous recursive DELETE trigger plus unhardened SECURITY DEFINER.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `retrieved` | 31 | Mostly accurate lock analysis and a clean expand/contract sequence with rollback at every stage. Minor bugs: `COMMENT ON CONSTRAINT` is applied to an index (invalid), the DELETE trigger returns OLD wi |
  | `checklist_v2` | 30 | Very complete coverage of all required elements, including Drizzle/Django dual-write and a cursor backfill. However, it fabricates a nonexistent lock mode ('ACCESS MODIFIED') in the core lock table, m |
  | `full` | 23 | Strong pre-flight checklist (PgBouncer transaction mode, timeouts, work_mem) and correct conceptual split. But the backfill is fundamentally broken: `COMMIT` inside a `DO $$` block is not allowed in P |
  | `checklist` | 24 | Accurate lock table for ADD COLUMN and good use of advisory locks plus bounded batches. But there are notable errors: `CITRAXTEXT` column type typo, an incorrect `REFERENCES accounts(email)` FK, `BIGB |
  | `control` | 17 | States the correct expand/contract idea but repeatedly violates it: ADD COLUMN is mislabeled 'ACCESS SHARE', and it runs a single massive `UPDATE ... WHERE primary_email IS NULL` instead of bounded ba |

**Run 4:**
- Ranking: `control > checklist > retrieved > checklist_v2 > full`
- Analysis: E and B are the strongest: both nail the lock semantics and produce clean, restartable backfill workers, with E edging ahead on reasoning clarity and explicitly handling the index-rebuild strategy while avoiding a functional bug. C is solid but over-engineers the trigger and relies on contiguous IDs. A has correct lock-level notes but is undermined by messy string/int scripting and truncates before verify/contract. D ranks last because it asserts the wrong lock level (ACCESS SHARE instead of ACCESS EXCLUSIVE) on a requirement that explicitly calls for lock-behavior accuracy.

  | Strategy | Score /35 | Justification |
  |---|---|---|
  | `checklist_v2` | 20 | Correctly identifies ADD COLUMN as ACCESS EXCLUSIVE (metadata-only) and CREATE INDEX CONCURRENTLY as SHARE UPDATE EXCLUSIVE, and provides version gates. But the backfill scripting is error-prone: mixe |
  | `checklist` | 28 | Excellent, comprehensive lock-behavior table and a clean, well-commented Python backfill worker with statement_timeout, advisory-lock guard, server-side cursor, and rate limiting. Solid expand→backfil |
  | `retrieved` | 27 | Correct lock-behavior table, good pre-flight, feature flag for instant rollback, and a defensive trigger-plus-ORM dual-write. Reaches Stage 3. However, the bidirectional trigger logic is over-engineer |
  | `full` | 19 | Contains a clear factual error: it claims ADD COLUMN (nullable, no default) acquires ACCESS SHARE, but it actually takes ACCESS EXCLUSIVE (catalog-only, fast). This directly undermines the required lo |
  | `control` | 30 | States ADD COLUMN lock behavior correctly (ACCESS EXCLUSIVE but instant), uses an idempotent state table, provides a clean retryable cursor-based backfill worker, and — uniquely and correctly — defers |

### Task `db-ratelimit-redis-ieee` (domain: Databases & Persistence)
