# Google C++ Style — Quick Reference

> Cheat sheet for the most commonly needed rules. Load `full_guide.md` for
> the full guide (~6,100 lines); use `TOC.md` to navigate.
> Key gotcha: Google C++ **disallows exceptions** and **RTTI**.

## Naming

| Entity | Style | Example |
|---|---|---|
| File | `snake_case.cc` / `.h` | `user_service.h` |
| Type (class, struct, alias, enum) | `PascalCase` | `UserService` |
| Function / method | `PascalCase` | `ComputeTotal()` |
| Simple accessor | `snake_case()` | `size()`, `is_valid()` |
| Variable (local, param) | `snake_case` | `user_count` |
| Class data member | `snake_case_` (trailing `_`) | `cache_size_` |
| Struct data member | `snake_case` (no trailing `_`) | `cache_size` |
| Constant / `constexpr` | `kPascalCase` | `kMaxRetries` |
| Namespace | `snake_case` | `internal_utils` |
| Macro | `UPPER_SNAKE_CASE` | `MY_PROJECT_LOG` |
| Enum member (scoped) | `kPascalCase` | `Status::kNotFound` |

## Headers

```cpp
// my_file.h — use include guard
#ifndef MY_PROJECT_PATH_MY_FILE_H_
#define MY_PROJECT_PATH_MY_FILE_H_

// Forward declarations to reduce coupling
class UserData;

namespace myproject {

class UserService {
 public:
  // Returns nullptr if not found. Thread-safe.
  std::unique_ptr<User> FindUser(absl::string_view id) const;

 private:
  mutable absl::Mutex mu_;
  absl::flat_hash_map<std::string, User> cache_ ABSL_GUARDED_BY(mu_);
};

}  // namespace myproject

#endif  // MY_PROJECT_PATH_MY_FILE_H_
```

```cpp
// my_file.cc — include own header first
#include "path/my_file.h"

#include <memory>          // stdlib
#include <string>

#include "absl/strings/string_view.h"  // third-party

#include "path/other_internal.h"       // internal
```

## Ownership & Pointers

```cpp
// Sole ownership — default choice
std::unique_ptr<User> user = std::make_unique<User>(id);

// Non-owning reference (caller keeps ownership)
void Process(const User& user);           // required, non-null
void Process(const User* user);           // optional, may be null

// Shared ownership — use sparingly
std::shared_ptr<Config> config = std::make_shared<Config>();

// Never raw new/delete in application code
User* u = new User();  // BAD
```

## No Exceptions — Use Status Returns

```cpp
// Instead of throw/catch:
absl::Status DoSomething(Input in);
absl::StatusOr<Result> Compute(Input in);

// Caller checks:
auto result = Compute(input);
if (!result.ok()) {
  return result.status();
}
Use(*result);

// No dynamic_cast / typeid — use virtual dispatch
```

## Classes

```cpp
class Widget {
 public:
  // Mark single-arg constructors explicit
  explicit Widget(int size);

  // Non-copyable types: delete copy
  Widget(const Widget&) = delete;
  Widget& operator=(const Widget&) = delete;

  // Movable if needed
  Widget(Widget&&) = default;
  Widget& operator=(Widget&&) = default;

  // Virtual destructor if subclassed
  virtual ~Widget() = default;

  int size() const { return size_; }   // simple accessors: snake_case

 private:
  int size_;   // trailing underscore
};
```

## `auto`

```cpp
// Good — type is long or obvious from context
auto it = container.begin();
auto result = std::make_unique<Widget>(size);

// Bad — type is not clear
auto x = GetValue();   // What type is x?
auto count = 42;       // Just write: int count = 42;
```

## Comments

```cpp
// Prefer // for all comments (single and multi-line)

// In the header, above the declaration:
// Computes the total cost for the given items.
// Returns 0 if items is empty. Thread-safe.
double ComputeTotal(absl::Span<const Item> items) const;

// In .cc, explain the why, not the what:
// Use a sentinel value instead of std::optional because
// the hot path avoids an extra branch.
int result = kNoResult;
```

## Namespaces

```cpp
namespace myproject {
namespace internal {

// No extra indentation inside namespace
void HelperFunction();

}  // namespace internal
}  // namespace myproject

// Anonymous namespace instead of static (for .cc files)
namespace {
void FileLocalHelper() { ... }
}  // namespace
```

## Formatting Highlights

| Rule | Value |
|---|---|
| Indentation | 2 spaces |
| Line length | 80 characters |
| Braces | K&R — opening on same line |
| Namespace content | 0 extra indent |
| Access specifiers (`public:`) | 1 space indent |
| Pointer/ref declarator | with name: `int* p`, `int& r` |

Run `clang-format -style=Google` — it handles all of the above automatically.

## Common Gotchas

| Pattern | Rule |
|---|---|
| `throw std::runtime_error(...)` | No exceptions — return `absl::Status` |
| `dynamic_cast<Derived*>(base)` | No RTTI — use virtual dispatch |
| `new Foo()` / `delete foo` | Use `make_unique<Foo>()` |
| Class member `int count;` | Add trailing `_`: `int count_;` |
| Constant `const int MaxRetries` | Use `constexpr int kMaxRetries` |
| `#include "everything.h"` | Include only what you use; forward-declare the rest |
| `#pragma once` | Prefer `#ifndef` guard (Google's own code uses guards) |
| `auto x = 42;` | Write the type: `int x = 42;` |
| Missing `explicit` on single-arg ctor | Always mark `explicit` |
