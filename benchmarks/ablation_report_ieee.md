### Table 2: Structural Component Ablation Scores & Token Magnitudes ($N=54$, 6 Tasks)

| Domain | Task ID | $A_0$ (Full) | $A_1$ (Balanced) | $A_2$ (No Examples) | $A_3$ (No Tables) | $A_4$ (No Types) | $A_5$ (Aggressive Bullets) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| Security & Auditing | `sec-webhook-audit-ieee` | 22.80 | 30.80 | 22.67 | 20.67 | 22.67 | 25.60 |
| SRE & Debugging | `sre-node-leak-ieee` | 24.60 | 23.00 | 23.00 | 18.00 | 24.00 | 23.00 |
| Testing & QA | `test-tdd-payment-state-machine-ieee` | 21.80 | 20.33 | 11.83 | 14.33 | 23.67 | 16.20 |
| Architecture & Refactoring | `arch-hexagonal-refactor-ieee` | 29.60 | 22.33 | 13.33 | 7.33 | 16.33 | 27.20 |
| DevOps & Cloud | `devops-multi-stage-docker-ieee` | 27.40 | 17.33 | 19.33 | 19.00 | 20.33 | 23.40 |
| Databases & Persistence | `db-postgres-partitioning-ieee` | 23.40 | 19.00 | 21.33 | 21.67 | 22.00 | 22.80 |

### Table 3: Observed Structural Sensitivity Matrix ($S_c$) Across Domains

| Domain | Narrative ($S_{\text{narr}}$) | Examples ($S_{\text{ex}}$) | Tables ($S_{\text{tbl}}$) | Types/Interfaces ($S_{\text{type}}$) | Compound Stripping ($S_{\text{comp}}$) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Security & Auditing | -0.260 | +0.264 | +0.329 | +0.264 | +0.169 |
| SRE & Debugging | +0.070 | +0.000 | +0.217 | -0.043 | +0.000 |
| Testing & QA | +0.072 | +0.418 | +0.295 | -0.164 | +0.203 |
| Architecture & Refactoring | +0.325 | +0.403 | +0.672 | +0.269 | -0.218 |
| DevOps & Cloud | +0.581 | -0.115 | -0.096 | -0.173 | -0.350 |
| Databases & Persistence | +0.232 | -0.123 | -0.140 | -0.158 | -0.200 |


### Exploratory Inferential Statistics (Blocked by Task, $N=6$ Pairs)

| Comparison | Mean Diff ($\Delta Q$) | Std | Paired $t$-stat | Raw $p$ | Holm-Bonf. $p_{\text{adj}}$ | Cohen's $d_z$ [95% CI] | Sig ($\alpha=0.05$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| A2 (No Examples) vs A1 | +3.55 | 5.54 | 1.571 | 0.1770 | 0.5311 | 0.64 [-0.24, 1.52] | No |
| A3 (No Tables) vs A1 | +5.30 | 6.78 | 1.914 | 0.1138 | 0.4552 | 0.78 [-0.13, 1.70] | No |
| A4 (No Types) vs A1 | +0.63 | 5.10 | 0.304 | 0.7731 | 0.7731 | 0.12 [-0.68, 0.93] | No |
| A5 (Aggressive Bullets) vs A1 | -0.90 | 4.78 | -0.461 | 0.6640 | 1.0000 | -0.19 [-1.00, 0.62] | No |