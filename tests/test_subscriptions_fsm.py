"""Tests for subscription billing finite-state machine."""

import pytest


# ---------------------------------------------------------------------------
# Slice 1 — SubscriptionState enum with all billing lifecycle states
# ---------------------------------------------------------------------------

class TestSubscriptionStates:

    def test_all_five_states_exist(self):
        """The FSM exposes exactly five billing states."""
        from skills.billing import SubscriptionState

        assert hasattr(SubscriptionState, "DRAFT")
        assert hasattr(SubscriptionState, "PENDING")
        assert hasattr(SubscriptionState, "ACTIVE")
        assert hasattr(SubscriptionState, "PAST_DUE")
        assert hasattr(SubscriptionState, "CANCELED")

    def test_state_values_match_billing_terminology(self):
        """Each state maps to its expected string value."""
        from skills.billing import SubscriptionState

        assert SubscriptionState.DRAFT.value == "draft"
        assert SubscriptionState.PENDING.value == "pending"
        assert SubscriptionState.ACTIVE.value == "active"
        assert SubscriptionState.PAST_DUE.value == "past_due"
        assert SubscriptionState.CANCELED.value == "canceled"

    def test_initializing_with_draft_state_works(self):
        """A subscription begins in DRAFT — the machine accepts it as initial state."""
        from skills.billing import SubscriptionStateMachine, SubscriptionState

        sm = SubscriptionStateMachine(initial_state=SubscriptionState.DRAFT)
        assert sm.current_state is SubscriptionState.DRAFT


# ---------------------------------------------------------------------------
# Slice 2 — Valid transitions: Draft → Pending; invalid transitions rejected
# ---------------------------------------------------------------------------

class TestValidTransitions:

    def test_draft_to_pending_succeeds(self):
        """DRAFT can transition to PENDING via the 'pending' action."""
        from skills.billing import SubscriptionStateMachine, SubscriptionState

        sm = SubscriptionStateMachine(initial_state=SubscriptionState.DRAFT)
        sm.transition("pending")
        assert sm.current_state is SubscriptionState.PENDING

    def test_draft_rejects_activate(self):
        """DRAFT cannot activate directly."""
        from skills.billing import SubscriptionStateMachine, SubscriptionState, InvalidTransitionError

        sm = SubscriptionStateMachine(initial_state=SubscriptionState.DRAFT)
        with pytest.raises(InvalidTransitionError):
            sm.transition("activate")

    def test_draft_rejects_cancel(self):
        """DRAFT cannot cancel directly."""
        from skills.billing import SubscriptionStateMachine, SubscriptionState, InvalidTransitionError

        sm = SubscriptionStateMachine(initial_state=SubscriptionState.DRAFT)
        with pytest.raises(InvalidTransitionError):
            sm.transition("cancel")


class TestPendingToActive:

    def test_pending_to_active_succeeds(self):
        """PENDING can transition to ACTIVE via the 'activate' action."""
        from skills.billing import SubscriptionStateMachine, SubscriptionState

        sm = SubscriptionStateMachine(initial_state=SubscriptionState.PENDING)
        sm.transition("activate")
        assert sm.current_state is SubscriptionState.ACTIVE

    def test_pending_rejects_past_due(self):
        """PENDING cannot go past_due directly."""
        from skills.billing import SubscriptionStateMachine, SubscriptionState, InvalidTransitionError

        sm = SubscriptionStateMachine(initial_state=SubscriptionState.PENDING)
        with pytest.raises(InvalidTransitionError):
            sm.transition("past_due")

    def test_pending_can_cancel(self):
        """PENDING can be canceled (e.g., user abandons setup)."""
        from skills.billing import SubscriptionStateMachine, SubscriptionState

        sm = SubscriptionStateMachine(initial_state=SubscriptionState.PENDING)
        sm.transition("cancel")
        assert sm.current_state is SubscriptionState.CANCELED


