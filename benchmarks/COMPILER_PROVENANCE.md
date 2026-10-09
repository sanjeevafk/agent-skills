# Compiler Provenance & Reproducibility Audit

Recorded findings from recompiling the benchmark skill corpus with
`crates/skills-compiler` at **v0.2.0** and diffing against the committed
`benchmarks/checklists_v2/manifest.json` (stamped `compiler_version: 0.1.0`,
2026-08-29).

Reproduce with:

```bash
cargo build --release --manifest-path crates/skills-compiler/Cargo.toml
./crates/skills-compiler/target/release/skills-compiler from-tasks \
    --tasks benchmarks/tasks_ieee.json --out-dir /tmp/audit
```

## Headline: the 30.0% claim survives

| quantity | value |
|---|---|
| source tokens | 38,685 |
| compiled tokens | 26,950 |
| aggregate reduction | **30.33%** |
| mean per-skill full | 2,149.2 |
| mean per-skill v2 | 1,497.2 |
| mean delta per skill/turn | 651.9 |

Manuscript §8.2 states 30.0% (2,270 → 1,590, Δ 680). The small discrepancy is
expected: the manifest averages over 18 skills including `debugging-code`,
whereas Table 3's per-arm figures come from the 17 tasks that completed.

## v0.1.0 → v0.2.0 produced identical output

Recompiling all 18 benchmark skills at v0.2.0 yields **16 of 17 shared
artifacts byte-identical** (SHA-256 match against the manifest).

The v0.2.0 release adds the A4 `--no-types` type-erasure path. It is additive
behind an opt-in flag (`keep_types` defaults to `true`), so it does not perturb
default `v2` compilation. The version bump is therefore benign.

Spot-check that A4 is live in v0.2.0:

```bash
./crates/skills-compiler/target/release/skills-compiler compile \
    --input skills/security-review/SKILL.md --no-types --output /tmp/a4.txt
# 3123 -> 2438 tokens (21.9%)
```

## Open issues

### 1. `skills/tdd/SKILL.md` drifted after the benchmark run

| | sha256 |
|---|---|
| recorded in manifest | `1d0a1439aefa…` |
| on disk now | `93ea419b76e9…` |

The skill file was edited between the August 2026 experiment run and now, so
its recorded reduction (**16.63%**) no longer reproduces from the current
source. Recompiling the *current* file gives **46.00%**.

The `tdd` skill is the source of the paper's one robust RQ4 finding
(tracer-bullet syntax removal, Δ = −8.50, n=6, §8.4), so its per-skill token
figures matter more than the other 17.

**To resolve:** restore `skills/tdd/SKILL.md` to the recorded `1d0a1439…`
version, or re-run the `tdd` cells against the current source and restate the
number. Until then, treat the 16.63% figure as historical.

### 2. `skills/debugging-code/` is missing from the tree

The v0.2.0 build reports:

```
❌ debugging-code: source not found in skills/
```

The manifest records it (2,903 source → 1,434 compiled tokens, 50.60%
reduction), and it backs the `sre-node-leak-ieee` task in the benchmark suite.
That task cannot currently be re-run.

**To resolve:** restore the skill directory, or formally drop the task from the
18-task suite and restate §5's counts (currently "18 defined, 17 completed").

### 3. Two compilers, divergent output

| | `scripts/compile_checklists_v2.py` | `crates/skills-compiler` (Rust) |
|---|---|---|
| A4 type erasure | **absent** (1 incidental match) | 28 references, 9 tests |
| lines | 319 | 1,590 across 5 files |
| tests | 0 | 19 |
| frontmatter parsing | `split("---", 2)` — truncates on any `---` | YAML-aware, 5 tests incl. BOM/CRLF |
| produced the paper's artifacts | no | **yes** |

The Python script cannot produce the A4 ablation condition at all, and its
docstring advertises "~40-50% token reduction" against the paper's 30.0%.
Retaining both invites confusion about which method generated which result.

**Recommendation:** make the Rust crate the single compiler and delete
`scripts/compile_checklists_v2.py`.

## Automated guards

These issues are now caught automatically rather than by manual audit:

- `tests/test_paper_claims.py::TestCompilerManifest` — verifies source and
  compiled hashes against the manifest. Issues 1 and 2 above are pinned as a
  `strict=True` xfail; restoring the sources flips them back to passing.
- `tests/test_paper_claims.py` — pins N=396, the 17 completed tasks, all five
  per-arm means, and the §7.4 analytical arithmetic to the archived JSON.
- `.github/workflows/ci.yml` — `compiler-determinism` job compiles the same
  skill twice and requires byte-identical output; `rust-compiler` job runs
  `cargo clippy -- -D warnings`.

## Note on token measurement

Prompt and output token figures throughout the paper are
`len(text) // 4` character-count estimates, not real tokenizer output
(`estimate_tokens` is duplicated across five scripts in this repo). The 680-token
and 30.0% numbers inherit that approximation. Replacing it with a real
tokenizer would not change the conclusion, but the paper should not describe
these as measured token counts without noting it.