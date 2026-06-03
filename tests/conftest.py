"""Shared pytest fixtures for framework tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from framework.io.load_json import load_json
from framework.types import fsm_from_dict, parse_test_suite, requirement_spec_from_dict

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixtures_dir() -> Path:
    return FIXTURES


@pytest.fixture
def gold_fsm():
    return fsm_from_dict(load_json(FIXTURES / "gold_fsm.json"))


@pytest.fixture
def generated_fsm():
    return fsm_from_dict(load_json(FIXTURES / "generated_fsm.json"))


@pytest.fixture
def nondeterministic_fsm():
    return fsm_from_dict(load_json(FIXTURES / "nondeterministic_fsm.json"))


@pytest.fixture
def guard_resolved_fsm():
    return fsm_from_dict(load_json(FIXTURES / "guard_resolved_fsm.json"))


@pytest.fixture
def requirement_spec():
    return requirement_spec_from_dict(load_json(FIXTURES / "requirement_spec.json"))


@pytest.fixture
def test_suite():
    return parse_test_suite(load_json(FIXTURES / "test_suite.json"))
