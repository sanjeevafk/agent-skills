# Example: Reviewing Over-Engineered Code (Reviewer Perspective)

**Scenario:** A junior developer built a custom 400-line async queue when `asyncio.Queue` was all that was needed. The reviewer wants to flag this without crushing their enthusiasm.

---

**User prompt:**
> I'm reviewing a PR from a junior dev. They added a 400-line async queue implementation when they really just needed `asyncio.Queue`. I want to flag this but I don't want to crush them. How should I write the comment?

---

**Agent response (applying Google eng practices):**

This is a complexity + over-engineering situation — one of the most important things to catch in review, because these costs compound over time. The good news: you can be direct and kind at the same time. Google's guidance is to comment on the code, not the person, and to explain *why* you're asking for the change.

Here's a comment you could leave:

---

> **Consider:** This custom async queue is doing a lot of work that `asyncio.Queue` already handles — including backpressure, consumer coordination, and graceful shutdown. Using the stdlib version would reduce this to a few lines, eliminate a significant maintenance surface, and make the intent immediately clear to future readers.
>
> The implementation here is well-structured — I can see the care that went into it! But the general principle is to prefer solving the problem with existing, battle-tested tools before building custom infrastructure. Would you be open to refactoring to use `asyncio.Queue`?

---

**Why this works:**

1. **Labels severity** — `Consider:` signals this is a genuine suggestion, not a nitpick, but the word choice ("Would you be open to...") keeps it collaborative.
2. **Explains the why** — it spells out the concrete costs of the custom implementation (maintenance, clarity) rather than just saying "use the stdlib."
3. **Acknowledges the good work** — the junior dev put effort in. Noting that is honest and kind without being hollow.
4. **Directs toward simplicity** — it teaches a principle (prefer existing tools) rather than just demanding a fix, which is more durable.

**What to avoid:**
- "Why did you write all this when `asyncio.Queue` exists?" — attacks the decision implicitly.
- "This is way too complex." — vague and discouraging.
- Just approving it because you don't want to seem harsh — that doesn't help the codebase or the developer long-term.

**One more thing:** if the PR is otherwise ready to go, you could give LGTM with this comment and trust the developer to address it (marking it `Optional:` or `Consider:` implies that). If you think it genuinely shouldn't merge with this complexity, use a blocking comment and be explicit: "I'd like to revisit this before merging — the complexity here is significant."
