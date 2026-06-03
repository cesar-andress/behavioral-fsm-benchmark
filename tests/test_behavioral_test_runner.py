"""Tests for framework.behavioral.test_runner."""

from __future__ import annotations

from framework.behavioral.test_runner import run_test_suite


def test_run_test_suite_on_gold(gold_fsm, test_suite) -> None:
    results = run_test_suite(gold_fsm, test_suite)
    assert results.tests_total == 3
    assert results.tests_passed == 3
    assert results.behavioral_pass_rate == 1.0
    assert len(results.test_results) == 3


def test_run_test_suite_generated_fails_negative(generated_fsm, test_suite) -> None:
    results = run_test_suite(generated_fsm, test_suite)
    assert results.tests_total == 3
    assert results.tests_passed == 2
    assert results.behavioral_pass_rate == 2 / 3
    reject = next(r for r in results.test_results if r.test_id == "reject_coffee_from_idle")
    assert not reject.passed
    assert reject.rejection_matched is False


def test_run_test_suite_empty_suite(generated_fsm) -> None:
    from framework.types import TestSuite

    results = run_test_suite(generated_fsm, TestSuite("demo", []))
    assert results.tests_total == 0
    assert results.oracle_pass_rate == 0.0
