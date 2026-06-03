"""Path / test-suite coverage metrics."""

from __future__ import annotations

from framework.behavioral.test_runner import run_test_suite
from framework.types import FSM, TestSuite


def compute_path_coverage(fsm: FSM, suite: TestSuite) -> float:
    results = run_test_suite(fsm, suite)
    return results.oracle_pass_rate
