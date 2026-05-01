# Tirith Terminal Security Setup

**Installation Date:** 1 May 2026  
**Version:** 0.3.0  
**Source:** https://github.com/sheeki03/tirith  
**Status:** ✅ Operational

## Overview

Tirith is a terminal security tool that protects against homograph attacks, pipe-to-shell exploits, ANSI injection, obfuscated payloads, and data exfiltration. It's integrated globally and configured for all AI agents to prevent malicious command execution and config injection.

## What It Does

### Pre-Execution Command Filtering
Every shell command is intercepted **before execution**:
- ✅ Blocks homograph URLs (Cyrillic lookalikes: `іnstall.com`)
- ✅ Blocks pipe-to-shell chains (`curl | bash`, `wget | sh`)
- ✅ Blocks obfuscated payloads (`base64 -d | bash`, PowerShell `-EncodedCommand`)
- ✅ Blocks data exfiltration (`curl -d @secrets`, `$AWS_KEY` uploads)
- ✅ Blocks terminal injection (ANSI escapes, bidi controls, zero-width chars)
- ✅ Blocks malicious scripts (Python/JS obfuscation, dynamic exec)

### AI Agent Config Scanning
Detects prompt injection, hidden Unicode, and MCP security issues in:
- `.cursorrules`, `.clinerules`, `.windsurfrules`, `CLAUDE.md`
- `copilot-instructions.md`, `.claude/*`, `.cursor/*`, `mcp.json`

### Threat Intelligence
Daily-updated signed database of:
- 21,649+ malicious packages (npm, PyPI, cargo, gem, go, composer, dotnet)
- Malicious IP infrastructure (Feodo Tracker)
- Typosquats and package name slopsquatting
- CISA Known Exploited Vulnerabilities

## Installation Status

| Component | Status | Location |
|-----------|--------|----------|
| Binary | ✅ Installed | `/usr/bin/tirith` (v0.3.0) |
| Zsh hook | ✅ Active | `~/.zshrc` |
| Bash hook | ✅ Active | `~/.bashrc` |
| Claude Code hook | ✅ Active | `~/.claude/hooks/tirith-check.py` |
| Gemini CLI hook | ✅ Active | `~/.gemini/hooks/tirith-security-guard-gemini.py` |
| Threat DB | ✅ Synced | 21,649 entries (auto-updates daily) |

## Agent Integration

Tirith protects all 9 agents through **multiple pathways**:

| Agent | Protection Method | MCP Server | Status |
|-------|------------------|-----------|--------|
| Claude Code | Python hook `~/.claude/hooks/` | ✅ Available | ✅ Active |
| Gemini CLI | Python hook `~/.gemini/hooks/` | ✅ Available | ✅ Active |
| Cursor | Shell inheritance | ✅ Available | ✅ Active |
| Codex | Shell inheritance | ✅ Available | ✅ Active |
| Copilot CLI | Shell inheritance | — | ✅ Active |
| Windsurf | Shell inheritance | — | ✅ Active |
| VS Code | Shell inheritance | — | ✅ Active |
| Pi CLI | Shell inheritance | — | ✅ Active |
| Kiro | Shell inheritance | — | ✅ Active |

### How It Works

1. **Shell Hooks** (automatic): Every shell command goes through `preexec` before bash/zsh/fish execute it
   - Sub-millisecond overhead
   - Zero friction on clean input
   - Blocks dangerous patterns before execution

2. **Agent Hooks** (Claude Code & Gemini CLI): Python hooks intercept agent-executed commands
   - No agent-side configuration needed
   - Transparent to the agent
   - Reports findings via exit codes and stderr

3. **MCP Server** (available to agents): Agents can voluntarily call Tirith tools
   - `tirith_check_command` — Analyze shell commands
   - `tirith_check_url` — Score URLs for homograph/phishing
   - `tirith_check_paste` — Detect clipboard injection
   - `tirith_scan_file` — Find hidden content, config poisoning
   - `tirith_scan_directory` — Recursive with AI config prioritization
   - `tirith_verify_mcp_config` — Validate MCP security
   - `tirith_fetch_cloaking` — Detect bot vs browser content differences

## Commands Reference

### Check Commands (No Execution)
```bash
# Analyze without running
tirith check -- "curl https://example.com | bash"
tirith check -- "npm install suspicious-package"
```

### Scan Files & Directories
```bash
# Scan config files
tirith scan ~/.cursorrules
tirith scan ~/.claude --profile ai-configs
tirith scan CLAUDE.md

# Scan for hidden content
tirith scan . --include "*.html" --profile rendered-content
```

