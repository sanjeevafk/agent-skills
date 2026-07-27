# Security & Policy Architecture

> Security model, policy enforcement hooks, system monitoring, and compliance patterns.

---

## 1. Security Guardrails Architecture

The framework enforces security across three distinct layers:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          SECURITY ARCHITECTURE                          │
├──────────────────────────────┬──────────────────────────────────────────┤
│ Layer                        │ Enforcement Mechanism                    │
├──────────────────────────────┼──────────────────────────────────────────┤
│ 1. Pre-Execution Hook Guard  │ hooks/tirith-security-guard-gemini.py    │
│                              │ Intercepts shell & destructive commands. │
├──────────────────────────────┼──────────────────────────────────────────┤
│ 2. Always-On Rule Invariants │ rules/user-global-rules.md & .agentrules  │
│                              │ Enforces tool restrictions (e.g. Chrome)  │
├──────────────────────────────┼──────────────────────────────────────────┤
│ 3. Specialized Security      │ skills/security-review, gateguard,       │
│    Skill Packages            │ healthcare-phi-compliance, bounty-hunter │
└──────────────────────────────┴──────────────────────────────────────────┘
```

---

## 2. Policy Enforcement Hook (`Tirith`)

The framework includes a pre-execution tool interception hook (`hooks/tirith-security-guard-gemini.py`):
* **Dangerous Command Prevention**: Intercepts un-guarded destructive shell operations (`rm -rf /`, `dd`, unauthorized network pushes).
* **Policy Interception**: Enforces local tool access rules (e.g., blocking deprecated browser subagents and directing execution to direct DevTools MCP servers).

---

## 3. System Monitoring Script

The repository includes a portable system monitoring setup template under `scripts/security/system/setup-system-monitoring.sh`:
* Configures Linux audit rules (`auditd`) to monitor execution of binaries (`execve`), file unlinks (`unlinkat`), and privilege escalation attempts.

To deploy system-level audit rules on Linux hosts:
```bash
sudo bash scripts/security/system/setup-system-monitoring.sh
```

---

## 4. Sensitive Data & Secret Management Standards

1. **Zero Secret Hardcoding**: Secrets, API keys, tokens, and private credentials must never be committed to git or rendered in agent responses.
2. **Environment Variables**: All external service keys (Supabase, Sentry, Exa, Tavily) must be loaded from environment variables (`.env`).
3. **PHI & PII Compliance**: When handling healthcare or sensitive user data, enforce HIPAA/PHI data classification patterns (`healthcare-phi-compliance`), ensuring data anonymization before external API transmission.
