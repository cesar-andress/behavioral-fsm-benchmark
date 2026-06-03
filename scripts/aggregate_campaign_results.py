#!/usr/bin/env python3
"""Aggregate frozen campaign metrics.csv into paper-ready summary tables."""

from __future__ import annotations

import argparse
import csv
import statistics
import sys
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from ollama_campaign_lib import METRIC_CSV_COLUMNS, RUN_OUTCOME_FAILED, RUN_OUTCOME_PASSED  # noqa: E402

G1_FAIL_STAGES = frozenset({"parsing", "json_extraction", "generation"})
SUMMARY_DIR_NAME = "summary"

CAMPAIGN_SUMMARY_COLUMNS = [
    "campaign_id",
    "total_runs",
    "passed_runs",
    "failed_runs",
    "evaluable_runs",
    "non_evaluable_runs",
    "pass_rate",
    "non_evaluable_rate",
    "mean_requirement_coverage",
    "mean_behavioral_pass_rate",
    "mean_final_state_agreement",
    "mean_trace_agreement",
    "mean_rejected_event_agreement",
]

GROUP_SUMMARY_COLUMNS = [
    "total_runs",
    "passed_runs",
    "failed_runs",
    "non_evaluable_rate",
    "mean_requirement_coverage",
    "mean_behavioral_pass_rate",
    "median_behavioral_pass_rate",
    "std_behavioral_pass_rate",
    "min_behavioral_pass_rate",
    "max_behavioral_pass_rate",
    "mean_final_state_agreement",
    "mean_trace_agreement",
    "mean_rejected_event_agreement",
    "mean_missing_transitions",
    "mean_extra_transitions",
]

MODEL_SUMMARY_COLUMNS = ["model", *GROUP_SUMMARY_COLUMNS]
SYSTEM_SUMMARY_COLUMNS = ["system_id", *GROUP_SUMMARY_COLUMNS]
MODEL_SYSTEM_SUMMARY_COLUMNS = ["model", "system_id", *GROUP_SUMMARY_COLUMNS]

FAILURE_SUMMARY_COLUMNS = [
    "failure_stage",
    "failure_category",
    "system_id",
    "model",
    "run_count",
]


@dataclass(frozen=True)
class CampaignSummary:
    campaign_id: str
    total_runs: int
    passed_runs: int
    failed_runs: int
    evaluable_runs: int
    non_evaluable_runs: int
    pass_rate: float | None
    non_evaluable_rate: float | None
    mean_requirement_coverage: float | None
    mean_behavioral_pass_rate: float | None
    mean_final_state_agreement: float | None
    mean_trace_agreement: float | None
    mean_rejected_event_agreement: float | None
    g1_pass_rate: float | None
    g2_pass_rate: float | None
    g3_pass_rate: float | None
    g3a_pass_rate: float | None


@dataclass(frozen=True)
class GroupSummary:
    total_runs: int
    passed_runs: int
    failed_runs: int
    non_evaluable_rate: float | None
    mean_requirement_coverage: float | None
    mean_behavioral_pass_rate: float | None
    median_behavioral_pass_rate: float | None
    std_behavioral_pass_rate: float | None
    min_behavioral_pass_rate: float | None
    max_behavioral_pass_rate: float | None
    mean_final_state_agreement: float | None
    mean_trace_agreement: float | None
    mean_rejected_event_agreement: float | None
    mean_missing_transitions: float | None
    mean_extra_transitions: float | None


@dataclass(frozen=True)
class ModelSummary:
    model: str
    summary: GroupSummary


@dataclass(frozen=True)
class SystemSummary:
    system_id: str
    summary: GroupSummary


@dataclass(frozen=True)
class ModelSystemSummary:
    model: str
    system_id: str
    summary: GroupSummary


@dataclass(frozen=True)
class FailureSummaryRow:
    failure_stage: str
    failure_category: str
    system_id: str
    model: str
    run_count: int


