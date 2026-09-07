# Ablation Report (corrected, N=69, compiler v0.2.0, tdd-A2 n=6)

Same-harness (24k judge window) cell means. =A1 marks byte-identical prompts (test-retest resamples). Reference = direct same-task A1 where available, else identical-prompt pool.

| Task | A1 ref (n) | A2 | A3 | A4 |
| :--- | :---: | :---: | :---: | :---: |
| `sec-webhook-audit-ieee` | 20.67 (n=3) | 22.67 (68.6%) | 20.67 (=A1) | 22.67 (0.9%) |
| `sre-node-leak-ieee` | 21.00 (n=6) | 23.00 (57.4%) | 18.00 (=A1) | 24.00 (=A1) |
| `test-tdd-payment-state-machine-ieee` | 20.33 (n=3) | 11.83 (18.5%, n=6) | 14.33 (=A1) | 23.67 (=A1) |
| `arch-hexagonal-refactor-ieee` | 22.33 (n=3) | 13.33 (26.8%) | 7.33 (=A1) | 16.33 (=A1) |
| `devops-multi-stage-docker-ieee` | 17.33 (n=3) | 19.33 (98.9%) | 19.00 (=A1) | 20.33 (=A1) |
| `db-postgres-partitioning-ieee` | 19.00 (n=3) | 21.33 (60.7%) | 21.67 (26.3%) | 22.00 (=A1) |

Pooled identical-prompt residual sd: 6.09 (n=42).

True-intervention deltas (intervention mean - reference mean):
- sec-webhook-audit-ieee a2_no_examples (n=3): 22.67 - 20.67 = +2.00
- sec-webhook-audit-ieee a4_no_types (n=3): 22.67 - 20.67 = +2.00
- sre-node-leak-ieee a2_no_examples (n=3): 23.00 - 21.00 = +2.00
- test-tdd-payment-state-machine-ieee a2_no_examples (n=6): 11.83 - 20.33 = -8.50
- arch-hexagonal-refactor-ieee a2_no_examples (n=3): 13.33 - 22.33 = -9.00
- devops-multi-stage-docker-ieee a2_no_examples (n=3): 19.33 - 17.33 = +2.00
- db-postgres-partitioning-ieee a2_no_examples (n=3): 21.33 - 19.00 = +2.33
- db-postgres-partitioning-ieee a3_no_tables (n=3): 21.67 - 19.00 = +2.67
