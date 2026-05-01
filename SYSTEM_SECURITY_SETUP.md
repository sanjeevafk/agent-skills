# System Security Setup (Portable Template)

This repo includes a portable system-security setup script:

- `scripts/security/system/setup-system-monitoring.sh`

## Purpose

Generate reproducible security monitoring assets for any target project while keeping machine-specific runtime state out of git.

## Run

From a target project root:

```bash
bash /path/to/agent-skills/scripts/security/system/setup-system-monitoring.sh
```

Or pass a project path explicitly:

```bash
bash /path/to/agent-skills/scripts/security/system/setup-system-monitoring.sh /abs/path/to/project
```

## What It Generates (in target project)

- `.security/system/audit-rules.conf`
- `.security/system/aide.conf`
- `.security/project/cron-security-checks.sh`
- `.security/project/hashes/`
- `.security/project/logs/`
- `scripts/security/project/check-integrity.sh`
- `scripts/security/project/monitor-processes.sh`
- `.git/hooks/pre-commit` (chains existing hook, non-destructive)

## Cron Recommendation

Daily full checks at 2 AM:

```cron
0 2 * * * /abs/path/to/project/.security/project/cron-security-checks.sh
```

Optional integrity-only every 6 hours:

```cron
0 */6 * * * cd /abs/path/to/project && bash scripts/security/project/check-integrity.sh
```

## Source-of-Truth Rules

Commit:
- `scripts/security/system/setup-system-monitoring.sh`
- docs and policy templates

Do not commit:
- `.security/` runtime outputs
- host-specific logs, hash baselines, generated configs