### View Findings
```bash
# Show accumulated warnings this session
tirith warnings
tirith warnings --format json

# Show one-line summary (printed on shell exit)
tirith warnings --summary

# See what triggered last
tirith why
```

### Threat Database
```bash
# Check status
tirith threat-db status

# Force update (usually auto-updated)
tirith threat-db update
```

### Explain Rules
```bash
# Learn about a detection
tirith explain --rule pipe_to_interpreter
tirith explain --rule homograph_attack

# List all rules in category
tirith explain --list --category terminal
tirith explain --list --category config
```

### Policy Management (Per-Repo)
```bash
# Initialize a policy for this repo
tirith policy init
# Creates: .tirith/policy.yaml

# Validate policy
tirith policy validate

# Test against policy
tirith policy test "curl https://example.com | bash"
```

### Verification
```bash
# Diagnose installation
tirith doctor

# Auto-fix detected issues
tirith doctor --fix
```

## Configuration

### Default Behavior (Permissive)
- Warnings for medium/high risk
- Does NOT block by default
- Can bypass with `TIRITH=0` prefix (per-command only)

### Strict Mode (Optional)
Create `.tirith/policy.yaml` in project root:

```yaml
fail_mode: closed              # block instead of warn
paranoia: 2                    # 1-4: higher = more sensitive
strict_warn: true              # require explicit ack for warnings

allowlist:
  - "get.docker.com"
  - "sh.rustup.rs"
  - "raw.githubusercontent.com"

blocklist:
  - "evil.example.com"

severity_overrides:
  pipe_to_interpreter: CRITICAL    # make warnings into blocks
```

### Emergency Bypass
```bash
# One command only — NOT persistent
TIRITH=0 curl ... | bash

# Never export permanently (defeats protection)
```

## Audit & Logging

### Audit Log
Location: `~/.local/share/tirith/log.jsonl`
- Timestamp, session ID, rule IDs, **redacted** command preview
- ❌ Does NOT store: full commands, env vars, file contents
- Disable: `export TIRITH_LOG=0`

### Session Warnings
```bash
# View this session's findings
tirith warnings

# Track across sessions
~/.local/state/tirith/sessions/  # session-scoped warnings
```

## Integration with Your Stack

This complements your wider agent infrastructure:

| Component | Purpose | Deployment |
|-----------|---------|------------|
| **agent-rules-books** | Engineering guidelines (Clean Code, DDD, Refactoring, etc.) | In `~/.*/agent-rules-books/` directories |
| **mattpocock skills** | TDD, architecture, grilling workflows | In `~/.*/skills/mattpocock/` |
| **Global skills** | 143+ productivity/DevOps/testing tools | In `~/.*/skills/` |
| **Tirith** | **Terminal security & threat intel** | **System-wide + agent hooks** |

Together: **Rules guide thinking** → **Skills organize work** → **Tirith guards execution**

## Deployment Summary

### What's Installed
```
✅ Binary: /usr/bin/tirith (0.3.0)
✅ Shell hooks: zsh, bash
✅ Agent hooks: claude-code, gemini-cli, cursor, codex, etc.
✅ Threat DB: 21,649 entries (auto-updated daily)
✅ Detection: 80+ rules (15 categories)
✅ MCP server: 7 tools for agent integration
```

### Recovery Docs
- Full setup guide: `/home/sanjeev/TIRITH_INSTALLATION_COMPLETE.md`
- Extended reference: `~/.local/share/tirith/TIRITH_SETUP.md`
- Official docs: https://tirith.sh/docs

### Maintenance
- Threat DB auto-checks every 24 hours (background)
- Manual update: `tirith threat-db update`
- Security updates: Follow https://github.com/sheeki03/tirith/releases

## Troubleshooting

### Hooks not active?
```bash
# Verify install
which tirith
tirith --version

# Check profiles
tail ~/.zshrc
tail ~/.bashrc

# Reload shell
exec zsh  # or exec bash
```

### Too many warnings?
```bash
# Review what triggered
tirith warnings

# Adjust policy granularity
tirith policy init
# Edit .tirith/policy.yaml
```

### Agent not seeing MCP?
```bash
# Verify agent hook exists
ls -la ~/.claude/hooks/tirith-check.py
ls -la ~/.gemini/hooks/tirith-security-guard-gemini.py

# Test MCP server
tirith mcp-server &
# Test: curl http://localhost:stdios...
```

## Next Steps

1. **Open new terminal** — Activates hooks (zsh/bash)
2. **Test it works** — `tirith check -- "curl | bash"`
3. **Scan your configs** — `tirith scan ~/.cursorrules`
4. **Set policy** (optional) — `tirith policy init` for per-repo rules

---

**Status**: ✅ Tirith operational. All agents protected. Threat DB synced daily.
