# Google Python Style — Quick Reference

> Cheat sheet for the most commonly needed rules. Load `full_guide.md` for
> authoritative detail on any specific section.

## Naming

| Entity | Convention | Example |
|---|---|---|
| Module / package | `snake_case` | `data_utils` |
| Class | `CapWords` | `DataLoader` |
| Exception | `CapWords` + `Error` | `ParseError` |
| Function / method | `snake_case` | `load_data()` |
| Instance variable | `snake_case` | `self.batch_size` |
| Class variable | `snake_case` | `cls.registry` |
| Constant | `UPPER_SNAKE_CASE` | `MAX_BATCH_SIZE` |
| Private | leading `_` | `_helper()` |
| Test method | `test_<behavior>` | `test_returns_empty_list_when_no_items` |

## Imports (§2.2, §3.13)

```python
# Correct order: stdlib → third-party → local
import os
import sys
from typing import Optional

import numpy as np
import requests

from my_package import utils
from my_package.models import User
```

- Use `import x` for modules/packages
- Use `from x import y` for sub-modules
- Never `from x import *`
- No relative imports

## Type Annotations (§2.21, §3.19)

```python
# All public functions annotated
def process(items: list[str], limit: int = 100) -> dict[str, int]:
    ...

# Use Optional for nullable params (Python < 3.10)
def find(key: str) -> Optional[str]:
    ...

# Python 3.10+ union syntax
def find(key: str) -> str | None:
    ...
```

## Docstrings (§3.8)

```python
def compute(value: float, scale: float = 1.0) -> float:
    """Compute the scaled value.

    Args:
        value: The raw input value.
        scale: Multiplier applied to value. Defaults to 1.0.

    Returns:
        The scaled result.

    Raises:
        ValueError: If value is negative.
    """
```

## Exceptions (§2.4)

```python
# Good — specific exception
try:
    data = json.loads(text)
except json.JSONDecodeError as e:
    raise ParseError(f"Invalid JSON: {e}") from e

# Bad — bare except / over-broad catch
try:
    ...
except:          # Never
except Exception: # Only if re-raising
```

## Comprehensions (§2.7)

```python
# Good — one for clause, optional filter
squares = [x**2 for x in range(10) if x % 2 == 0]

# Bad — multiple for clauses
pairs = [(x, y) for x in range(5) for y in range(5)]  # Use explicit loops
```

## Formatting

- 4-space indentation
- 80-char line limit
- Blank lines: 2 between top-level defs, 1 between methods
- Use `with` for resources
- Trailing comma in multi-line collections

## Common Gotchas

| Pattern | Rule |
|---|---|
| `def f(x=[])` | Never mutable defaults — use `None` sentinel |
| `assert` for validation | Only in tests; use `raise ValueError` in production |
| `lambda` for multi-step logic | Use a named `def` instead |
| `global x` | Avoid; use class/function scope or pass as argument |
| String concat in loop | Use `''.join(parts)` instead of `+=` |
