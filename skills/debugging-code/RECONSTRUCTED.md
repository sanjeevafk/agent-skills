# Superseded

This note is kept only so the file it describes is not mistaken for live
documentation. It is **no longer accurate**.

It originally recorded that `skills/debugging-code/SKILL.md` was absent from
the repository and that its source had been *reconstructed* by prepending
YAML frontmatter to the surviving compiled artifact — a lossy stand-in, since
the compiler prunes narrative prose (`keep_narrative = false`) and the original
bytes could not be recovered.

That is no longer the case. The genuine benchmark-time source was found
verbatim in `benchmarks/ablations/debugging-code_a0_full.md`, whose A0 ablation
condition is a raw passthrough of the benchmark-time input. It is 11,613 bytes
and matches the manifest's recorded `source_sha256` (`cb00d683…`) exactly.

The file now in place as `SKILL.benchmark-time.md`:

- reproduces the recorded compiled artifact byte-for-byte, and
- matches the recorded *source* hash — so the full narrative prose is
  recovered, not just what the compiler kept.

The live `skills/debugging-code/SKILL.md` is the post-run condensation, which
is what current tooling uses. See `skills/RECOVERY.md` for the full account and
for how the checks resolve a source.