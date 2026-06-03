#!/usr/bin/env python3
"""Aggregate frozen campaign metrics.csv into paper-ready summary tables."""

from __future__ import annotations

import argparse
import csv
import statistics
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from ollama_campaign_lib import METRIC_CSV_COLUMNS  # noqa: E402

G1_FAIL_STAGES = frozenset({"parsing", "json_extraction", "generation"})
PARSING_FAIL_STAGES = frozenset({"parsing", "json_extraction"})

CAMPAIGN_SUMMARY_COLUMNS = [
    "campaign_id",
    "runs_total",
    "g1_pass_rate",
    "g2_pass_rate",
    "g3_pass_rate",
    "g3a_pass_rate",
    "mean_behavioral_pass_rate",
    "median_behavioral_pass_rate",
    "std_behavioral_pass_rate",
    "mean_final_state_agreement",
    "mean_trace_agreement",
    "mean_rejected_event_agreement",
    "parsing_failures",
    "schema_failures",
    "non_evaluable_runs",
    "mean_replicate_variance",
]

MODEL_SUMMARY_COLUMNS = [
    "model",
    "runs_total",
    "g1_pass_rate",
    "g2_pass_rate",
    "g3_pass_rate",
    "g3a_pass_rate",
    "mean_behavioral_pass_rate",
    "median_behavioral_pass_rate",
    "std_behavioral_pass_rate",
    "mean_final_state_agreement",
    "mean_trace_agreement",
    "mean_rejected_event_agreement",
    "parsing_failures",
    "schema_failures",
    "non_evaluable_runs",
    "replicate_variance",
]

SYSTEM_SUMMARY_COLUMNS = [
    "system_id",
    "runs_total",
    "g1_pass_rate",
    "g2_pass_rate",
    "g3_pass_rate",
    "g3a_pass_rate",
    "mean_behavioral_pass_rate",
    "median_behavioral_pass_rate",
    "std_behavioral_pass_rate",
    "mean_final_state_agreement",
    "mean_trace_agreement",
    "mean_rejected_event_agreement",
    "parsing_failures",
    "schema_failures",
    "non_evaluable_runs",
]


@dataclass(frozen=True)
class AggregationSummary:
    campaign_id: str
    runs_total: int
    g1_pass_rate: float | None
    g2_pass_rate: float | None
    g3_pass_rate: float | None
    g3a_pass_rate: float | None
    mean_behavioral_pass_rate: float | None
    median_behavioral_pass_rate: float | None
    std_behavioral_pass_rate: float | None
    mean_final_state_agreement: float | None
    mean_trace_agreement: float | None
    mean_rejected_event_agreement: float | None
    parsing_failures: int
    schema_failures: int
    non_evaluable_runs: int
    mean_replicate_variance: float | None


@dataclass(frozen=True)
class ModelSummary:
    model: str
    runs_total: int
    g1_pass_rate: float | None
    g2_pass_rate: float | None
    g3_pass_rate: float | None
    g3a_pass_rate: float | None
    mean_behavioral_pass_rate: float | None
    median_behavioral_pass_rate: float | None
    std_behavioral_pass_rate: float | None
    mean_final_state_agreement: float | None
    mean_trace_agreement: float | None
    mean_rejected_event_agreement: float | None
    parsing_failures: int
    schema_failures: int
    non_evaluable_runs: int
    replicate_variance: float | None


@dataclass(frozen=True)
class SystemSummary:
    system_id: str
    runs_total: int
    g1_pass_rate: float | None
    g2_pass_rate: float | None
    g3_pass_rate: float | None
    g3a_pass_rate: float | None
    mean_behavioral_pass_rate: float | None
    median_behavioral_pass_rate: float | None
    std_behavioral_pass_rate: float | None
    mean_final_state_agreement: float | None
    mean_trace_agreement: float | None
    mean_rejected_event_agreement: float | None
    parsing_failures: int
    schema_failures: int
    non_evaluable_runs: int


@dataclass(frozen=True)
class CampaignAggregationReport:
    campaign_summary: AggregationSummary
    model_summaries: list[ModelSummary]
    system_summaries: list[SystemSummary]


def parse_optional_bool(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    text = str(value).strip()
    if not text:
        return None
    lowered = text.lower()
    if lowered in {"true", "1", "yes"}:
        return True
    if lowered in {"false", "0", "no"}:
        return False
    return None


def parse_optional_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, float):
        return value
    if isinstance(value, int):
        return float(value)
    text = str(value).strip()
    if not text:
        return None
    return float(text)


