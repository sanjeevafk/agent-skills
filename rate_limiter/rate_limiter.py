"""Sliding-window rate limiter with per-key tracking."""

from __future__ import annotations

import asyncio
import time as _time_module
from collections import OrderedDict
from dataclasses import dataclass
from typing import Protocol


# ---------------------------------------------------------------------------
# Public types
# ---------------------------------------------------------------------------

class Clock(Protocol):
    """Time source that can be injected for testing."""
    def now(self) -> float: ...


def _real_clock() -> Clock:
    """Return a clock backed by ``time.perf_counter``."""
    class Impl:
        def now(self) -> float:
            return _time_module.time()
    return Impl()


@dataclass(frozen=True)
class RateInfo:
    allowed: bool
    current_count: int          # requests currently in window
    limit: int
    window: float               # window size in seconds
    retry_after: float | None   # seconds until one slot frees up, if denied


# ---------------------------------------------------------------------------
# Core limiter
# ---------------------------------------------------------------------------

class RateLimiter:
    """Per-key sliding-window rate limiter.

    Each key maintains an ordered list of (timestamp, sequence) entries.
    Sequence numbers guarantee uniqueness even when multiple requests share
    the same clock tick.

    Parameters
    ----------
    limit : int
        Maximum number of requests allowed within *window* seconds.
    window : float
        Sliding window duration in seconds.
    clock : Clock | None
        Time source; defaults to real wall-clock.

    Example
    -------
    >>> limiter = RateLimiter(limit=10, window=60.0)
    >>> allowed, info = limiter.allow("user:42")
    """

    def __init__(self, limit: int, window: float, clock: Clock | None = None) -> None:
        self._limit = limit
        self._window = window
        self._clock = clock or _real_clock()
        self._stores: dict[str, OrderedDict[int, tuple[float, int]]] = {}
        self._locks: dict[str, asyncio.Lock] = {}

    # -- internal helpers ---------------------------------------------------

    def _get_store(self, key: str) -> tuple[OrderedDict[int, tuple[float, int]], asyncio.Lock]:
        """Lazily create a per-key store and lock."""
        if key not in self._stores:
            self._stores[key] = OrderedDict()
            self._locks[key] = asyncio.Lock()
        return self._stores[key], self._locks[key]

    @staticmethod
    def _prune(store: OrderedDict[int, tuple[float, int]], cutoff: float) -> None:
        """Evict entries whose timestamp is strictly before *cutoff*."""
        while store and store[next(iter(store))][0] < cutoff:
            store.popitem(last=False)

    # -- synchronous API (callable without event loop) ----------------------

    def allow(self, key: str) -> tuple[bool, RateInfo]:
        """Check whether *key* is allowed under the rate limit.

        This method does **not** acquire any lock — it is safe for
        single-threaded / serial usage only.  For concurrent access
        use ``allow_async``.
        """
        now = self._clock.now()

        store, _lock = self._get_store(key)
        self._prune(store, now - self._window)

        count = len(store)

        if count < self._limit:
            store[count] = (now, count)
            return True, RateInfo(
                allowed=True,
                current_count=count + 1,
                limit=self._limit,
                window=self._window,
                retry_after=None,
            )

        # Denied — calculate how long until oldest entry expires
        oldest_ts, _ = next(iter(store.values()))
        retry_after = (oldest_ts + self._window) - now
        return False, RateInfo(
            allowed=False,
            current_count=count,
            limit=self._limit,
            window=self._window,
            retry_after=max(retry_after, 0.0),
        )

    # -- async API (with distributed-safe locking) --------------------------

    async def allow_async(self, key: str) -> tuple[bool, RateInfo]:
        """Coroutinesafe variant of :meth:`allow`.

        Acquires a per-key lock so concurrent coroutines competing on the
        same key cannot exceed the configured limit.
        """
        _, lock = self._get_store(key)
        async with lock:
            return self.allow(key)
