#!/usr/bin/env python3
"""Generate repository-neutral campaign reports (CSV, JSON, Markdown) from summaries."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

SUMMARY_DIR_NAME = "summary"
REPORTS_DIR_NAME = "campaign_reports"

FORBIDDEN_SUMMARY_PHRASES = (
    "this proves",
    "this demonstrates",
    "this suggests",
    "this indicates",
)


@dataclass(frozen=True)
class SummaryInputs:
    run_dir: Path
    summary_dir: Path
    campaign_summary: dict[str, str]
    model_summary: list[dict[str, str]]
    system_summary: list[dict[str, str]]
    model_system_summary: list[dict[str, str]]
    failure_summary: list[dict[str, str]]
    rq_summary_text: str
    rq_summary_parsed: dict[str, str]


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_single_row_csv(path: Path) -> dict[str, str]:
    rows = read_csv_rows(path)
    if not rows:
        msg = f"Expected one row in {path}"
        raise ValueError(msg)
    return rows[0]


def parse_optional_int(value: str | None) -> int | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    return int(text)


def parse_rq_summary_markdown(text: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for line in text.splitlines():
        match = re.match(r"^- (.+): (.+)$", line.strip())
        if match:
            parsed[match.group(1).strip()] = match.group(2).strip()
    campaign_match = re.search(r"Campaign: `([^`]+)`", text)
    if campaign_match:
        parsed["campaign_id"] = campaign_match.group(1)
    total_match = re.search(r"Total runs: (\d+)", text)
    if total_match:
        parsed["total_runs"] = total_match.group(1)
    return parsed


def load_summary_inputs(run_dir: Path) -> SummaryInputs:
    summary_dir = run_dir / SUMMARY_DIR_NAME
    required = {
        "campaign_summary": summary_dir / "campaign_summary.csv",
        "model_summary": summary_dir / "model_summary.csv",
        "system_summary": summary_dir / "system_summary.csv",
        "model_system_summary": summary_dir / "model_system_summary.csv",
        "failure_summary": summary_dir / "failure_summary.csv",
        "rq_summary": summary_dir / "rq_summary.md",
    }
    missing = [name for name, path in required.items() if not path.is_file()]
    if missing:
        msg = f"Missing summary inputs in {summary_dir}: {', '.join(missing)}"
        raise FileNotFoundError(msg)

    rq_text = required["rq_summary"].read_text(encoding="utf-8")
    return SummaryInputs(
        run_dir=run_dir,
        summary_dir=summary_dir,
        campaign_summary=read_single_row_csv(required["campaign_summary"]),
        model_summary=read_csv_rows(required["model_summary"]),
        system_summary=read_csv_rows(required["system_summary"]),
        model_system_summary=read_csv_rows(required["model_system_summary"]),
        failure_summary=read_csv_rows(required["failure_summary"]),
        rq_summary_text=rq_text,
        rq_summary_parsed=parse_rq_summary_markdown(rq_text),
    )


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def aggregate_failure_stage_counts(failure_rows: list[dict[str, str]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in failure_rows:
        stage = row.get("failure_stage", "")
        if stage == "none":
            continue
        counts[stage] = counts.get(stage, 0) + parse_optional_int(row.get("run_count")) or 0
    return counts


def build_rq1_rows(inputs: SummaryInputs) -> list[dict[str, Any]]:
    campaign = inputs.campaign_summary
    rq = inputs.rq_summary_parsed
    failure_stages = aggregate_failure_stage_counts(inputs.failure_summary)
    return [
        {
            "campaign_id": campaign.get("campaign_id", rq.get("campaign_id", "")),
            "total_runs": campaign.get("total_runs", rq.get("total_runs", "")),
            "g1_pass_rate": rq.get("G1 pass rate", ""),
            "g2_pass_rate": rq.get("G2 pass rate", ""),
            "g3_pass_rate": rq.get("G3 pass rate", ""),
            "g3a_pass_rate": rq.get("G3a pass rate", ""),
            "parsing_failures": failure_stages.get("parsing", 0)
            + failure_stages.get("json_extraction", 0),
            "schema_validation_failures": failure_stages.get("schema_validation", 0),
            "non_evaluable_runs": campaign.get("non_evaluable_runs", ""),
        }
    ]


def build_rq2_rows(inputs: SummaryInputs) -> list[dict[str, Any]]:
    campaign = inputs.campaign_summary
    rows: list[dict[str, Any]] = [
        {
            "scope": "campaign",
            "model": "",
            "total_runs": campaign.get("total_runs", ""),
            "evaluable_runs": campaign.get("evaluable_runs", ""),
            "mean_behavioral_pass_rate": campaign.get("mean_behavioral_pass_rate", ""),
            "mean_final_state_agreement": campaign.get("mean_final_state_agreement", ""),
            "mean_trace_agreement": campaign.get("mean_trace_agreement", ""),
            "mean_rejected_event_agreement": campaign.get("mean_rejected_event_agreement", ""),
            "g2_pass_rate": inputs.rq_summary_parsed.get("G2 pass rate", ""),
        }
    ]
    for row in inputs.model_summary:
        rows.append(
            {
                "scope": "model",
                "model": row.get("model", ""),
                "total_runs": row.get("total_runs", ""),
                "evaluable_runs": "",
                "mean_behavioral_pass_rate": row.get("mean_behavioral_pass_rate", ""),
                "mean_final_state_agreement": row.get("mean_final_state_agreement", ""),
                "mean_trace_agreement": row.get("mean_trace_agreement", ""),
                "mean_rejected_event_agreement": row.get("mean_rejected_event_agreement", ""),
                "g2_pass_rate": "",
            }
        )
    return rows


def build_rq3_rows(inputs: SummaryInputs) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in inputs.system_summary:
        rows.append(
            {
                "system_id": row.get("system_id", ""),
                "total_runs": row.get("total_runs", ""),
                "mean_behavioral_pass_rate": row.get("mean_behavioral_pass_rate", ""),
                "mean_missing_transitions": row.get("mean_missing_transitions", ""),
                "mean_extra_transitions": row.get("mean_extra_transitions", ""),
                "mean_final_state_agreement": row.get("mean_final_state_agreement", ""),
                "mean_trace_agreement": row.get("mean_trace_agreement", ""),
            }
        )
    return rows


def build_rq4_rows(inputs: SummaryInputs) -> list[dict[str, Any]]:
    rq = inputs.rq_summary_parsed
    rows: list[dict[str, Any]] = [
        {
            "model": "campaign",
            "system_id": "",
            "total_runs": inputs.campaign_summary.get("total_runs", ""),
            "std_behavioral_pass_rate": "",
            "min_behavioral_pass_rate": "",
            "max_behavioral_pass_rate": "",
            "replicate_variance": rq.get("Mean replicate variance (model-system cells)", ""),
        }
    ]
    for row in inputs.model_system_summary:
        rows.append(
            {
                "model": row.get("model", ""),
                "system_id": row.get("system_id", ""),
                "total_runs": row.get("total_runs", ""),
                "std_behavioral_pass_rate": row.get("std_behavioral_pass_rate", ""),
                "min_behavioral_pass_rate": row.get("min_behavioral_pass_rate", ""),
                "max_behavioral_pass_rate": row.get("max_behavioral_pass_rate", ""),
                "replicate_variance": "",
            }
        )
    for row in inputs.model_summary:
        key = f"Replicate variance ({row.get('model', '')})"
        if key in rq:
            rows.append(
                {
                    "model": row.get("model", ""),
                    "system_id": "model_aggregate",
                    "total_runs": row.get("total_runs", ""),
                    "std_behavioral_pass_rate": row.get("std_behavioral_pass_rate", ""),
                    "min_behavioral_pass_rate": row.get("min_behavioral_pass_rate", ""),
                    "max_behavioral_pass_rate": row.get("max_behavioral_pass_rate", ""),
                    "replicate_variance": rq.get(key, ""),
                }
            )
    return rows


def build_rq5_rows(inputs: SummaryInputs) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in inputs.system_summary:
        rows.append(
            {
                "system_id": row.get("system_id", ""),
                "total_runs": row.get("total_runs", ""),
                "non_evaluable_rate": row.get("non_evaluable_rate", ""),
                "mean_behavioral_pass_rate": row.get("mean_behavioral_pass_rate", ""),
                "median_behavioral_pass_rate": row.get("median_behavioral_pass_rate", ""),
                "min_behavioral_pass_rate": row.get("min_behavioral_pass_rate", ""),
                "max_behavioral_pass_rate": row.get("max_behavioral_pass_rate", ""),
            }
        )
    return rows


def build_results_summary(inputs: SummaryInputs) -> str:
    campaign = inputs.campaign_summary
    rq = inputs.rq_summary_parsed
    lines = [
        "# Campaign results summary",
        "",
        f"Campaign: `{campaign.get('campaign_id', rq.get('campaign_id', ''))}`",
        f"Run directory: `{inputs.run_dir}`",
        "",
        "## RQ1 Structural Validity",
        "",
        f"- G1 pass rate: {rq.get('G1 pass rate', '')}.",
        f"- G2 pass rate: {rq.get('G2 pass rate', '')}.",
        f"- G3 pass rate: {rq.get('G3 pass rate', '')}.",
        f"- G3a pass rate: {rq.get('G3a pass rate', '')}.",
        "",
        "## RQ2 Behavioral Correctness",
        "",
        f"- The mean behavioral pass rate is {campaign.get('mean_behavioral_pass_rate', '')}.",
        f"- Mean final-state agreement: {campaign.get('mean_final_state_agreement', '')}.",
        f"- Mean trace agreement: {campaign.get('mean_trace_agreement', '')}.",
        f"- Mean rejected-event agreement: {campaign.get('mean_rejected_event_agreement', '')}.",
        "",
        "## RQ3 Behavioral Agreement",
        "",
        f"- Mean missing transitions: {rq.get('Mean missing transitions', '')}.",
        f"- Mean extra transitions: {rq.get('Mean extra transitions', '')}.",
        "",
        "## RQ4 Robustness",
        "",
        f"- Mean replicate variance (model-system cells): "
        f"{rq.get('Mean replicate variance (model-system cells)', '')}.",
        "",
        "## RQ5 System Difficulty",
        "",
    ]
    for row in inputs.system_summary:
        lines.append(
            f"- {row.get('system_id', '')}: mean behavioral pass rate="
            f"{row.get('mean_behavioral_pass_rate', '')}, "
            f"non-evaluable rate={row.get('non_evaluable_rate', '')}."
        )
    lines.append("")
    text = "\n".join(lines)
    lowered = text.lower()
    for phrase in FORBIDDEN_SUMMARY_PHRASES:
        if phrase in lowered:
            msg = f"Forbidden interpretive phrase in summary: {phrase}"
            raise ValueError(msg)
    return text


def generate_campaign_reports(run_dir: Path, output_dir: Path | None = None) -> dict[str, Path]:
    inputs = load_summary_inputs(run_dir)
    out_dir = output_dir or (run_dir / REPORTS_DIR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)

    rq1_rows = build_rq1_rows(inputs)
    rq2_rows = build_rq2_rows(inputs)
    rq3_rows = build_rq3_rows(inputs)
    rq4_rows = build_rq4_rows(inputs)
    rq5_rows = build_rq5_rows(inputs)

    rq1_csv = out_dir / "rq1_structural_validity.csv"
    rq2_csv = out_dir / "rq2_behavioral_correctness.csv"
    rq3_csv = out_dir / "rq3_behavioral_agreement.csv"
    rq4_csv = out_dir / "rq4_robustness.csv"
    rq5_csv = out_dir / "rq5_system_difficulty.csv"

    write_csv(
        rq1_csv,
        [
            "campaign_id",
            "total_runs",
            "g1_pass_rate",
            "g2_pass_rate",
            "g3_pass_rate",
            "g3a_pass_rate",
            "parsing_failures",
            "schema_validation_failures",
            "non_evaluable_runs",
        ],
        rq1_rows,
    )
    write_csv(
        rq2_csv,
        [
            "scope",
            "model",
            "total_runs",
            "evaluable_runs",
            "mean_behavioral_pass_rate",
            "mean_final_state_agreement",
            "mean_trace_agreement",
            "mean_rejected_event_agreement",
            "g2_pass_rate",
        ],
        rq2_rows,
    )
    write_csv(
        rq3_csv,
        [
            "system_id",
            "total_runs",
            "mean_behavioral_pass_rate",
            "mean_missing_transitions",
            "mean_extra_transitions",
            "mean_final_state_agreement",
            "mean_trace_agreement",
        ],
        rq3_rows,
    )
    write_csv(
        rq4_csv,
        [
            "model",
            "system_id",
            "total_runs",
            "std_behavioral_pass_rate",
            "min_behavioral_pass_rate",
            "max_behavioral_pass_rate",
            "replicate_variance",
        ],
        rq4_rows,
    )
    write_csv(
        rq5_csv,
        [
            "system_id",
            "total_runs",
            "non_evaluable_rate",
            "mean_behavioral_pass_rate",
            "median_behavioral_pass_rate",
            "min_behavioral_pass_rate",
            "max_behavioral_pass_rate",
        ],
        rq5_rows,
    )

    report_json = out_dir / "campaign_report.json"
    report_json.write_text(
        json.dumps(
            {
                "campaign_id": rq1_rows[0].get("campaign_id", ""),
                "run_dir": str(inputs.run_dir),
                "rq1_structural_validity": rq1_rows,
                "rq2_behavioral_correctness": rq2_rows,
                "rq3_behavioral_agreement": rq3_rows,
                "rq4_robustness": rq4_rows,
                "rq5_system_difficulty": rq5_rows,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    summary_path = out_dir / "results_summary.md"
    summary_path.write_text(build_results_summary(inputs), encoding="utf-8")

    return {
        "output_dir": out_dir,
        "rq1_csv": rq1_csv,
        "rq2_csv": rq2_csv,
        "rq3_csv": rq3_csv,
        "rq4_csv": rq4_csv,
        "rq5_csv": rq5_csv,
        "campaign_report_json": report_json,
        "results_summary": summary_path,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate repository-neutral campaign reports from summary CSV files.",
    )
    parser.add_argument(
        "--run-dir",
        type=Path,
        required=True,
        help="Frozen campaign run directory containing summary/ inputs",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help=f"Output directory (default: <run-dir>/{REPORTS_DIR_NAME})",
    )
    args = parser.parse_args(argv)
    run_dir = args.run_dir.resolve()
    output_dir = (args.output_dir or (run_dir / REPORTS_DIR_NAME)).resolve()

    paths = generate_campaign_reports(run_dir, output_dir)
    print(f"output_dir={paths['output_dir']}")
    for key, path in sorted(paths.items()):
        if key != "output_dir":
            print(f"{key}={path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
