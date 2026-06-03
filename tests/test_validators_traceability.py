"""Tests for framework.validators.traceability_validator."""

from __future__ import annotations

from framework.types import FSM, Transition
from framework.validators.traceability_validator import validate_traceability


def test_traceability_full_coverage(generated_fsm, requirement_spec) -> None:
    result = validate_traceability(generated_fsm, requirement_spec)
    assert not result.missing_requirements
    assert result.covered_requirements


def test_traceability_missing_requirements() -> None:
    fsm = FSM(
        states=["A"],
        initial_state="A",
        events=["e"],
        transitions=[Transition("A", "e", "A", requirement="R99")],
    )
    from framework.types import Requirement, RequirementSpec

    spec = RequirementSpec("demo", "test", [Requirement("R1", "only R1")])
    result = validate_traceability(fsm, spec)
    assert result.missing_requirements == ["R1"]
    assert result.unsupported_transitions >= 1


def test_traceability_empty_requirement_field() -> None:
    fsm = FSM(
        states=["A"],
        initial_state="A",
        events=["e"],
        transitions=[Transition("A", "e", "A", requirement="")],
    )
    from framework.types import RequirementSpec

    result = validate_traceability(fsm, RequirementSpec("demo", "test", []))
    assert result.empty_requirement_transitions == 1
