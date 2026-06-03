"""Behavioral test suite execution."""

from __future__ import annotations

from framework.behavioral.metrics import apply_metrics_to_results
from framework.behavioral.oracle import evaluate_oracle
from framework.types import FSM, BehavioralResults, TestCaseResult, TestSuite


def run_test_suite(fsm: FSM, suite: TestSuite) -> BehavioralResults:
    results: list[TestCaseResult] = []
    passed = 0
    evaluable = 0

    for test in suite.tests:
        outcome = evaluate_oracle(fsm, test)
        if outcome.evaluable:
            evaluable += 1
            if outcome.passed:
                passed += 1
        results.append(
            TestCaseResult(
                test_id=test.test_id,
                passed=outcome.passed,
                evaluable=outcome.evaluable,
                message=outcome.message,
                simulation=outcome.simulation,
                kind=test.kind,
                final_state_matched=outcome.final_state_matched,
                trace_matched=outcome.trace_matched,
                rejection_matched=outcome.rejection_matched,
            )
        )

    rate = passed / evaluable if evaluable else 0.0
    behavioral = BehavioralResults(
        oracle_pass_rate=rate,
        tests_passed=passed,
        tests_total=evaluable,
        test_results=results,
        behavioral_pass_rate=rate,
    )
    return apply_metrics_to_results(behavioral, suite.tests)
