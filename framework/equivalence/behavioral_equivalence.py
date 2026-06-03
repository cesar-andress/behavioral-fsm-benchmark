"""Gold vs generated FSM comparison."""

from __future__ import annotations

from framework.behavioral.test_runner import run_test_suite
from framework.coverage.requirement_coverage import compute_requirement_coverage
from framework.coverage.transition_coverage import compute_transition_coverage
from framework.equivalence.transition_matcher import format_transition_key, transition_set
from framework.types import (
    FSM,
    EquivalenceResults,
    RequirementSpec,
    TestSuite,
    extract_requirement_refs,
)


def compare_fsms(
    gold: FSM,
    candidate: FSM,
    *,
    spec: RequirementSpec | None = None,
    test_suite: TestSuite | None = None,
) -> EquivalenceResults:
    gold_exact = transition_set(gold, include_guard=True)
    cand_exact = transition_set(candidate, include_guard=True)

    missing_exact = sorted(gold_exact - cand_exact, key=str)
    extra_exact = sorted(cand_exact - gold_exact, key=str)

    gold_state_count = len(gold.states)
    gold_event_count = len(gold.events)
    shared_states = set(gold.states) & set(candidate.states)
    state_overlap = len(shared_states) / gold_state_count if gold_state_count else 0.0
    shared_events = set(gold.events) & set(candidate.events)
    event_overlap = len(shared_events) / gold_event_count if gold_event_count else 0.0
    exact_rate = len(gold_exact & cand_exact) / len(gold_exact) if gold_exact else 0.0

    unsupported = 0
    if spec is not None:
        spec_ids = spec.requirement_ids
        for transition in candidate.transitions:
            refs = extract_requirement_refs(transition.requirement)
            if not refs or refs.isdisjoint(spec_ids):
                unsupported += 1

    behavioral_rate = 0.0
    if test_suite is not None:
        behavioral = run_test_suite(candidate, test_suite)
        behavioral_rate = behavioral.oracle_pass_rate

    return EquivalenceResults(
        exact_transition_match_rate=exact_rate,
        state_overlap_rate=state_overlap,
        event_overlap_rate=event_overlap,
        missing_transitions=[format_transition_key(k) for k in missing_exact],
        extra_transitions=[format_transition_key(k) for k in extra_exact],
        unsupported_transitions=unsupported,
        behavioral_agreement_rate=behavioral_rate,
    )


def build_equivalence_with_coverage(
    gold: FSM,
    candidate: FSM,
    spec: RequirementSpec,
    test_suite: TestSuite | None = None,
) -> tuple[EquivalenceResults, dict[str, float]]:
    equivalence = compare_fsms(gold, candidate, spec=spec, test_suite=test_suite)
    req_cov = compute_requirement_coverage(candidate, spec)
    trans_cov = compute_transition_coverage(candidate, gold)
    metrics = {
        "requirement_coverage": req_cov.coverage,
        "transition_coverage_exact": trans_cov.exact,
        "transition_coverage_relaxed": trans_cov.relaxed,
    }
    return equivalence, metrics
