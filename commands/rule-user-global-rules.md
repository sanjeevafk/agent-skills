<!-- AUTO-GENERATED RULE COMMAND — DO NOT EDIT MANUALLY -->
<!-- Source of truth: rules/user-global-rules.md -->
---
description: "Rule: user-global-rules"
category: "rule"
namespace: "/rule/user-global-rules"
flat_command: "/rule-user-global-rules"
---

# Rule Command: /rule/user-global-rules

> **Source Rule File**: [rules/user-global-rules.md](file:///home/sanjeev/Downloads/agent-skills/rules/user-global-rules.md)

---

# Browser Interactions
- **Universal Rule**: NEVER invoke the `browser_subagent` or `read_browser_page` tools under any circumstances.
- **Action**: Always use the direct `chrome-devtools` MCP server tools (e.g., `chrome_devtools_navigate`, `chrome_devtools_click`, etc.) when browser testing, rendering, or navigation is required.
