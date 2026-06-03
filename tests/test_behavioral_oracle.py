"""Tests for framework.behavioral.oracle."""

from __future__ import annotations

from framework.behavioral.oracle import evaluate_oracle
from framework.types import TestCase


def test_oracle_passes_expected_final_state(gold_fsm) -> None:
    test = TestCase(
        test_id="happy",
        kind="oracle",
        events=["insert_coin", "press_coffee", "dispense_complete"],
        expected_final_state="Idle",
    )
    outcome = evaluate_oracle(gold_fsm, test)
    assert outcome.passed and outcome.evaluable
    assert outcome.simulation.success
    assert outcome.final_state_matched is True


def test_oracle_negative_test_expects_rejection(gold_fsm) -> None:
    test = TestCase(
        test_id="reject",
        kind="negative",
        events=["press_coffee"],
        expected_final_state=None,
    )
    outcome = evaluate_oracle(gold_fsm, test)
    assert outcome.passed and outcome.evaluable
    assert outcome.rejection_matched is True
    assert "rejection" in outcome.message


def test_oracle_fails_wrong_final_state(gold_fsm) -> None:
    test = TestCase(
        test_id="wrong",
        kind="oracle",
        events=["insert_coin"],
        expected_final_state="Dispensing",
    )
    outcome = evaluate_oracle(gold_fsm, test)
    assert not outcome.passed and outcome.evaluable
    assert outcome.final_state_matched is False


def test_oracle_expected_trace(gold_fsm) -> None:
    test = TestCase(
        test_id="trace",
        kind="oracle",
        events=["insert_coin", "press_coffee", "dispense_complete"],
        expected_final_state="Idle",
        expected_trace=["CreditAvailable", "Dispensing", "Idle"],
    )
    outcome = evaluate_oracle(gold_fsm, test)
    assert outcome.passed and outcome.evaluable
    assert outcome.trace_matched is True
