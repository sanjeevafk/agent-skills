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
| A2/A3/A4 ablation modes | **absent** — only `--tasks`/`--skills`/`--out` | all three flags + `ablate` subcommand |
| lines | 319 | 1,590 across 5 files |
| tests | 0 | 24 |
| frontmatter parsing | `split("---", 2)` — truncates on any `---` | YAML-aware, 5 tests incl. BOM/CRLF |
| produced `benchmarks/checklists_v2/` | no | **yes** |
| produced `benchmarks/ablations/` (A0–A5) | **no** | **yes** |

The Rust crate is the **only** tool in the repository capable of producing the
ablation conditions that back manuscript §8.4, and the only one that produced
the published `checklists_v2/` artifacts.

`scripts/compile_checklists_v2.py` is now marked **SUPERSEDED** in its module
docstring with the evidence above. It is retained only as a record of the
pre-Rust approach, not because anything depends on it — no script imports or
invokes it, and `skill_delivery_experiment.py:load_checklist_v2` reads the
committed `.txt` artifacts rather than calling it.

**Manuscript fix required.** §7.1 says "Compiler v0.2.0" without naming an
implementation language, while §8.7 names `scripts/laya_router.py` for the
router. That asymmetry invites the question *"which tool produced these
numbers?"*. Add one sentence to §7.1 naming the crate and stating that all
five delivery arms and all ablation conditions come from it.

### 4. The `checklist_v1` artifacts have no reproducing generator

`benchmarks/checklists_ieee/` (19 files, the `checklist_v1` experimental arm)
matches **neither** compiler:

| artifact set | reproduces with |
|---|---|
| `checklists_v2/` (18 files) | Rust `from-tasks` ✓ (16/17 shared, `tdd` drifted) |
| `ablations/*_a5_v1_bullets.md` | Rust `checklist_v1()` — but starts `[CHECKLIST GUIDELINES]`, unlike the committed v1 files |
| `checklists_ieee/*.txt` | **nothing in this repository** |

The committed v1 files begin with `# When to Activate`, whereas the Rust
`checklist_v1()` path begins `[CHECKLIST GUIDELINES]` and drops that section —
so they came from a different tool or an earlier version that no longer exists.

**The data itself is consistent with the paper.** Mean compiled size of the v1
artefacts is 501 tokens; adding the ~144-token task prompt gives ≈645, against
the 663 tokens reported in §6.2/Table 3. So the *numbers* are credible; only
the *generator* is missing.

**To resolve:** locate or reimplement the tool that produced
`checklists_ieee/`, or regenerate the `checklist_v1` arm with the Rust crate
and restate §8.1/§8.3 for that arm. As written, the `checklist_v1` arm cannot
be independently reproduced from the artifact.

## Automated guards

These issues are now caught automatically rather than by manual audit:

- `scripts/verify_compiled_artifacts.py` (CI job `artifact-reproducibility`) —
  recompiles the benchmark corpus and compares SHA-256 digests against
  `checklists_v2/manifest.json`. Fails on any drift not declared in its
  `KNOWN_EXCEPTIONS` table, and fails if a declared exception starts
  reproducing (which means the table is stale). Issues 1 and 2 above are
  declared there rather than silently skipped.
- `tests/test_paper_claims.py::TestCompilerManifest` — verifies source and
  compiled hashes against the manifest. Issues 1 and 2 above are pinned as a
  `strict=True` xfail; restoring the sources flips them back to passing.
- `tests/test_paper_claims.py` — pins N=396, the 17 completed tasks, all five
  per-arm means, and the §7.4 analytical arithmetic to the archived JSON.
- `.github/workflows/ci.yml` — `compiler-determinism` job compiles the same
  skill twice and requires byte-identical output; `rust-compiler` job runs
  `cargo clippy -- -D warnings`.

## Known limitations of the A4 type eraser

Characterised by `a4_known_gap_*` tests in `compiler.rs`, which pin current
behaviour deliberately so a future fix surfaces as a test failure to be
reviewed rather than silently changing recorded A4 artefacts:

- optional parameter annotations survive (`b?: number`)
- variable annotations survive (`const arr: string[] = []`)
- generic call type arguments survive (`new Map<string, number>()`)

Switch/case labels, type predicates (`x is T`), required parameters, return
types, and Python annotations are handled correctly and pinned by tests.

Practical impact is bounded: across the 18 evaluated skills the realised A4
magnitude is 0.9% (`security-review`) and 0.0% elsewhere, and §8.4 already
reports this as bounded below the noise floor rather than as a proven null.

## Test-count correction

§7.1 states "13 unit tests pin this behavior" for the A4 eraser. As of
2026-10-09 the crate has **24 tests, of which 14 are A4 tests** (9 behavioural
guards + 3 known-gap characterisation tests + 2 added in this audit). Update
the manuscript figure to match.

## Note on token measurement

Prompt and output token figures throughout the paper are
`len(text) // 4` character-count estimates, not real tokenizer output
(`estimate_tokens` is duplicated across five scripts in this repo). The 680-token
and 30.0% numbers inherit that approximation. Replacing it with a real
tokenizer would not change the conclusion, but the paper should not describe
these as measured token counts without noting it.