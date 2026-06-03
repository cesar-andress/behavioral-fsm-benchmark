"""Tests for framework.io."""

from __future__ import annotations

import json
from pathlib import Path

from framework.io.load_json import load_json
from framework.io.paths import (
    BENCHMARK_DIR,
    FIXTURES_DIR,
    REPO_ROOT,
    SCHEMA_DIR,
    schema_path,
)
from framework.io.write_json import write_json


def test_repo_paths_exist() -> None:
    assert REPO_ROOT.is_dir()
    assert BENCHMARK_DIR.is_dir()
    assert SCHEMA_DIR.is_dir()
    assert FIXTURES_DIR.is_dir()
    assert schema_path("generated_fsm.schema.json").is_file()


def test_load_json_fixture(fixtures_dir: Path) -> None:
    payload = load_json(fixtures_dir / "gold_fsm.json")
    assert payload["initial_state"] == "Idle"


def test_write_json_roundtrip(tmp_path: Path) -> None:
    target = tmp_path / "nested" / "out.json"
    payload = {"states": ["A"], "initial_state": "A", "events": [], "transitions": []}
    write_json(target, payload)
    assert target.is_file()
    with target.open(encoding="utf-8") as handle:
        loaded = json.load(handle)
    assert loaded == payload
