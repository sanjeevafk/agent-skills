[ENGINEERING IMPLEMENTATION STANDARDS & ARCHITECTURAL CONSTRAINTS]

## Core Principles
- **Fail fast and loudly** — surface errors at the boundary where they occur; don't bury them
- **Typed errors over string messages** — errors are first-class values with structure
- **User messages ≠ developer messages** — show friendly text to users, log full context server-side
- **Never swallow errors silently** — every `catch` block must either handle, re-throw, or log
- **Errors are part of your API contract** — document every error code a client may receive
### Typed Error Classes
```typescript
// Define an error hierarchy for your domain
export class AppError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly statusCode: number = 500,
    public readonly details?: unknown,
  ) {
    super(message)
    this.name = this.constructor.name
    // Maintain correct prototype chain in transpiled ES5 JavaScript.
  # ... [syntax pattern continues] ...
  }
}
```

### Result Pattern (no-throw style)
```typescript
type Result<T, E = AppError> =
  | { ok: true; value: T }
  | { ok: false; error: E }
function ok<T>(value: T): Result<T> {
  return { ok: true, value }
}
function err<E>(error: E): Result<never, E> {
  return { ok: false, error }
}
// Usage
async function fetchUser(id: string): Promise<Result<User>> {
  # ... [syntax pattern continues] ...
// TypeScript knows result.value here
console.log(result.value.email)
```

### API Error Handler (Next.js / Express)
```typescript
import { NextRequest, NextResponse } from 'next/server'
function handleApiError(error: unknown): NextResponse {
  // Known application error
  if (error instanceof AppError) {
    return NextResponse.json(
      {
        error: {
          code: error.code,
          message: error.message,
          ...(error.details ? { details: error.details } : {}),
        },
  # ... [syntax pattern continues] ...
  }
}
```

### React Error Boundary
```typescript
import { Component, ErrorInfo, ReactNode } from 'react'
interface Props {
  fallback: ReactNode
  onError?: (error: Error, info: ErrorInfo) => void
  children: ReactNode
}
interface State {
  hasError: boolean
  error: Error | null
}
export class ErrorBoundary extends Component<Props, State> {
  # ... [syntax pattern continues] ...
  <MyComponent />
</ErrorBoundary>
```

### Custom Exception Hierarchy
```python
class AppError(Exception):
    """Base application error."""
    def __init__(self, message: str, code: str, status_code: int = 500):
        super().__init__(message)
        self.code = code
        self.status_code = status_code
class NotFoundError(AppError):
    def __init__(self, resource: str, id: str):
        super().__init__(f"{resource} not found: {id}", "NOT_FOUND", 404)
class ValidationError(AppError):
    def __init__(self, message: str, details: list[dict] | None = None):
        super().__init__(message, "VALIDATION_ERROR", 422)
        self.details = details or []
```

### FastAPI Global Exception Handler
```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
app = FastAPI()
@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": str(exc)}},
    )
@app.exception_handler(Exception)
async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
  # ... [syntax pattern continues] ...
        content={"error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred"}},
    )
```

### Sentinel Errors and Error Wrapping
```go
package domain
import "errors"
// Sentinel errors for type-checking
var (
    ErrNotFound    = errors.New("not found")
    ErrUnauthorized = errors.New("unauthorized")
    ErrConflict     = errors.New("conflict")
)
// Wrap errors with context — never lose the original
func (r *UserRepository) FindByID(ctx context.Context, id string) (*User, error) {
    user, err := r.db.QueryRow(ctx, "SELECT * FROM users WHERE id = $1", id)
  # ... [syntax pattern continues] ...
    writeJSON(w, http.StatusOK, user)
}
```

## Retry with Exponential Backoff
```typescript
interface RetryOptions {
  maxAttempts?: number
  baseDelayMs?: number
  maxDelayMs?: number
  retryIf?: (error: unknown) => boolean
}
async function withRetry<T>(
  fn: () => Promise<T>,
  options: RetryOptions = {},
): Promise<T> {
  const {
  # ... [syntax pattern continues] ...
  retryIf: (error) => !(error instanceof AppError && error.statusCode < 500),
})
```

## User-Facing Error Messages
```typescript
const USER_ERROR_MESSAGES: Record<string, string> = {
  NOT_FOUND: 'The requested item could not be found.',
  UNAUTHORIZED: 'Please sign in to continue.',
  FORBIDDEN: "You don't have permission to do that.",
  VALIDATION_ERROR: 'Please check your input and try again.',
  RATE_LIMITED: 'Too many requests. Please wait a moment and try again.',
  INTERNAL_ERROR: 'Something went wrong on our end. Please try again later.',
}

export function getUserMessage(code: string): string {
  return USER_ERROR_MESSAGES[code] ?? USER_ERROR_MESSAGES.INTERNAL_ERROR
}
```

## Error Handling Checklist
- [ ] Every `catch` block handles, re-throws, or logs — no silent swallowing
- [ ] API errors follow the standard envelope `{ error: { code, message } }`
- [ ] User-facing messages contain no stack traces or internal details
- [ ] Full error context is logged server-side
- [ ] Custom error classes extend a base `AppError` with a `code` field
- [ ] Async functions surface errors to callers — no fire-and-forget without fallback
- [ ] Retry logic only retries retriable errors (not 4xx client errors)
- [ ] React components are wrapped in `ErrorBoundary` for rendering errors
