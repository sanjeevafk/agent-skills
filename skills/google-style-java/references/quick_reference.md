# Google Java Style — Quick Reference

> Cheat sheet for the most commonly needed rules. Load `full_guide.md` for
> authoritative detail. Key gotcha: **2-space indentation** (not 4).

## Naming

| Entity | Style | Example |
|---|---|---|
| Package | `lowercase.dot.separated` | `com.example.user` |
| Class / Interface / Enum | `UpperCamelCase` | `UserRepository` |
| Method | `lowerCamelCase` | `findById()` |
| Non-constant field | `lowerCamelCase` | `retryCount` |
| `static final` constant | `UPPER_SNAKE_CASE` | `MAX_RETRIES` |
| Local variable | `lowerCamelCase` | `userCount` |
| Type parameter | Single letter or `T`-suffixed | `E`, `K`, `ResponseT` |

**Acronyms as words**: `XmlParser` not `XMLParser`, `HttpUrl` not `HTTPUrl`.

## File Structure (in order)

```java
// 1. (optional) License header
// 2. Package declaration
package com.example.user;

// 3. Imports — static first, then alphabetical by group
import static org.junit.Assert.assertEquals;

import java.util.List;
import java.util.Optional;

import com.example.internal.Helper;

// 4. Exactly one top-level class
public final class UserService { ... }
```

**No wildcard imports** — ever. No `import java.util.*`.

## Braces — K&R Style

```java
// Always braces. Opening brace on same line.
if (condition) {
  doSomething();
} else {
  doOther();
}

// No braceless bodies — even single statements
for (int i = 0; i < n; i++) {
  process(i);  // braces required
}
```

## Formatting

| Rule | Value |
|---|---|
| Indentation | **2 spaces** (not 4) |
| Continuation indent | +4 spaces (double the block indent) |
| Column limit | 100 characters |
| One statement per line | Required |
| Trailing whitespace | Never |

```java
// Continuation lines: +4 extra indent
SomeType result =
    someObject.method1()
        .method2()
        .method3();
```

## Javadoc

```java
/**
 * Returns the user with the given identifier.
 *
 * <p>Queries the backing store and caches the result for {@code cacheTtl}
 * seconds. Use {@link #invalidate(String)} to clear an entry.
 *
 * @param id the user identifier; must not be null or empty
 * @param includeDeleted whether soft-deleted users are returned
 * @return the user, or {@link Optional#empty()} if not found
 * @throws IllegalArgumentException if {@code id} is null
 */
public Optional<User> findById(String id, boolean includeDeleted) { ... }
```

- Every `public` class, method, and field gets Javadoc.
- `{@code x}` for inline code; `{@link Foo#bar()}` for cross-references.
- First sentence: concise summary ending with `.`.

## Annotations

```java
// One per line, above the declaration
@Override
@Nullable
public String getDisplayName() { ... }

// @Override always when overriding or implementing
@Override
public String toString() { ... }
```

## Switch

```java
switch (status) {
  case ACTIVE:
    handleActive();
    break;
  case PENDING:
    handlePending();
    break;
  default:        // always required
    throw new IllegalStateException("Unknown status: " + status);
}
```

## Numeric Literals

```java
long timeout = 30_000L;      // L uppercase, underscores OK
float ratio = 0.5f;          // f lowercase OK
double pi = 3.14_159_265;    // underscores for readability
```

## Common Gotchas

| Pattern | Rule |
|---|---|
| `import java.util.*` | Never — explicit imports only |
| 4-space indentation | Use 2 spaces |
| `if (x) doThing();` braceless | Always use braces |
| Acronym as `HTTP` in name | Treat as word: `Http` |
| Missing `@Override` | Always add when overriding |
| `switch` without `default:` | Add `default:` always |
| Long literal `100l` | Use uppercase `100L` |
| Missing Javadoc on public API | Javadoc required on all public members |
