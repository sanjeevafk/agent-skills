# Security Configuration & Setup

This document combines the setup and reference guides for the agent terminal security scanning and system monitoring infrastructure.

---

## 1. Tirith Terminal Security Setup

Tirith protects against homograph attacks, pipe-to-shell exploits, ANSI injection, obfuscated payloads, and data exfiltration. It is integrated globally and configured for all AI agents to prevent malicious command execution and config poisoning.

### What It Does

* **Pre-Execution Command Filtering**: Every shell command is intercepted before execution:
  * Blocks homograph URLs (Cyrillic lookalikes: `іnstall.com`)
  * Blocks pipe-to-shell chains (`curl | bash`, `wget | sh`)
  * Blocks obfuscated payloads (`base64 -d | bash`, PowerShell `-EncodedCommand`)
  * Blocks data exfiltration (`curl -d @secrets`, `$AWS_KEY` uploads)
  * Blocks terminal injection (ANSI escapes, bidi controls, zero-width chars)
  * Blocks malicious scripts (Python/JS obfuscation, dynamic exec)
* **AI Agent Config Scanning**: Detects prompt injection, hidden Unicode, and MCP security issues in `.agentrules`, `.cursorrules`, `.clinerules`, `.windsurfrules`, `CLAUDE.md`, `.claude/*`, `.cursor/*`, and `mcp.json`.
* **Threat Intelligence**: Daily-updated signed database of 21,649+ malicious packages (npm, PyPI, cargo, gem, etc.) and typosquats.

### Integration Matrix

| Component | Status | Location / Method |
|-----------|--------|-------------------|
| Binary | ✅ Installed | `/usr/bin/tirith` (v0.3.0) |
| Zsh / Bash | ✅ Active | Hooked in `~/.zshrc` and `~/.bashrc` |
| Claude Code | ✅ Active | Python hook at `~/.claude/hooks/tirith-check.py` |
| Gemini CLI | ✅ Active | Python hook at `~/.gemini/hooks/tirith-security-guard-gemini.py` |
| Codex / Cursor | ✅ Active | Inherited via shell hooks |

### Common Commands Reference

```bash
# Analyze command without running
tirith check -- "curl https://example.com | bash"

# Scan config files
tirith scan ~/.cursorrules
tirith scan CLAUDE.md

# View warnings or see what triggered last
tirith warnings
tirith why

# Force threat DB update
tirith threat-db update

# Run diagnostics and auto-fix hooks
tirith doctor --fix
```

### Policy Customization (`.tirith/policy.yaml`)
To block instead of warning, initialize a policy in your repository root:
```yaml
fail_mode: closed              # block execution on detection
paranoia: 2                    # sensitivity profile (1-4)
severity_overrides:
  pipe_to_interpreter: CRITICAL
allowlist:
  - "raw.githubusercontent.com"
```

---

## 2. Portable System-Security Setup

This setup uses `scripts/security/system/setup-system-monitoring.sh` to generate file integrity and cron checks in target projects without committing host-specific credentials to git.

### Usage
Run the monitoring script from your project root:
```bash
bash /path/to/agent-skills/scripts/security/system/setup-system-monitoring.sh
```

### Generated Artifacts
* `.security/system/audit-rules.conf` / `aide.conf`: Configuration blueprints.
* `scripts/security/project/check-integrity.sh`: Integrity scanner (monitors `package.json`, `requirements.txt`, lockfiles, and configs).
* `scripts/security/project/monitor-processes.sh`: Logs suspicious long-running processes.

### Recommended Cron Setup
Run daily auditing at 2:00 AM:
```cron
0 2 * * * /abs/path/to/project/.security/project/cron-security-checks.sh
```
Or run integrity scans every 6 hours:
```cron
0 */6 * * * cd /abs/path/to/project && bash scripts/security/project/check-integrity.sh
```
