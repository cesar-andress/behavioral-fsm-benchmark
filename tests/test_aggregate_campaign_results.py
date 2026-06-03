"""Tests for scripts/aggregate_campaign_results.py."""

from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "aggregate_campaign_results.py"
sys.path.insert(0, str(REPO_ROOT / "scripts"))


def _load_aggregate_module():
    spec = importlib.util.spec_from_file_location("aggregate_campaign_results", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def aggregate_mod():
    return _load_aggregate_module()


def _sample_rows() -> list[dict[str, object]]:
    base = {
        "campaign_id": "C1_test",
        "run_status": "passed",
        "failure_category": "none",
        "failure_reason": "",
        "started_at": "2026-06-03T00:00:00+00:00",
        "finished_at": "2026-06-03T00:01:00+00:00",
        "requirement_coverage": 1.0,
        "missing_transitions": 0,
        "extra_transitions": 0,
    }
    return [
        {
            **base,
            "run_id": "r1",
            "system_id": "atm",
            "model": "model_a",
            "replicate": 1,
            "run_index": 1,
            "failure_stage": "none",
            "schema_valid": True,
            "referential_valid": True,
            "strict_deterministic": True,
            "guard_aware_deterministic": True,
            "behavioral_pass_rate": 1.0,
            "final_state_agreement": 1.0,
            "trace_agreement": 1.0,
            "rejected_event_agreement": 1.0,
        },
        {
            **base,
            "run_id": "r2",
            "system_id": "atm",
            "model": "model_a",
            "replicate": 2,
            "run_index": 2,
            "failure_stage": "none",
            "schema_valid": True,
            "referential_valid": True,
            "strict_deterministic": True,
            "guard_aware_deterministic": True,
            "behavioral_pass_rate": 0.5,
            "final_state_agreement": 0.5,
            "trace_agreement": 0.5,
            "rejected_event_agreement": 0.5,
        },
        {
            **base,
            "run_id": "r3",
            "system_id": "login_system",
            "model": "model_a",
            "replicate": 1,
            "run_index": 3,
            "failure_stage": "parsing",
            "schema_valid": None,
            "referential_valid": None,
            "strict_deterministic": None,
            "guard_aware_deterministic": None,
            "behavioral_pass_rate": None,
            "final_state_agreement": None,
            "trace_agreement": None,
            "rejected_event_agreement": None,
            "requirement_coverage": None,
            "missing_transitions": None,
            "extra_transitions": None,
        },
        {
            **base,
            "run_id": "r4",
            "system_id": "login_system",
            "model": "model_b",
            "replicate": 1,
            "run_index": 4,
            "failure_stage": "schema_validation",
            "schema_valid": False,
            "referential_valid": False,
            "strict_deterministic": None,
            "guard_aware_deterministic": None,
            "behavioral_pass_rate": None,
            "final_state_agreement": None,
            "trace_agreement": None,
            "rejected_event_agreement": None,
            "requirement_coverage": None,
            "missing_transitions": None,
            "extra_transitions": None,
        },
        {
            **base,
            "run_id": "r5",
            "system_id": "vending_machine",
            "model": "model_b",
            "replicate": 1,
            "run_index": 5,
            "failure_stage": "none",
            "schema_valid": True,
            "referential_valid": True,
            "strict_deterministic": False,
            "guard_aware_deterministic": True,
            "behavioral_pass_rate": 0.25,
            "final_state_agreement": 0.25,
            "trace_agreement": 0.25,
            "rejected_event_agreement": 0.25,
        },
    ]


def _write_metrics_csv(path: Path, rows: list[dict[str, object]], aggregate_mod) -> None:
    from ollama_campaign_lib import METRIC_CSV_COLUMNS

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=METRIC_CSV_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    key: aggregate_mod.format_csv_value(row.get(key))
                    for key in METRIC_CSV_COLUMNS
                }
            )


