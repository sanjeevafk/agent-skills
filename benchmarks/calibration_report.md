# Post-Hoc Execution Calibration Report: LLM Judge Reliability & Construct Validity

**Execution Date:** 2026-09-04 17:53:10 UTC
**Sample Size:** N = 238 executable runs evaluated across tasks and delivery strategies
**Linear Model:** `Predicted Judge Score = 24.99 + 0.65 × Pass Rate` (R² = 0.002)

## Executive Summary

To assess the **Construct Validity** of the IEEE 35-point scoring rubric and quantify LLM judge reliability, we executed concrete source code and unit test suites extracted directly from agent raw outputs across N = 238 executable runs under a strict 15-second subprocess sandbox timeout.

Across the pooled heterogeneous benchmark, aggregate execution pass rate shows weak linear correlation with composite judge scores (**Pearson r = 0.047, p = 0.473**; **Spearman ρ = 0.046, p = 0.481**). Crucially, subgroup decomposition reveals why: the cross-task aggregate is heavily confounded by ambient dependency requirements (e.g. uninstalled browser drivers or Redis daemons in isolated sandboxes). In self-contained tasks, syntax compilation aligns strongly with the judge's Correctness subscore (e.g. **`sec-django-hardening-ieee`**: **r = +0.616, p = 0.001**; **`arch-godclass-refactor-ieee`**: **r = +0.344, p = 0.108**).

---

## Correlation Matrix: Ground-Truth Execution vs. Rubric Dimensions (Pooled N=238)

| Rubric Dimension | Pearson r | Pearson p-value | Spearman ρ | Spearman p-value | Significance (α=0.05) |
|:---|:---:|:---:|:---:|:---:|:---:|
| **Composite (35-pt)** | 0.047 | 0.4726 | 0.046 | 0.4811 | Not significant |
| **Correctness** | -0.025 | 0.7011 | -0.014 | 0.8270 | Not significant |
| **Completeness** | 0.107 | 0.0996 | 0.093 | 0.1515 | Not significant |
| **Maintainability** | 0.057 | 0.3803 | 0.062 | 0.3412 | Not significant |
| **Architecture** | 0.070 | 0.2797 | 0.074 | 0.2560 | Not significant |
| **Security** | -0.065 | 0.3182 | -0.049 | 0.4474 | Not significant |
| **Reasoning_quality** | 0.062 | 0.3407 | 0.051 | 0.4333 | Not significant |
| **Instruction_adherence** | 0.073 | 0.2632 | 0.066 | 0.3075 | Not significant |
| **Syntax Pass Rate** | 0.085 | 0.1918 | 0.116 | 0.0748 | Not significant |
| **Binary Execution Pass** | 0.067 | 0.3006 | 0.072 | 0.2653 | Not significant |

---

## Task-Level Subgroup Calibration (Homogeneous Task Analysis)

| Task ID | N | Syntax vs. Correctness (r) | p-value | Pass Rate vs. Composite (r) | p-value | Alignment Interpretation |
|:---|:---:|:---:|:---:|:---:|:---:|:---|
| `arch-form-statemachine-types` | 25 | **+0.000** | 1.000 | **+0.000** | 1.000 | Environment-bounded |
| `arch-godclass-refactor` | 24 | **-0.021** | 0.924 | **+0.354** | 0.090 | Moderate positive trend |
| `db-zerodowntime-rename` | 17 | **+0.068** | 0.796 | **+0.241** | 0.351 | Moderate positive trend |
| `qa-checkout-e2e` | 10 | **+0.000** | 1.000 | **+0.000** | 1.000 | Environment-bounded |
| `qa-dashboard-browserqa` | 13 | **-0.318** | 0.290 | **-0.461** | 0.113 | Environment-bounded |
| `qa-ratelimiter-tdd` | 24 | **+0.047** | 0.826 | **+0.007** | 0.975 | Environment-bounded |
| `sec-django-hardening` | 25 | **+0.616** | 0.001 | **+0.270** | 0.191 | Strong syntax alignment |
| `sec-webhook-audit` | 24 | **-0.582** | 0.003 | **-0.480** | 0.018 | Environment-bounded |
| `sre-flaky-ci` | 25 | **+0.062** | 0.768 | **+0.155** | 0.460 | Environment-bounded |
| `sre-node-leak` | 24 | **-0.403** | 0.051 | **+0.000** | 1.000 | Environment-bounded |
| `sre-p99-regression` | 24 | **-0.030** | 0.891 | **+0.080** | 0.712 | Environment-bounded |

---

## Calibration Table (Representative Runs & Residuals)

