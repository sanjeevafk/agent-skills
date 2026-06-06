# Google TypeScript Style — Quick Reference

> Cheat sheet for the most commonly needed rules. Load `full_guide.md` for
> authoritative detail on any specific section.

## Naming

| Entity | Convention | Example |
|---|---|---|
| Variable / function | `camelCase` | `getUserById()` |
| Class / interface | `PascalCase` | `UserService` |
| Type alias | `PascalCase` | `ApiResponse` |
| Enum member (if used) | `PascalCase` | `Status.Active` |
| Constant | `UPPER_SNAKE_CASE` | `MAX_RETRIES` |
| Private field | `#name` or `private name` | `#cache` |
| File | `kebab-case.ts` | `user-service.ts` |

## Imports

```typescript
// Type-only import — won't appear in emitted JS
import type { User } from './models/user';

// Regular import
import { fetchData } from './api/client';

// Avoid namespace imports unless module has no named exports
import * as path from 'path'; // only acceptable for Node built-ins

// Never
const fs = require('fs'); // No CommonJS
```

## Types vs Interfaces

```typescript
// Prefer interface for object shapes (extensible)
interface Config {
  timeout: number;
  retries: number;
}

// Use type for unions, intersections, utility types
type Status = 'active' | 'inactive' | 'pending';
type ReadonlyConfig = Readonly<Config>;
type ApiError = NetworkError | ParseError;
```

## Avoid `any` and `!`

```typescript
// Bad
function process(data: any) { ... }
const value = maybeNull!.property;

// Good
function process(data: unknown) {
  if (typeof data === 'string') { ... }
}
const value = maybeNull?.property ?? defaultValue;
```

## Enums → Union Types

```typescript
// Bad — avoid enum
enum Direction { Left, Right, Up, Down }

// Good — string literal union
type Direction = 'left' | 'right' | 'up' | 'down';

// Good — const object when you need the values as a record
const Direction = { Left: 'left', Right: 'right' } as const;
type Direction = typeof Direction[keyof typeof Direction];
```

## `var` / `let` / `const`

```typescript
const x = 1;           // Default — always prefer const
let count = 0;         // Only when you must reassign
// var — never
```

## Class Visibility

```typescript
class UserService {
  // Private field (ES private — truly inaccessible)
  #cache = new Map<string, User>();

  // TypeScript private (accessible via casting — weaker)
  private logger: Logger;

  // Public is the default — don't add the keyword
  fetchUser(id: string): Promise<User> { ... }
}
```

## Null Safety

```typescript
// Optional chaining
const name = user?.profile?.displayName;

// Nullish coalescing (not || — that drops 0 and "")
const timeout = config.timeout ?? 5000;

// Non-null assertion — only when TypeScript can't infer
// and you're certain. Avoid in production code.
const el = document.getElementById('root')!;
```

## Function Signatures

```typescript
// Always annotate return types on exported functions
export function parseResponse(raw: string): ParsedResponse {
  ...
}

// Arrow functions for callbacks
const items = data.map((item) => item.id);

// Avoid overloads when union types work
function format(value: string | number): string { ... }
```

## File Structure

```typescript
// 1. Imports (type-only first, then regular)
import type { Config } from './types';
import { validate } from './utils';

// 2. Types / interfaces
interface ServiceOptions { ... }

// 3. Constants
const DEFAULT_TIMEOUT = 5000;

// 4. Main implementation
export class MyService { ... }

// 5. Helper functions (if not in a separate file)
function helper() { ... }
```

## Common Gotchas

| Pattern | Rule |
|---|---|
| `enum Foo {}` | Use union type or `const` object instead |
| `as any` | Use `unknown` + narrowing |
| `!` non-null | Use `?.` and `??` instead |
| `require()` | Use `import` |
| Implicit `any` in callbacks | Annotate params: `arr.map((x: string) => ...)` |
| `public` keyword on class members | Redundant — omit it |
