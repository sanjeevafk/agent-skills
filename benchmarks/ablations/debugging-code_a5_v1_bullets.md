[CHECKLIST GUIDELINES]

## Starting a Session
- **Have a hypothesis** — set a breakpoint where you expect the bug: `dap debug script.py --break script.py:42`
- **Conditional breakpoint** — only stop when a condition is met: `dap debug script.py --break "script.py:42:x > 5"` (
- **Multi-file app** — breakpoints across modules: `--break src/api/routes.py:55 --break src/models/user.py:30`
- **No hypothesis, small program** — walk from entry: `dap debug script.py --stop-on-entry` (avoid for large projects —
- **Exception, location unknown** — `dap debug script.py --break-on-exception raised` (Python) / `all` (Go/JS)
- **Remote process** — `dap debug --attach host:port --backend <name>`
- **Process already running (stuck server, live issue)** — attach without restarting:
**Session isolation:** `--session <name>` keeps concurrent agents from interfering.
## The Debugging Mindset
**Two strikes, rethink.:** If two hypotheses fail at the same location, your mental model is wrong.
**Escalate gradually.:** Start with `dap eval` to test a quick hypothesis. Use conditional breakpoints
**Mimic the user journey.:** If you're debugging a user flow, set breakpoints along the path you expect the code to take.
**Set breakpoints instead of prints.:** When you feel the urge to print something, set a breakpoint instead.
## Know Your State
- Do the local variables have the values I expected?
- Is the call stack showing the code path I expected?
- Does the output so far reveal anything unexpected?
**Trace causation up the stack.:** If a value is wrong at frame 0, check `dap eval "<expr>" --frame 1` to see what the
## Setting Breakpoints Strategically
- Set where the problem *begins*, not where it *manifests*
- Exception at line 80? Root cause is upstream — start earlier
- Uncertain? Bisect: `--break f:20 --break f:60` — wrong state before or after halves the search space
**Where to break**
- **Boundaries** — where data crosses a format, representation, or module boundary; state is cleanest here
- **State transitions** — the line that assigns or mutates the corrupted value
- **Wrong branch** — the condition whose inputs led to the bad path
- **Antipatterns** — don't break inside library code; break at the call site instead. Don't use unconditional breaks in
## Walkthrough
**Bug: `compute()` returns `None`**
**No hypothesis (exception, unknown location)**
