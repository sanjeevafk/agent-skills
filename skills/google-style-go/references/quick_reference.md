# Google Go Style — Quick Reference

> Cheat sheet for the most commonly needed rules. Consult the full reference
> files for depth: `guide.md` (rules), `best_practices.md` (patterns),
> `decisions.md` (rationale).

## Naming

| Entity | Style | Example |
|---|---|---|
| Package | lowercase, singular, no underscores | `user`, `httpclient` |
| Exported type/func | `PascalCase` | `UserService`, `Parse` |
| Unexported | `camelCase` | `parseInternal` |
| Acronyms | preserve case | `HTTPServer`, `userID`, `parseURL` |
| Interface | behaviour noun, often `-er` | `Reader`, `Closer`, `Stringer` |
| Error variable | `Err` prefix | `ErrNotFound` |
| Error type | `Error` suffix | `NotFoundError` |
| Receiver | 1-2 char abbreviation, consistent | `c *Client`, `s *Server` |
| Test func | `TestFunctionName_Scenario` | `TestParse_EmptyInput` |

**Avoid**: `util`, `common`, `misc`, `helper` as package names. Avoid stutter
(`user.UserClient` → `user.Client`).

## Error Handling

```go
// Always check errors
result, err := doSomething()
if err != nil {
    return fmt.Errorf("doing something: %w", err)
}

// Wrapping preserves the chain — use %w
return fmt.Errorf("fetching user %q: %w", id, err)

// Inspect errors with errors.Is / errors.As — never string matching
if errors.Is(err, ErrNotFound) { ... }

var nfe *NotFoundError
if errors.As(err, &nfe) { ... }

// Sentinel errors — only when callers need to match
var ErrNotFound = errors.New("not found")
```

## Context

```go
// ctx is always first, named ctx
func (c *Client) Fetch(ctx context.Context, id string) (*User, error) { ... }

// Never store in a struct
type Service struct {
    ctx context.Context  // BAD — pass through calls
}
```

## Goroutines

```go
// Every goroutine needs a stop mechanism
go func() {
    defer wg.Done()
    for {
        select {
        case <-ctx.Done():
            return
        case item := <-work:
            process(item)
        }
    }
}()

// Bound concurrency with a semaphore or worker pool
sem := make(chan struct{}, maxWorkers)
```

## Comments (exported identifiers)

```go
// Package doc — first sentence is the summary
// Package user provides types for managing user accounts.
package user

// Client manages authenticated connections to the user service.
// It is safe for concurrent use.
type Client struct { ... }

// Fetch retrieves the user with the given ID.
// It returns ErrNotFound if no such user exists.
func (c *Client) Fetch(ctx context.Context, id string) (*User, error) { ... }
```

## Imports

```go
import (
    // 1. stdlib
    "context"
    "fmt"

    // 2. third-party
    "github.com/some/lib"

    // 3. internal
    "mycompany.com/internal/user"
)
// goimports handles this automatically
```

## Interfaces

```go
// Define interfaces where they're consumed, not implemented
// In package transport:
type Fetcher interface {
    Fetch(ctx context.Context, id string) (*User, error)
}

// In package user (implementation) — no interface declaration needed there
```

## Table-Driven Tests

```go
func TestParse(t *testing.T) {
    tests := []struct {
        name  string
        input string
        want  *User
        err   bool
    }{
        {name: "valid", input: `{"id":"1"}`, want: &User{ID: "1"}},
        {name: "empty", input: `{}`, err: true},
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got, err := Parse(tt.input)
            if (err != nil) != tt.err {
                t.Fatalf("Parse() error = %v, wantErr %v", err, tt.err)
            }
            if !tt.err && !cmp.Equal(got, tt.want) {
                t.Errorf("Parse() = %v, want %v", got, tt.want)
            }
        })
    }
}
```

## Common Gotchas

| Pattern | Rule |
|---|---|
| Ignoring `err` with `_` | Never for real errors; document why if truly safe |
| `errors.New("not found")` checked via string | Use `errors.Is()` with sentinel |
| Goroutine with no stop | Always pass `ctx` or done channel |
| `context.Background()` mid-stack | Only at entry points; propagate from caller |
| `type Foo interface{}` in implementation pkg | Define interfaces at usage site |
| Stutter: `user.UserID` | Remove package prefix: `user.ID` |
| `for i, _ := range slice` | Just `for i := range slice` |
