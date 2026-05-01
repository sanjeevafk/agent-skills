## Installed Skills

```text
ci-cd-pipeline-builder
code-refactor
code-review-and-quality
code-reviewer
code-review-expert
dependency-auditor
feature-planning
find-skills
fullstack-feature-scaffold
git-pushing
git-workflow-and-versioning
gsd-add-phase
gsd-add-tests
gsd-add-todo
gsd-audit-milestone
gsd-autonomous
gsd-check-todos
gsd-cleanup
gsd-complete-milestone
gsd-debug
gsd-discuss-phase
gsd-do
gsd-execute-phase
gsd-health
gsd-help
gsd-insert-phase
gsd-join-discord
gsd-list-phase-assumptions
gsd-map-codebase
gsd-new-milestone
gsd-new-project
gsd-note
gsd-pause-work
gsd-plan-milestone-gaps
gsd-plan-phase
gsd-progress
gsd-quick
gsd-reapply-patches
gsd-remove-phase
gsd-research-phase
gsd-resume-work
gsd-set-profile
gsd-settings
gsd-stats
gsd-ui-phase
gsd-ui-review
gsd-update
gsd-validate-phase
gsd-verify-work
nextjs-15-expert
performance-profiler
planning-and-task-breakdown
pr-review-expert
python-ts-interop-mcp-builder
security-and-hardening
sentry-android-sdk
sentry-browser-sdk
sentry-cloudflare-sdk
sentry-cocoa-sdk
sentry-code-review
sentry-create-alert
sentry-dotnet-sdk
sentry-elixir-sdk
sentry-feature-setup
sentry-fix-issues
sentry-flutter-sdk
sentry-go-sdk
sentry-nestjs-sdk
sentry-nextjs-sdk
sentry-node-sdk
sentry-otel-exporter-setup
sentry-php-sdk
sentry-pr-code-review
sentry-python-sdk
sentry-react-native-sdk
sentry-react-sdk
sentry-ruby-sdk
sentry-sdk-setup
sentry-sdk-skill-creator
sentry-sdk-upgrade
sentry-setup-ai-monitoring
sentry-svelte-sdk
sentry-workflow
skill-security-auditor
supabase-expert
tailwind-radix-expert
tech-debt-tracker
test-driven-development
testing-loop-master
```

## Best Way To Trigger Them

Use explicit wording. This is the most reliable pattern:

```text
Use the <skill-name> skill for this task.
Task: <what the operator want>.
Output: <expected format>.
Constraints: <important rules>.
```

For multiple skills:

```text
Use skills: <skill-a>, <skill-b>, <skill-c>.
Primary skill: <skill-a>.
Then implement and verify with tests.
```

## Prompt Triggers Cheat Sheet

- Code review: `Use code-reviewer` or `Use code-review-and-quality` or `Use pr-review-expert`
- Planning: `Use planning-and-task-breakdown` or `Use feature-planning`
- Refactor: `Use code-refactor to rename/replace across files`
- Testing: `Use testing-loop-master` or `Use test-driven-development`
- Next.js: `Use nextjs-15-expert`
- Supabase/RLS/Auth: `Use supabase-expert` and `security-and-hardening`
- Tailwind/Radix UI: `Use tailwind-radix-expert`
- Python/TS contracts: `Use python-ts-interop-mcp-builder`
- CI/CD: `Use ci-cd-pipeline-builder`
- Performance: `Use performance-profiler`
- Dependency risk: `Use dependency-auditor`
- Security scan for skills/plugins: `Use skill-security-auditor`
- Tech debt analysis: `Use tech-debt-tracker`
- Sentry work: `Use sentry-workflow` or SDK-specific skill like `sentry-nextjs-sdk`, `sentry-node-sdk`, etc.
- Skill discovery: `Use find-skills`
- Git workflow: `Use git-workflow-and-versioning` and `git-pushing`
- GSD flows: `Use gsd-<name>` (example: `gsd-plan-phase`, `gsd-execute-phase`, `gsd-debug`, `gsd-verify-work`)
