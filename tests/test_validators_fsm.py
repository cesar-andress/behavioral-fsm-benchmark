"""Tests for framework.validators.fsm_validator."""

from __future__ import annotations

from framework.types import FSM, Transition
from framework.validators.fsm_validator import (
    count_duplicate_pairs,
    count_duplicate_triples,
    unreachable_states,
    validate_determinism,
    validate_fsm,
    validate_referential,
)


def test_validate_referential_ok(gold_fsm) -> None:
    ok, errors, warnings = validate_referential(gold_fsm)
    assert ok
    assert not errors


def test_validate_referential_bad_initial_state() -> None:
    fsm = FSM(
        states=["A"],
        initial_state="Missing",
        events=["e"],
        transitions=[],
    )
    ok, errors, _ = validate_referential(fsm)
    assert not ok
    assert any("initial_state" in err for err in errors)


def test_validate_referential_bad_transition_target() -> None:
    fsm = FSM(
        states=["A"],
        initial_state="A",
        events=["e"],
        transitions=[Transition("A", "e", "B")],
    )
    ok, errors, _ = validate_referential(fsm)
    assert not ok
    assert any("target" in err for err in errors)


def test_unreachable_states_detected() -> None:
    fsm = FSM(
        states=["A", "B", "Orphan"],
        initial_state="A",
        events=["e"],
        transitions=[Transition("A", "e", "B")],
    )
    assert unreachable_states(fsm) == ["Orphan"]


def test_strict_determinism_nondeterministic(nondeterministic_fsm) -> None:
    det = validate_determinism(nondeterministic_fsm)
    assert not det.strict_deterministic
    assert det.duplicate_source_event_pairs >= 1


def test_guard_aware_passes_mutually_exclusive_guards(guard_resolved_fsm) -> None:
    det = validate_determinism(guard_resolved_fsm)
    assert not det.strict_deterministic
    assert det.guard_aware_deterministic
    assert not det.guard_aware_conflicts


def test_gold_fsm_strict_deterministic(gold_fsm) -> None:
    det = validate_determinism(gold_fsm)
    assert det.strict_deterministic
    assert det.guard_aware_deterministic


def test_count_duplicate_pairs_and_triples(nondeterministic_fsm) -> None:
    transitions = nondeterministic_fsm.transitions
    assert count_duplicate_pairs(transitions) >= 1
    assert count_duplicate_triples(transitions) == 0


def test_validate_fsm_schema_flag(gold_fsm) -> None:
    structural = validate_fsm(gold_fsm, schema_valid=False)
    assert not structural.schema_valid
    assert structural.referential_valid
