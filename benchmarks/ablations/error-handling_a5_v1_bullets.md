[CHECKLIST GUIDELINES]

## Core Principles
- **Fail fast and loudly** — surface errors at the boundary where they occur; don't bury them
- **Typed errors over string messages** — errors are first-class values with structure
- **User messages ≠ developer messages** — show friendly text to users, log full context server-side
- **Never swallow errors silently** — every `catch` block must either handle, re-throw, or log
- **Errors are part of your API contract** — document every error code a client may receive
## Error Handling Checklist
- [ ] Every `catch` block handles, re-throws, or logs — no silent swallowing
- [ ] API errors follow the standard envelope `{ error: { code, message } }`
- [ ] User-facing messages contain no stack traces or internal details
- [ ] Full error context is logged server-side
- [ ] Custom error classes extend a base `AppError` with a `code` field
- [ ] Async functions surface errors to callers — no fire-and-forget without fallback
- [ ] Retry logic only retries retriable errors (not 4xx client errors)
- [ ] React components are wrapped in `ErrorBoundary` for rendering errors
