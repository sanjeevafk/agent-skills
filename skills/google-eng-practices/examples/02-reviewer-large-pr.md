# Example: Handling a Massive PR (Reviewer Perspective)

**Scenario:** A PR arrives with 47 files and 2,300 lines spanning auth, billing, and notifications — all to "refactor the user model."

---

**User prompt:**
> Someone sent me a PR with 47 files changed and 2,300 lines. It touches the auth service, the billing module, and the notification system — apparently to 'refactor the user model'. I don't even know where to start. What do I do?

---

**Agent response (applying Google eng practices):**

You are right to be stuck — this PR is too large to review effectively, and that's not your problem to solve. Google's guidance is direct: **reviewers have discretion to reject a CL solely because it is too large**, and asking for a split is appropriate and expected.

Here's how to handle it:

### Step 1: Respond promptly, not with silence

Don't sit on a huge PR hoping to find time. Send a quick response today:

> Thanks for the work here — this is clearly a significant effort. Before I dig in, I want to flag that 2,300 lines across auth, billing, and notifications is more than I can review thoroughly in a single pass. I'd like to ask you to split this into smaller, focused PRs.
>
> Some possible splits:
> - The core user model schema change (data model only)
> - Auth service updates
> - Billing service updates  
> - Notification service updates
>
> If you want to talk through how to sequence these (some may have dependencies), I'm happy to do that. In the meantime, if there's one file or section that represents the "heart" of the change, point me at it and I'll start there.

### Step 2: If they genuinely can't split it

Sometimes a migration truly can't be decomposed. If that's the case:
- Ask them to walk you through the architecture of the change (video call or design doc).
- Review in passes — first the core model, then each service separately.
- Send design-level feedback first, before getting into line-level review.
- Be explicit: "I'll need more than one review session for something this size."

### Step 3: If you do start reviewing now

Navigate systematically:
1. Read the PR description. Does the overall direction make sense?
2. Find the "heart" — probably the user model definition itself. Review that for design.
3. If there are design problems in the model, send that feedback now. Don't review all 47 files if the foundation is wrong — most of that code may change anyway.

### The broader point

A PR this size is usually a sign of planning debt: the author didn't plan how to submit the work incrementally. The kindest thing you can do (for them and for the codebase) is redirect early, before they're emotionally invested in defending 2,300 lines as a single unit. The earlier you say "please split this," the less work is wasted.