class TestActiveLifecycle:

    def test_active_to_past_due(self):
        """ACTIVE becomes PAST_DUE when payment fails."""
        from skills.billing import SubscriptionStateMachine, SubscriptionState

        sm = SubscriptionStateMachine(initial_state=SubscriptionState.ACTIVE)
        sm.transition("past_due")
        assert sm.current_state is SubscriptionState.PAST_DUE

    def test_active_cannot_go_to_canceled_directly(self):
        """Active must go through past_due before canceling."""
        from skills.billing import SubscriptionStateMachine, SubscriptionState, InvalidTransitionError

        sm = SubscriptionStateMachine(initial_state=SubscriptionState.ACTIVE)
        with pytest.raises(InvalidTransitionError):
            sm.transition("cancel")


class TestPastDueResume:

    def test_past_due_can_resume_to_pending(self):
        """PAST_DUE can resume back to PENDING after payment is fixed."""
        from skills.billing import SubscriptionStateMachine, SubscriptionState

        sm = SubscriptionStateMachine(initial_state=SubscriptionState.PAST_DUE)
        sm.transition("resume")
        assert sm.current_state is SubscriptionState.PENDING

    def test_past_due_cannot_go_directly_to_active(self):
        """PAST_DUE must first resume to PENDING before activating."""
        from skills.billing import SubscriptionStateMachine, SubscriptionState, InvalidTransitionError

        sm = SubscriptionStateMachine(initial_state=SubscriptionState.PAST_DUE)
        with pytest.raises(InvalidTransitionError):
            sm.transition("activate")

    def test_past_due_can_cancel(self):
        """PAST_DUE can also be canceled without resuming."""
        from skills.billing import SubscriptionStateMachine, SubscriptionState

        sm = SubscriptionStateMachine(initial_state=SubscriptionState.PAST_DUE)
        sm.transition("cancel")
        assert sm.current_state is SubscriptionState.CANCELED


# ---------------------------------------------------------------------------
# Slice 3 — Successful transitions emit TransitionEvents (source, target, timestamp)
# ---------------------------------------------------------------------------

class TestTransitionEvents:

    def test_transition_returns_event_with_source_and_target(self):
        """transition() returns an event describing where we came from and where we went."""
        from skills.billing import SubscriptionStateMachine, SubscriptionState, TransitionEvent

        sm = SubscriptionStateMachine(initial_state=SubscriptionState.DRAFT)
        event = sm.transition("pending")

        assert isinstance(event, TransitionEvent)
        assert event.source == "draft"
        assert event.target == "pending"

    def test_event_timestamp_is_utc_aware(self):
        """The event's timestamp is a timezone-aware UTC datetime."""
        from datetime import timezone
        from skills.billing import SubscriptionStateMachine, SubscriptionState

        sm = SubscriptionStateMachine(initial_state=SubscriptionState.PENDING)
        event = sm.transition("activate")

        assert event.timestamp.tzinfo is not None
        # Should be close to now (within 1 second of being created)
        from datetime import datetime
        delta = abs((datetime.now(timezone.utc) - event.timestamp).total_seconds())
        assert delta < 1

    def test_event_repr_is_readable(self):
        """TransitionEvent.__str__ / __repr__ produces a clean arrow notation."""
        from skills.billing import SubscriptionStateMachine, SubscriptionState

        sm = SubscriptionStateMachine(initial_state=SubscriptionState.DRAFT)
        event = sm.transition("pending")

        s = str(event)
        assert "draft" in s.lower()
        assert "pending" in s.lower()
        assert "→" in s


# ---------------------------------------------------------------------------
# Slice 4 — History tracks all transitions; returned as an immutable copy
# ---------------------------------------------------------------------------

