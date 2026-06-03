"""Requirement traceability validation."""

from __future__ import annotations

from framework.types import FSM, RequirementSpec, TraceabilityResults, extract_requirement_refs


def validate_traceability(fsm: FSM, spec: RequirementSpec) -> TraceabilityResults:
    spec_ids = spec.requirement_ids
    covered: set[str] = set()
    unsupported = 0
    empty_req = 0

    for transition in fsm.transitions:
        refs = extract_requirement_refs(transition.requirement)
        if not transition.requirement.strip():
            empty_req += 1
        if not refs or refs.isdisjoint(spec_ids):
            unsupported += 1
        covered.update(refs & spec_ids)

    missing = sorted(spec_ids - covered)
    return TraceabilityResults(
        covered_requirements=sorted(covered),
        missing_requirements=missing,
        unsupported_transitions=unsupported,
        empty_requirement_transitions=empty_req,
    )