| Task ID | Condition / Strategy | Run | Lang | Syntax Ok | Tests (Pass/Total) | Pass Rate | Judge Score | Correctness | Residual | Status / Diagnostic |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| `arch-form-statemachine-types` | `checklist` | r1 | TY | No | N/A | 0.00 | **21/35** | 2/5 | -3.99 | error TS6231: Could not resolve the path |
| `arch-form-statemachine-types` | `checklist` | r2 | TY | No | 0/1 | 0.00 | **22/35** | 3/5 | -2.99 | index.ts(194,132): error TS1005: ',' exp |
| `arch-form-statemachine-types` | `checklist` | r3 | TY | No | N/A | 0.00 | **15/35** | 2/5 | -9.99 | error TS6231: Could not resolve the path |
| `arch-form-statemachine-types` | `checklist` | r4 | TY | No | 0/1 | 0.00 | **21/35** | 3/5 | -3.99 | error TS6231: Could not resolve the path |
| `arch-form-statemachine-types` | `checklist` | r5 | TY | No | N/A | 0.00 | **18/35** | 2/5 | -6.99 | index.ts(30,51): error TS1109: Expressio |
| `arch-form-statemachine-types` | `checklist_v2` | r1 | TY | No | 0/1 | 0.00 | **27/35** | 3/5 | +2.01 | error TS6231: Could not resolve the path |
| `arch-form-statemachine-types` | `checklist_v2` | r2 | TY | No | N/A | 0.00 | **27/35** | 4/5 | +2.01 | error TS6231: Could not resolve the path |
| `arch-form-statemachine-types` | `checklist_v2` | r3 | TY | No | N/A | 0.00 | **17/35** | 2/5 | -7.99 | error TS6231: Could not resolve the path |
| `arch-form-statemachine-types` | `checklist_v2` | r4 | TY | No | N/A | 0.00 | **24/35** | 3/5 | -0.99 | error TS6231: Could not resolve the path |
| `arch-form-statemachine-types` | `checklist_v2` | r5 | TY | No | N/A | 0.00 | **28/35** | 4/5 | +3.01 | error TS6231: Could not resolve the path |
| `arch-form-statemachine-types` | `control` | r1 | TY | No | N/A | 0.00 | **30/35** | 3/5 | +5.01 | error TS6231: Could not resolve the path |
| `arch-form-statemachine-types` | `control` | r2 | TY | No | 0/1 | 0.00 | **30/35** | 3/5 | +5.01 | error TS6231: Could not resolve the path |
| `arch-form-statemachine-types` | `control` | r3 | TY | No | 0/1 | 0.00 | **24/35** | 3/5 | -0.99 | error TS6231: Could not resolve the path |
| `arch-form-statemachine-types` | `control` | r4 | TY | No | N/A | 0.00 | **16/35** | 2/5 | -8.99 | error TS6231: Could not resolve the path |
| `arch-form-statemachine-types` | `control` | r5 | TY | No | N/A | 0.00 | **19/35** | 2/5 | -5.99 | error TS6231: Could not resolve the path |
| `arch-form-statemachine-types` | `full` | r1 | TY | No | N/A | 0.00 | **31/35** | 4/5 | +6.01 | index.ts(253,22): error TS1005: '>' expe |
| `arch-form-statemachine-types` | `full` | r2 | TY | No | N/A | 0.00 | **19/35** | 2/5 | -5.99 | error TS6231: Could not resolve the path |
| `arch-form-statemachine-types` | `full` | r3 | TY | No | 0/1 | 0.00 | **20/35** | 2/5 | -4.99 | index.ts(391,28): error TS1005: '>' expe |
| `arch-form-statemachine-types` | `full` | r4 | TY | No | 0/1 | 0.00 | **17/35** | 2/5 | -7.99 | index.ts(201,40): error TS1005: ';' expe |
| `arch-form-statemachine-types` | `full` | r5 | TY | No | N/A | 0.00 | **28/35** | 3/5 | +3.01 | error TS6231: Could not resolve the path |
| `arch-form-statemachine-types` | `retrieved` | r1 | TY | No | 0/1 | 0.00 | **19/35** | 2/5 | -5.99 | index.ts(313,31): error TS1005: '>' expe |
| `arch-form-statemachine-types` | `retrieved` | r2 | TY | No | 0/1 | 0.00 | **24/35** | 3/5 | -0.99 | index.ts(328,26): error TS1005: ',' expe |
| `arch-form-statemachine-types` | `retrieved` | r3 | TY | No | 0/1 | 0.00 | **22/35** | 3/5 | -2.99 | index.ts(146,3): error TS1110: Type expe |
| `arch-form-statemachine-types` | `retrieved` | r4 | TY | No | 0/1 | 0.00 | **27/35** | 3/5 | +2.01 | error TS6231: Could not resolve the path |
| `arch-form-statemachine-types` | `retrieved` | r5 | TY | No | N/A | 0.00 | **21/35** | 3/5 | -3.99 | index.ts(340,1): error TS1128: Declarati |
| `arch-godclass-refactor` | `checklist` | r1 | PY | No | 0/1 | 0.00 | **19/35** | 3/5 | -5.99 | 1 tests failed/errored |
| `arch-godclass-refactor` | `checklist` | r2 | PY | Yes | N/A | 1.00 | **32/35** | 5/5 | +6.36 | Syntax ok |
| `arch-godclass-refactor` | `checklist` | r3 | PY | No | 0/1 | 0.00 | **28/35** | 4/5 | +3.01 | 1 tests failed/errored |
| `arch-godclass-refactor` | `checklist` | r4 | PY | No | 0/0 | 0.00 | **25/35** | 4/5 | +0.01 | ImportError while loading conftest '/tmp |
| `arch-godclass-refactor` | `checklist` | r5 | PY | No | N/A | 0.00 | **32/35** | 5/5 | +7.01 | File "/tmp/tmp79g0j045/solution.py", lin |
| `arch-godclass-refactor` | `checklist_v2` | r1 | PY | No | 0/1 | 0.00 | **24/35** | 4/5 | -0.99 | 1 tests failed/errored |
| `arch-godclass-refactor` | `checklist_v2` | r2 | PY | No | 0/3 | 0.00 | **26/35** | 4/5 | +1.01 | 3 tests failed/errored |
| `arch-godclass-refactor` | `checklist_v2` | r3 | PY | No | N/A | 0.00 | **23/35** | 4/5 | -1.99 | File "/tmp/tmp_qdm9bs_/solution.py", lin |
| `arch-godclass-refactor` | `checklist_v2` | r4 | PY | Yes | N/A | 1.00 | **29/35** | 5/5 | +3.36 | Syntax ok |
| `arch-godclass-refactor` | `checklist_v2` | r5 | PY | Yes | 0/1 | 0.00 | **31/35** | 4/5 | +6.01 | 1 tests failed/errored |
| `arch-godclass-refactor` | `control` | r1 | PY | No | 0/1 | 0.00 | **23/35** | 3/5 | -1.99 | 1 tests failed/errored |
| `arch-godclass-refactor` | `control` | r2 | PY | No | 0/0 | 0.00 | **33/35** | 5/5 | +8.01 | ImportError while loading conftest '/tmp |
| `arch-godclass-refactor` | `control` | r3 | PY | No | 0/1 | 0.00 | **20/35** | 3/5 | -4.99 | 1 tests failed/errored |
| `arch-godclass-refactor` | `control` | r4 | PY | Yes | N/A | 1.00 | **31/35** | 4/5 | +5.36 | Syntax ok |
| `arch-godclass-refactor` | `control` | r5 | PY | No | 0/1 | 0.00 | **30/35** | 4/5 | +5.01 | 1 tests failed/errored |
| `arch-godclass-refactor` | `full` | r1 | PY | No | N/A | 0.00 | **32/35** | 4/5 | +7.01 | File "/tmp/tmp96fwgwo2/solution.py", lin |
| `arch-godclass-refactor` | `full` | r2 | PY | No | 0/1 | 0.00 | **33/35** | 5/5 | +8.01 | 1 tests failed/errored |
| `arch-godclass-refactor` | `full` | r3 | PY | No | 0/1 | 0.00 | **22/35** | 4/5 | -2.99 | 1 tests failed/errored |
| `arch-godclass-refactor` | `full` | r4 | PY | No | N/A | 0.00 | **30/35** | 4/5 | +5.01 | File "/tmp/tmph1zuk88e/characterization/ |
| `arch-godclass-refactor` | `full` | r5 | PY | No | N/A | 0.00 | **31/35** | 5/5 | +6.01 | Sorry: IndentationError: unexpected inde |
| `arch-godclass-refactor` | `retrieved` | r1 | TY | No | 0/1 | 0.00 | **24/35** | 4/5 | -0.99 | index.ts(129,24): error TS1138: Paramete |
| `arch-godclass-refactor` | `retrieved` | r2 | PY | No | 0/16 | 0.00 | **23/35** | 3/5 | -1.99 | 16 tests failed/errored |
| `arch-godclass-refactor` | `retrieved` | r4 | PY | No | 3/3 | 1.00 | **32/35** | 5/5 | +6.36 | OK |
| `arch-godclass-refactor` | `retrieved` | r5 | PY | Yes | 0/3 | 0.00 | **29/35** | 4/5 | +4.01 | 3 tests failed/errored |
| `db-zerodowntime-rename` | `checklist` | r2 | PY | No | N/A | 0.00 | **32/35** | 5/5 | +7.01 | Syntax errors detected |
| `db-zerodowntime-rename` | `checklist` | r3 | PY | No | N/A | 0.00 | **24/35** | 3/5 | -0.99 | Sorry: IndentationError: unindent does n |
| `db-zerodowntime-rename` | `checklist` | r4 | PY | No | N/A | 0.00 | **28/35** | 4/5 | +3.01 | File "/tmp/tmp3zoyx1nr/solution.py", lin |
| `db-zerodowntime-rename` | `checklist_v2` | r2 | PY | Yes | N/A | 1.00 | **26/35** | 3/5 | +0.36 | Syntax ok |
| `db-zerodowntime-rename` | `checklist_v2` | r3 | PY | Yes | N/A | 1.00 | **30/35** | 3/5 | +4.36 | Syntax ok |
| `db-zerodowntime-rename` | `checklist_v2` | r4 | PY | No | N/A | 0.00 | **20/35** | 3/5 | -4.99 | Syntax errors detected |
| `db-zerodowntime-rename` | `control` | r1 | PY | No | N/A | 0.00 | **16/35** | 2/5 | -8.99 | File "/tmp/tmpvg83q3ab/solution.py", lin |
| `db-zerodowntime-rename` | `control` | r2 | PY | Yes | N/A | 1.00 | **19/35** | 2/5 | -6.64 | Syntax ok |
| `db-zerodowntime-rename` | `control` | r3 | PY | Yes | N/A | 1.00 | **17/35** | 2/5 | -8.64 | Syntax ok |
| `db-zerodowntime-rename` | `control` | r4 | PY | Yes | N/A | 1.00 | **30/35** | 5/5 | +4.36 | Syntax ok |
| `db-zerodowntime-rename` | `full` | r1 | PY | No | N/A | 0.00 | **18/35** | 2/5 | -6.99 | Syntax errors detected |
| `db-zerodowntime-rename` | `full` | r2 | PY | Yes | N/A | 1.00 | **26/35** | 3/5 | +0.36 | Syntax ok |
| `db-zerodowntime-rename` | `full` | r4 | PY | No | N/A | 0.00 | **19/35** | 2/5 | -5.99 | File "/tmp/tmpyszxqx20/solution.py", lin |
| `db-zerodowntime-rename` | `retrieved` | r1 | PY | Yes | N/A | 1.00 | **26/35** | 4/5 | +0.36 | Syntax ok |
| `db-zerodowntime-rename` | `retrieved` | r2 | PY | Yes | N/A | 1.00 | **24/35** | 3/5 | -1.64 | Syntax ok |
| `db-zerodowntime-rename` | `retrieved` | r3 | PY | Yes | N/A | 1.00 | **31/35** | 4/5 | +5.36 | Syntax ok |
| `db-zerodowntime-rename` | `retrieved` | r4 | PY | No | N/A | 0.00 | **27/35** | 4/5 | +2.01 | Sorry: IndentationError: expected an ind |
| `devops-ml-docker` | `control` | r2 | PY | Yes | N/A | 1.00 | **19/35** | 1/5 | -6.64 | Syntax ok |
| `devops-ml-docker` | `full` | r4 | PY | Yes | N/A | 1.00 | **26/35** | 3/5 | +0.36 | Syntax ok |
| `qa-checkout-e2e` | `checklist` | r1 | TY | No | 0/1 | 0.00 | **18/35** | 2/5 | -6.99 | index.ts(443,21): error TS1005: ',' expe |
| `qa-checkout-e2e` | `checklist` | r2 | TY | No | 0/1 | 0.00 | **24/35** | 3/5 | -0.99 | error TS6231: Could not resolve the path |
| `qa-checkout-e2e` | `checklist_v2` | r1 | TY | No | 0/1 | 0.00 | **13/35** | 1/5 | -11.99 | index.ts(183,20): error TS1005: ';' expe |
| `qa-checkout-e2e` | `checklist_v2` | r2 | TY | No | 0/1 | 0.00 | **27/35** | 4/5 | +2.01 | error TS6231: Could not resolve the path |
| `qa-checkout-e2e` | `control` | r1 | TY | No | 0/1 | 0.00 | **26/35** | 3/5 | +1.01 | error TS6231: Could not resolve the path |
| `qa-checkout-e2e` | `control` | r2 | TY | No | 0/1 | 0.00 | **21/35** | 2/5 | -3.99 | index.ts(191,42): error TS1005: ',' expe |
| `qa-checkout-e2e` | `full` | r1 | TY | No | 0/1 | 0.00 | **20/35** | 2/5 | -4.99 | error TS6231: Could not resolve the path |
| `qa-checkout-e2e` | `full` | r2 | TY | No | 0/1 | 0.00 | **20/35** | 2/5 | -4.99 | error TS6231: Could not resolve the path |
| `qa-checkout-e2e` | `retrieved` | r1 | TY | No | 0/1 | 0.00 | **23/35** | 3/5 | -1.99 | error TS6231: Could not resolve the path |
| `qa-checkout-e2e` | `retrieved` | r2 | TY | No | 0/1 | 0.00 | **25/35** | 3/5 | +0.01 | error TS6231: Could not resolve the path |
| `qa-dashboard-browserqa` | `checklist` | r3 | PY | Yes | N/A | 1.00 | **20/35** | 3/5 | -5.64 | Syntax ok |
| `qa-dashboard-browserqa` | `checklist` | r5 | TY | No | 0/1 | 0.00 | **26/35** | 3/5 | +1.01 | error TS6231: Could not resolve the path |
| `qa-dashboard-browserqa` | `checklist_v2` | r2 | TY | No | 0/1 | 0.00 | **22/35** | 3/5 | -2.99 | error TS6231: Could not resolve the path |
| `qa-dashboard-browserqa` | `checklist_v2` | r3 | TY | No | 0/1 | 0.00 | **27/35** | 3/5 | +2.01 | index.ts(448,1): error TS1128: Declarati |
| `qa-dashboard-browserqa` | `checklist_v2` | r5 | TY | No | 0/1 | 0.00 | **29/35** | 4/5 | +4.01 | error TS6231: Could not resolve the path |
| `qa-dashboard-browserqa` | `control` | r3 | TY | No | 0/1 | 0.00 | **21/35** | 3/5 | -3.99 | index.ts(194,48): error TS1005: ',' expe |
| `qa-dashboard-browserqa` | `control` | r4 | TY | No | N/A | 0.00 | **31/35** | 5/5 | +6.01 | error TS6231: Could not resolve the path |
| `qa-dashboard-browserqa` | `control` | r5 | TY | No | 0/1 | 0.00 | **26/35** | 4/5 | +1.01 | error TS6231: Could not resolve the path |
| `qa-dashboard-browserqa` | `full` | r4 | TY | No | 0/1 | 0.00 | **23/35** | 4/5 | -1.99 | index.ts(264,48): error TS1005: '}' expe |
| `qa-dashboard-browserqa` | `full` | r5 | TY | No | 0/1 | 0.00 | **29/35** | 4/5 | +4.01 | index.ts(323,79): error TS1005: ',' expe |
| `qa-dashboard-browserqa` | `retrieved` | r2 | TY | No | 0/1 | 0.00 | **25/35** | 4/5 | +0.01 | error TS6231: Could not resolve the path |
| `qa-dashboard-browserqa` | `retrieved` | r4 | TY | No | 0/1 | 0.00 | **28/35** | 5/5 | +3.01 | error TS6231: Could not resolve the path |
| `qa-dashboard-browserqa` | `retrieved` | r5 | TY | No | 0/1 | 0.00 | **34/35** | 5/5 | +9.01 | error TS6231: Could not resolve the path |
| `qa-ratelimiter-tdd` | `checklist` | r1 | PY | No | 0/1 | 0.00 | **19/35** | 3/5 | -5.99 | 1 tests failed/errored |
| `qa-ratelimiter-tdd` | `checklist` | r2 | PY | No | 0/2 | 0.00 | **19/35** | 3/5 | -5.99 | 2 tests failed/errored |
| `qa-ratelimiter-tdd` | `checklist` | r3 | PY | No | 0/1 | 0.00 | **20/35** | 3/5 | -4.99 | 1 tests failed/errored |
| `qa-ratelimiter-tdd` | `checklist` | r4 | PY | No | 0/3 | 0.00 | **16/35** | 3/5 | -8.99 | 3 tests failed/errored |
| `qa-ratelimiter-tdd` | `checklist_v2` | r1 | PY | No | 0/2 | 0.00 | **14/35** | 2/5 | -10.99 | 2 tests failed/errored |
| `qa-ratelimiter-tdd` | `checklist_v2` | r2 | PY | No | 0/8 | 0.00 | **20/35** | 4/5 | -4.99 | 8 tests failed/errored |
| `qa-ratelimiter-tdd` | `checklist_v2` | r3 | PY | Yes | 0/1 | 0.00 | **21/35** | 2/5 | -3.99 | 1 tests failed/errored |
| `qa-ratelimiter-tdd` | `checklist_v2` | r4 | PY | No | 9/14 | 0.64 | **26/35** | 5/5 | +0.59 | 5 tests failed/errored |
| `qa-ratelimiter-tdd` | `checklist_v2` | r5 | PY | Yes | 0/1 | 0.00 | **21/35** | 3/5 | -3.99 | 1 tests failed/errored |
| `qa-ratelimiter-tdd` | `control` | r1 | PY | No | 0/1 | 0.00 | **16/35** | 2/5 | -8.99 | 1 tests failed/errored |
| `qa-ratelimiter-tdd` | `control` | r2 | PY | No | 0/1 | 0.00 | **21/35** | 4/5 | -3.99 | 1 tests failed/errored |
| `qa-ratelimiter-tdd` | `control` | r3 | PY | No | 0/1 | 0.00 | **25/35** | 4/5 | +0.01 | 1 tests failed/errored |
| `qa-ratelimiter-tdd` | `control` | r4 | PY | Yes | 7/20 | 0.35 | **18/35** | 2/5 | -7.22 | 13 tests failed/errored |
| `qa-ratelimiter-tdd` | `control` | r5 | PY | Yes | 0/7 | 0.00 | **16/35** | 2/5 | -8.99 | 7 tests failed/errored |
| `qa-ratelimiter-tdd` | `full` | r1 | PY | No | 0/1 | 0.00 | **24/35** | 4/5 | -0.99 | 1 tests failed/errored |
| `qa-ratelimiter-tdd` | `full` | r2 | PY | No | 0/2 | 0.00 | **23/35** | 3/5 | -1.99 | 2 tests failed/errored |
| `qa-ratelimiter-tdd` | `full` | r3 | PY | No | 0/11 | 0.00 | **20/35** | 2/5 | -4.99 | 11 tests failed/errored |
| `qa-ratelimiter-tdd` | `full` | r4 | PY | No | 0/2 | 0.00 | **21/35** | 4/5 | -3.99 | 2 tests failed/errored |
| `qa-ratelimiter-tdd` | `full` | r5 | PY | No | 0/1 | 0.00 | **21/35** | 3/5 | -3.99 | 1 tests failed/errored |
| `qa-ratelimiter-tdd` | `retrieved` | r1 | PY | No | 0/2 | 0.00 | **16/35** | 2/5 | -8.99 | 2 tests failed/errored |
| `qa-ratelimiter-tdd` | `retrieved` | r2 | PY | No | 0/1 | 0.00 | **20/35** | 2/5 | -4.99 | 1 tests failed/errored |
| `qa-ratelimiter-tdd` | `retrieved` | r3 | PY | No | 6/7 | 0.86 | **16/35** | 1/5 | -9.55 | 1 tests failed/errored |
| `qa-ratelimiter-tdd` | `retrieved` | r4 | PY | No | 15/23 | 0.65 | **19/35** | 3/5 | -6.41 | 8 tests failed/errored |
| `qa-ratelimiter-tdd` | `retrieved` | r5 | PY | Yes | 0/1 | 0.00 | **18/35** | 3/5 | -6.99 | 1 tests failed/errored |
| `sec-amm-pool` | `control` | r4 | TY | No | N/A | 0.00 | **30/35** | 4/5 | +5.01 | error TS6231: Could not resolve the path |
| `sec-django-hardening` | `checklist` | r1 | PY | Yes | N/A | 1.00 | **30/35** | 4/5 | +4.36 | Syntax ok |
| `sec-django-hardening` | `checklist` | r2 | PY | No | N/A | 0.00 | **29/35** | 5/5 | +4.01 | Syntax errors detected |
| `sec-django-hardening` | `checklist` | r3 | PY | No | N/A | 0.00 | **28/35** | 5/5 | +3.01 | Syntax errors detected |
| `sec-django-hardening` | `checklist` | r4 | PY | No | N/A | 0.00 | **20/35** | 3/5 | -4.99 | File "/tmp/tmpq5u61dcq/reports/views.py" |
| `sec-django-hardening` | `checklist` | r5 | PY | No | 0/1 | 0.00 | **34/35** | 5/5 | +9.01 | 1 tests failed/errored |
| `sec-django-hardening` | `checklist_v2` | r1 | PY | No | N/A | 0.00 | **26/35** | 4/5 | +1.01 | Syntax errors detected |
| `sec-django-hardening` | `checklist_v2` | r2 | PY | No | N/A | 0.00 | **31/35** | 5/5 | +6.01 | Syntax errors detected |
| `sec-django-hardening` | `checklist_v2` | r3 | PY | No | N/A | 0.00 | **24/35** | 3/5 | -0.99 | File "/tmp/tmpcbbx8f_6/apps/reports/view |
| `sec-django-hardening` | `checklist_v2` | r4 | PY | No | N/A | 0.00 | **26/35** | 4/5 | +1.01 | File "/tmp/tmpcaunearh/settings/base.py" |
| `sec-django-hardening` | `checklist_v2` | r5 | PY | No | N/A | 0.00 | **34/35** | 5/5 | +9.01 | Syntax errors detected |
| `sec-django-hardening` | `control` | r1 | PY | No | N/A | 0.00 | **25/35** | 4/5 | +0.01 | Syntax errors detected |
| `sec-django-hardening` | `control` | r2 | PY | No | N/A | 0.00 | **29/35** | 4/5 | +4.01 | Syntax errors detected |
| `sec-django-hardening` | `control` | r3 | PY | No | N/A | 0.00 | **20/35** | 4/5 | -4.99 | Syntax errors detected |
| `sec-django-hardening` | `control` | r4 | PY | No | 0/1 | 0.00 | **25/35** | 4/5 | +0.01 | 1 tests failed/errored |
| `sec-django-hardening` | `control` | r5 | PY | Yes | N/A | 1.00 | **32/35** | 5/5 | +6.36 | Syntax ok |
| `sec-django-hardening` | `full` | r1 | PY | No | N/A | 0.00 | **28/35** | 4/5 | +3.01 | File "/tmp/tmpeuk046a_/solution.py", lin |
| `sec-django-hardening` | `full` | r2 | PY | No | N/A | 0.00 | **26/35** | 4/5 | +1.01 | File "/tmp/tmp9tdajgzw/myproject/setting |
| `sec-django-hardening` | `full` | r3 | PY | No | N/A | 0.00 | **19/35** | 3/5 | -5.99 | File "/tmp/tmp1si3ia5v/serializers.py",  |
| `sec-django-hardening` | `full` | r4 | PY | No | N/A | 0.00 | **28/35** | 4/5 | +3.01 | Syntax errors detected |
| `sec-django-hardening` | `full` | r5 | PY | No | N/A | 0.00 | **30/35** | 5/5 | +5.01 | File "/tmp/tmp7z2c7uwn/solution.py", lin |
| `sec-django-hardening` | `retrieved` | r1 | PY | Yes | 0/1 | 0.00 | **28/35** | 4/5 | +3.01 | 1 tests failed/errored |
| `sec-django-hardening` | `retrieved` | r2 | PY | No | N/A | 0.00 | **30/35** | 5/5 | +5.01 | Syntax errors detected |
| `sec-django-hardening` | `retrieved` | r3 | PY | No | N/A | 0.00 | **26/35** | 4/5 | +1.01 | Syntax errors detected |
| `sec-django-hardening` | `retrieved` | r4 | PY | No | N/A | 0.00 | **21/35** | 3/5 | -3.99 | File "/tmp/tmpwot9ot5c/settings.py", lin |
| `sec-django-hardening` | `retrieved` | r5 | PY | No | N/A | 0.00 | **32/35** | 5/5 | +7.01 | Syntax errors detected |
| `sec-webhook-audit` | `checklist` | r1 | PY | Yes | N/A | 1.00 | **33/35** | 5/5 | +7.36 | Syntax ok |
| `sec-webhook-audit` | `checklist` | r2 | PY | Yes | N/A | 1.00 | **14/35** | 1/5 | -11.64 | Syntax ok |
| `sec-webhook-audit` | `checklist` | r4 | PY | No | N/A | 0.00 | **34/35** | 5/5 | +9.01 | File "/tmp/tmpbz2z_xn9/solution.py", lin |
| `sec-webhook-audit` | `checklist` | r5 | PY | Yes | N/A | 1.00 | **31/35** | 4/5 | +5.36 | Syntax ok |
| `sec-webhook-audit` | `checklist_v2` | r1 | PY | Yes | N/A | 1.00 | **32/35** | 5/5 | +6.36 | Syntax ok |
| `sec-webhook-audit` | `checklist_v2` | r2 | PY | Yes | N/A | 1.00 | **31/35** | 4/5 | +5.36 | Syntax ok |
| `sec-webhook-audit` | `checklist_v2` | r3 | PY | No | N/A | 0.00 | **35/35** | 5/5 | +10.01 | File "/tmp/tmppaika48r/solution.py", lin |
| `sec-webhook-audit` | `checklist_v2` | r4 | PY | Yes | N/A | 1.00 | **24/35** | 3/5 | -1.64 | Syntax ok |
| `sec-webhook-audit` | `checklist_v2` | r5 | PY | No | N/A | 0.00 | **32/35** | 5/5 | +7.01 | File "/tmp/tmp2irx3s1j/solution.py", lin |
| `sec-webhook-audit` | `control` | r1 | PY | Yes | N/A | 1.00 | **26/35** | 4/5 | +0.36 | Syntax ok |
| `sec-webhook-audit` | `control` | r2 | PY | No | N/A | 0.00 | **34/35** | 5/5 | +9.01 | File "/tmp/tmpbl7lq_ah/solution.py", lin |
| `sec-webhook-audit` | `control` | r3 | PY | No | N/A | 0.00 | **35/35** | 5/5 | +10.01 | File "/tmp/tmpl5_w43uk/solution.py", lin |
| `sec-webhook-audit` | `control` | r4 | PY | Yes | N/A | 1.00 | **23/35** | 2/5 | -2.64 | Syntax ok |
| `sec-webhook-audit` | `control` | r5 | PY | Yes | N/A | 1.00 | **29/35** | 4/5 | +3.36 | Syntax ok |
| `sec-webhook-audit` | `full` | r1 | PY | Yes | N/A | 1.00 | **22/35** | 2/5 | -3.64 | Syntax ok |
| `sec-webhook-audit` | `full` | r2 | PY | No | N/A | 0.00 | **22/35** | 2/5 | -2.99 | File "/tmp/tmp9wsu_3ve/solution.py", lin |
| `sec-webhook-audit` | `full` | r3 | PY | No | N/A | 0.00 | **24/35** | 3/5 | -0.99 | File "/tmp/tmpbxr2161m/solution.py", lin |
| `sec-webhook-audit` | `full` | r4 | PY | Yes | N/A | 1.00 | **28/35** | 4/5 | +2.36 | Syntax ok |
| `sec-webhook-audit` | `full` | r5 | PY | Yes | N/A | 1.00 | **18/35** | 2/5 | -7.64 | Syntax ok |
| `sec-webhook-audit` | `retrieved` | r1 | PY | Yes | N/A | 1.00 | **27/35** | 3/5 | +1.36 | Syntax ok |
| `sec-webhook-audit` | `retrieved` | r2 | PY | Yes | N/A | 1.00 | **21/35** | 2/5 | -4.64 | Syntax ok |
| `sec-webhook-audit` | `retrieved` | r3 | PY | Yes | N/A | 1.00 | **26/35** | 3/5 | +0.36 | Syntax ok |
| `sec-webhook-audit` | `retrieved` | r4 | PY | Yes | N/A | 1.00 | **19/35** | 2/5 | -6.64 | Syntax ok |
| `sec-webhook-audit` | `retrieved` | r5 | PY | No | N/A | 0.00 | **34/35** | 5/5 | +9.01 | Sorry: IndentationError: expected an ind |
| `sre-flaky-ci` | `checklist` | r1 | PY | Yes | 0/1 | 0.00 | **30/35** | 5/5 | +5.01 | 1 tests failed/errored |
| `sre-flaky-ci` | `checklist` | r2 | PY | Yes | 0/1 | 0.00 | **27/35** | 4/5 | +2.01 | 1 tests failed/errored |
| `sre-flaky-ci` | `checklist` | r3 | PY | No | 0/1 | 0.00 | **30/35** | 4/5 | +5.01 | 1 tests failed/errored |
| `sre-flaky-ci` | `checklist` | r4 | PY | No | 0/1 | 0.00 | **29/35** | 4/5 | +4.01 | 1 tests failed/errored |
| `sre-flaky-ci` | `checklist` | r5 | PY | Yes | 0/1 | 0.00 | **28/35** | 4/5 | +3.01 | 1 tests failed/errored |
| `sre-flaky-ci` | `checklist_v2` | r1 | PY | No | 0/1 | 0.00 | **33/35** | 5/5 | +8.01 | 1 tests failed/errored |
| `sre-flaky-ci` | `checklist_v2` | r2 | PY | No | 0/1 | 0.00 | **29/35** | 4/5 | +4.01 | 1 tests failed/errored |
| `sre-flaky-ci` | `checklist_v2` | r3 | PY | Yes | 4/6 | 0.67 | **32/35** | 5/5 | +6.58 | 2 tests failed/errored |
| `sre-flaky-ci` | `checklist_v2` | r4 | PY | Yes | 0/1 | 0.00 | **19/35** | 2/5 | -5.99 | 1 tests failed/errored |
| `sre-flaky-ci` | `checklist_v2` | r5 | PY | Yes | 0/1 | 0.00 | **35/35** | 5/5 | +10.01 | 1 tests failed/errored |
| `sre-flaky-ci` | `control` | r1 | PY | No | 0/2 | 0.00 | **24/35** | 3/5 | -0.99 | 2 tests failed/errored |
| `sre-flaky-ci` | `control` | r2 | PY | No | 0/0 | 0.00 | **31/35** | 4/5 | +6.01 | ImportError while loading conftest '/tmp |
| `sre-flaky-ci` | `control` | r3 | PY | No | 0/0 | 0.00 | **26/35** | 3/5 | +1.01 | ImportError while loading conftest '/tmp |
| `sre-flaky-ci` | `control` | r4 | PY | Yes | 0/1 | 0.00 | **26/35** | 3/5 | +1.01 | 1 tests failed/errored |
| `sre-flaky-ci` | `control` | r5 | PY | No | 0/1 | 0.00 | **32/35** | 4/5 | +7.01 | 1 tests failed/errored |
| `sre-flaky-ci` | `full` | r1 | PY | Yes | 0/1 | 0.00 | **31/35** | 5/5 | +6.01 | 1 tests failed/errored |
| `sre-flaky-ci` | `full` | r2 | PY | Yes | 0/1 | 0.00 | **26/35** | 4/5 | +1.01 | 1 tests failed/errored |
| `sre-flaky-ci` | `full` | r3 | PY | Yes | 0/1 | 0.00 | **25/35** | 3/5 | +0.01 | 1 tests failed/errored |
| `sre-flaky-ci` | `full` | r4 | PY | Yes | 0/1 | 0.00 | **30/35** | 4/5 | +5.01 | 1 tests failed/errored |
| `sre-flaky-ci` | `full` | r5 | PY | No | 0/1 | 0.00 | **34/35** | 5/5 | +9.01 | 1 tests failed/errored |
| `sre-flaky-ci` | `retrieved` | r1 | PY | Yes | 0/1 | 0.00 | **20/35** | 2/5 | -4.99 | 1 tests failed/errored |
| `sre-flaky-ci` | `retrieved` | r2 | PY | Yes | 0/1 | 0.00 | **33/35** | 5/5 | +8.01 | 1 tests failed/errored |
| `sre-flaky-ci` | `retrieved` | r3 | PY | Yes | 0/1 | 0.00 | **33/35** | 5/5 | +8.01 | 1 tests failed/errored |
| `sre-flaky-ci` | `retrieved` | r4 | PY | Yes | 0/1 | 0.00 | **32/35** | 5/5 | +7.01 | 1 tests failed/errored |
| `sre-flaky-ci` | `retrieved` | r5 | PY | Yes | 0/1 | 0.00 | **29/35** | 4/5 | +4.01 | 1 tests failed/errored |
| `sre-node-leak` | `checklist` | r1 | TY | No | 0/1 | 0.00 | **15/35** | 2/5 | -9.99 | error TS6231: Could not resolve the path |
| `sre-node-leak` | `checklist` | r2 | TY | No | N/A | 0.00 | **28/35** | 4/5 | +3.01 | index.ts(198,48): error TS1128: Declarat |
| `sre-node-leak` | `checklist` | r3 | TY | No | 0/1 | 0.00 | **26/35** | 3/5 | +1.01 | error TS6231: Could not resolve the path |
| `sre-node-leak` | `checklist` | r4 | TY | No | 0/1 | 0.00 | **18/35** | 2/5 | -6.99 | error TS6231: Could not resolve the path |
| `sre-node-leak` | `checklist` | r5 | TY | No | 0/1 | 0.00 | **28/35** | 3/5 | +3.01 | error TS6231: Could not resolve the path |
| `sre-node-leak` | `checklist_v2` | r1 | TY | No | N/A | 0.00 | **33/35** | 4/5 | +8.01 | index.ts(71,20): error TS1005: ';' expec |
| `sre-node-leak` | `checklist_v2` | r2 | TY | No | 0/1 | 0.00 | **16/35** | 2/5 | -8.99 | error TS6231: Could not resolve the path |
| `sre-node-leak` | `checklist_v2` | r3 | PY | No | N/A | 0.00 | **17/35** | 1/5 | -7.99 | Syntax errors detected |
| `sre-node-leak` | `checklist_v2` | r4 | TY | No | N/A | 0.00 | **27/35** | 3/5 | +2.01 | error TS6231: Could not resolve the path |
| `sre-node-leak` | `checklist_v2` | r5 | TY | No | N/A | 0.00 | **22/35** | 2/5 | -2.99 | error TS6231: Could not resolve the path |
| `sre-node-leak` | `control` | r1 | TY | No | 0/1 | 0.00 | **34/35** | 5/5 | +9.01 | error TS6231: Could not resolve the path |
| `sre-node-leak` | `control` | r2 | TY | No | 0/1 | 0.00 | **18/35** | 2/5 | -6.99 | error TS6231: Could not resolve the path |
| `sre-node-leak` | `control` | r3 | TY | No | 0/1 | 0.00 | **23/35** | 2/5 | -1.99 | error TS6231: Could not resolve the path |
| `sre-node-leak` | `control` | r4 | TY | No | 0/1 | 0.00 | **25/35** | 3/5 | +0.01 | error TS6231: Could not resolve the path |
| `sre-node-leak` | `full` | r1 | TY | No | 0/1 | 0.00 | **25/35** | 3/5 | +0.01 | error TS6231: Could not resolve the path |
| `sre-node-leak` | `full` | r2 | TY | No | 0/1 | 0.00 | **28/35** | 4/5 | +3.01 | error TS6231: Could not resolve the path |
| `sre-node-leak` | `full` | r3 | TY | No | 0/1 | 0.00 | **18/35** | 2/5 | -6.99 | index.ts(25,77): error TS1005: ')' expec |
| `sre-node-leak` | `full` | r4 | TY | No | 0/1 | 0.00 | **25/35** | 3/5 | +0.01 | index.ts(221,37): error TS1005: ';' expe |
| `sre-node-leak` | `full` | r5 | TY | No | 0/1 | 0.00 | **27/35** | 3/5 | +2.01 | error TS6231: Could not resolve the path |
| `sre-node-leak` | `retrieved` | r1 | TY | No | 0/1 | 0.00 | **24/35** | 3/5 | -0.99 | error TS6231: Could not resolve the path |
| `sre-node-leak` | `retrieved` | r2 | TY | No | 0/1 | 0.00 | **24/35** | 3/5 | -0.99 | index.ts(325,34): error TS1128: Declarat |
| `sre-node-leak` | `retrieved` | r3 | TY | No | 0/1 | 0.00 | **26/35** | 3/5 | +1.01 | error TS6231: Could not resolve the path |
| `sre-node-leak` | `retrieved` | r4 | TY | No | N/A | 0.00 | **31/35** | 5/5 | +6.01 | error TS6231: Could not resolve the path |
| `sre-node-leak` | `retrieved` | r5 | TY | No | 0/1 | 0.00 | **22/35** | 2/5 | -2.99 | index.ts(169,33): error TS1109: Expressi |
| `sre-p99-regression` | `checklist` | r1 | PY | No | N/A | 0.00 | **28/35** | 4/5 | +3.01 | File "/tmp/tmphdlwdu13/solution.py", lin |
| `sre-p99-regression` | `checklist` | r2 | PY | No | N/A | 0.00 | **27/35** | 4/5 | +2.01 | Syntax errors detected |
| `sre-p99-regression` | `checklist` | r3 | PY | No | N/A | 0.00 | **20/35** | 3/5 | -4.99 | Syntax errors detected |
| `sre-p99-regression` | `checklist` | r4 | PY | No | N/A | 0.00 | **26/35** | 3/5 | +1.01 | Syntax errors detected |
| `sre-p99-regression` | `checklist` | r5 | PY | No | N/A | 0.00 | **25/35** | 4/5 | +0.01 | File "/tmp/tmp5d70_yyt/diagnostic_query_ |
| `sre-p99-regression` | `checklist_v2` | r1 | PY | Yes | N/A | 1.00 | **26/35** | 4/5 | +0.36 | Syntax ok |
| `sre-p99-regression` | `checklist_v2` | r2 | PY | No | N/A | 0.00 | **21/35** | 3/5 | -3.99 | File "/tmp/tmpuy0i89ls/solution.py", lin |
| `sre-p99-regression` | `checklist_v2` | r3 | PY | No | N/A | 0.00 | **25/35** | 3/5 | +0.01 | File "/tmp/tmpb08rdf9q/solution.py", lin |
| `sre-p99-regression` | `checklist_v2` | r4 | PY | No | N/A | 0.00 | **26/35** | 3/5 | +1.01 | File "/tmp/tmpag4iabev/app/models/db.py" |
| `sre-p99-regression` | `checklist_v2` | r5 | PY | No | N/A | 0.00 | **18/35** | 3/5 | -6.99 | File "/tmp/tmp6u392z5w/solution.py", lin |
| `sre-p99-regression` | `control` | r1 | PY | No | N/A | 0.00 | **20/35** | 2/5 | -4.99 | File "/tmp/tmpi3ksh9s2/solution.py", lin |
| `sre-p99-regression` | `control` | r2 | PY | No | N/A | 0.00 | **27/35** | 4/5 | +2.01 | File "/tmp/tmp2_vamst3/profiling/diagnos |
| `sre-p99-regression` | `control` | r3 | PY | No | N/A | 0.00 | **28/35** | 4/5 | +3.01 | /tmp/tmpupq5qae_/app/investigations/regr |
| `sre-p99-regression` | `control` | r4 | PY | Yes | N/A | 1.00 | **30/35** | 4/5 | +4.36 | Syntax ok |
| `sre-p99-regression` | `control` | r5 | PY | Yes | N/A | 1.00 | **19/35** | 3/5 | -6.64 | Syntax ok |
| `sre-p99-regression` | `full` | r1 | PY | Yes | N/A | 1.00 | **27/35** | 4/5 | +1.36 | Syntax ok |
| `sre-p99-regression` | `full` | r2 | PY | No | N/A | 0.00 | **29/35** | 4/5 | +4.01 | File "/tmp/tmpduis_rhw/solution.py", lin |
| `sre-p99-regression` | `full` | r3 | PY | No | N/A | 0.00 | **26/35** | 4/5 | +1.01 | File "/tmp/tmpnh9f7jrm/solution.py", lin |
| `sre-p99-regression` | `full` | r4 | PY | No | N/A | 0.00 | **28/35** | 3/5 | +3.01 | File "/tmp/tmp0vhg5v2g/solution.py", lin |
| `sre-p99-regression` | `full` | r5 | PY | No | N/A | 0.00 | **20/35** | 3/5 | -4.99 | File "/tmp/tmp35y85bzi/solution.py", lin |
| `sre-p99-regression` | `retrieved` | r1 | PY | Yes | N/A | 1.00 | **24/35** | 3/5 | -1.64 | Syntax ok |
| `sre-p99-regression` | `retrieved` | r3 | PY | No | N/A | 0.00 | **27/35** | 4/5 | +2.01 | Sorry: IndentationError: unindent does n |
| `sre-p99-regression` | `retrieved` | r4 | PY | No | N/A | 0.00 | **27/35** | 4/5 | +2.01 | File "/tmp/tmp1xmy4q_8/solution.py", lin |
| `sre-p99-regression` | `retrieved` | r5 | PY | No | N/A | 0.00 | **17/35** | 2/5 | -7.99 | File "/tmp/tmp5idkb7kw/config/database.p |

