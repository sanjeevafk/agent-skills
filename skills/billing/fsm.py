"""Subscription billing finite-state machine.

Five states govern a subscription's lifecycle:

    DRAFT -> PENDING -> ACTIVE -> PAST_DUE -> PENDING
             |  |        |          |
             |  +--------+----------+----> CANCELED (terminal)

Transition rules are data-driven (``_TRANSITION_RULES``) so the legal graph can
be inspected or extended without touching the transition logic. Every successful
transition emits a ``TransitionEvent`` onto ``history`` and notifies registered
handlers; handlers are isolated so one raising does not break the transition or
the other handlers.

Auto-cancel is time-gated rather than action-gated: ``auto_cancel`` is only
legal from PENDING and only once ``TIMEOUT_GRACE_PERIOD_SECONDS`` has elapsed
since ``created_at``.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

__all__ = [
    "SubscriptionState",
    "SubscriptionStateMachine",
    "TransitionEvent",
    "InvalidTransitionError",
    "TIMEOUT_GRACE_PERIOD_SECONDS",
]

# An abandoned PENDING subscription is swept after this long. 24 hours matches
# the billing convention of a full day to finish or abandon setup.
TIMEOUT_GRACE_PERIOD_SECONDS = 24 * 60 * 60


class InvalidTransitionError(Exception):
    """Raised when an action is not legal from the current state."""


class SubscriptionState(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"


# action -> {source state -> target state}. An absent entry is illegal, which is
# how terminal states reject everything without a special case.
_TRANSITION_RULES: Dict[str, Dict[SubscriptionState, SubscriptionState]] = {
    "pending": {SubscriptionState.DRAFT: SubscriptionState.PENDING},
    "activate": {SubscriptionState.PENDING: SubscriptionState.ACTIVE},
    "past_due": {SubscriptionState.ACTIVE: SubscriptionState.PAST_DUE},
    "resume": {SubscriptionState.PAST_DUE: SubscriptionState.PENDING},
    # ACTIVE must pass through PAST_DUE before it can cancel; a cancel is only
    # directly legal once the customer has not settled a bill.
    "cancel": {
        SubscriptionState.PENDING: SubscriptionState.CANCELED,
        SubscriptionState.PAST_DUE: SubscriptionState.CANCELED,
    },
}

_AUTO_CANCEL_TARGET = SubscriptionState.CANCELED


@dataclass(frozen=True)
class TransitionEvent:
    """An immutable record of one state change."""

    source: str
    target: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    extra: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"{self.source}→{self.target}"

    def __repr__(self) -> str:
        return (
            f"TransitionEvent(source={self.source!r}, target={self.target!r}, "
            f"timestamp={self.timestamp.isoformat()}, extra={self.extra!r})"
        )


# Handlers are notified with the event; failures are swallowed on purpose so a
# bad subscriber cannot abort a state change that already succeeded.
TransitionHandler = Callable[[TransitionEvent], None]


class SubscriptionStateMachine:
    """Thread-safe subscription lifecycle machine.

    All state reads and writes are serialised by a single re-entrant lock, so
    the check-and-mutate in :meth:`transition` is atomic. Two threads racing the
    same action produce exactly one success and one ``InvalidTransitionError``.
    """

    def __init__(self, initial_state: SubscriptionState = SubscriptionState.DRAFT):
        if not isinstance(initial_state, SubscriptionState):
            raise TypeError("initial_state must be a SubscriptionState")
        self._lock = threading.RLock()
        self._state = initial_state
        self._history: List[TransitionEvent] = [
            TransitionEvent(source="__init__", target=initial_state.value)
        ]
        self._handlers: List[TransitionHandler] = []
        self.created_at = datetime.now(timezone.utc)

    # ------------------------------------------------------------------ reads

    @property
    def current_state(self) -> SubscriptionState:
        with self._lock:
            return self._state

    @property
    def history(self) -> List[TransitionEvent]:
        """A copy of the transition log; mutating it cannot corrupt state."""
        with self._lock:
            return list(self._history)

    def can_transition(self, action: str) -> bool:
        with self._lock:
            return self._resolve(action) is not None

    # -------------------------------------------------------------- mutations

    def transition(self, action: str) -> TransitionEvent:
        """Apply ``action``. Raises ``InvalidTransitionError`` if not legal."""
        with self._lock:
            target = self._resolve(action)
            if target is None:
                raise InvalidTransitionError(
                    f"cannot {action!r} from state {self._state.value!r}"
                )
            event = self._apply(action, target)

        self._notify(event)
        return event

    def trigger_transition(
        self,
        action: str,
        now: Optional[datetime] = None,
    ) -> TransitionEvent:
        """Apply a time-gated action.

        ``auto_cancel`` is only legal from PENDING and only after
        ``TIMEOUT_GRACE_PERIOD_SECONDS`` has elapsed. ``now`` overrides the clock
        for testing.
        """
        if action == "auto_cancel":
            return self._auto_cancel(now)
        return self.transition(action)

    def _auto_cancel(self, now: Optional[datetime]) -> TransitionEvent:
        moment = now or datetime.now(timezone.utc)
        with self._lock:
            if self._state is not SubscriptionState.PENDING:
                raise InvalidTransitionError(
                    f"auto_cancel is only legal from PENDING, not "
                    f"{self._state.value!r}"
                )
            elapsed = (moment - self.created_at).total_seconds()
            if elapsed < TIMEOUT_GRACE_PERIOD_SECONDS:
                remaining = TIMEOUT_GRACE_PERIOD_SECONDS - elapsed
                raise InvalidTransitionError(
                    f"auto_cancel blocked: grace period not elapsed "
                    f"({remaining:.0f}s remaining)"
                )
            event = self._apply(
                "auto_cancel",
                _AUTO_CANCEL_TARGET,
                extra={"reason": "grace_period_expired"},
            )

        self._notify(event)
        return event

    def on_transition(self, handler: TransitionHandler) -> None:
        with self._lock:
            if handler not in self._handlers:
                self._handlers.append(handler)

    def remove_transition_handler(self, handler: TransitionHandler) -> None:
        with self._lock:
            if handler in self._handlers:
                self._handlers.remove(handler)

    # --------------------------------------------------------------- internals

    def _resolve(self, action: str) -> Optional[SubscriptionState]:
        """Resolve the target for ``action``, or None when it is illegal."""
        if action == "auto_cancel":
            # Only ever reachable from PENDING, and only via the grace period,
            # so transition() must not accept it directly.
            return None
        return _TRANSITION_RULES.get(action, {}).get(self._state)

    def _apply(
        self,
        action: str,
        target: SubscriptionState,
        extra: Optional[Dict[str, Any]] = None,
    ) -> TransitionEvent:
        event = TransitionEvent(
            source=self._state.value,
            target=target.value,
            extra=dict(extra or {}),
        )
        self._state = target
        self._history.append(event)
        return event

    def _notify(self, event: TransitionEvent) -> None:
        with self._lock:
            handlers = list(self._handlers)
        for handler in handlers:
            try:
                handler(event)
            except Exception:
                # A failing subscriber must not undo a transition that is already
                # committed, nor stop the remaining handlers.
                continue