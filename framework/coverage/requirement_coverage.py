"""Requirement coverage metrics."""

from __future__ import annotations

from dataclasses import dataclass

from framework.types import FSM, RequirementSpec, extract_requirement_refs


@dataclass(frozen=True)
class RequirementCoverage:
    coverage: float
    covered: list[str]
    missing: list[str]
    total: int


def compute_requirement_coverage(fsm: FSM, spec: RequirementSpec) -> RequirementCoverage:
    spec_ids = spec.requirement_ids
    covered: set[str] = set()
    for transition in fsm.transitions:
        covered.update(extract_requirement_refs(transition.requirement) & spec_ids)
    missing = sorted(spec_ids - covered)
    total = len(spec_ids)
    rate = len(covered) / total if total else 0.0
    return RequirementCoverage(rate, sorted(covered), missing, total)