def parse_optional_int(value: Any) -> int | None:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    text = str(value).strip()
    if not text:
        return None
    return int(text)


def parse_metric_row(raw: dict[str, str]) -> dict[str, Any]:
    row: dict[str, Any] = {}
    for key in METRIC_CSV_COLUMNS:
        value = raw.get(key, "")
        if key in {"replicate", "run_index", "missing_transitions", "extra_transitions"}:
            row[key] = parse_optional_int(value)
        elif key in {
            "schema_valid",
            "referential_valid",
            "strict_deterministic",
            "guard_aware_deterministic",
        }:
            row[key] = parse_optional_bool(value)
        elif key in {
            "requirement_coverage",
            "behavioral_pass_rate",
            "final_state_agreement",
            "trace_agreement",
            "rejected_event_agreement",
        }:
            row[key] = parse_optional_float(value)
        else:
            row[key] = value
    return row


def load_campaign_metrics(run_dir: Path) -> list[dict[str, Any]]:
    csv_path = run_dir / "metrics.csv"
    if not csv_path.is_file():
        msg = f"metrics.csv not found in {run_dir}"
        raise FileNotFoundError(msg)
    with csv_path.open(encoding="utf-8", newline="") as handle:
        return [parse_metric_row(row) for row in csv.DictReader(handle)]


def is_g1_pass(row: dict[str, Any]) -> bool:
    stage = str(row.get("failure_stage") or "")
    return stage not in G1_FAIL_STAGES


def is_g2_eligible(row: dict[str, Any]) -> bool:
    return is_g1_pass(row)


def is_g2_pass(row: dict[str, Any]) -> bool:
    if not is_g2_eligible(row):
        return False
    schema_valid = parse_optional_bool(row.get("schema_valid"))
    referential_valid = parse_optional_bool(row.get("referential_valid"))
    if schema_valid is None or referential_valid is None:
        return False
    return schema_valid and referential_valid


def is_g3_eligible(row: dict[str, Any]) -> bool:
    return is_g2_pass(row)


def is_g3_pass(row: dict[str, Any]) -> bool:
    if not is_g3_eligible(row):
        return False
    return parse_optional_bool(row.get("strict_deterministic")) is True


def is_g3a_eligible(row: dict[str, Any]) -> bool:
    return is_g2_pass(row)


def is_g3a_pass(row: dict[str, Any]) -> bool:
    if not is_g3a_eligible(row):
        return False
    return parse_optional_bool(row.get("guard_aware_deterministic")) is True


def is_parsing_failure(row: dict[str, Any]) -> bool:
    return str(row.get("failure_stage") or "") in PARSING_FAIL_STAGES


def is_schema_failure(row: dict[str, Any]) -> bool:
    stage = str(row.get("failure_stage") or "")
    if stage == "schema_validation":
        return True
    if not is_g2_eligible(row):
        return False
    return parse_optional_bool(row.get("schema_valid")) is False


def is_non_evaluable(row: dict[str, Any]) -> bool:
    return parse_optional_float(row.get("behavioral_pass_rate")) is None


def pass_rate(passed: int, eligible: int) -> float | None:
    if eligible == 0:
        return None
    return passed / eligible


def mean_or_none(values: list[float]) -> float | None:
    if not values:
        return None
    return statistics.fmean(values)


def median_or_none(values: list[float]) -> float | None:
    if not values:
        return None
    return statistics.median(values)


def std_or_none(values: list[float]) -> float | None:
    if len(values) < 2:
        return None
    return statistics.pstdev(values)


def collect_float_field(rows: list[dict[str, Any]], field: str) -> list[float]:
    values: list[float] = []
    for row in rows:
        parsed = parse_optional_float(row.get(field))
        if parsed is not None:
            values.append(parsed)
    return values


def structural_rates(
    rows: list[dict[str, Any]],
) -> tuple[float | None, float | None, float | None, float | None]:
    g1_eligible = len(rows)
    g1_passed = sum(1 for row in rows if is_g1_pass(row))

    g2_rows = [row for row in rows if is_g2_eligible(row)]
    g2_passed = sum(1 for row in g2_rows if is_g2_pass(row))

    g3_rows = [row for row in rows if is_g3_eligible(row)]
    g3_passed = sum(1 for row in g3_rows if is_g3_pass(row))

    g3a_rows = [row for row in rows if is_g3a_eligible(row)]
    g3a_passed = sum(1 for row in g3a_rows if is_g3a_pass(row))

    return (
        pass_rate(g1_passed, g1_eligible),
        pass_rate(g2_passed, len(g2_rows)),
        pass_rate(g3_passed, len(g3_rows)),
        pass_rate(g3a_passed, len(g3a_rows)),
    )