class TestHistoryTracking:

    def test_history_includes_initial_state(self):
        """The initial state seeding appears as the first history entry."""
        from skills.billing import SubscriptionStateMachine, SubscriptionState

        sm = SubscriptionStateMachine(initial_state=SubscriptionState.DRAFT)
        hist = sm.history
        assert len(hist) == 1
        assert hist[0].source == "__init__"
        assert hist[0].target == "draft"

    def test_each_transition_appends_to_history(self):
        """Calling transition() appends a new event to history."""
        from skills.billing import SubscriptionStateMachine, SubscriptionState

        sm = SubscriptionStateMachine(initial_state=SubscriptionState.DRAFT)
        sm.transition("pending")
        sm.transition("activate")
        assert len(sm.history) == 3

    def test_history_is_immutable_copy(self):
        """Mutating the returned history does not affect internal state."""
        from skills.billing import SubscriptionStateMachine, SubscriptionState

        sm = SubscriptionStateMachine(initial_state=SubscriptionState.DRAFT)
        hist = sm.history
        hist.clear()
        assert len(sm.history) == 1


# ---------------------------------------------------------------------------
# Slice 5 — Event handler callbacks (pytest-mock)
# ---------------------------------------------------------------------------

class TestEventHandlerCallbacks:

    def test_callback_receives_event_on_transition(self, mocker):
        """A registered handler receives the TransitionEvent when a transition fires."""
        from skills.billing import SubscriptionStateMachine, SubscriptionState

        sm = SubscriptionStateMachine(initial_state=SubscriptionState.DRAFT)
        mock_handler = mocker.Mock()
        sm.on_transition(mock_handler)

        sm.transition("pending")

        mock_handler.assert_called_once()
        event = mock_handler.call_args[0][0]
        assert event.source == "draft"
        assert event.target == "pending"

    def test_multiple_handlers_all_invoke(self, mocker):
        """All registered handlers receive the same event."""
        from skills.billing import SubscriptionStateMachine, SubscriptionState

        sm = SubscriptionStateMachine(initial_state=SubscriptionState.PENDING)
        handler_a = mocker.Mock()
        handler_b = mocker.Mock()
        sm.on_transition(handler_a)
        sm.on_transition(handler_b)

        sm.transition("activate")

        handler_a.assert_called_once()
        handler_b.assert_called_once()
        assert handler_a.call_args == handler_b.call_args

    def test_removed_handler_no_longer_invoked(self, mocker):
        """After removal, the handler no longer receives events."""
        from skills.billing import SubscriptionStateMachine, SubscriptionState

        sm = SubscriptionStateMachine(initial_state=SubscriptionState.ACTIVE)
        handler = mocker.Mock()
        sm.on_transition(handler)
        sm.remove_transition_handler(handler)

        sm.transition("past_due")

        handler.assert_not_called()

    def test_handler_exception_does_not_crash_subsequent_handlers(self, mocker):
        """A crashing handler does not prevent other handlers from running."""
        from skills.billing import SubscriptionStateMachine, SubscriptionState

        sm = SubscriptionStateMachine(initial_state=SubscriptionState.PENDING)
        results: list[str] = []

        def bad_handler(event):
            raise RuntimeError("boom")

        def good_handler(event):
            results.append("called")

        sm.on_transition(bad_handler)
        sm.on_transition(good_handler)

        sm.transition("activate")

        assert results == ["called"]
        assert sm.current_state is SubscriptionState.ACTIVE


# ---------------------------------------------------------------------------
# Slice 6 — CANCELED is a terminal sink state; no outgoing transitions allowed
# ---------------------------------------------------------------------------

class TestCanceledSinkState:

    def test_no_transition_from_canceled(self):
        """A canceled subscription cannot be reactivated, resumed, or changed."""
        from skills.billing import SubscriptionStateMachine, SubscriptionState, InvalidTransitionError

        sm = SubscriptionStateMachine(initial_state=SubscriptionState.CANCELED)
        for action in ("pending", "activate", "past_due", "resume", "cancel"):
            with pytest.raises(InvalidTransitionError):
                sm.transition(action)


# ---------------------------------------------------------------------------
# Slice 7 — Auto-cancel timeout via trigger_transition (grace period enforced)
# ---------------------------------------------------------------------------

