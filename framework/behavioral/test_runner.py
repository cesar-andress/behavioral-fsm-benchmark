"""Behavioral test suite execution."""

from __future__ import annotations

from framework.behavioral.oracle import evaluate_oracle
from framework.types import FSM, BehavioralResults, TestCaseResult, TestSuite


def run_test_suite(fsm: FSM, suite: TestSuite) -> BehavioralResults:
    results: list[TestCaseResult] = []
    passed = 0
    evaluable = 0

    for test in suite.tests:
        ok, is_evaluable, message, simulation = evaluate_oracle(fsm, test)
        if is_evaluable:
            evaluable += 1
            if ok:
                passed += 1
        results.append(
            TestCaseResult(
                test_id=test.test_id,
                passed=ok,
                evaluable=is_evaluable,
                message=message,
                simulation=simulation,
            )
        )

    rate = passed / evaluable if evaluable else 0.0
    return BehavioralResults(
        oracle_pass_rate=rate,
        tests_passed=passed,
        tests_total=evaluable,
        test_results=results,
    )
