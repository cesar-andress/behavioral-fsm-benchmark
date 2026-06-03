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


def schema_path(name: str) -> Path:
    return SCHEMA_DIR / name
