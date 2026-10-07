# Example: Structuring a PR as the Author

**Scenario:** A developer finished an API rate-limiting feature touching middleware, a Redis counter service, unit tests, and API spec — and wants to know how to structure it as a PR.

---

**User prompt:**
> I just finished a feature that adds rate limiting to our API. It touches the middleware layer, a new Redis-backed counter service, unit tests, and I updated the OpenAPI spec. How should I structure this as a PR — should it be one PR or multiple? And what should the description say?

---

**Agent response (applying Google eng practices):**

### Should this be one PR or multiple?

Most likely **multiple**, but the right split depends on whether the pieces have a clean dependency order. Let me reason through it:

**The natural split here:**

1. **PR 1 — The Redis counter service** (the new dependency)  
   Just the `RateLimitCounter` class/module and its unit tests. This is a pure addition with no integration yet — reviewers can evaluate the data model and logic independently.

2. **PR 2 — The middleware integration + OpenAPI spec update**  
   Wire the counter into the middleware, write integration tests, update the API spec. This depends on PR 1 and is the "this is live" change.

**Why split this way?**
- PR 1 is pure new code that can be reviewed for correctness in isolation.
- PR 2 is the integration risk — reviewers can focus on "does this fit the middleware design?" rather than simultaneously evaluating the Redis logic.
- If PR 1 gets feedback requiring a redesign (e.g., "use a different Redis client"), PR 2 hasn't been written yet around the wrong design.

**When one PR is fine:**
If the Redis service is very small (say, under 80 lines) and the middleware wiring is straightforward, combining them into one PR is defensible. Reviewers rarely complain about a CL being too small; they often complain about one being too large.

---

### PR descriptions

**PR 1 description:**
```
Add Redis-backed rate limit counter service.

Implements RateLimitCounter, a thin wrapper around Redis that tracks
per-client request counts using a sliding window algorithm. Uses atomic
INCR + EXPIRE to avoid race conditions under concurrent load.

Intended to be consumed by the API rate-limiting middleware in a
follow-up PR. Includes unit tests with a Redis mock.
```

**PR 2 description:**
```
Add rate limiting middleware using RateLimitCounter.

Applies per-client rate limits at the API gateway layer using the
RateLimitCounter service introduced in [link to PR 1].

Limits: 100 req/min for authenticated users, 20 req/min for
unauthenticated. Returns HTTP 429 with a Retry-After header when
the limit is exceeded.

OpenAPI spec updated to document 429 responses on all endpoints.
Integration tests cover both the happy path and the throttled path.
```

---

### Key principles applied
- **First line is imperative and specific** — a future developer searching git log will immediately understand what changed.
- **Body answers "why"** — the sliding window choice, the limit values, the Retry-After behavior are all decisions that should be documented.
- **Each PR is self-contained** — PR 1 is useful and reviewable on its own; PR 2 depends on it but doesn't require it to be merged first (you can stack them).
