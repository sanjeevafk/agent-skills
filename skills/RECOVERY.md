# Recovered Sources

`skills/tdd/` and `skills/debugging-code/` were edited after the benchmark run,
breaking the SHA-256 provenance chain in
`benchmarks/checklists_v2/manifest.json`. **Both benchmark-time sources are now
recovered byte-for-byte.** The manifest's `source_sha256` for all 18 benchmark
skills matches a file on disk, and all 18 compiled artifacts reproduce.

## Where the sources came from

Not git. Neither benchmark-time source was ever committed: local history begins
2026-10-08, weeks after the 2026-08-24 run.

| skill | recovered from | bytes | sha256 |
|---|---|---:|---|
| `tdd` | `benchmarks/ablations/tdd_a0_full.md` | 4211 | `1d0a1439…` |
| `debugging-code` | `benchmarks/ablations/debugging-code_a0_full.md` | 11613 | `cb00d683…` |

The A0 ablation condition is a **raw passthrough** of the benchmark-time input,
so those files *are* the sources the experiment consumed. Both match the v1
manifest's `source_sha256` and `source_bytes` exactly.

An earlier attempt reconstructed these sources by prepending frontmatter to the
surviving v2 artifacts. That reconstruction is superseded — it was lossy (it
could not recover the prose the compiler prunes, `keep_narrative = false`) and
its hash never matched the manifest. The files now in place are the genuine
sources, so the residual gap the reconstruction left is closed.
`skills/debugging-code/RECONSTRUCTED.md` records the same supersession for that
skill and is now a pointer here rather than a stale claim.

The other 16 skills needed nothing: their live `SKILL.md` still hashes exactly
to what the manifest recorded.

## tdd: both versions kept

The live `skills/tdd/SKILL.md` is a genuine post-run **rewrite**, not a
condensation — it re-frames the skill around pre-agreed test seams and
cross-references other skills. It is what the canonical suite and downstream
tooling use, so it was not reverted.

- `skills/tdd/SKILL.md` — current post-run version (the active skill).
- `skills/tdd/SKILL.benchmark-time.md` — the recovered benchmark-time source,
  4211 bytes, SHA-256 `1d0a1439…`, matching the manifest.

An earlier `SKILL.post-run.md` byte-identical copy of the active file was
removed; `SKILL.md` already is that version, so the duplicate carried no
information.

`skills/debugging-code/SKILL.md` is likewise a post-run condensation; its
recorded source sits beside it as `SKILL.benchmark-time.md`.

## How the checks consume these

Both `scripts/verify_compiled_artifacts.py` and
`tests/test_paper_claims.py::TestCompilerProvenance::test_source_hashes_still_match_disk`
resolve a skill's source by trying the live path first, then the sibling
`SKILL.benchmark-time.md`.

A candidate is accepted **only** when its SHA-256 equals the manifest's recorded
`source_sha256`. This is deliberately stricter than "recompiles to the same
artifact": a reconstruction that reproduced the artifact while carrying the
wrong source bytes would be rejected. That distinction is what made the earlier
reconstruction insufficient, and it is why this one is sufficient.

## Verification

```bash
uv run python scripts/verify_compiled_artifacts.py
# 18/18 artifacts reproduce byte-for-byte; 0 documented exceptions remain.
```

`KNOWN_EXCEPTIONS` in the verifier is now empty. It is retained as a structure
so that any future drift must be declared explicitly rather than silently
skipped, and the script still fails if a declared exception starts reproducing.