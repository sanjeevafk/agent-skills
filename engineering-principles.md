---
description: Lightweight engineering principles reference (optimized for token efficiency)
applyTo: "/home/sanjeev/agent-skills/**/*.{ts,tsx,js,jsx,py,md}"
---

# Engineering Principles Quick Reference

**For full detailed rules, see:** `~/.copilot/archived-rules/agent-rules-books/`  
**Ask me directly:** "Show me clean code patterns" or "DDD rules for this schema"

## Core Philosophy

1. **Explicit > Clever** - Readability and maintainability first
2. **Hide Complexity** - Simple interfaces, deep implementations
3. **Separation of Concerns** - One responsibility per unit
4. **Test-Driven** - Tests before implementation
5. **Defend Boundaries** - Validate at edges, trust inside

## Quick Decision Tree

### Am I writing...

**Business Logic?**
- Use pure functions
- Make invalid states impossible
- Test edge cases first
- Validate inputs at boundary

**API/Database Code?**
- Parameterized queries always
- Whitelist inputs, not blacklist
- Log security events
- Enforce auth at layer boundary

**User-Facing Code?**
- Accessibility first
- Responsive design
- Semantic HTML
- Keyboard navigation

**Infrastructure/Tooling?**
- Fail fast and loud
- Comprehensive logging
- Graceful degradation
- Document assumptions

## By Technology

### TypeScript
- Strict mode always: `strict: true`
- No `any` except interop boundaries
- Discriminated unions for complex state
- Readonly where possible

### Python
- Type hints on all functions
- Dataclasses > dicts for structured data
- Context managers for resources
- Single-responsibility functions

### Database (Postgres/Supabase)
- RLS on every user-facing table
- Migrations testable and reversible
- Foreign keys enforced
- Audit logs for sensitive data

### APIs (REST/GraphQL)
- Consistent error responses
- Pagination for lists
- CORS/auth on all endpoints
- API versioning strategy

## Security Patterns

**Authentication:** Use established libraries (Supabase Auth, NextAuth)  
**Secrets:** Environment variables only, never in code  
**SQL:** Parameterized queries, never string concatenation  
**Validation:** Validate at all trust boundaries  
**Errors:** Don't leak internal implementation details

## Testing

- Unit tests for business logic
- Integration tests for flows
- E2E tests for user-critical paths
- Aim for 80%+ coverage on core code

## Common Anti-Patterns to Avoid

- Mixing business logic with UI
- Global state without isolation
- Hardcoded configuration values
- Catching all exceptions silently
- Temporary code that becomes permanent
- Over-engineering simple problems

## Response Style

**Canonical Rule:** No emojis in any responses. Use clear text and formatting instead. Applies to all agents and all response contexts.

---

**For deeper guidance on any topic, ask me directly.**