---

## Construct Validity & Residual Outlier Analysis

- **Mean Absolute Residual:** `4.35` points (on a 35-point scale).
- **Residual Standard Deviation:** `5.20` points.

### Runs with Largest Negative Residuals (Strict Judge / Under-Scored relative to execution):
- **`qa-checkout-e2e-ieee` (checklist_v2 r1):** Pass rate = `0.00`, Judge score = `13/35`, Residual = `-11.99`. *Judge finding:* Contains fatal syntax errors ('await page.route \'url\', handler' missing parentheses) repeated across the stub service, a placeholder throw in performFreshLogin, an undefined cust...
- **`sec-webhook-audit-ieee` (checklist r2):** Pass rate = `1.00`, Judge score = `14/35`, Residual = `-11.64`. *Judge finding:* Under-weights the race condition (MEDIUM) and error leakage (LOW) despite both being core requirements. Multiple serious flaws: the ReplayLedger falls back to the exact in-memory d...
- **`qa-ratelimiter-tdd-ieee` (checklist_v2 r1):** Pass rate = `0.00`, Judge score = `14/35`, Residual = `-10.99`. *Judge finding:* Synchronous `is_allowed` with clock patched through a private staticmethod (`limiter._clock = ...`), an initial append-before-check bug, and repeated admissions that the tests are ...

