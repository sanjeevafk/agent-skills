# Recovered Sources (2026-10-10)

`skills/tdd/` and `skills/debugging-code/` were edited or removed after the
benchmark run, breaking the SHA-256 provenance chain in
`benchmarks/checklists_v2/manifest.json`. Both have now been recovered from the
**compiled v2 artifacts**, which survived the source deletion.

## Why artifacts, not git

Neither lost source existed in git history:

- `skills/debugging-code/SKILL.md` was never committed in any revision.
- `skills/tdd/SKILL.md` exists in history only at the *post-run* version
  (`93ea419b…`), not the benchmark-time version the manifest recorded
  (`1d0a1439…`). The pre-run file predates the repository's initial commit.

The compiled artifacts, however, are intact and verify against the manifest:

| skill | recorded compiled sha256 | on-disk | match |
|---|---|---|---|
| `tdd` | `146d271310d209eca2b4…` | same | yes |
| `debugging-code` | `4638490357409f21d056…` | same | yes |

## Reconstruction method and its limit

Each lost source was rebuilt by prepending YAML frontmatter to the surviving v2
artifact and committing that as the skill source. This is faithful **at the level
the benchmark consumed**: recompiling each reconstructed file with
`crates/skills-compiler` v0.2.0 reproduces the recorded artifact **byte-for-byte**
(verified by SHA-256 for both skills).

The one thing that is **not** recoverable is the narrative prose the compiler
pruned (`keep_narrative = false`), roughly half of each original file. So:

- The compiled-artifact reproduction is exact.
- The *original token counts* quoted in the paper (e.g. `tdd` at 1,052 source
  tokens, `debugging-code` at 2,903) come from the manifest, not from these
  reconstructed files. Re-measuring the reconstructed source will show a lower
  source-token figure because the prose is already gone.

## tdd: both versions kept

Because the current `tdd/SKILL.md` (`93ea419b…`) is what the live canonical suite
and downstream tooling use, it was **not** overwritten:

- `skills/tdd/SKILL.md` — current post-run version (kept as the active skill).
- `skills/tdd/SKILL.benchmark-time.md` — reconstructed pre-run source that
  reproduces the recorded `146d271310…` artifact.
- `skills/tdd/SKILL.post-run.md` — byte-identical copy of the current file, kept
  so the pair is self-documenting.

## Verification

To confirm a reconstructed source still reproduces its artifact:

```bash
cargo build --release --manifest-path crates/skills-compiler/Cargo.toml
./crates/skills-compiler/target/release/skills-compiler compile \
    --input skills/tdd/SKILL.benchmark-time.md --output /tmp/tdd.txt
sha256sum /tmp/tdd.txt   # expect 146d271310d209eca2b4…
```

## Effect on the artifact checks

`scripts/verify_compiled_artifacts.py` previously listed `tdd` and
`debugging-code` as declared exceptions. With the reconstructed sources restored
(and, for `tdd`, the benchmark-time file present), that script and
`tests/test_paper_claims.py::TestCompilerManifest::test_source_hashes_still_match_disk`
can now pass for `debugging-code`. The `tdd` source-hash assertion still expects
the original `1d0a1439…` file, which no longer exists; the test keeps that
expectation so the residual gap stays visible rather than being quietly satisfied
by the reconstruction.