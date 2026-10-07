# Google JavaScript Style — Quick Reference

> Cheat sheet for the most commonly needed rules. Load `full_guide.md` for
> authoritative detail. Note: 2-space indentation (different from Python's 4).

## Naming

| Entity | Convention | Example |
|---|---|---|
| Variable / function | `camelCase` | `parseResponse()` |
| Class | `PascalCase` | `HttpClient` |
| Constant (module-level) | `UPPER_SNAKE_CASE` | `MAX_RETRIES` |
| Private field | `#name` or `_name` | `#cache` |
| File | `kebab-case.js` | `http-client.js` |
| Enum-like object | `PascalCase` keys | `Direction.Left` |

## Variables

```javascript
// Always: const > let > (never) var
const MAX = 100;
let count = 0;

// Destructuring — use it
const { id, name } = user;
const [first, ...rest] = items;

// Default params
function fetch(url, timeout = 5000) { ... }

// Rest / spread
function log(...args) { console.log(...args); }
const merged = { ...defaults, ...overrides };
```

## Strings

```javascript
// Single quotes for literals
const greeting = 'Hello, world';

// Template literals for interpolation and multi-line
const msg = `Hello, ${user.name}! You have ${count} messages.`;

// Never concatenate
const bad = 'Hello, ' + name + '!';  // use template literal
```

## Modules

```javascript
// ES modules only — no require()
import { parseUser } from './user-parser.js';
import defaultExport from './config.js';

export function computeTotal(items) { ... }
export const MAX_ITEMS = 100;
```

## Functions

```javascript
// Named declaration for top-level (hoisted, better traces)
function processItems(items) { ... }

// Arrow function for callbacks
const ids = users.map((u) => u.id);

// Never use arguments — use rest
function sum(...nums) { return nums.reduce((a, b) => a + b, 0); }

// Class methods
class Fetcher {
  async get(url) { ... }  // no 'function' keyword in class body
}
```

## Classes & OOP

```javascript
class UserService {
  #cache = new Map();  // private field

  constructor(config) {
    this.config = config;
  }

  async getUser(id) {
    if (this.#cache.has(id)) return this.#cache.get(id);
    const user = await fetch(`/users/${id}`);
    this.#cache.set(id, user);
    return user;
  }
}
```

## JSDoc (public APIs)

```javascript
/**
 * Parses a raw API response into a User object.
 *
 * @param {!Object} raw The raw JSON response.
 * @param {boolean=} strict If true, throws on missing fields.
 * @return {!User} The parsed user.
 * @throws {ParseError} If required fields are missing in strict mode.
 */
function parseUser(raw, strict = false) { ... }
```

## Formatting Highlights

| Rule | Value |
|---|---|
| Indentation | 2 spaces (not 4) |
| Line length | 80 chars |
| Semicolons | Required |
| Quotes | Single `'` |
| Trailing commas | Required in multi-line |
| Braces | Always, even for single-line bodies |

## Common Gotchas

| Pattern | Rule |
|---|---|
| `var x = ...` | Never — use `const` or `let` |
| `"double quotes"` | Use `'single'` unless escaping |
| `str1 + str2` | Use template literal `` `${str1}${str2}` `` |
| `arguments` | Use rest params `...args` |
| `fn.apply(ctx, args)` | Use `fn.call(ctx, ...args)` or spread |
| `require('./module')` | Use `import { x } from './module.js'` |
| `for...in` on arrays | Use `for...of` or `.forEach()` |
| `==` equality | Use `===` always |