### Runs with Largest Positive Residuals (Forgiving Judge / Over-Scored relative to execution):
- **`sre-flaky-ci-ieee` (checklist_v2 r5):** Pass rate = `0.00`, Judge score = `35/35`, Residual = `+10.01`. *Judge finding:* Best overall: falsifiable hypothesis ranking, explicit timezone-neutral fixtures plus a parametrized timezone math test, a reusable await_condition helper with proper asyncio primi...
- **`sec-webhook-audit-ieee` (control r3):** Pass rate = `0.00`, Judge score = `35/35`, Residual = `+10.01`. *Judge finding:* Also enumerates 10 vulnerabilities with a table for the top issue and adds rate limiting and dependency-wiring concerns. Implementation is correct: atomic SQLite INSERT via PRIMARY...
- **`sec-webhook-audit-ieee` (checklist_v2 r3):** Pass rate = `0.00`, Judge score = `35/35`, Residual = `+10.01`. *Judge finding:* Identifies 10 vulnerabilities in clean severity order with 'attack surface' and 'fix' for each, and the corrected implementation correctly remediates all of them (raw-bytes-first H...

---

## Text for IEEE Paper: Construct Validity Section

```markdown
### Construct Validity & Execution Calibration
To assess whether the LLM judge evaluates functional engineering soundness rather than mere fluency, we executed a post-hoc execution calibration across N = 238 executable task runs under a 15-second subprocess timeout. In the pooled heterogeneous sample, aggregate execution pass rate correlates weakly with composite scores (Pearson r = 0.047, p = 0.473; Spearman ρ = 0.046, p = 0.481), driven by ambient dependency constraints in isolated sandboxes (e.g., Playwright or Redis). However, within self-contained environments, syntax compilation aligns strongly with the judge's Correctness subscore (e.g., sec-django-hardening: r = +0.616, p = 0.001; arch-godclass-refactor: r = +0.354, p = 0.090). Furthermore, residual outlier analysis reveals that the judge penalizes syntactically valid code when critical domain invariants (e.g., atomic replay handling) are violated, confirming that the multi-dimensional rubric measures architectural and security criteria beyond syntax.
```
