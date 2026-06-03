"""Tests for framework.benchmark loader and validation."""

from __future__ import annotations

import pytest
from framework.behavioral.test_runner import run_test_suite
from framework.benchmark.loader import (
    load_gold_fsm,
    load_requirement_spec,
    load_system_benchmark,
    load_test_suite,
)
from framework.benchmark.validate import run_gold_self_test, validate_gold_fsm, validate_test_suite
from framework.coverage.requirement_coverage import compute_requirement_coverage
from framework.equivalence.transition_diagnostics import compute_transition_diagnostics
from framework.io.load_json import load_json
from framework.io.paths import gold_fsm_path
from framework.io.paths import test_suite_path as benchmark_suite_path
from framework.validators.fsm_validator import validate_determinism
from framework.validators.traceability_validator import validate_traceability

PILOT_SYSTEMS = ["vending_machine", "login_system", "atm"]
CORE_SYSTEMS = [
    "parking_gate",
    "access_control",
    "bike_rental",
    "warehouse_inventory",
    "smart_thermostat",
    "elevator",
    "hotel_booking",
    "train_ticket_booking",
    "package_locker",
]
ALL_BENCHMARK_SYSTEMS = PILOT_SYSTEMS + CORE_SYSTEMS


@pytest.mark.parametrize("system_id", ALL_BENCHMARK_SYSTEMS)
def test_load_gold_fsm(system_id: str) -> None:
    gold = load_gold_fsm(system_id)
    assert gold.initial_state
    assert gold.metadata.get("status") == "approved"


@pytest.mark.parametrize("system_id", ALL_BENCHMARK_SYSTEMS)
def test_load_test_suite(system_id: str) -> None:
    suite = load_test_suite(system_id)
    assert suite.tests
    assert suite.system_name


@pytest.mark.parametrize("system_id", ALL_BENCHMARK_SYSTEMS)
def test_load_system_benchmark(system_id: str) -> None:
    bundle = load_system_benchmark(system_id)
    assert bundle.system_id == system_id
    assert bundle.requirement_spec is not None
    assert bundle.requirement_spec.requirement_ids


@pytest.mark.parametrize("system_id", ALL_BENCHMARK_SYSTEMS)
def test_gold_self_test_passes(system_id: str) -> None:
    bundle = load_system_benchmark(system_id)
    ok, results = run_gold_self_test(bundle.gold, bundle.test_suite)
    assert ok, results.test_results
    assert results.behavioral_pass_rate == 1.0
    assert results.final_state_agreement_rate == 1.0
    assert results.trace_agreement_rate == 1.0
    assert results.rejected_event_agreement_rate == 1.0


@pytest.mark.parametrize("system_id", ALL_BENCHMARK_SYSTEMS)
def test_validate_gold_schema_payload(system_id: str) -> None:
    payload = load_json(gold_fsm_path(system_id))
    ok, errors = validate_gold_fsm(payload)
    assert ok, errors


@pytest.mark.parametrize("system_id", ALL_BENCHMARK_SYSTEMS)
def test_validate_test_suite_payload(system_id: str) -> None:
    payload = load_json(benchmark_suite_path(system_id))
    ok, errors = validate_test_suite(payload)
    assert ok, errors


@pytest.mark.parametrize("system_id", ALL_BENCHMARK_SYSTEMS)
def test_gold_strict_and_guard_aware_determinism(system_id: str) -> None:
    gold = load_gold_fsm(system_id)
    det = validate_determinism(gold)
    assert det.strict_deterministic, det.guard_aware_conflicts
    assert det.guard_aware_deterministic, det.guard_aware_conflicts


@pytest.mark.parametrize("system_id", CORE_SYSTEMS)
def test_core_requirement_traceability(system_id: str) -> None:
    bundle = load_system_benchmark(system_id)
    assert bundle.requirement_spec is not None
    trace = validate_traceability(bundle.gold, bundle.requirement_spec)
    assert not trace.missing_requirements, trace.missing_requirements
    cov = compute_requirement_coverage(bundle.gold, bundle.requirement_spec)
    assert cov.coverage == 1.0
    assert not cov.missing


@pytest.mark.parametrize("system_id", CORE_SYSTEMS)
def test_core_test_suite_composition(system_id: str) -> None:
    suite = load_test_suite(system_id)
    kinds = {test.kind for test in suite.tests}
    counts = {kind: sum(1 for test in suite.tests if test.kind == kind) for kind in kinds}
    assert counts.get("oracle", 0) >= 8
    assert counts.get("negative", 0) >= 2
    assert counts.get("path", 0) >= 6


def test_load_requirement_spec_vending() -> None:
    spec = load_requirement_spec("vending_machine")
    assert "R2" in spec.requirement_ids


def test_transition_diagnostics_extra_transition(generated_fsm, gold_fsm) -> None:
    diagnostics = compute_transition_diagnostics(gold_fsm, generated_fsm)
    assert diagnostics.extra_count >= 1
    assert diagnostics.extra_transitions


def test_run_test_suite_metrics_on_benchmark() -> None:
    gold = load_gold_fsm("vending_machine")
    suite = load_test_suite("vending_machine")
    results = run_test_suite(gold, suite)
    assert results.behavioral_pass_rate == 1.0
    assert results.final_state_matches == results.final_state_tests
    assert results.rejection_matches == results.negative_tests