@dataclass(frozen=True)
class CampaignAggregationReport:
    campaign_summary: CampaignSummary
    model_summaries: list[ModelSummary]
    system_summaries: list[SystemSummary]
    model_system_summaries: list[ModelSystemSummary]
    failure_summaries: list[FailureSummaryRow]


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


def is_evaluable(row: dict[str, Any]) -> bool:
    return parse_optional_float(row.get("behavioral_pass_rate")) is not None


def is_passed(row: dict[str, Any]) -> bool:
    return str(row.get("run_status") or "") == RUN_OUTCOME_PASSED


def is_failed(row: dict[str, Any]) -> bool:
    return str(row.get("run_status") or "") == RUN_OUTCOME_FAILED


def rate(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return numerator / denominator


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


def min_or_none(values: list[float]) -> float | None:
    if not values:
        return None
    return min(values)


def max_or_none(values: list[float]) -> float | None:
    if not values:
        return None
    return max(values)


def collect_float_field(rows: Iterable[dict[str, Any]], field: str) -> list[float]:
    values: list[float] = []
    for row in rows:
        parsed = parse_optional_float(row.get(field))
        if parsed is not None:
            values.append(parsed)
    return values


def collect_int_field(rows: Iterable[dict[str, Any]], field: str) -> list[float]:
    values: list[float] = []
    for row in rows:
        parsed = parse_optional_int(row.get(field))
        if parsed is not None:
            values.append(float(parsed))
    return values


def evaluable_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in rows if is_evaluable(row)]


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


def structural_rates(
    rows: list[dict[str, Any]],
) -> tuple[float | None, float | None, float | None, float | None]:
    g1_passed = sum(1 for row in rows if is_g1_pass(row))
    g2_rows = [row for row in rows if is_g2_eligible(row)]
    g2_passed = sum(1 for row in g2_rows if is_g2_pass(row))
    g3_rows = [row for row in rows if is_g3_eligible(row)]
    g3_passed = sum(1 for row in g3_rows if is_g3_pass(row))
    g3a_rows = [row for row in rows if is_g3a_eligible(row)]
    g3a_passed = sum(1 for row in g3a_rows if is_g3a_pass(row))
    return (
        rate(g1_passed, len(rows)),
        rate(g2_passed, len(g2_rows)),
        rate(g3_passed, len(g3_rows)),
        rate(g3a_passed, len(g3a_rows)),
    )


def summarize_group(rows: list[dict[str, Any]]) -> GroupSummary:
    evaluable = evaluable_rows(rows)
    behavioral_values = collect_float_field(evaluable, "behavioral_pass_rate")
    total_runs = len(rows)
    non_evaluable_runs = total_runs - len(evaluable)

    return GroupSummary(
        total_runs=total_runs,
        passed_runs=sum(1 for row in rows if is_passed(row)),
        failed_runs=sum(1 for row in rows if is_failed(row)),
        non_evaluable_rate=rate(non_evaluable_runs, total_runs),
        mean_requirement_coverage=mean_or_none(
            collect_float_field(evaluable, "requirement_coverage")
        ),
        mean_behavioral_pass_rate=mean_or_none(behavioral_values),
        median_behavioral_pass_rate=median_or_none(behavioral_values),
        std_behavioral_pass_rate=std_or_none(behavioral_values),
        min_behavioral_pass_rate=min_or_none(behavioral_values),
        max_behavioral_pass_rate=max_or_none(behavioral_values),
        mean_final_state_agreement=mean_or_none(
            collect_float_field(evaluable, "final_state_agreement")
        ),
        mean_trace_agreement=mean_or_none(collect_float_field(evaluable, "trace_agreement")),
        mean_rejected_event_agreement=mean_or_none(
            collect_float_field(evaluable, "rejected_event_agreement")
        ),
        mean_missing_transitions=mean_or_none(collect_int_field(evaluable, "missing_transitions")),
        mean_extra_transitions=mean_or_none(collect_int_field(evaluable, "extra_transitions")),
    )


