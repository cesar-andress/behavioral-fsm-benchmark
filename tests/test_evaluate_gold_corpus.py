"""Tests for scripts/evaluate_gold_corpus.py."""

from __future__ import annotations

import csv
import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "evaluate_gold_corpus.py"


def _load_corpus_module():
    spec = importlib.util.spec_from_file_location("evaluate_gold_corpus", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def corpus_eval():
    return _load_corpus_module()


def test_load_corpus_systems_includes_pilot_and_core(corpus_eval) -> None:
    entries = corpus_eval.load_corpus_systems()
    system_ids = {entry.system_id for entry in entries}
    tiers = {entry.system_id: entry.tier for entry in entries}

    assert "vending_machine" in system_ids
    assert "atm" in system_ids
    assert "parking_gate" in system_ids
    assert "package_locker" in system_ids
    assert tiers["vending_machine"] == "pilot"
    assert tiers["parking_gate"] == "core"
    assert len(entries) == 12


def test_evaluate_corpus_all_pass(corpus_eval) -> None:
    report = corpus_eval.evaluate_corpus()
    assert report.systems_total == 12
    assert report.systems_passed == 12
    assert report.all_passed
    for item in report.systems:
        assert item.all_pass
        assert item.schema_valid
        assert item.g2_pass
        assert item.g3_pass
        assert item.g3a_pass
        assert item.gold_self_test_pass
        assert item.behavioral_pass_rate == 1.0
        assert item.transition_coverage_exact == 1.0
        assert item.path_coverage == 1.0

    core_ids = {
        "parking_gate",
        "access_control",
        "bike_rental",
        "warehouse_inventory",
        "smart_thermostat",
        "elevator",
        "hotel_booking",
        "train_ticket_booking",
        "package_locker",
    }
    by_id = {item.system_id: item for item in report.systems}
    for system_id in core_ids:
        assert by_id[system_id].requirement_coverage == 1.0


def test_export_corpus_report_writes_outputs(corpus_eval, tmp_path: Path) -> None:
    report = corpus_eval.evaluate_corpus()
    paths = corpus_eval.export_corpus_report(report, tmp_path)

    assert paths["csv"].is_file()
    assert paths["json"].is_file()
    assert paths["summary"].is_file()

    with paths["csv"].open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == report.systems_total
    assert {
        "system_id",
        "tier",
        "schema_valid",
        "g2_pass",
        "g3_pass",
        "g3a_pass",
        "gold_self_test_pass",
        "behavioral_pass_rate",
        "requirement_coverage",
        "transition_coverage_exact",
        "path_coverage",
        "all_pass",
    }.issubset(rows[0].keys())

    summary = paths["summary"].read_text(encoding="utf-8")
    assert "# Gold corpus evaluation summary" in summary
    assert "PASS" in summary


def test_load_corpus_systems_falls_back_to_catalog(corpus_eval, tmp_path: Path) -> None:
    catalog_path = tmp_path / "catalog.json"
    index_path = tmp_path / "missing-index.json"
    catalog_path.write_text(
        json.dumps(
            {
                "benchmark_name": "test-benchmark",
                "tiers": {
                    "pilot": {"systems": [{"system_id": "alpha"}]},
                    "core": {"systems": [{"system_id": "beta"}]},
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )

    entries = corpus_eval.load_corpus_systems(index_path=index_path, catalog_path=catalog_path)
    assert [(entry.system_id, entry.tier) for entry in entries] == [
        ("alpha", "pilot"),
        ("beta", "core"),
    ]


def test_evaluate_system_detects_schema_failure(corpus_eval, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "benchmark" / "gold_fsms").mkdir(parents=True)
    (repo / "benchmark" / "test_suites").mkdir(parents=True)
    (repo / "benchmark" / "datasets" / "systems").mkdir(parents=True)

    gold = {
        "system_name": "Broken",
        "domain": "test",
        "metadata": {"status": "approved", "source": "x"},
        "states": ["A"],
        "initial_state": "Missing",
        "events": [],
        "transitions": [],
        "forbidden_behaviours": [],
    }
    suite = {
        "system_name": "Broken",
        "tests": [{"test_id": "t1", "kind": "oracle", "events": [], "expected_final_state": "A"}],
    }
    req = {"system_name": "Broken", "requirements": ["R1: starts in A"]}

    (repo / "benchmark" / "gold_fsms" / "broken.json").write_text(
        json.dumps(gold),
        encoding="utf-8",
    )
    (repo / "benchmark" / "test_suites" / "broken.json").write_text(
        json.dumps(suite),
        encoding="utf-8",
    )
    (repo / "benchmark" / "datasets" / "systems" / "broken.json").write_text(
        json.dumps(req),
        encoding="utf-8",
    )

    metrics = corpus_eval.evaluate_system(
        corpus_eval.CorpusSystemEntry("broken", "pilot"),
        repo_root=repo,
    )
    assert not metrics.g2_pass
    assert not metrics.gold_self_test_pass
    assert not metrics.all_pass
    assert metrics.errors
