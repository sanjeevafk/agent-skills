# Author Guide

Full reference for the CL author perspective, distilled from Google's eng-practices repository.

---

## Writing Small CLs

The single most impactful thing you can do as an author is keep your changes small.

### Why small CLs win
- **Reviewed faster.** Reviewers can find five 5-minute windows more easily than one 30-minute block.
- **Reviewed more thoroughly.** Large CLs overwhelm reviewers; important feedback gets buried or missed.
- **Fewer bugs.** Smaller changes are easier to reason about — for both you and your reviewer.
- **Less wasted work.** If a large CL goes in the wrong direction, you've wasted far more effort.
- **Easier to merge.** Long-lived large changes accumulate conflicts.
- **Easier to roll back.** Small, focused changes are far simpler to revert.
- **Keeps you unblocked.** You can send a small CL for review and immediately start the next one.

Reviewers have discretion to reject a CL solely because it is too large. Writing small CLs from
the start avoids this friction.

### What counts as small?
One self-contained change — ideally addressing **one thing**. This usually means one part of a
feature, not a whole feature at once. As a rough guide:
- ~100 lines: usually fine
- ~1000 lines: almost always too large

The number of files also matters. A 200-line change across one file is different from one spread
across 50 files. When in doubt, go smaller. Reviewers almost never complain about a CL being too small.

A CL must be complete enough that:
- Everything the reviewer needs to understand it is available (code, description, or existing codebase context).
- The system continues to work after submission.
- It doesn't introduce an unused API (include a usage example if you add a new API).

### When large CLs are acceptable
- Deleting an entire file (trivial to review).
- Automated refactoring from a trusted tool, where the reviewer only needs to verify intent.

### Strategies for splitting work

**Stacking:** Write one small CL, send it for review, then immediately start the next CL based
on it. Most VCS tools support this workflow. You stay productive while waiting.

**By files:** Split changes that require different reviewers into separate CLs, coordinating so
reviewers have context for each.

**Horizontally (by layer):** Use shared interfaces or stubs to decouple changes across layers
(e.g., define the API contract first, then implement service and client independently).

**Vertically (by feature):** Break a large feature into parallel sub-features, each a full
vertical slice through the stack.

**Combine both:** Chart out a grid of (layer × sub-feature) and treat each cell as its own CL.

### Keep refactorings separate
Move/rename/restructure in a dedicated CL. Feature logic and refactoring in the same CL make
both harder to understand, review, and roll back. Minor cleanups (renaming a local variable)
are fine to include in a feature CL; large restructuring is not.

### Always include test code
Tests belong in the same CL as the logic they test. "Smallness" is about conceptual scope, not
line count — a CL is complete only when it includes its tests.

Independent test additions (covering pre-existing code, refactoring test helpers) can go in
separate CLs, like any other refactoring.

### Don't break the build
If your CLs are stacked and dependent, make sure each one leaves the system in a working state.

---

## Writing Good CL Descriptions

Your CL description is a permanent record in version control. It will be read by future
developers searching for context, often years from now. Make it count.

### Structure

**First line:** A short, imperative summary of *what* is changing.
- Complete sentence written as an order: "Delete the FizzBuzz RPC and replace it with the new system."
- Short enough to skim in a version history view.
- Stands alone — a future developer should understand what changed without reading the body.

**Body:** Fill in *why* — the context, decisions, tradeoffs, and background that the code itself
can't capture.
- Describe the problem being solved and why this is the right approach.
- Mention shortcomings or limitations if relevant.
- Include bug numbers, design doc links, benchmark results.
- Include enough context that the description is useful even if external links become unavailable.

### Bad descriptions (real examples to avoid)
- "Fix bug." — Which bug? How?
- "Fix build."
- "Add patch."
- "Moving code from A to B."
- "Phase 1."

### Good description examples

**Functionality change:**
```
RPC: Remove size limit on RPC server message freelist.

Servers like FizzBuzz have very large messages and would benefit from reuse.
Make the freelist larger, and add a goroutine that frees the freelist entries
slowly over time, so that idle servers eventually release all freelist entries.
```

**Refactoring:**
```
Construct a Task with a TimeKeeper to use its TimeStr and Now methods.

Add a Now method to Task, so the borglet() getter method can be removed (which
was only used by OOMCandidate to call borglet's Now method). This replaces the
methods on Borglet that delegate to a TimeKeeper.

Allowing Tasks to supply Now is a step toward eliminating the dependency on
Borglet. Eventually, collaborators that depend on getting Now from the Task
should be changed to use a TimeKeeper directly, but this has been an
accommodation to refactoring in small steps.

Continuing the long-range goal of refactoring the Borglet Hierarchy.
```

**Small CL needing context:**
```
Create a Python3 build rule for status.py.

This allows consumers who are already using this as Python3 to depend on a
rule that is next to the original status build rule instead of somewhere in
their own tree. It encourages new consumers to use Python3 if they can,
instead of Python2, and significantly simplifies some automated build file
refactoring tools being worked on currently.
```

### Review the description before submitting
CLs change significantly during review. Re-read your description before merging to make sure
it still accurately reflects what the final CL does.

---

## Handling Reviewer Comments

### Don't take it personally
The reviewer is critiquing the code, not you. Their goal is to help the codebase.

If a comment feels harsh, ask yourself: "What constructive thing are they trying to tell me?"
and respond to that. Never reply in anger — those responses are permanent and visible to
everyone. Walk away if you need to. If the reviewer's tone is genuinely unprofessional, address
it privately and directly.

### Clarify the code, not the review thread
When a reviewer doesn't understand something:
1. First, can you make the code itself clearer? If so, do that.
2. If not, add a code comment explaining *why* the code is written this way.
3. Only if neither of those applies, respond in the review thread.

Code comments help all future readers. A review-thread response helps no one after the review closes.

### Think collaboratively, not combatively
When you disagree with a comment, the goal is shared understanding — not winning.

❌ Bad: "No, I'm not going to do that."

✅ Good: "I went with X because of [these pros/cons] with [these tradeoffs]. My understanding is that using Y would be worse because of [these reasons]. Are you suggesting Y better serves the original tradeoffs, that we should weigh the tradeoffs differently, or something else?"

Explain your reasoning. Ask what they're optimizing for. Usually you can reach consensus on
technical facts. When you can't, escalate rather than stalling.

### Don't defer cleanup
"I'll fix it in a follow-up CL" sounds reasonable but rarely happens. The longer the time since
the original CL, the less likely cleanup is. Reviewers know this. If they ask you to fix
something now, take it seriously — they're protecting the codebase from gradual decay.

If there's a genuinely pre-existing issue that can't be addressed in this CL, file a bug,
assign it to yourself, and add a TODO in the code referencing the bug.

### Resolving conflicts
If you and your reviewer can't reach consensus:
1. Have a synchronous conversation (video call or in person). Record the outcome as a CL comment.
2. Escalate to a tech lead, senior engineer, or team discussion.
3. See the [code review standard](../SKILL.md) for governing principles.

Do not let a CL stall indefinitely over a disagreement.
