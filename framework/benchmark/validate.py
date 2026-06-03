"""Validate benchmark gold FSMs and behavioral test suites."""

from __future__ import annotations

from typing import Any

from framework.behavioral.test_runner import run_test_suite
from framework.types import FSM, BehavioralResults, TestSuite, fsm_from_dict
from framework.validators.fsm_validator import validate_determinism, validate_fsm
from framework.validators.schema_validator import validate_against_schema


def validate_gold_fsm(payload: dict[str, Any]) -> tuple[bool, list[str]]:
    ok, errors = validate_against_schema(payload, "reference_fsm.schema.json")
    if not ok:
        return False, errors
    fsm = fsm_from_dict(payload)
    structural = validate_fsm(fsm, schema_valid=True)
    if not structural.referential_valid:
        return False, structural.errors
    determinism = validate_determinism(fsm)
    if not determinism.guard_aware_deterministic:
        return False, [f"G3a failed: {c}" for c in determinism.guard_aware_conflicts]
    return True, []


def validate_test_suite(payload: dict[str, Any]) -> tuple[bool, list[str]]:
    return validate_against_schema(payload, "testsuite.schema.json")


def run_gold_self_test(gold: FSM, suite: TestSuite) -> tuple[bool, BehavioralResults]:
    """Run a gold FSM against its reference test suite (must pass at 100%)."""
    results = run_test_suite(gold, suite)
    passed = results.behavioral_pass_rate == 1.0 and results.tests_passed == results.tests_total
    return passed, results
