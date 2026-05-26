# Example: Pushing Back on Reviewer Feedback (Author Perspective)

**Scenario:** A reviewer repeatedly asks the author to split a 200-line class into smaller pieces, but the author believes the split would harm cohesion. The reviewer is insistent.

---

**User prompt:**
> My reviewer keeps asking me to break a 200-line class into smaller pieces, but the class is already well-organized and I think the split would make the code harder to follow because the pieces are tightly coupled. They're being pretty insistent. How do I push back without causing conflict?

---

**Agent response (applying Google eng practices):**

Pushback is legitimate — reviewers aren't always right, and you're closer to the code than they are. Google's process explicitly recognizes this. The key is to make your disagreement *substantive and collaborative*, not defensive.

### First: genuinely consider whether they're right

Before drafting your response, sit with the concern. Ask yourself:
- Is the coupling I perceive *essential* coupling (these things really must change together) or *accidental* coupling (they happen to be together, but don't need to be)?
- Would a new developer coming to this code for the first time find a 200-line class easy to navigate? Or would they appreciate a smaller, focused entry point?
- Is my reluctance partly because I wrote it and I'm used to it?

If after this reflection you still believe the split is wrong, your pushback is on solid ground.

### How to push back well

The goal is to make the reviewer understand your *reasoning*, not to win an argument. Something like:

> I hear you on the complexity concern — I want to make sure I understand what you're seeing. My hesitation with splitting this class is that `ComponentA`, `ComponentB`, and `ComponentC` all share mutable state and a lifecycle that must stay synchronized. If we separate them, callers need to manage that coordination themselves, which I think actually increases the total complexity of the system.
>
> That said, I could be wrong about where the right boundary is. Could you sketch what the split would look like? I'd like to understand whether you see a way to isolate the lifecycle management, because I haven't found one.

**Why this works:**
- It demonstrates that you understand their concern (complexity).
- It explains your specific objection based on engineering principles (shared state, lifecycle).
- It invites them to elaborate rather than digging into a position.
- It leaves room for you to be convinced — which you might be.

### If you're still in disagreement after that exchange

1. **Propose a concrete alternative.** "What if instead of splitting the class, I extract the largest private method into a helper and add more comments explaining the lifecycle?" Sometimes a partial concession shows good faith and resolves the underlying concern.

2. **Ask for the principle, not the solution.** "Is your concern that this class is hard to understand? Or that it's hard to test? Or that it violates SRP?" Understanding *why* they want the split often reveals whether there's a third option.

3. **Escalate if truly stuck.** If you've gone multiple rounds and can't reach consensus, the right move is to bring in a third opinion — a tech lead or another senior engineer. Don't let the PR stall indefinitely. Google's process says: do not let a CL sit because author and reviewer can't agree. Get a decision.

### What to avoid

- "No, I'm not going to do that." — shuts down the conversation.
- Explaining your reasoning only in the review thread — if you're going back and forth more than twice, get on a call.
- Deferring ("I'll refactor it in a follow-up") — reviewers rightly distrust this, because it rarely happens.
- Caving when you still disagree, just to get the PR merged — the reviewer's concern may be valid, and merging code you know is problematic stores up debt.
