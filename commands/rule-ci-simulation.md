<!-- AUTO-GENERATED RULE COMMAND — DO NOT EDIT MANUALLY -->
<!-- Source of truth: rules/ci-simulation.md -->
---
description: "Rule: ci-simulation"
category: "rule"
namespace: "/rule/ci-simulation"
flat_command: "/rule-ci-simulation"
---

# Rule Command: /rule/ci-simulation

> **Source Rule File**: [rules/ci-simulation.md](file:///home/sanjeev/Downloads/agent-skills/rules/ci-simulation.md)

---

# Local CI Simulation & Push Protocol
1. **Simulate CI Locally**: Before declaring any change complete or pushing to remote, always execute the full CI suite locally (e.g., linter, static type checker, unit/integration test suite).
2. **Environment Isolation**: Ensure tests run cleanly in both local and isolated environments (e.g., without relying on uncommitted local system state or hardcoded personal database paths).
3. **Verification Before Push**: Only make final commits and push to remote after all linter, typecheck, and test commands return zero exit codes.