class TestAutoCancelTimeout:

    def test_auto_cancel_fails_before_grace_period(self):
        """Before the grace period, auto_cancel raises an error."""
        from skills.billing import SubscriptionStateMachine, SubscriptionState, InvalidTransitionError
        from skills.billing.fsm import TIMEOUT_GRACE_PERIOD_SECONDS
        from datetime import timedelta

        sm = SubscriptionStateMachine(initial_state=SubscriptionState.PENDING)
        with pytest.raises(InvalidTransitionError, match="grace period"):
            sm.trigger_transition("auto_cancel", now=sm.created_at + timedelta(seconds=0))

    def test_auto_cancel_succeeds_after_grace_period(self):
        """After the grace period elapses, auto_cancel transitions to CANCELED."""
        from skills.billing import SubscriptionStateMachine, SubscriptionState, TransitionEvent, InvalidTransitionError
        from skills.billing.fsm import TIMEOUT_GRACE_PERIOD_SECONDS
        from datetime import timedelta

        sm = SubscriptionStateMachine(initial_state=SubscriptionState.PENDING)
        late_time = sm.created_at + timedelta(seconds=TIMEOUT_GRACE_PERIOD_SECONDS + 1)
        event = sm.trigger_transition("auto_cancel", now=late_time)

        assert sm.current_state is SubscriptionState.CANCELED
        assert isinstance(event, TransitionEvent)
        assert event.source == "pending"
        assert event.target == "canceled"
        assert event.extra.get("reason") == "grace_period_expired"

    def test_auto_cancel_only_works_from_pending(self):
        """Auto-cancel cannot be triggered from ACTIVE or PAST_DUE states."""
        from skills.billing import SubscriptionStateMachine, SubscriptionState, InvalidTransitionError

        for state in (SubscriptionState.ACTIVE, SubscriptionState.PAST_DUE):
            sm = SubscriptionStateMachine(initial_state=state)
            with pytest.raises(InvalidTransitionError):
                sm.trigger_transition("auto_cancel")


# ---------------------------------------------------------------------------
# Slice 8 — Concurrent transitions (thread safety via RLock)
# ---------------------------------------------------------------------------

class TestConcurrentTransitions:

    def test_concurrent_same_action_one_succeeds(self):
        """Two threads attempting active→past_due simultaneously: one wins."""
        import threading
        from skills.billing import SubscriptionStateMachine, SubscriptionState, InvalidTransitionError

        sm = SubscriptionStateMachine(initial_state=SubscriptionState.ACTIVE)
        results: list[str | None] = [None, None]

        def try_past_due(idx):
            try:
                sm.transition("past_due")
                results[idx] = "succeeded"
            except InvalidTransitionError:
                results[idx] = "rejected"

        t1 = threading.Thread(target=try_past_due, args=(0,))
        t2 = threading.Thread(target=try_past_due, args=(1,))
        t1.start()
        t2.start()
        t1.join(timeout=5)
        t2.join(timeout=5)

        assert "succeeded" in results
        assert "rejected" in results
        # Exactly one succeeded
        assert results.count("succeeded") == 1

    def test_concurrent_different_actions_no_deadlock(self):
        """Different actions from the same state complete without deadlock."""
        import threading
        from skills.billing import SubscriptionStateMachine, SubscriptionState, InvalidTransitionError

        sm = SubscriptionStateMachine(initial_state=SubscriptionState.PENDING)
        results: list[str] = []

        def do_activate():
            try:
                sm.transition("activate")
                results.append("activated")
            except InvalidTransitionError:
                results.append("activate_rejected")

        def do_cancel():
            try:
                sm.transition("cancel")
                results.append("canceled")
            except InvalidTransitionError:
                results.append("cancel_rejected")

        threads = [threading.Thread(target=f) for f in [do_activate, do_cancel]]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=5)

        # Both completed — no deadlock
        assert len(results) == 2
        # One succeeded, one was rejected (order unknown due to race)
        assert any(r == "activated" for r in results) or any(r == "canceled" for r in results)
