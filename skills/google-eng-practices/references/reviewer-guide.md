# Reviewer Guide

Full reference for the reviewer perspective, distilled from Google's eng-practices repository.

---

## The Standard

**Approve a CL once it clearly improves the overall code health of the system — even if it isn't perfect.**

This is the senior principle. The reviewer's job is not to insist on ideal code; it is to prevent
the codebase from *degrading* while still allowing progress. Codebases most often deteriorate
through many small compromises, not dramatic mistakes. Guard against small regressions.

### The balance
- If you make every review a grind, developers stop improving the codebase. That's bad.
- If you rubber-stamp everything, code health erodes. That's also bad.
- The goal is *continuous improvement*, not perfection on every change.

### Key principles
- **Technical facts and data overrule opinions and personal preferences.**
- The style guide is the authority on style. Purely personal style preferences (not in the guide) should not block a CL.
- **Software design is almost never just personal preference.** It rests on engineering principles. If multiple approaches are genuinely equivalent, accept the author's.
- When no other rule applies, ask the author to be consistent with the existing codebase — as long as that doesn't worsen code health.

### Mentoring
It's fine and valuable to leave educational comments. Prefix them with `Nit:` or `FYI:` to
signal they are not required for approval. Sharing knowledge is part of code health.

---

## What to Look For

Work through these dimensions when reviewing any change. Let the
[review standard](#the-standard) guide your judgment on each one.

### Design
The most important question. Does the overall architecture make sense?
- Do the interactions between components in the CL make sense?
- Does this change belong in the codebase at all, or in a library?
- Does it integrate cleanly with the rest of the system?
- Is this the right time to add this functionality?

### Functionality
Does the code do what the developer intended, and is that intention good for users?
- Think about edge cases and failure modes.
- For concurrent code: are there potential race conditions or deadlocks?
- For UI changes: you may want to see a demo — visual behavior is hard to infer from code.

### Complexity
"Too complex" means: a reader can't understand it quickly, or a future developer is likely to
introduce bugs when modifying it.
- Are individual lines, functions, and classes as simple as they can be?
- Watch for **over-engineering**: solving problems that don't exist yet. Encourage solving
  the problem at hand now; the future problem can be solved when it arrives and its actual
  shape is known.

### Tests
- Tests should be in the same CL as the logic change (except emergencies).
- Will the test actually *fail* when the code is broken?
- Is each test making clear, focused assertions?
- Tests are code too — don't accept unnecessary complexity in them.

### Naming
Good names fully communicate what something is or does, without being so long they become hard
to read. Names are first-class documentation.

### Comments
- Good comments explain *why* code exists, not *what* it does.
- If the code isn't clear enough to explain itself, the code should be made simpler.
- Regular expressions and complex algorithms are reasonable exceptions — comments on *what*
  they do are appropriate there.
- Check whether pre-existing comments (TODOs, warnings) can now be removed.
- Documentation (docstrings, API docs) is different from inline comments — it should explain
  purpose, usage, and behavior.

### Style
Follow the project's style guide. Comment on style deviations you notice, but prefix
non-blocking suggestions with `Nit:`. Don't block a CL solely on personal style preferences.

If an author mixes large-scale style reformatting with logic changes, ask them to split it:
a formatting-only CL first, then the logic change. Mixed CLs are hard to review and hard to roll back.

### Documentation
If the CL changes how users build, test, interact with, or release code, check that it also
updates the relevant documentation (READMEs, API docs, changelogs). If it deletes or deprecates
something, the docs should follow.

### Every line
In general, look at every line of code you are asked to review. It is acceptable to skim
data files or generated code, but never skim a human-written function or class. If you don't
understand some code, ask the author to clarify — and treat that confusion as a signal that
future readers will share it.

If you are only reviewing part of a CL (e.g., your area of expertise), say so in a comment
so expectations are clear.

### Context
Look at the full file, not just the diff. Four new lines might look fine in isolation but
belong inside a 50-line method that needs to be decomposed. Also consider the system as a
whole: is this change making the system more or less complex overall?

### Good things
If you see something done well — a clean algorithm, excellent test coverage, an elegant
approach — say so. Positive reinforcement of good practices is part of good mentoring and
makes code review a more human experience.

---

## Navigating a Change

### Step 1: Get the big picture
- Read the CL description. Does the change make sense? Is the description informative?
- If the change should not happen at all, say so immediately and courteously, and suggest
  what should be done instead. Don't let the author sink more work into the wrong direction.

### Step 2: Find the most important parts
- Identify the file(s) with the core logic. Review those for design first.
- If there are significant design problems, send that feedback immediately — even before
  finishing the rest of the review. Waiting wastes time (the author may build more on top of
  a flawed design) and delays the author (major rewrites take time).
- If the CL is too large to know where to start, ask the author to split it or tell you what
  to look at first.

### Step 3: Review the rest in sequence
- After the major parts, go through remaining files in order.
- Reading tests before main code is often helpful — tests reveal intended behavior.

---

## Speed

**Respond within one business day.** For an active review, multiple rounds in a single day is
the ideal.

The *response* time matters most, not the total time for the review to close. Quick responses
— even "I'll look at this tomorrow morning" — dramatically reduce developer frustration.

**Don't interrupt deep focus work** to do a review. The cognitive cost of context-switching
outweighs the benefit of a faster response. Wait for a natural break.

### LGTM with comments
You can approve a CL while still leaving minor comments. Do this when:
- You're confident the author will address the remaining comments appropriately.
- The remaining comments are not blocking requirements.
- The suggestions are minor (sort imports, fix a typo, etc.).

This is especially important across time zones — don't make someone wait a full working day
just for a "LGTM, no changes."

### Large CLs
Ask them to be split. A CL so large you don't know when you'll finish it is almost always
splittable. If it truly cannot be split, at least write comments on the overall design and
send it back so the author can take action.

---

## Writing Comments

- Be courteous. Comment on the **code**, not the **developer**.
- Explain *why*. A good comment demonstrates understanding of the code and articulates why
  a change would improve code health.
- Label severity:
  - (no label) — blocking requirement
  - `Nit:` — minor polish, author may choose to ignore
  - `Optional:` / `Consider:` — good idea but not required
  - `FYI:` — informational, no action expected in this CL
- Balance pointing out problems with providing guidance. Sometimes a concrete suggestion is
  most helpful; sometimes pointing to the issue and letting the author solve it teaches more
  and yields a better solution.
- If you see good things, say so.
- When you ask the author to explain something, the explanation should end up in the code
  (clearer code or a code comment), not only in the review thread.

---

## Handling Pushback

When a developer pushes back:
1. **Consider whether they're right.** They know the code better than you. If their argument
   makes sense from a code-health perspective, acknowledge it and move on.
2. **If you still believe the change is needed**, explain your reasoning more fully. Show
   that you understand their point and explain why the code-health benefit still justifies
   the change. Stay polite — hear them, disagree constructively.
3. **"I'll clean it up later"** — this almost never happens. If the issue is significant,
   insist on fixing it now. If it can't be fixed now and is an exposure of a pre-existing
   issue, have the author file a bug and add a TODO referencing that bug.
4. **Strictness complaints** often fade when you improve your response speed. Fast, strict
   reviews are far less frustrating than slow, strict ones.
5. **Unresolvable conflicts**: escalate. Don't let a CL sit indefinitely.
