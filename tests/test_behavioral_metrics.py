"""Tests for framework.behavioral.metrics."""

from __future__ import annotations

from framework.behavioral.metrics import summarize_behavioral_metrics
from framework.behavioral.test_runner import run_test_suite
from framework.types import TestCase, TestCaseResult


def test_summarize_behavioral_metrics() -> None:
    tests = [
        TestCase("t1", "oracle", ["e"], expected_final_state="B"),
        TestCase("t2", "negative", ["bad"], expected_final_state=None),
        TestCase("t3", "oracle", ["e"], expected_final_state="B", expected_trace=["B"]),
    ]
    results = [
        TestCaseResult("t1", True, True, final_state_matched=True, kind="oracle"),
        TestCaseResult("t2", True, True, rejection_matched=True, kind="negative"),
        TestCaseResult(
            "t3", False, True, final_state_matched=True, trace_matched=False, kind="oracle"
        ),
    ]
    summary = summarize_behavioral_metrics(results, tests)
    assert summary.behavioral_pass_rate == 2 / 3
    assert summary.final_state_agreement_rate == 1.0
    assert summary.trace_agreement_rate == 0.0
    assert summary.rejected_event_agreement_rate == 1.0


def test_metrics_applied_by_runner(gold_fsm, test_suite) -> None:
    results = run_test_suite(gold_fsm, test_suite)
    assert results.behavioral_pass_rate == results.oracle_pass_rate
    assert results.negative_tests >= 1
    assert results.rejection_matches == results.negative_tests
