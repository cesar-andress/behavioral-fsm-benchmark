"""Tests for framework.behavioral.test_runner."""

from __future__ import annotations

from framework.behavioral.test_runner import run_test_suite


def test_run_test_suite_on_generated(generated_fsm, test_suite) -> None:
    results = run_test_suite(generated_fsm, test_suite)
    assert results.tests_total == 3
    assert results.tests_passed == 3
    assert results.oracle_pass_rate == 1.0
    assert len(results.test_results) == 3


def test_run_test_suite_empty_suite(generated_fsm) -> None:
    from framework.types import TestSuite

    results = run_test_suite(generated_fsm, TestSuite("demo", []))
    assert results.tests_total == 0
    assert results.oracle_pass_rate == 0.0
