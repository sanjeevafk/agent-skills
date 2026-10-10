"""Sliding-window rate limiter tests."""

from __future__ import annotations

import asyncio
import time as _time_module

from rate_limiter.rate_limiter import RateLimiter, RateInfo, Clock


# ---------------------------------------------------------------------------
# Clock helpers
# ---------------------------------------------------------------------------

class RealClock:
    """Thin wrapper so tests can use the real wall-clock when they want."""
    def now(self) -> float:
        return _time_module.time()


class FakeClock:
    """Hand-wound clock for deterministic testing."""

    def __init__(self, start: float = 0.0) -> None:
        self._now = start

    def now(self) -> float:
        return self._now

    def advance(self, seconds: float) -> None:
        self._now += seconds


# ===========================================================================
# INCREMENT 1 — basic allow / reject semantics
# ===========================================================================

class TestIncrement1:
    """Core acceptance & rejection behavior."""

    def test_allow_when_empty(self) -> None:
        """A fresh limiter should allow any request when no history exists."""
        clock = FakeClock(start=100.0)
        limiter = RateLimiter(limit=3, window=10.0, clock=clock)

        allowed, info = limiter.allow("user:1")

        assert allowed is True
        assert info.current_count == 1
        assert info.limit == 3
        assert info.window == 10.0
        assert info.retry_after is None

    def test_reject_at_limit(self) -> None:
        """Once *limit* requests have been made within a window, further
        calls are rejected until entries expire."""
        clock = FakeClock(start=50.0)
        limiter = RateLimiter(limit=2, window=10.0, clock=clock)

        # Fill up
        limiter.allow("k1")  # t=50
        limiter.allow("k1")  # t=50, now at limit

        # Over
        allowed, info = limiter.allow("k1")
        assert allowed is False
        assert info.current_count == 2
        assert info.retry_after is not None


class TestBoundaryExactlyAtLimit:
    """The Nth request is allowed; (N+1)th rejected."""

    def test_boundary_exactly_at_limit(self) -> None:
        """The Nth request should be allowed; the (N+1)th rejected."""
        clock = FakeClock(start=100.0)
        limiter = RateLimiter(limit=3, window=10.0, clock=clock)

        for i in range(3):
            allowed, info = limiter.allow("user:1")
            assert allowed is True, f"Request {i + 1} should be allowed"
            assert info.current_count == i + 1

        # One over
        allowed, info = limiter.allow("user:1")
        assert allowed is False
        assert info.current_count == 3
        assert info.retry_after is not None


class TestBoundaryOver:
    """One-request-over boundary with retry_after precision."""

    def test_over_limit_one(self) -> None:
        """When one past the limit, current_count reflects full capacity
        and retry_after tells how long until the oldest slot frees."""
        clock = FakeClock(start=0.0)
        limiter = RateLimiter(limit=2, window=10.0, clock=clock)

        clock.advance(1.0)
        limiter.allow("u")  # count=1, t=1
        clock.advance(1.0)
        limiter.allow("u")  # count=2, t=2, at limit

        clock.advance(5.0)
        allowed, info = limiter.allow("u")  # 4th call

        assert allowed is False
        assert info.current_count == 2
        assert info.limit == 2
        assert info.retry_after is not None
        assert info.retry_after > 0  # oldest entry at t=1 expires at t=11; now=t=7 → 4s left


# ===========================================================================
# INCREMENT 3 — clock injection & window rollover
# ===========================================================================

class TestWindowRollover:
    """Expired entries are evicted so old requests stop counting."""

    def test_window_rollover(self) -> None:
        """After the window passes, old entries expire and new requests
        are allowed again."""
        clock = FakeClock(start=0.0)
        limiter = RateLimiter(limit=2, window=5.0, clock=clock)

        # Fill the bucket
        limiter.allow("k")  # t=0
        limiter.allow("k")  # t=0, full

        # Should be rejected
        allowed, _ = limiter.allow("k")
        assert allowed is False

        # Advance past the window
        clock.advance(6.0)  # now t=6, all entries from t=0 expired

        # Should be allowed again
        allowed, info = limiter.allow("k")
        assert allowed is True
        assert info.current_count == 1


class TestClockInjection:
    """Using a fake clock lets us skip real-time waits entirely."""

    def test_clock_injection(self) -> None:
        """A FakeClock replaces time.sleep() logic so tests run instantly.
        
        Demonstration: fill a rate-limited key, verify rejection, advance the
        fake clock past one entry's expiry, and confirm a new request succeeds
        without any real waiting.
        """
        clock = FakeClock(start=1000.0)
        limiter = RateLimiter(limit=1, window=1.0, clock=clock)

        # First call: allowed
        allowed, info = limiter.allow("u")
        assert allowed is True
        assert info.current_count == 1

        # Second call at same time: denied
        allowed, info = limiter.allow("u")
        assert allowed is False
        assert info.retry_after is not None

        # Injected time jump — no sleep involved
        clock.advance(1.1)

        # After window rollover via clock injection: allowed again
        allowed, info = limiter.allow("u")
        assert allowed is True
        assert info.current_count == 1


# ===========================================================================
# INCREMENT 4 — concurrent async acquisition
# ===========================================================================

class TestConcurrent:
    """Two coroutines competing for the same key can't exceed the limit."""

    def test_concurrent_from_two_coroutines(self) -> None:
        """When two coroutines race on the same key, at most *limit* calls
        should succeed. The asyncio per-key lock prevents over-counting."""
        clock = FakeClock(start=0.0)
        limiter = RateLimiter(limit=2, window=10.0, clock=clock)
        results: list[bool] = []
        
        async def _worker(n: int) -> None:
            for _ in range(n):
                allowed, _ = await limiter.allow_async("shared")
                results.append(allowed)

        # Launch 5 coroutines each trying 3 requests = 15 attempts
        async def _run() -> None:
            await asyncio.gather(*[_worker(3) for _ in range(5)])
        asyncio.run(_run())

        allowed_count = sum(1 for r in results if r)
        denied_count = sum(1 for r in results if not r)

        assert allowed_count == 2, f"Expected exactly 2 allowed, got {allowed_count}"
        assert denied_count == 13
        assert len(results) == 15


# ===========================================================================
# INCREMENT 5 — key isolation
# ===========================================================================

class TestKeyIsolation:
    """Each key maintains an independent rate bucket."""

    def test_key_isolation(self) -> None:
        """Using up Key A's quota must not affect Key B."""
        clock = FakeClock(start=0.0)
        limiter = RateLimiter(limit=1, window=10.0, clock=clock)

        # Exhaust key A
        allowed_a, _ = limiter.allow("A")
        assert allowed_a is True
        denied_a, _ = limiter.allow("A")
        assert denied_a is False

        # Key B should be unaffected
        allowed_b, info_b = limiter.allow("B")
        assert allowed_b is True
        assert info_b.current_count == 1

    def test_multiple_keys_independent_counts(self) -> None:
        """Three keys, each with limit=1; each tracks independently."""
        clock = FakeClock(start=100.0)
        limiter = RateLimiter(limit=1, window=10.0, clock=clock)

        infos = [limiter.allow(f"k{i}")[1] for i in range(3)]
        for info in infos:
            assert info.allowed
            assert info.current_count == 1

        # Second call to each should be denied
        for i in range(3):
            allowed, _ = limiter.allow(f"k{i}")
            assert allowed is False

