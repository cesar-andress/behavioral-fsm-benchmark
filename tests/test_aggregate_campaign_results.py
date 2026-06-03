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
        "failure_reason": "",
        "started_at": "2026-06-03T00:00:00+00:00",
        "finished_at": "2026-06-03T00:01:00+00:00",
    }
    return [
        {
            **base,
            "run_id": "r1",
            "system_id": "atm",
            "model": "model_a",
            "replicate": 1,
            "run_index": 1,
            "run_status": "passed",
            "failure_stage": "none",
            "failure_category": "none",
            "schema_valid": True,
            "referential_valid": True,
            "strict_deterministic": True,
            "guard_aware_deterministic": True,
            "requirement_coverage": 1.0,
            "behavioral_pass_rate": 1.0,
            "final_state_agreement": 1.0,
            "trace_agreement": 1.0,
            "rejected_event_agreement": 1.0,
            "missing_transitions": 0,
            "extra_transitions": 0,
        },
        {
            **base,
            "run_id": "r2",
            "system_id": "atm",
            "model": "model_a",
            "replicate": 2,
            "run_index": 2,
            "run_status": "passed",
            "failure_stage": "none",
            "failure_category": "none",
            "schema_valid": True,
            "referential_valid": True,
            "strict_deterministic": True,
            "guard_aware_deterministic": True,
            "requirement_coverage": 0.5,
            "behavioral_pass_rate": 0.5,
            "final_state_agreement": 0.5,
            "trace_agreement": 0.5,
            "rejected_event_agreement": 0.5,
            "missing_transitions": 1,
            "extra_transitions": 2,
        },
        {
            **base,
            "run_id": "r3",
            "system_id": "login_system",
            "model": "model_a",
            "replicate": 1,
            "run_index": 3,
            "run_status": "failed",
            "failure_stage": "parsing",
            "failure_category": "parse_error",
            "schema_valid": None,
            "referential_valid": None,
            "strict_deterministic": None,
            "guard_aware_deterministic": None,
            "requirement_coverage": None,
            "behavioral_pass_rate": None,
            "final_state_agreement": None,
            "trace_agreement": None,
            "rejected_event_agreement": None,
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
            "run_status": "failed",
            "failure_stage": "schema_validation",
            "failure_category": "schema_error",
            "schema_valid": False,
            "referential_valid": False,
            "strict_deterministic": None,
            "guard_aware_deterministic": None,
            "requirement_coverage": None,
            "behavioral_pass_rate": None,
            "final_state_agreement": None,
            "trace_agreement": None,
            "rejected_event_agreement": None,
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
            "run_status": "passed",
            "failure_stage": "none",
            "failure_category": "none",
            "schema_valid": True,
            "referential_valid": True,
            "strict_deterministic": False,
            "guard_aware_deterministic": True,
            "requirement_coverage": 0.25,
            "behavioral_pass_rate": 0.25,
            "final_state_agreement": 0.25,
            "trace_agreement": 0.25,
            "rejected_event_agreement": 0.25,
            "missing_transitions": 3,
            "extra_transitions": 4,
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


def test_campaign_level_aggregation(aggregate_mod) -> None:
    summary = aggregate_mod.summarize_campaign(_sample_rows())

    assert summary.total_runs == 5
    assert summary.passed_runs == 3
    assert summary.failed_runs == 2
    assert summary.evaluable_runs == 3
    assert summary.non_evaluable_runs == 2
    assert summary.pass_rate == pytest.approx(0.6)
    assert summary.non_evaluable_rate == pytest.approx(0.4)
    assert summary.mean_behavioral_pass_rate == pytest.approx(1.75 / 3)
    assert summary.mean_requirement_coverage == pytest.approx(1.75 / 3)


def test_grouping_by_model(aggregate_mod) -> None:
    report = aggregate_mod.aggregate_campaign(_sample_rows())
    model_a = next(item for item in report.model_summaries if item.model == "model_a")
    model_b = next(item for item in report.model_summaries if item.model == "model_b")

    assert model_a.summary.total_runs == 3
    assert model_a.summary.mean_behavioral_pass_rate == pytest.approx(0.75)
    assert model_b.summary.total_runs == 2
    assert model_b.summary.mean_behavioral_pass_rate == pytest.approx(0.25)


def test_grouping_by_system(aggregate_mod) -> None:
    report = aggregate_mod.aggregate_campaign(_sample_rows())
    atm = next(item for item in report.system_summaries if item.system_id == "atm")
    login = next(item for item in report.system_summaries if item.system_id == "login_system")

    assert atm.summary.mean_behavioral_pass_rate == pytest.approx(0.75)
    assert atm.summary.mean_missing_transitions == pytest.approx(0.5)
    assert login.summary.mean_behavioral_pass_rate is None
    assert login.summary.non_evaluable_rate == pytest.approx(1.0)


def test_failure_summary(aggregate_mod) -> None:
    report = aggregate_mod.aggregate_campaign(_sample_rows())

    assert len(report.failure_summaries) == 4
    by_key = {
        (
            item.failure_stage,
            item.failure_category,
            item.system_id,
            item.model,
        ): item.run_count
        for item in report.failure_summaries
    }
    assert by_key[("parsing", "parse_error", "login_system", "model_a")] == 1
    assert by_key[("schema_validation", "schema_error", "login_system", "model_b")] == 1
    assert by_key[("none", "none", "atm", "model_a")] == 2


def test_null_values_not_treated_as_zero(aggregate_mod) -> None:
    summary = aggregate_mod.summarize_campaign(_sample_rows())

    assert summary.mean_behavioral_pass_rate == pytest.approx(1.75 / 3)
    assert summary.mean_behavioral_pass_rate != pytest.approx(1.75 / 5)

    group = aggregate_mod.summarize_group(
        [row for row in _sample_rows() if row["system_id"] == "login_system"]
    )
    assert group.mean_behavioral_pass_rate is None
    assert group.mean_missing_transitions is None


def test_rq_summary_markdown_creation(aggregate_mod, tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    _write_metrics_csv(run_dir / "metrics.csv", _sample_rows(), aggregate_mod)

    report = aggregate_mod.aggregate_campaign_run_dir(run_dir)
    rq_path = run_dir / aggregate_mod.SUMMARY_DIR_NAME / "rq_summary.md"
    text = rq_path.read_text(encoding="utf-8")

    assert rq_path.is_file()
    assert "## RQ1 Structural Validity" in text
    assert "## RQ2 Behavioral Correctness" in text
    assert "## RQ3 Behavioral Agreement" in text
    assert "## RQ4 Robustness" in text
    assert "## RQ5 System Difficulty" in text
    assert "atm:" in text
    assert report.campaign_summary.campaign_id == "C1_test"


def test_export_writes_all_summary_files(aggregate_mod, tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    _write_metrics_csv(run_dir / "metrics.csv", _sample_rows(), aggregate_mod)

    aggregate_mod.aggregate_campaign_run_dir(run_dir)
    summary_dir = run_dir / aggregate_mod.SUMMARY_DIR_NAME

    expected = [
        "campaign_summary.csv",
        "model_summary.csv",
        "system_summary.csv",
        "model_system_summary.csv",
        "failure_summary.csv",
        "rq_summary.md",
    ]
    for filename in expected:
        assert (summary_dir / filename).is_file()


def test_model_system_summary(aggregate_mod) -> None:
    report = aggregate_mod.aggregate_campaign(_sample_rows())
    cell = next(
        item
        for item in report.model_system_summaries
        if item.model == "model_a" and item.system_id == "atm"
    )

    assert cell.summary.total_runs == 2
    assert cell.summary.min_behavioral_pass_rate == pytest.approx(0.5)
    assert cell.summary.max_behavioral_pass_rate == pytest.approx(1.0)


def test_main_cli(aggregate_mod, tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "run"
    _write_metrics_csv(run_dir / "metrics.csv", _sample_rows(), aggregate_mod)

    exit_code = aggregate_mod.main(["--run-dir", str(run_dir)])
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "campaign_summary=" in output
    assert "rq_summary=" in output
    assert (run_dir / "summary" / "campaign_summary.csv").is_file()


def test_load_campaign_metrics_missing_file(aggregate_mod, tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        aggregate_mod.load_campaign_metrics(tmp_path)
