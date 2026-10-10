# Reconstructed 2026-10-10

`skills/debugging-code/SKILL.md` was absent from the repository but its
compiled artifact survived in `benchmarks/checklists_v2/debugging-code.txt`,
verified byte-identical (sha256 46384903...) against the manifest recorded at
experiment time.

The source above was reconstructed by prepending YAML frontmatter to that
artifact. This is faithful at the level the benchmark consumed: recompiling
it with crates/skills-compiler v0.2.0 reproduces the recorded artifact
byte-for-byte, confirmed by hash. Narrative prose pruned by the compiler
(~50.6% of the original) is NOT recoverable, so the original file's token
count cannot be restored; the benchmark's 2,903-token figure comes from the
manifest, not from this file.
