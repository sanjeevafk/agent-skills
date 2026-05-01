# Contributing

Thanks for helping improve `agent-skills`.

## What to Contribute

- Skill recommendations for the curated set
- New docs or setup improvements
- Better defaults for cross-agent compatibility
- Bug fixes in scripts (`global-skills.sh`, installers, security templates)

## Submitting a Change

1. Fork the repository.
2. Create a feature branch.
3. Make focused changes with clear commit messages.
4. Test shell scripts with `bash -n`.
5. Open a pull request with:
- what changed
- why it helps
- any migration notes

## Skill Proposal Checklist

When proposing a new curated skill, include:

- Skill source repository
- Why it should be curated by default
- Typical usage pattern
- Any risk or maintenance concerns

## Style Guidelines

- Keep docs public-facing and environment-agnostic.
- Avoid hardcoded user paths.
- Keep scripts idempotent and safe to re-run.
- Prefer additive, backwards-compatible changes when possible.

## Local Validation

Example checks before PR:

```bash
bash -n global-skills.sh
bash -n install-global-skills.sh
bash -n codex-exclusive-skills.sh
```