def summarize_campaign(rows: list[dict[str, Any]], *, campaign_id: str = "") -> CampaignSummary:
    evaluable = evaluable_rows(rows)
    total_runs = len(rows)
    non_evaluable_runs = total_runs - len(evaluable)
    g1_rate, g2_rate, g3_rate, g3a_rate = structural_rates(rows)
    if rows:
        resolved_campaign_id = campaign_id or str(rows[0].get("campaign_id") or "")
    else:
        resolved_campaign_id = campaign_id

    return CampaignSummary(
        campaign_id=resolved_campaign_id,
        total_runs=total_runs,
        passed_runs=sum(1 for row in rows if is_passed(row)),
        failed_runs=sum(1 for row in rows if is_failed(row)),
        evaluable_runs=len(evaluable),
        non_evaluable_runs=non_evaluable_runs,
        pass_rate=rate(sum(1 for row in rows if is_passed(row)), total_runs),
        non_evaluable_rate=rate(non_evaluable_runs, total_runs),
        mean_requirement_coverage=mean_or_none(
            collect_float_field(evaluable, "requirement_coverage")
        ),
        mean_behavioral_pass_rate=mean_or_none(
            collect_float_field(evaluable, "behavioral_pass_rate")
        ),
        mean_final_state_agreement=mean_or_none(
            collect_float_field(evaluable, "final_state_agreement")
        ),
        mean_trace_agreement=mean_or_none(collect_float_field(evaluable, "trace_agreement")),
        mean_rejected_event_agreement=mean_or_none(
            collect_float_field(evaluable, "rejected_event_agreement")
        ),
        g1_pass_rate=g1_rate,
        g2_pass_rate=g2_rate,
        g3_pass_rate=g3_rate,
        g3a_pass_rate=g3a_rate,
    )


def group_rows(rows: list[dict[str, Any]], key: str) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        group_key = str(row.get(key) or "")
        grouped.setdefault(group_key, []).append(row)
    return grouped


def group_rows_by_keys(
    rows: list[dict[str, Any]],
    keys: tuple[str, ...],
) -> dict[tuple[str, ...], list[dict[str, Any]]]:
    grouped: dict[tuple[str, ...], list[dict[str, Any]]] = {}
    for row in rows:
        group_key = tuple(str(row.get(key) or "") for key in keys)
        grouped.setdefault(group_key, []).append(row)
    return grouped


def summarize_failures(rows: list[dict[str, Any]]) -> list[FailureSummaryRow]:
    counter: Counter[tuple[str, str, str, str]] = Counter()
    for row in rows:
        key = (
            str(row.get("failure_stage") or ""),
            str(row.get("failure_category") or ""),
            str(row.get("system_id") or ""),
            str(row.get("model") or ""),
        )
        counter[key] += 1
    return [
        FailureSummaryRow(
            failure_stage=failure_stage,
            failure_category=failure_category,
            system_id=system_id,
            model=model,
            run_count=run_count,
        )
        for (failure_stage, failure_category, system_id, model), run_count in sorted(
            counter.items()
        )
    ]


def replicate_variance_for_rows(rows: list[dict[str, Any]]) -> float | None:
    by_cell: dict[tuple[str, str], list[float]] = {}
    for row in rows:
        model = str(row.get("model") or "")
        system_id = str(row.get("system_id") or "")
        rate_value = parse_optional_float(row.get("behavioral_pass_rate"))
        if rate_value is None:
            continue
        by_cell.setdefault((model, system_id), []).append(rate_value)

    cell_variances: list[float] = []
    for rates in by_cell.values():
        if len(rates) >= 2:
            cell_variances.append(statistics.pvariance(rates))
    return mean_or_none(cell_variances)


