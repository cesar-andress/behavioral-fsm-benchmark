"""Comprehensive framework tests."""

from __future__ import annotations

from pathlib import Path

from framework.behavioral.simulator import simulate
from framework.coverage.requirement_coverage import compute_requirement_coverage
from framework.coverage.transition_coverage import compute_transition_coverage
from framework.equivalence.behavioral_equivalence import compare_fsms
from framework.evaluation import evaluate_case
from framework.guards.guard_overlap import find_guard_aware_conflicts, guards_mutually_exclusive
from framework.guards.guard_parser import eval_guard
from framework.io.load_json import load_json
from framework.types import fsm_from_dict, parse_test_suite, requirement_spec_from_dict
from framework.validators.fsm_validator import validate_determinism
from framework.validators.schema_validator import validate_against_schema

FIXTURES = Path(__file__).parent / "fixtures"


def test_schema_validation_valid_generated() -> None:
    payload = load_json(FIXTURES / "generated_fsm.json")
    ok, errors = validate_against_schema(payload, "generated_fsm.schema.json")
    assert ok, errors


def test_schema_validation_invalid_missing_initial_state() -> None:
    payload = load_json(FIXTURES / "invalid_schema_fsm.json")
    ok, errors = validate_against_schema(payload, "generated_fsm.schema.json")
    assert not ok
    assert errors


def test_strict_determinism_nondeterministic_fixture() -> None:
    fsm = fsm_from_dict(load_json(FIXTURES / "nondeterministic_fsm.json"))
    det = validate_determinism(fsm)
    assert not det.strict_deterministic
    assert det.duplicate_source_event_pairs >= 1


def test_guard_mutually_exclusive_numeric() -> None:
    assert guards_mutually_exclusive("balance >= 10", "balance < 5") is True
    assert guards_mutually_exclusive("", "") is False


def test_guard_aware_conflicts_detected() -> None:
    fsm = fsm_from_dict(load_json(FIXTURES / "nondeterministic_fsm.json"))
    conflicts = find_guard_aware_conflicts(fsm.transitions)
    assert conflicts


def test_simulation_success() -> None:
    fsm = fsm_from_dict(load_json(FIXTURES / "gold_fsm.json"))
    result = simulate(fsm, ["insert_coin", "press_coffee", "dispense_complete"])
    assert result.success
    assert result.final_state == "Idle"


def test_simulation_failure_from_idle_coffee() -> None:
    fsm = fsm_from_dict(load_json(FIXTURES / "gold_fsm.json"))
    result = simulate(fsm, ["press_coffee"])
    assert not result.success


def test_behavioral_suite_on_generated() -> None:
    fsm = fsm_from_dict(load_json(FIXTURES / "generated_fsm.json"))
    suite = parse_test_suite(load_json(FIXTURES / "test_suite.json"))
    from framework.behavioral.test_runner import run_test_suite

    results = run_test_suite(fsm, suite)
    assert results.tests_total == 3
    assert results.oracle_pass_rate == 1.0


def test_gold_vs_generated_comparison() -> None:
    gold = fsm_from_dict(load_json(FIXTURES / "gold_fsm.json"))
    candidate = fsm_from_dict(load_json(FIXTURES / "generated_fsm.json"))
    spec = requirement_spec_from_dict(load_json(FIXTURES / "requirement_spec.json"))
    suite = parse_test_suite(load_json(FIXTURES / "test_suite.json"))
    eq = compare_fsms(gold, candidate, spec=spec, test_suite=suite)
    assert eq.state_overlap_rate == 1.0
    assert eq.extra_transitions
    assert eq.behavioral_agreement_rate == 1.0


def test_requirement_coverage() -> None:
    fsm = fsm_from_dict(load_json(FIXTURES / "generated_fsm.json"))
    spec = requirement_spec_from_dict(load_json(FIXTURES / "requirement_spec.json"))
    cov = compute_requirement_coverage(fsm, spec)
    assert cov.coverage == 1.0
    assert not cov.missing


def test_transition_coverage() -> None:
    gold = fsm_from_dict(load_json(FIXTURES / "gold_fsm.json"))
    candidate = fsm_from_dict(load_json(FIXTURES / "generated_fsm.json"))
    cov = compute_transition_coverage(candidate, gold)
    assert cov.exact == 1.0
    assert cov.relaxed == 1.0


def test_evaluate_case_full_pipeline() -> None:
    candidate = fsm_from_dict(load_json(FIXTURES / "generated_fsm.json"))
    spec = requirement_spec_from_dict(load_json(FIXTURES / "requirement_spec.json"))
    gold = fsm_from_dict(load_json(FIXTURES / "gold_fsm.json"))
    suite = parse_test_suite(load_json(FIXTURES / "test_suite.json"))
    result = evaluate_case(candidate, spec=spec, gold=gold, test_suite=suite, schema_valid=True)
    assert result.structural.referential_valid
    assert result.behavioral is not None
    assert result.coverage is not None
    assert result.coverage.path_coverage == 1.0


def test_guard_eval_with_context() -> None:
    assert eval_guard("balance >= 10", {"balance": 15}) is True
    assert eval_guard("balance >= 10", {"balance": 5}) is False
