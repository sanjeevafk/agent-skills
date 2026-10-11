---
name: pattern-guardrails-safety
description: "Establish multi-layered defensive shields: input sanitization, prompt injection detection, PII masking, schema gates, and egress filters."
metadata:
  category: agent-architecture
  tier: enterprise
  chapter: 18
  source: "Antonio Gulli: Agentic Design Patterns"
---

# Guardrails & Safety Pattern

## 1. Overview & Intent

Establish multi-layered defensive shields: input sanitization, prompt injection detection, PII masking, schema gates, and egress filters.

> **Intent & Scope:** Use in untrusted enterprise environments to prevent prompt injections, toxic content, data exfiltration, and unsafe tool execution.

---

## 2. Architectural Blueprint

```
[User Input] --> [Input Guardrail: Injection/PII Check] --(Clean)--> [Agent Core]
                                                                        |
                                                                   (Tool Call)
                                                                        |
                                                                        v
                                                           [Permission Guardrail]
                                                                        |
                                                                   (Raw Output)
                                                                        |
                                                                        v
[Final Clean Output] <--(Passed)-- [Output Guardrail: Leakage Filter]
```

---

## 3. Core Implementation Principles

- **Defense-in-depth:** apply guardrails at input, tool invocation, and final output stages.\n- Sanitize input against indirect prompt injection (especially from web pages and external files).\n- Mask Personally Identifiable Information (PII) before forwarding payloads to external LLM providers.\n- Enforce strict schema validation and egress domain whitelisting on all external network tool calls.

---

## 4. Reference Implementation Pattern

```python
import re

class SafetyGuardrail:
    FORBIDDEN_PATTERNS = [
        re.compile(r"ignore previous instructions", re.IGNORECASE),
        re.compile(r"system prompt override", re.IGNORECASE)
    ]

    @classmethod
    def validate_input(cls, user_text: str) -> bool:
        for pattern in cls.FORBIDDEN_PATTERNS:
            if pattern.search(user_text):
                raise ValueError("Security violation: Prompt injection detected.")
        return True

```

---

## 5. Verification & Failure Modes

- **Verification Checklist:**
  - [ ] Inputs are validated via strict typed schemas before processing.
  - [ ] Error cascades and timeouts are bounded.
  - [ ] Intermediate artifacts and trace telemetry are logged.
  - [ ] Verification criteria are objectively evaluated before task completion.

- **Common Failure Modes:**
  - **Cascading Hallucination:** Unchecked intermediate model drift polluting downstream stages.
  - **Infinite Looping:** Lack of maximum iteration guards or convergence detection.
  - **Context Bloat:** Carrying unpruned conversational history or verbose tool errors across turns.