def test_structural_rates_and_failures(aggregate_mod) -> None:
    rows = _sample_rows()
    summary = aggregate_mod.summarize_rows(rows)

    assert summary.runs_total == 5
    assert summary.g1_pass_rate == pytest.approx(4 / 5)
    assert summary.g2_pass_rate == pytest.approx(3 / 4)
    assert summary.g3_pass_rate == pytest.approx(2 / 3)
    assert summary.g3a_pass_rate == pytest.approx(3 / 3)
    assert summary.parsing_failures == 1
    assert summary.schema_failures == 1
    assert summary.non_evaluable_runs == 2


def test_behavioral_and_agreement_means(aggregate_mod) -> None:
    summary = aggregate_mod.summarize_rows(_sample_rows())

    assert summary.mean_behavioral_pass_rate == pytest.approx(1.75 / 3)
    assert summary.median_behavioral_pass_rate == pytest.approx(0.5)
    assert summary.std_behavioral_pass_rate == pytest.approx(0.311805, rel=1e-4)
    assert summary.mean_final_state_agreement == pytest.approx(1.75 / 3)
    assert summary.mean_trace_agreement == pytest.approx(1.75 / 3)
    assert summary.mean_rejected_event_agreement == pytest.approx(1.75 / 3)


def test_model_replicate_variance(aggregate_mod) -> None:
    report = aggregate_mod.aggregate_campaign(_sample_rows())
    model_a = next(item for item in report.model_summaries if item.model == "model_a")

    assert model_a.replicate_variance == pytest.approx(0.0625)
    assert report.campaign_summary.mean_replicate_variance == pytest.approx(0.0625)


def test_system_difficulty_summary(aggregate_mod) -> None:
    report = aggregate_mod.aggregate_campaign(_sample_rows())
    atm = next(item for item in report.system_summaries if item.system_id == "atm")
    login = next(item for item in report.system_summaries if item.system_id == "login_system")

    assert atm.mean_behavioral_pass_rate == pytest.approx(0.75)
    assert login.mean_behavioral_pass_rate is None
    assert login.non_evaluable_runs == 2


def test_export_campaign_aggregation_writes_csvs(aggregate_mod, tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    _write_metrics_csv(run_dir / "metrics.csv", _sample_rows(), aggregate_mod)

    report = aggregate_mod.aggregate_campaign_run_dir(run_dir, run_dir / "summaries")
    paths = {
        "campaign_summary": run_dir / "summaries" / "campaign_summary.csv",
        "model_summary": run_dir / "summaries" / "model_summary.csv",
        "system_summary": run_dir / "summaries" / "system_summary.csv",
    }

    for path in paths.values():
        assert path.is_file()

    with paths["campaign_summary"].open(encoding="utf-8", newline="") as handle:
        campaign_rows = list(csv.DictReader(handle))
    assert len(campaign_rows) == 1
    assert campaign_rows[0]["campaign_id"] == "C1_test"
    assert campaign_rows[0]["runs_total"] == "5"
    assert float(campaign_rows[0]["g1_pass_rate"]) == pytest.approx(0.8)

    with paths["model_summary"].open(encoding="utf-8", newline="") as handle:
        model_rows = list(csv.DictReader(handle))
    assert {row["model"] for row in model_rows} == {"model_a", "model_b"}

    with paths["system_summary"].open(encoding="utf-8", newline="") as handle:
        system_rows = list(csv.DictReader(handle))
    assert len(system_rows) == 3
    assert report.campaign_summary.runs_total == 5


def test_load_campaign_metrics_missing_file(aggregate_mod, tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        aggregate_mod.load_campaign_metrics(tmp_path)


def test_main_cli(aggregate_mod, tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "run"
    _write_metrics_csv(run_dir / "metrics.csv", _sample_rows(), aggregate_mod)

    exit_code = aggregate_mod.main(["--run-dir", str(run_dir)])
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "campaign_summary=" in output
    assert "model_summary=" in output
    assert "system_summary=" in output
    assert (run_dir / "campaign_summary.csv").is_file()
    assert (run_dir / "model_summary.csv").is_file()
    assert (run_dir / "system_summary.csv").is_file()
