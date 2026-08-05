# Rule: Git & Remote Documentation Policy

- **Universal Rule**: NEVER commit internal planning documents, private roadmaps, or working notes to git or push them to remote repositories.
- **Allowed Remote Docs**: Only public-facing architectural standards, system technical specifications, or user-facing explanatory documentation may be committed and pushed to remote repositories.
- **Local Internal Storage**: Store internal planning documents in `docs/internal/` or using the `*.internal.md` naming convention, which must be protected by `.gitignore` to remain strictly local and uncommitted.