def failure_counts(rows: list[dict[str, Any]]) -> tuple[int, int, int]:
    parsing_failures = sum(1 for row in rows if is_parsing_failure(row))
    schema_failures = sum(1 for row in rows if is_schema_failure(row))
    non_evaluable_runs = sum(1 for row in rows if is_non_evaluable(row))
    return parsing_failures, schema_failures, non_evaluable_runs


def behavioral_stats(rows: list[dict[str, Any]]) -> tuple[float | None, float | None, float | None]:
    behavioral_values = collect_float_field(rows, "behavioral_pass_rate")
    return (
        mean_or_none(behavioral_values),
        median_or_none(behavioral_values),
        std_or_none(behavioral_values),
    )


def agreement_means(rows: list[dict[str, Any]]) -> tuple[float | None, float | None, float | None]:
    return (
        mean_or_none(collect_float_field(rows, "final_state_agreement")),
        mean_or_none(collect_float_field(rows, "trace_agreement")),
        mean_or_none(collect_float_field(rows, "rejected_event_agreement")),
    )


def replicate_variance_for_rows(rows: list[dict[str, Any]]) -> float | None:
    by_system: dict[str, list[float]] = {}
    for row in rows:
        system_id = str(row.get("system_id") or "")
        rate = parse_optional_float(row.get("behavioral_pass_rate"))
        if rate is None:
            continue
        by_system.setdefault(system_id, []).append(rate)

    cell_variances: list[float] = []
    for rates in by_system.values():
        if len(rates) >= 2:
            cell_variances.append(statistics.pvariance(rates))
    return mean_or_none(cell_variances)


def summarize_rows(rows: list[dict[str, Any]], *, campaign_id: str = "") -> AggregationSummary:
    g1_rate, g2_rate, g3_rate, g3a_rate = structural_rates(rows)
    mean_bpr, median_bpr, std_bpr = behavioral_stats(rows)
    mean_fsa, mean_trace, mean_rejected = agreement_means(rows)
    parsing_failures, schema_failures, non_evaluable_runs = failure_counts(rows)
    if rows:
        resolved_campaign_id = campaign_id or str(rows[0].get("campaign_id") or "")
    else:
        resolved_campaign_id = campaign_id

    return AggregationSummary(
        campaign_id=resolved_campaign_id,
        runs_total=len(rows),
        g1_pass_rate=g1_rate,
        g2_pass_rate=g2_rate,
        g3_pass_rate=g3_rate,
        g3a_pass_rate=g3a_rate,
        mean_behavioral_pass_rate=mean_bpr,
        median_behavioral_pass_rate=median_bpr,
        std_behavioral_pass_rate=std_bpr,
        mean_final_state_agreement=mean_fsa,
        mean_trace_agreement=mean_trace,
        mean_rejected_event_agreement=mean_rejected,
        parsing_failures=parsing_failures,
        schema_failures=schema_failures,
        non_evaluable_runs=non_evaluable_runs,
        mean_replicate_variance=replicate_variance_for_rows(rows),
    )


def summarize_model_rows(model: str, rows: list[dict[str, Any]]) -> ModelSummary:
    g1_rate, g2_rate, g3_rate, g3a_rate = structural_rates(rows)
    mean_bpr, median_bpr, std_bpr = behavioral_stats(rows)
    mean_fsa, mean_trace, mean_rejected = agreement_means(rows)
    parsing_failures, schema_failures, non_evaluable_runs = failure_counts(rows)

    return ModelSummary(
        model=model,
        runs_total=len(rows),
        g1_pass_rate=g1_rate,
        g2_pass_rate=g2_rate,
        g3_pass_rate=g3_rate,
        g3a_pass_rate=g3a_rate,
        mean_behavioral_pass_rate=mean_bpr,
        median_behavioral_pass_rate=median_bpr,
        std_behavioral_pass_rate=std_bpr,
        mean_final_state_agreement=mean_fsa,
        mean_trace_agreement=mean_trace,
        mean_rejected_event_agreement=mean_rejected,
        parsing_failures=parsing_failures,
        schema_failures=schema_failures,
        non_evaluable_runs=non_evaluable_runs,
        replicate_variance=replicate_variance_for_rows(rows),
    )


