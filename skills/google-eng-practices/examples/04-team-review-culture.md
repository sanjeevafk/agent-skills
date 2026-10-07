# Example: Fixing Slow Code Review Culture (Team/Process)

**Scenario:** Reviews take 3-4 days. Senior engineers defend thoroughness; junior devs feel blocked.

---

**User prompt:**
> Our team's code reviews are taking 3-4 days on average. Some senior engineers say they're too busy to review quickly and the reviews are thorough, so it's worth it. But the junior devs are frustrated and feel blocked. How do we fix this?

---

**Agent response (applying Google eng practices):**

This is a very common pattern, and Google's eng practices have a clear answer: **the slowness is the problem, not the thoroughness**. The good news is that fixing speed usually fixes the frustration — without sacrificing quality.

### Why the seniors are wrong (kindly)

The argument "we're thorough, so it's worth the wait" confuses two things:
- **Response time** (how quickly you respond to a review request)
- **Review completeness** (how thorough the review is when you do it)

You can be thorough *and* fast. The target is to **respond within one business day** — not to finish the entire review, just to send a meaningful response. That response might be:
- "I'll look at this Thursday morning" (sets expectations)
- "Here are my design-level concerns — I'll finish line-level review once those are addressed"
- "LGTM with a few minor comments"

Most complaints about strict reviewers disappear when the *response time* improves. The friction isn't that seniors have high standards — it's that junior devs are sitting idle for days not knowing what's wrong.

### Practical fixes

**1. Establish a response-time norm, not a completion-time norm.**  
The rule should be: acknowledge a review request within one business day. A quick response ("I'll look at this Friday at 9am") costs 30 seconds and eliminates days of anxiety.

**2. Teach "LGTM with comments."**  
Seniors should feel empowered to approve a PR while leaving minor suggestions. This unblocks the author while still communicating the feedback. It's appropriate when:
- The remaining comments don't block the change
- You trust the author to address them

**3. Don't interrupt deep work — but respond at break points.**  
Senior engineers are right that context-switching is expensive. The solution isn't "review whenever" — it's "designate review windows." First thing in the morning, after lunch, after a meeting. Review then, not mid-session.

**4. Ask juniors to write smaller PRs.**  
Some of the slowness may be self-inflicted — large PRs are harder to schedule time for. If juniors learn to send smaller changes, reviews become easier to fit into busy schedules.

**5. Cross-timezone consideration.**  
If reviewer and author are in different time zones, a 3-4 day cycle might be just 2-3 response exchanges, each taking a full day because of the offset. In this case, "LGTM with comments" becomes even more important — don't hold up a PR for 24 hours just to say "all good."

### The deeper point

Slow reviews hurt code health, counterintuitively. When reviews are slow:
- Developers avoid sending small, incremental improvements (not worth the wait).
- Code cleanup and refactoring PRs get deprioritized.
- Pressure builds to approve things that shouldn't be approved, just to unblock people.

Fast *and* rigorous is the goal. It's achievable. The team just needs to agree that response time is a shared commitment, not an individual preference.
