"""Tests for framework.behavioral.simulator."""

from __future__ import annotations

from framework.behavioral.simulator import enabled_transitions, simulate


def test_simulation_success(gold_fsm) -> None:
    result = simulate(gold_fsm, ["insert_coin", "press_coffee", "dispense_complete"])
    assert result.success
    assert result.final_state == "Idle"
    assert len(result.trace) == 3


def test_simulation_failure_from_idle_coffee(gold_fsm) -> None:
    result = simulate(gold_fsm, ["press_coffee"])
    assert not result.success
    assert "no enabled transition" in (result.error or "")


def test_simulation_guard_context_selects_branch(guard_resolved_fsm) -> None:
    high = simulate(guard_resolved_fsm, ["insert_coin"], guard_context={"balance": 15})
    low = simulate(guard_resolved_fsm, ["insert_coin"], guard_context={"balance": 3})
    assert high.success and high.final_state == "High"
    assert low.success and low.final_state == "Low"


def test_simulation_nondeterministic_choice(nondeterministic_fsm) -> None:
    result = simulate(nondeterministic_fsm, ["insert_coin"], guard_context={"balance": 20})
    assert not result.success
    assert "nondeterministic" in (result.error or "")


def test_enabled_transitions_empty_guard_always_enabled(gold_fsm) -> None:
    enabled = enabled_transitions(gold_fsm, "Idle", "insert_coin", {})
    assert len(enabled) == 1
    assert enabled[0].target == "CreditAvailable"


def test_simulation_invalid_initial_state(gold_fsm) -> None:
    result = simulate(gold_fsm, [], initial_state="Unknown")
    assert not result.success
