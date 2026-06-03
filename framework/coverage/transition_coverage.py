"""Transition coverage metrics."""

from __future__ import annotations

from dataclasses import dataclass

from framework.equivalence.transition_matcher import transition_set
from framework.types import FSM


@dataclass(frozen=True)
class TransitionCoverage:
    exact: float
    relaxed: float
    matched_exact: int
    matched_relaxed: int
    reference_total: int


def compute_transition_coverage(candidate: FSM, reference: FSM) -> TransitionCoverage:
    ref_exact = transition_set(reference, include_guard=True)
    cand_exact = transition_set(candidate, include_guard=True)
    ref_relaxed = transition_set(reference, include_guard=False)
    cand_relaxed = transition_set(candidate, include_guard=False)

    matched_exact = len(ref_exact & cand_exact)
    matched_relaxed = len(ref_relaxed & cand_relaxed)
    total = len(ref_exact)

    return TransitionCoverage(
        exact=matched_exact / total if total else 0.0,
        relaxed=matched_relaxed / len(ref_relaxed) if ref_relaxed else 0.0,
        matched_exact=matched_exact,
        matched_relaxed=matched_relaxed,
        reference_total=total,
    )
