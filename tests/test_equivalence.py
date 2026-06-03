"""Tests for framework.equivalence."""

from __future__ import annotations

from framework.equivalence.behavioral_equivalence import (
    build_equivalence_with_coverage,
    compare_fsms,
)
from framework.equivalence.transition_matcher import format_transition_key, transition_set
from framework.types import Transition, transition_key


def test_transition_set_and_format(gold_fsm) -> None:
    keys = transition_set(gold_fsm, include_guard=True)
    assert keys
    sample = next(iter(keys))
    formatted = format_transition_key(sample)
    assert " -> " in formatted


def test_transition_key_helper() -> None:
    key = transition_key(Transition("A", "e", "B", guard="g"), include_guard=False)
    assert key == ("A", "e", "B")


def test_gold_vs_generated_comparison(
    gold_fsm, generated_fsm, requirement_spec, test_suite
) -> None:
    eq = compare_fsms(gold_fsm, generated_fsm, spec=requirement_spec, test_suite=test_suite)
    assert eq.state_overlap_rate == 1.0
    assert eq.extra_transitions
    assert eq.behavioral_agreement_rate == 2 / 3


def test_build_equivalence_with_coverage(
    gold_fsm, generated_fsm, requirement_spec, test_suite
) -> None:
    eq, metrics = build_equivalence_with_coverage(
        gold_fsm, generated_fsm, requirement_spec, test_suite
    )
    assert eq.state_overlap_rate == 1.0
    assert metrics["requirement_coverage"] == 1.0
    assert metrics["transition_coverage_exact"] == 1.0
