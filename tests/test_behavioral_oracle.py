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
    ok, evaluable, message, simulation = evaluate_oracle(gold_fsm, test)
    assert ok and evaluable
    assert simulation.success


def test_oracle_negative_test_expects_rejection(gold_fsm) -> None:
    test = TestCase(
        test_id="reject",
        kind="negative",
        events=["press_coffee"],
        expected_final_state=None,
    )
    ok, evaluable, message, simulation = evaluate_oracle(gold_fsm, test)
    assert ok and evaluable
    assert "rejection" in message


def test_oracle_fails_wrong_final_state(gold_fsm) -> None:
    test = TestCase(
        test_id="wrong",
        kind="oracle",
        events=["insert_coin"],
        expected_final_state="Dispensing",
    )
    ok, evaluable, _, _ = evaluate_oracle(gold_fsm, test)
    assert not ok and evaluable


def test_oracle_expected_trace(gold_fsm) -> None:
    test = TestCase(
        test_id="trace",
        kind="oracle",
        events=["insert_coin", "press_coffee", "dispense_complete"],
        expected_final_state="Idle",
        expected_trace=["CreditAvailable", "Dispensing", "Idle"],
    )
    ok, evaluable, _, _ = evaluate_oracle(gold_fsm, test)
    assert ok and evaluable
