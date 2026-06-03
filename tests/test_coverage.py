"""Tests for framework.coverage."""

from __future__ import annotations

from framework.coverage.path_coverage import compute_path_coverage
from framework.coverage.requirement_coverage import compute_requirement_coverage
from framework.coverage.transition_coverage import compute_transition_coverage


def test_requirement_coverage(generated_fsm, requirement_spec) -> None:
    cov = compute_requirement_coverage(generated_fsm, requirement_spec)
    assert cov.coverage == 1.0
    assert not cov.missing
    assert cov.total >= 1


def test_transition_coverage(gold_fsm, generated_fsm) -> None:
    cov = compute_transition_coverage(generated_fsm, gold_fsm)
    assert cov.exact == 1.0
    assert cov.relaxed == 1.0
    assert cov.matched_exact == cov.reference_total


def test_path_coverage(gold_fsm, test_suite) -> None:
    rate = compute_path_coverage(gold_fsm, test_suite)
    assert rate == 1.0
