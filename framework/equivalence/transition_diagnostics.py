"""Missing and extra transition diagnostics for gold comparison."""

from __future__ import annotations

from dataclasses import dataclass

from framework.equivalence.transition_matcher import format_transition_key, transition_set
from framework.types import FSM


@dataclass(frozen=True)
class TransitionDiagnostics:
    missing_transitions: list[str]
    extra_transitions: list[str]
    missing_count: int
    extra_count: int
    shared_count: int
    gold_total: int
    candidate_total: int


def compute_transition_diagnostics(
    gold: FSM,
    candidate: FSM,
    *,
    include_guard: bool = True,
) -> TransitionDiagnostics:
    gold_keys = transition_set(gold, include_guard=include_guard)
    cand_keys = transition_set(candidate, include_guard=include_guard)
    missing = sorted(gold_keys - cand_keys, key=str)
    extra = sorted(cand_keys - gold_keys, key=str)
    shared = gold_keys & cand_keys
    return TransitionDiagnostics(
        missing_transitions=[format_transition_key(k) for k in missing],
        extra_transitions=[format_transition_key(k) for k in extra],
        missing_count=len(missing),
        extra_count=len(extra),
        shared_count=len(shared),
        gold_total=len(gold_keys),
        candidate_total=len(cand_keys),
    )