def aggregate_campaign(rows: list[dict[str, Any]]) -> CampaignAggregationReport:
    campaign_summary = summarize_campaign(rows)
    model_summaries = [
        ModelSummary(model=model, summary=summarize_group(model_rows))
        for model, model_rows in sorted(group_rows(rows, "model").items())
    ]
    system_summaries = [
        SystemSummary(system_id=system_id, summary=summarize_group(system_rows))
        for system_id, system_rows in sorted(group_rows(rows, "system_id").items())
    ]
    model_system_summaries = [
        ModelSystemSummary(
            model=model,
            system_id=system_id,
            summary=summarize_group(cell_rows),
        )
        for (model, system_id), cell_rows in sorted(
            group_rows_by_keys(rows, ("model", "system_id")).items()
        )
    ]
    return CampaignAggregationReport(
        campaign_summary=campaign_summary,
        model_summaries=model_summaries,
        system_summaries=system_summaries,
        model_system_summaries=model_system_summaries,
        failure_summaries=summarize_failures(rows),
    )


def format_csv_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return format(value, ".6g")
    return str(value)


def group_summary_to_row(
    summary: GroupSummary,
    extra_fields: dict[str, Any] | None = None,
) -> dict[str, str]:
    row = {column: format_csv_value(getattr(summary, column)) for column in GROUP_SUMMARY_COLUMNS}
    if extra_fields:
        row.update({key: format_csv_value(value) for key, value in extra_fields.items()})
    return row


