"""Behavioral test-suite metric aggregation."""

from __future__ import annotations

from dataclasses import dataclass

from framework.types import BehavioralResults, TestCase, TestCaseResult


@dataclass(frozen=True)
class BehavioralMetricSummary:
    behavioral_pass_rate: float
    final_state_agreement_rate: float
    trace_agreement_rate: float
    rejected_event_agreement_rate: float
    final_state_tests: int
    final_state_matches: int
    trace_tests: int
    trace_matches: int
    negative_tests: int
    rejection_matches: int


def _rate(matches: int, total: int) -> float:
    return matches / total if total else 0.0


def summarize_behavioral_metrics(
    test_results: list[TestCaseResult],
    tests: list[TestCase],
) -> BehavioralMetricSummary:
    tests_by_id = {test.test_id: test for test in tests}

    final_state_total = 0
    final_state_matches = 0
    trace_total = 0
    trace_matches = 0
    negative_total = 0
    rejection_matches = 0

    for result in test_results:
        if not result.evaluable:
            continue
        test = tests_by_id.get(result.test_id)
        if test is None:
            continue

        if test.expected_final_state is not None:
            final_state_total += 1
            if result.final_state_matched:
                final_state_matches += 1

        if test.expected_trace is not None:
            trace_total += 1
            if result.trace_matched:
                trace_matches += 1

        if test.kind == "negative" or test.expected_final_state is None:
            negative_total += 1
            if result.rejection_matched:
                rejection_matches += 1

    evaluable = sum(1 for r in test_results if r.evaluable)
    passed = sum(1 for r in test_results if r.evaluable and r.passed)

    return BehavioralMetricSummary(
        behavioral_pass_rate=_rate(passed, evaluable),
        final_state_agreement_rate=_rate(final_state_matches, final_state_total),
        trace_agreement_rate=_rate(trace_matches, trace_total),
        rejected_event_agreement_rate=_rate(rejection_matches, negative_total),
        final_state_tests=final_state_total,
        final_state_matches=final_state_matches,
        trace_tests=trace_total,
        trace_matches=trace_matches,
        negative_tests=negative_total,
        rejection_matches=rejection_matches,
    )


def apply_metrics_to_results(
    results: BehavioralResults,
    tests: list[TestCase],
) -> BehavioralResults:
    summary = summarize_behavioral_metrics(results.test_results, tests)
    results.behavioral_pass_rate = summary.behavioral_pass_rate
    results.oracle_pass_rate = summary.behavioral_pass_rate
    results.final_state_agreement_rate = summary.final_state_agreement_rate
    results.trace_agreement_rate = summary.trace_agreement_rate
    results.rejected_event_agreement_rate = summary.rejected_event_agreement_rate
    results.final_state_tests = summary.final_state_tests
    results.final_state_matches = summary.final_state_matches
    results.trace_tests = summary.trace_tests
    results.trace_matches = summary.trace_matches
    results.negative_tests = summary.negative_tests
    results.rejection_matches = summary.rejection_matches
    return results
