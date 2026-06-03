"""Tests for framework.validators.schema_validator."""

from __future__ import annotations

from pathlib import Path

from framework.io.load_json import load_json
from framework.validators.schema_validator import validate_against_schema


def test_schema_validation_valid_generated(fixtures_dir: Path) -> None:
    payload = load_json(fixtures_dir / "generated_fsm.json")
    ok, errors = validate_against_schema(payload, "generated_fsm.schema.json")
    assert ok, errors


def test_schema_validation_invalid_missing_initial_state(fixtures_dir: Path) -> None:
    payload = load_json(fixtures_dir / "invalid_schema_fsm.json")
    ok, errors = validate_against_schema(payload, "generated_fsm.schema.json")
    assert not ok
    assert errors


def test_schema_validation_requirement_spec(fixtures_dir: Path) -> None:
    payload = load_json(fixtures_dir / "requirement_spec.json")
    ok, errors = validate_against_schema(payload, "requirement_spec.schema.json")
    assert ok, errors


def test_schema_validation_test_suite(fixtures_dir: Path) -> None:
    payload = load_json(fixtures_dir / "test_suite.json")
    ok, errors = validate_against_schema(payload, "testsuite.schema.json")
    assert ok, errors
