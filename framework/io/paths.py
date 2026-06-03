"""Repository path helpers."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BENCHMARK_DIR = REPO_ROOT / "benchmark"
SCHEMA_DIR = BENCHMARK_DIR / "schemas"
DATASETS_DIR = BENCHMARK_DIR / "datasets"
GOLD_FSMS_DIR = BENCHMARK_DIR / "gold_fsms"
TEST_SUITES_DIR = BENCHMARK_DIR / "test_suites"
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures"
DATASETS_SYSTEMS_DIR = DATASETS_DIR / "systems"


def schema_path(name: str) -> Path:
    return SCHEMA_DIR / name


def gold_fsm_path(system_id: str) -> Path:
    return GOLD_FSMS_DIR / f"{system_id}.json"


def test_suite_path(system_id: str) -> Path:
    return TEST_SUITES_DIR / f"{system_id}.json"


def requirement_spec_path(system_id: str) -> Path:
    return DATASETS_SYSTEMS_DIR / f"{system_id}.json"
