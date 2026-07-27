# Browser Interactions
- **Universal Rule**: NEVER invoke the `browser_subagent` or `read_browser_page` tools under any circumstances.
- **Action**: Always use the direct `chrome-devtools` MCP server tools (e.g., `chrome_devtools_navigate`, `chrome_devtools_click`, etc.) when browser testing, rendering, or navigation is required.