def write_summary_csv(path: Path, columns: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def format_rate(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.6g}"


def format_mean(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.6g}"


def render_rq_summary(report: CampaignAggregationReport, rows: list[dict[str, Any]]) -> str:
    campaign = report.campaign_summary
    lines = [
        "# Campaign RQ summary",
        "",
        f"Campaign: `{campaign.campaign_id}`",
        f"Total runs: {campaign.total_runs}",
        "",
        "## RQ1 Structural Validity",
        "",
        f"- G1 pass rate: {format_rate(campaign.g1_pass_rate)}",
        f"- G2 pass rate: {format_rate(campaign.g2_pass_rate)}",
        f"- G3 pass rate: {format_rate(campaign.g3_pass_rate)}",
        f"- G3a pass rate: {format_rate(campaign.g3a_pass_rate)}",
        "",
        "## RQ2 Behavioral Correctness",
        "",
        f"- Evaluable runs: {campaign.evaluable_runs}",
        f"- Non-evaluable runs: {campaign.non_evaluable_runs}",
        f"- Mean behavioral pass rate: {format_mean(campaign.mean_behavioral_pass_rate)}",
        f"- Mean final-state agreement: {format_mean(campaign.mean_final_state_agreement)}",
        f"- Mean trace agreement: {format_mean(campaign.mean_trace_agreement)}",
        f"- Mean rejected-event agreement: {format_mean(campaign.mean_rejected_event_agreement)}",
        "",
        "## RQ3 Behavioral Agreement",
        "",
    ]

    evaluable = evaluable_rows(rows)
    mean_missing = mean_or_none(collect_int_field(evaluable, "missing_transitions"))
    mean_extra = mean_or_none(collect_int_field(evaluable, "extra_transitions"))
    lines.extend(
        [
            f"- Mean missing transitions: {format_mean(mean_missing)}",
            f"- Mean extra transitions: {format_mean(mean_extra)}",
            (
                "- Mean behavioral pass rate (gold-aligned suite): "
                f"{format_mean(campaign.mean_behavioral_pass_rate)}"
            ),
            "",
            "## RQ4 Robustness",
            "",
            (
                "- Mean replicate variance (model-system cells): "
                f"{format_mean(replicate_variance_for_rows(rows))}"
            ),
        ]
    )

    for model_summary in report.model_summaries:
        model_variance = replicate_variance_for_rows(
            group_rows(rows, "model").get(model_summary.model, [])
        )
        lines.append(
            f"- Replicate variance ({model_summary.model}): {format_mean(model_variance)}"
        )

    lines.extend(["", "## RQ5 System Difficulty", ""])
    for system_summary in report.system_summaries:
        summary = system_summary.summary
        lines.append(
            "- "
            f"{system_summary.system_id}: "
            f"mean behavioral pass rate={format_mean(summary.mean_behavioral_pass_rate)}, "
            f"non-evaluable rate={format_rate(summary.non_evaluable_rate)}, "
            f"total runs={summary.total_runs}"
        )
    lines.append("")
    return "\n".join(lines)


def export_campaign_aggregation(
    report: CampaignAggregationReport,
    output_dir: Path,
    *,
    source_rows: list[dict[str, Any]],
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "campaign_summary": output_dir / "campaign_summary.csv",
        "model_summary": output_dir / "model_summary.csv",
        "system_summary": output_dir / "system_summary.csv",
        "model_system_summary": output_dir / "model_system_summary.csv",
        "failure_summary": output_dir / "failure_summary.csv",
        "rq_summary": output_dir / "rq_summary.md",
    }

    campaign = report.campaign_summary
    write_summary_csv(
        paths["campaign_summary"],
        CAMPAIGN_SUMMARY_COLUMNS,
        [
            {
                column: format_csv_value(getattr(campaign, column))
                for column in CAMPAIGN_SUMMARY_COLUMNS
            }
        ],
    )
    write_summary_csv(
        paths["model_summary"],
        MODEL_SUMMARY_COLUMNS,
        [
            group_summary_to_row(item.summary, {"model": item.model})
            for item in report.model_summaries
        ],
    )
    write_summary_csv(
        paths["system_summary"],
        SYSTEM_SUMMARY_COLUMNS,
        [
            group_summary_to_row(item.summary, {"system_id": item.system_id})
            for item in report.system_summaries
        ],
    )
    write_summary_csv(
        paths["model_system_summary"],
        MODEL_SYSTEM_SUMMARY_COLUMNS,
        [
            group_summary_to_row(
                item.summary,
                {"model": item.model, "system_id": item.system_id},
            )
            for item in report.model_system_summaries
        ],
    )
    write_summary_csv(
        paths["failure_summary"],
        FAILURE_SUMMARY_COLUMNS,
        [
            {
                column: format_csv_value(getattr(item, column))
                for column in FAILURE_SUMMARY_COLUMNS
            }
            for item in report.failure_summaries
        ],
    )
    paths["rq_summary"].write_text(render_rq_summary(report, source_rows), encoding="utf-8")
    return paths


def aggregate_campaign_run_dir(
    run_dir: Path,
    output_dir: Path | None = None,
) -> CampaignAggregationReport:
    rows = load_campaign_metrics(run_dir)
    report = aggregate_campaign(rows)
    export_campaign_aggregation(
        report,
        output_dir or (run_dir / SUMMARY_DIR_NAME),
        source_rows=rows,
    )
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
        help=f"Directory for summary outputs (default: <run-dir>/{SUMMARY_DIR_NAME})",
    )
    args = parser.parse_args(argv)
    run_dir = args.run_dir.resolve()
    output_dir = (args.output_dir or (run_dir / SUMMARY_DIR_NAME)).resolve()

    report = aggregate_campaign_run_dir(run_dir, output_dir)
    paths = {
        "campaign_summary": output_dir / "campaign_summary.csv",
        "model_summary": output_dir / "model_summary.csv",
        "system_summary": output_dir / "system_summary.csv",
        "model_system_summary": output_dir / "model_system_summary.csv",
        "failure_summary": output_dir / "failure_summary.csv",
        "rq_summary": output_dir / "rq_summary.md",
    }
    print(f"campaign_id={report.campaign_summary.campaign_id}")
    print(f"total_runs={report.campaign_summary.total_runs}")
    for name, path in paths.items():
        print(f"{name}={path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
