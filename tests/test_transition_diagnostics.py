"""Tests for framework.equivalence.transition_diagnostics."""

from __future__ import annotations

from framework.equivalence.transition_diagnostics import compute_transition_diagnostics
from framework.types import FSM, Transition


def test_diagnostics_identical_fsms(gold_fsm) -> None:
    diagnostics = compute_transition_diagnostics(gold_fsm, gold_fsm)
    assert diagnostics.missing_count == 0
    assert diagnostics.extra_count == 0
    assert diagnostics.shared_count == diagnostics.gold_total


def test_diagnostics_missing_and_extra() -> None:
    gold = FSM(
        states=["A", "B"],
        initial_state="A",
        events=["go"],
        transitions=[Transition("A", "go", "B", requirement="R1")],
    )
    candidate = FSM(
        states=["A", "B", "C"],
        initial_state="A",
        events=["go", "skip"],
        transitions=[
            Transition("A", "skip", "C", requirement="R2"),
        ],
    )
    diagnostics = compute_transition_diagnostics(gold, candidate)
    assert diagnostics.missing_count == 1
    assert diagnostics.extra_count == 1
    assert "A" in diagnostics.missing_transitions[0]
    assert "skip" in diagnostics.extra_transitions[0]
