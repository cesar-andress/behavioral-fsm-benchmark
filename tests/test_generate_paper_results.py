"""Tests for scripts/generate_paper_results.py."""

from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
AGGREGATE_SCRIPT = REPO_ROOT / "scripts" / "aggregate_campaign_results.py"
GENERATE_SCRIPT = REPO_ROOT / "scripts" / "generate_paper_results.py"
sys.path.insert(0, str(REPO_ROOT / "scripts"))


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def aggregate_mod():
    return _load_module(AGGREGATE_SCRIPT, "aggregate_campaign_results")


@pytest.fixture(scope="module")
def generate_mod():
    return _load_module(GENERATE_SCRIPT, "generate_paper_results")


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


@pytest.fixture
def prepared_run_dir(aggregate_mod, tmp_path: Path) -> Path:
    run_dir = tmp_path / "run"
    _write_metrics_csv(run_dir / "metrics.csv", _sample_rows(), aggregate_mod)
    aggregate_mod.aggregate_campaign_run_dir(run_dir)
    return run_dir


EXPECTED_CSV_FILES = [
    "rq1_structural_validity.csv",
    "rq2_behavioral_correctness.csv",
    "rq3_behavioral_agreement.csv",
    "rq4_robustness.csv",
    "rq5_system_difficulty.csv",
]

EXPECTED_TEX_FILES = [
    "rq1_table.tex",
    "rq2_table.tex",
    "rq3_table.tex",
    "rq4_table.tex",
    "rq5_table.tex",
]

EXPECTED_FIGURE_STEMS = [
    "rq1_structural_funnel",
    "rq2_behavioral_gap",
    "rq3_gold_agreement",
    "rq4_replicate_variance",
    "rq5_system_difficulty",
]


def test_output_directory_creation(generate_mod, prepared_run_dir: Path) -> None:
    output_dir = prepared_run_dir / "paper_results"
    paths = generate_mod.generate_paper_results(prepared_run_dir, output_dir)

    assert output_dir.is_dir()
    assert paths["output_dir"] == output_dir


def test_csv_artefact_creation(generate_mod, prepared_run_dir: Path) -> None:
    output_dir = prepared_run_dir / "paper_results"
    generate_mod.generate_paper_results(prepared_run_dir, output_dir)

    for filename in EXPECTED_CSV_FILES:
        path = output_dir / filename
        assert path.is_file()
        with path.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        assert rows


def test_latex_table_creation(generate_mod, prepared_run_dir: Path) -> None:
    output_dir = prepared_run_dir / "paper_results"
    generate_mod.generate_paper_results(prepared_run_dir, output_dir)

    for filename in EXPECTED_TEX_FILES:
        text = (output_dir / filename).read_text(encoding="utf-8")
        assert r"\begin{table}" in text
        assert r"\toprule" in text
        assert r"\bottomrule" in text


def test_figure_creation(generate_mod, prepared_run_dir: Path) -> None:
    output_dir = prepared_run_dir / "paper_results"
    generate_mod.generate_paper_results(prepared_run_dir, output_dir)
    figures_dir = output_dir / "figures"

    for stem in EXPECTED_FIGURE_STEMS:
        assert (figures_dir / f"{stem}.png").is_file()
        assert (figures_dir / f"{stem}.pdf").is_file()


def test_results_summary_creation(generate_mod, prepared_run_dir: Path) -> None:
    output_dir = prepared_run_dir / "paper_results"
    generate_mod.generate_paper_results(prepared_run_dir, output_dir)

    summary_path = output_dir / "results_summary.md"
    text = summary_path.read_text(encoding="utf-8")

    assert summary_path.is_file()
    assert "## RQ1 Structural Validity" in text
    assert "## RQ5 System Difficulty" in text
    lowered = text.lower()
    for phrase in generate_mod.FORBIDDEN_SUMMARY_PHRASES:
        assert phrase not in lowered


def test_null_values_not_treated_as_zero(generate_mod, aggregate_mod) -> None:
    login_rows = [row for row in _sample_rows() if row["system_id"] == "login_system"]
    group = aggregate_mod.summarize_group(login_rows)
    assert group.mean_behavioral_pass_rate is None
    assert group.mean_missing_transitions is None

    inputs = generate_mod.SummaryInputs(
        run_dir=Path("/tmp/unused"),
        summary_dir=Path("/tmp/unused/summary"),
        campaign_summary={"total_runs": "5", "mean_behavioral_pass_rate": "0.583333"},
        model_summary=[],
        system_summary=[
            {
                "system_id": "login_system",
                "total_runs": "2",
                "mean_behavioral_pass_rate": "",
                "mean_missing_transitions": "",
                "mean_extra_transitions": "",
                "mean_final_state_agreement": "",
                "mean_trace_agreement": "",
                "non_evaluable_rate": "1.0",
                "median_behavioral_pass_rate": "",
                "min_behavioral_pass_rate": "",
                "max_behavioral_pass_rate": "",
            }
        ],
        model_system_summary=[],
        failure_summary=[],
        rq_summary_text="",
        rq_summary_parsed={},
    )

    rq3_rows = generate_mod.build_rq3_rows(inputs)
    login_row = rq3_rows[0]
    assert login_row["mean_behavioral_pass_rate"] == ""
    assert login_row["mean_missing_transitions"] == ""
    assert login_row["mean_extra_transitions"] == ""

    assert generate_mod.optional_float_or_nan("") != 0.0
    assert generate_mod.parse_optional_float("") is None

    missing_plot = generate_mod.optional_float_or_nan(login_row["mean_missing_transitions"])
    assert missing_plot != 0.0
    assert missing_plot != missing_plot  # NaN check


def test_main_cli(generate_mod, prepared_run_dir: Path, capsys) -> None:
    exit_code = generate_mod.main(["--run-dir", str(prepared_run_dir)])
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "output_dir=" in output
    assert (prepared_run_dir / "paper_results" / "results_summary.md").is_file()
