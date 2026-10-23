---
name: mcp-builder
description: Guide for creating high-quality MCP (Model Context Protocol) servers that enable LLMs to interact with external services through well-designed tools. Use when building MCP servers to integrate external APIs or services, whether in Python (FastMCP) or Node/TypeScript (MCP SDK).
license: Complete terms in LICENSE.txt
---

[ENGINEERING IMPLEMENTATION STANDARDS & ARCHITECTURAL CONSTRAINTS]

#### 1.1 Understand Modern MCP Design
**API Coverage vs. Workflow Tools**
**Tool Naming and Discoverability**
**Context Management**
**Actionable Error Messages**
#### 1.2 Study MCP Protocol Documentation
**Navigate the MCP specification**
- Specification overview and architecture
- Transport mechanisms (streamable HTTP, stdio)
- Tool, resource, and prompt definitions
#### 1.3 Study Framework Documentation
**Recommended stack**
- **Language**: TypeScript (high-quality SDK support and good compatibility in many execution environments e.g. MCPB. Plus AI models are good at generating TypeScript code, benefiting from its broad usage, static typing and good linting tools)
- **Transport**: Streamable HTTP for remote servers, using stateless JSON (simpler to scale and maintain, as opposed to stateful sessions and streaming responses). stdio for local servers.
**Load framework documentation**
- **MCP Best Practices**: [📋 View Best Practices](./reference/mcp_best_practices.md) - Core guidelines
**For TypeScript (recommended)**
- **TypeScript SDK**: Use WebFetch to load `https://raw.githubusercontent.com/modelcontextprotocol/typescript-sdk/main/README.md`
- [⚡ TypeScript Guide](./reference/node_mcp_server.md) - TypeScript patterns and examples
**For Python**
- **Python SDK**: Use WebFetch to load `https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/main/README.md`
- [🐍 Python Guide](./reference/python_mcp_server.md) - Python patterns and examples
#### 1.4 Plan Your Implementation
**Understand the API**
**Tool Selection**
#### 2.1 Set Up Project Structure
- [⚡ TypeScript Guide](./reference/node_mcp_server.md) - Project structure, package.json, tsconfig.json
- [🐍 Python Guide](./reference/python_mcp_server.md) - Module organization, dependencies
#### 2.2 Implement Core Infrastructure
- API client with authentication
- Error handling helpers
- Response formatting (JSON/Markdown)
- Pagination support
#### 2.3 Implement Tools
**Input Schema**
- Use Zod (TypeScript) or Pydantic (Python)
- Include constraints and clear descriptions
- Add examples in field descriptions
**Output Schema**
- Define `outputSchema` where possible for structured data
- Use `structuredContent` in tool responses (TypeScript SDK feature)
- Helps clients understand and process tool outputs
**Tool Description**
- Concise summary of functionality
- Parameter descriptions
- Return type schema
**Implementation**
- Async/await for I/O operations
- Proper error handling with actionable messages
- Support pagination where applicable
- Return both text content and structured data when using modern SDKs
**Annotations**
- `readOnlyHint`: true/false
- `destructiveHint`: true/false
- `idempotentHint`: true/false
- `openWorldHint`: true/false
#### 3.1 Code Quality
- No duplicated code (DRY principle)
- Consistent error handling
- Full type coverage
- Clear tool descriptions
#### 3.2 Build and Test
**TypeScript**
- Run `npm run build` to verify compilation
- Test with MCP Inspector: `npx @modelcontextprotocol/inspector`
**Python**
- Verify syntax: `python -m py_compile your_server.py`
- Test with MCP Inspector
### Phase 4: Create Evaluations
**Load [✅ Evaluation Guide](./reference/evaluation.md) for complete evaluation guidelines.**
#### 4.2 Create 10 Evaluation Questions
- **Tool Inspection**: List available tools and understand their capabilities
- **Content Exploration**: Use READ-ONLY operations to explore available data
- **Question Generation**: Create 10 complex, realistic questions
- **Answer Verification**: Solve each question yourself to verify answers
#### 4.3 Evaluation Requirements
- **Independent**: Not dependent on other questions
- **Read-only**: Only non-destructive operations required
- **Complex**: Requiring multiple tool calls and deep exploration
- **Realistic**: Based on real use cases humans would care about
- **Verifiable**: Single, clear answer that can be verified by string comparison
- **Stable**: Answer won't change over time
#### 4.4 Output Format
```xml
<evaluation>
  <qa_pair>
    <question>Find discussions about AI model launches with animal codenames. One model needed a specific safety designation that uses the format ASL-X. What number X was being determined for the model named after a spotted wild cat?</question>
    <answer>3</answer>
  </qa_pair>
<!-- More qa_pairs... -->
</evaluation>
```

### Core MCP Documentation (Load First)
- **MCP Protocol**: Start with sitemap at `https://modelcontextprotocol.io/sitemap.xml`, then fetch specific pages with `.md` suffix
- [📋 MCP Best Practices](./reference/mcp_best_practices.md) - Universal MCP guidelines including:
- Server and tool naming conventions
- Response format guidelines (JSON vs Markdown)
- Pagination best practices
- Transport selection (streamable HTTP vs stdio)
- Security and error handling standards
### SDK Documentation (Load During Phase 1/2)
- **Python SDK**: Fetch from `https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/main/README.md`
- **TypeScript SDK**: Fetch from `https://raw.githubusercontent.com/modelcontextprotocol/typescript-sdk/main/README.md`
### Language-Specific Implementation Guides (Load During Phase 2)
- [🐍 Python Implementation Guide](./reference/python_mcp_server.md) - Complete Python/FastMCP guide with:
- Server initialization patterns
- Pydantic model examples
- Tool registration with `@mcp.tool`
- Complete working examples
- Quality checklist
- [⚡ TypeScript Implementation Guide](./reference/node_mcp_server.md) - Complete TypeScript guide with:
- Project structure
- Zod schema patterns
- Tool registration with `server.registerTool`
### Evaluation Guide (Load During Phase 4)
- [✅ Evaluation Guide](./reference/evaluation.md) - Complete evaluation creation guide with:
- Question creation guidelines
- Answer verification strategies
- XML format specifications
- Example questions and answers
- Running an evaluation with the provided scripts
