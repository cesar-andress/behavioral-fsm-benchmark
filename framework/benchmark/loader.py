"""Load gold FSMs, test suites, and requirement specs from benchmark/."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from framework.io.load_json import load_json
from framework.io.paths import DATASETS_SYSTEMS_DIR, GOLD_FSMS_DIR, TEST_SUITES_DIR
from framework.types import (
    FSM,
    RequirementSpec,
    TestSuite,
    fsm_from_dict,
    parse_test_suite,
    requirement_spec_from_dict,
)


@dataclass(frozen=True)
class SystemBenchmark:
    system_id: str
    gold: FSM
    test_suite: TestSuite
    requirement_spec: RequirementSpec | None = None


def _systems_dir() -> Path:
    return DATASETS_SYSTEMS_DIR


def gold_fsm_path(system_id: str) -> Path:
    return GOLD_FSMS_DIR / f"{system_id}.json"


def test_suite_path(system_id: str) -> Path:
    return TEST_SUITES_DIR / f"{system_id}.json"


def requirement_spec_path(system_id: str) -> Path:
    return _systems_dir() / f"{system_id}.json"


def load_gold_fsm(
    system_id: str,
    *,
    validate: bool = True,
    gold_dir: Path | None = None,
) -> FSM:
    path = (gold_dir or GOLD_FSMS_DIR) / f"{system_id}.json"
    payload = load_json(path)
    if validate:
        from framework.benchmark.validate import validate_gold_fsm

        ok, errors = validate_gold_fsm(payload)
        if not ok:
            raise ValueError(f"Invalid gold FSM '{system_id}': {'; '.join(errors)}")
    return fsm_from_dict(payload)


def load_test_suite(
    system_id: str,
    *,
    validate: bool = True,
    suite_dir: Path | None = None,
) -> TestSuite:
    path = (suite_dir or TEST_SUITES_DIR) / f"{system_id}.json"
    payload = load_json(path)
    if validate:
        from framework.benchmark.validate import validate_test_suite

        ok, errors = validate_test_suite(payload)
        if not ok:
            raise ValueError(f"Invalid test suite '{system_id}': {'; '.join(errors)}")
    return parse_test_suite(payload)


def load_requirement_spec(
    system_id: str,
    *,
    datasets_dir: Path | None = None,
) -> RequirementSpec:
    path = (datasets_dir or _systems_dir()) / f"{system_id}.json"
    if not path.is_file():
        raise FileNotFoundError(f"Requirement spec not found: {path}")
    return requirement_spec_from_dict(load_json(path))


def load_system_benchmark(
    system_id: str,
    *,
    validate: bool = True,
    include_requirements: bool = True,
) -> SystemBenchmark:
    gold = load_gold_fsm(system_id, validate=validate)
    suite = load_test_suite(system_id, validate=validate)
    spec: RequirementSpec | None = None
    if include_requirements:
        spec_path = requirement_spec_path(system_id)
        if spec_path.is_file():
            spec = load_requirement_spec(system_id)
    return SystemBenchmark(system_id=system_id, gold=gold, test_suite=suite, requirement_spec=spec)