def summarize_system_rows(system_id: str, rows: list[dict[str, Any]]) -> SystemSummary:
    g1_rate, g2_rate, g3_rate, g3a_rate = structural_rates(rows)
    mean_bpr, median_bpr, std_bpr = behavioral_stats(rows)
    mean_fsa, mean_trace, mean_rejected = agreement_means(rows)
    parsing_failures, schema_failures, non_evaluable_runs = failure_counts(rows)

    return SystemSummary(
        system_id=system_id,
        runs_total=len(rows),
        g1_pass_rate=g1_rate,
        g2_pass_rate=g2_rate,
        g3_pass_rate=g3_rate,
        g3a_pass_rate=g3a_rate,
        mean_behavioral_pass_rate=mean_bpr,
        median_behavioral_pass_rate=median_bpr,
        std_behavioral_pass_rate=std_bpr,
        mean_final_state_agreement=mean_fsa,
        mean_trace_agreement=mean_trace,
        mean_rejected_event_agreement=mean_rejected,
        parsing_failures=parsing_failures,
        schema_failures=schema_failures,
        non_evaluable_runs=non_evaluable_runs,
    )


def group_rows(rows: list[dict[str, Any]], key: str) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        group_key = str(row.get(key) or "")
        grouped.setdefault(group_key, []).append(row)
    return grouped


def aggregate_campaign(rows: list[dict[str, Any]]) -> CampaignAggregationReport:
    campaign_summary = summarize_rows(rows)
    model_summaries = [
        summarize_model_rows(model, model_rows)
        for model, model_rows in sorted(group_rows(rows, "model").items())
    ]
    system_summaries = [
        summarize_system_rows(system_id, system_rows)
        for system_id, system_rows in sorted(group_rows(rows, "system_id").items())
    ]
    return CampaignAggregationReport(
        campaign_summary=campaign_summary,
        model_summaries=model_summaries,
        system_summaries=system_summaries,
    )


def format_csv_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return format(value, ".6g")
    return str(value)


def summary_to_row(
    summary: AggregationSummary | ModelSummary | SystemSummary,
    columns: list[str],
) -> dict[str, str]:
    return {column: format_csv_value(getattr(summary, column)) for column in columns}


def write_summary_csv(path: Path, columns: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def export_campaign_aggregation(
    report: CampaignAggregationReport,
    output_dir: Path,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "campaign_summary": output_dir / "campaign_summary.csv",
        "model_summary": output_dir / "model_summary.csv",
        "system_summary": output_dir / "system_summary.csv",
    }
    write_summary_csv(
        paths["campaign_summary"],
        CAMPAIGN_SUMMARY_COLUMNS,
        [summary_to_row(report.campaign_summary, CAMPAIGN_SUMMARY_COLUMNS)],
    )
    write_summary_csv(
        paths["model_summary"],
        MODEL_SUMMARY_COLUMNS,
        [summary_to_row(item, MODEL_SUMMARY_COLUMNS) for item in report.model_summaries],
    )
    write_summary_csv(
        paths["system_summary"],
        SYSTEM_SUMMARY_COLUMNS,
        [summary_to_row(item, SYSTEM_SUMMARY_COLUMNS) for item in report.system_summaries],
    )
    return paths


def aggregate_campaign_run_dir(
    run_dir: Path,
    output_dir: Path | None = None,
) -> CampaignAggregationReport:
    rows = load_campaign_metrics(run_dir)
    report = aggregate_campaign(rows)
    export_campaign_aggregation(report, output_dir or run_dir)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Aggregate campaign metrics.csv into paper-ready summary tables.",
    )
    parser.add_argument(
        "--run-dir",
        type=Path,
        required=True,
        help="Frozen campaign run directory containing metrics.csv",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directory for summary CSV files (default: same as --run-dir)",
    )
    args = parser.parse_args(argv)
    run_dir = args.run_dir.resolve()
    output_dir = (args.output_dir or run_dir).resolve()

    report = aggregate_campaign_run_dir(run_dir, output_dir)
    paths = {
        "campaign_summary": output_dir / "campaign_summary.csv",
        "model_summary": output_dir / "model_summary.csv",
        "system_summary": output_dir / "system_summary.csv",
    }
    print(f"campaign_id={report.campaign_summary.campaign_id}")
    print(f"runs_total={report.campaign_summary.runs_total}")
    print(f"campaign_summary={paths['campaign_summary']}")
    print(f"model_summary={paths['model_summary']}")
    print(f"system_summary={paths['system_summary']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
