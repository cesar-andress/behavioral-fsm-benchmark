#!/usr/bin/env python3
"""Generate paper-ready CSV, LaTeX, figures, and markdown from campaign summaries."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from aggregate_campaign_results import (  # noqa: E402
    is_g3_eligible,
    is_g3_pass,
    is_g3a_eligible,
    is_g3a_pass,
    load_campaign_metrics,
    structural_rates,
)

SUMMARY_DIR_NAME = "summary"
PAPER_RESULTS_DIR_NAME = "paper_results"
FIGURES_DIR_NAME = "figures"

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


def parse_optional_float(value: str | None) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    return float(text)


def optional_float_or_nan(value: str | None) -> float:
    parsed = parse_optional_float(value)
    return parsed if parsed is not None else float("nan")


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


def format_number(value: float | int | None) -> str:
    if value is None:
        return ""
    if isinstance(value, int):
        return str(value)
    return format(value, ".6g")


def escape_latex(text: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "_": r"\_",
        "#": r"\#",
    }
    escaped = text
    for old, new in replacements.items():
        escaped = escaped.replace(old, new)
    return escaped


def write_latex_table(
    path: Path,
    caption: str,
    label: str,
    columns: list[str],
    rows: list[list[str]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    col_spec = "l" * len(columns)
    header = " & ".join(escape_latex(column) for column in columns) + r" \\"
    body_lines = [" & ".join(escape_latex(cell) for cell in row) + r" \\" for row in rows]
    content = "\n".join(
        [
            r"\begin{table}[t]",
            r"  \centering",
            f"  \\caption{{{escape_latex(caption)}}}",
            f"  \\label{{{label}}}",
            f"  \\begin{{tabular}}{{{col_spec}}}",
            r"    \toprule",
            f"    {header}",
            r"    \midrule",
            *(f"    {line}" for line in body_lines),
            r"    \bottomrule",
            r"  \end{tabular}",
            r"\end{table}",
            "",
        ]
    )
    path.write_text(content, encoding="utf-8")


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


def structural_funnel_counts(run_dir: Path, total_runs: int) -> dict[str, int]:
    metrics_path = run_dir / "metrics.csv"
    if not metrics_path.is_file():
        return {
            "total_runs": total_runs,
            "g1_pass": 0,
            "g2_pass": 0,
            "g3_pass": 0,
            "g3a_pass": 0,
        }
    rows = load_campaign_metrics(run_dir)
    g1_rate, g2_rate, _g3_rate, _g3a_rate = structural_rates(rows)
    g1_pass = round((g1_rate or 0.0) * len(rows))
    g2_eligible = sum(
        1
        for row in rows
        if str(row.get("failure_stage") or "")
        not in {"parsing", "json_extraction", "generation"}
    )
    g2_pass = round((g2_rate or 0.0) * g2_eligible) if g2_eligible else 0
    g3_eligible = sum(1 for row in rows if is_g3_eligible(row))
    g3_pass = sum(1 for row in rows if is_g3_pass(row))
    g3a_eligible = sum(1 for row in rows if is_g3a_eligible(row))
    g3a_pass = sum(1 for row in rows if is_g3a_pass(row))
    return {
        "total_runs": len(rows),
        "g1_pass": g1_pass,
        "g2_pass": g2_pass,
        "g3_pass": g3_pass if g3_eligible else 0,
        "g3a_pass": g3a_pass if g3a_eligible else 0,
    }


def save_matplotlib_figure(stem: Path, plot_fn) -> tuple[Path, Path]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(6, 4))
    plot_fn(ax)
    fig.tight_layout()
    png_path = stem.with_suffix(".png")
    pdf_path = stem.with_suffix(".pdf")
    stem.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(png_path, dpi=150)
    fig.savefig(pdf_path)
    plt.close(fig)
    return png_path, pdf_path


def generate_figures(inputs: SummaryInputs, figures_dir: Path) -> dict[str, Path]:
    paths: dict[str, Path] = {}
    campaign = inputs.campaign_summary
    total_runs = parse_optional_int(campaign.get("total_runs")) or 0
    funnel = structural_funnel_counts(inputs.run_dir, total_runs)

    png, pdf = save_matplotlib_figure(
        figures_dir / "rq1_structural_funnel",
        lambda ax: ax.bar(
            ["Total", "G1 pass", "G2 pass", "G3 pass", "G3a pass"],
            [
                funnel["total_runs"],
                funnel["g1_pass"],
                funnel["g2_pass"],
                funnel["g3_pass"],
                funnel["g3a_pass"],
            ],
        ),
    )
    paths["rq1_structural_funnel_png"] = png
    paths["rq1_structural_funnel_pdf"] = pdf

    png, pdf = save_matplotlib_figure(
        figures_dir / "rq2_behavioral_gap",
        lambda ax: ax.bar(
            ["G2 pass rate", "Mean behavioral pass rate"],
            [
                optional_float_or_nan(inputs.rq_summary_parsed.get("G2 pass rate")),
                optional_float_or_nan(campaign.get("mean_behavioral_pass_rate")),
            ],
        ),
    )
    paths["rq2_behavioral_gap_png"] = png
    paths["rq2_behavioral_gap_pdf"] = pdf

    systems = [row["system_id"] for row in inputs.system_summary]
    missing = [
        optional_float_or_nan(row.get("mean_missing_transitions"))
        for row in inputs.system_summary
    ]
    extra = [
        optional_float_or_nan(row.get("mean_extra_transitions"))
        for row in inputs.system_summary
    ]
    x = range(len(systems))
    width = 0.35

    def plot_rq3(ax):
        ax.bar([i - width / 2 for i in x], missing, width, label="missing_transitions")
        ax.bar([i + width / 2 for i in x], extra, width, label="extra_transitions")
        ax.set_xticks(list(x))
        ax.set_xticklabels(systems, rotation=20, ha="right")
        ax.legend()

    png, pdf = save_matplotlib_figure(figures_dir / "rq3_gold_agreement", plot_rq3)
    paths["rq3_gold_agreement_png"] = png
    paths["rq3_gold_agreement_pdf"] = pdf

    labels = [
        f"{row.get('model', '')}\n{row.get('system_id', '')}"
        for row in inputs.model_system_summary
    ]
    std_values = [
        optional_float_or_nan(row.get("std_behavioral_pass_rate"))
        for row in inputs.model_system_summary
    ]
    png, pdf = save_matplotlib_figure(
        figures_dir / "rq4_replicate_variance",
        lambda ax: ax.bar(labels, std_values),
    )
    paths["rq4_replicate_variance_png"] = png
    paths["rq4_replicate_variance_pdf"] = pdf

    system_ids = [row["system_id"] for row in inputs.system_summary]
    bpr_values = [
        optional_float_or_nan(row.get("mean_behavioral_pass_rate"))
        for row in inputs.system_summary
    ]
    png, pdf = save_matplotlib_figure(
        figures_dir / "rq5_system_difficulty",
        lambda ax: ax.bar(system_ids, bpr_values),
    )
    paths["rq5_system_difficulty_png"] = png
    paths["rq5_system_difficulty_pdf"] = pdf
    return paths


def build_results_summary(inputs: SummaryInputs) -> str:
    campaign = inputs.campaign_summary
    rq = inputs.rq_summary_parsed
    lines = [
        "# Campaign results summary",
        "",
        f"Campaign: `{campaign.get('campaign_id', rq.get('campaign_id', ''))}`",
        f"Run directory: `{inputs.run_dir}`",
        "",
        "## Campaign totals",
        "",
        f"- The campaign contains {campaign.get('total_runs', rq.get('total_runs', ''))} runs.",
        f"- Passed runs: {campaign.get('passed_runs', '')}.",
        f"- Failed runs: {campaign.get('failed_runs', '')}.",
        f"- Evaluable runs: {campaign.get('evaluable_runs', '')}.",
        f"- Non-evaluable runs: {campaign.get('non_evaluable_runs', '')}.",
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


def generate_paper_results(run_dir: Path, output_dir: Path | None = None) -> dict[str, Path]:
    inputs = load_summary_inputs(run_dir)
    out_dir = output_dir or (run_dir / PAPER_RESULTS_DIR_NAME)
    figures_dir = out_dir / FIGURES_DIR_NAME
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

    write_latex_table(
        out_dir / "rq1_table.tex",
        "Structural validity summary (RQ1)",
        "tab:rq1-structural-validity",
        [
            "Campaign",
            "Runs",
            "G1",
            "G2",
            "G3",
            "G3a",
            "Non-evaluable",
        ],
        [
            [
                rq1_rows[0]["campaign_id"],
                str(rq1_rows[0]["total_runs"]),
                str(rq1_rows[0]["g1_pass_rate"]),
                str(rq1_rows[0]["g2_pass_rate"]),
                str(rq1_rows[0]["g3_pass_rate"]),
                str(rq1_rows[0]["g3a_pass_rate"]),
                str(rq1_rows[0]["non_evaluable_runs"]),
            ]
        ],
    )
    write_latex_table(
        out_dir / "rq2_table.tex",
        "Behavioral correctness by model (RQ2)",
        "tab:rq2-behavioral-correctness",
        ["Model", "Runs", "Mean BPR", "Mean FSA", "Mean trace", "Mean REA"],
        [
            [
                row.get("model") or "campaign",
                str(row.get("total_runs", "")),
                str(row.get("mean_behavioral_pass_rate", "")),
                str(row.get("mean_final_state_agreement", "")),
                str(row.get("mean_trace_agreement", "")),
                str(row.get("mean_rejected_event_agreement", "")),
            ]
            for row in rq2_rows
        ],
    )
    write_latex_table(
        out_dir / "rq3_table.tex",
        "Gold agreement by system (RQ3)",
        "tab:rq3-gold-agreement",
        ["System", "Mean BPR", "Missing", "Extra", "Mean FSA", "Mean trace"],
        [
            [
                row["system_id"],
                str(row.get("mean_behavioral_pass_rate", "")),
                str(row.get("mean_missing_transitions", "")),
                str(row.get("mean_extra_transitions", "")),
                str(row.get("mean_final_state_agreement", "")),
                str(row.get("mean_trace_agreement", "")),
            ]
            for row in rq3_rows
        ],
    )
    write_latex_table(
        out_dir / "rq4_table.tex",
        "Cross-run dispersion by model-system cell (RQ4)",
        "tab:rq4-robustness",
        ["Model", "System", "Std BPR", "Min BPR", "Max BPR"],
        [
            [
                row.get("model", ""),
                row.get("system_id", ""),
                str(row.get("std_behavioral_pass_rate", "")),
                str(row.get("min_behavioral_pass_rate", "")),
                str(row.get("max_behavioral_pass_rate", "")),
            ]
            for row in rq4_rows
            if row.get("system_id") not in {"", "model_aggregate", "campaign"}
        ],
    )
    write_latex_table(
        out_dir / "rq5_table.tex",
        "System difficulty summary (RQ5)",
        "tab:rq5-system-difficulty",
        ["System", "Runs", "Non-evaluable rate", "Mean BPR", "Median BPR"],
        [
            [
                row["system_id"],
                str(row.get("total_runs", "")),
                str(row.get("non_evaluable_rate", "")),
                str(row.get("mean_behavioral_pass_rate", "")),
                str(row.get("median_behavioral_pass_rate", "")),
            ]
            for row in rq5_rows
        ],
    )

    figure_paths = generate_figures(inputs, figures_dir)
    summary_path = out_dir / "results_summary.md"
    summary_path.write_text(build_results_summary(inputs), encoding="utf-8")

    paths = {
        "output_dir": out_dir,
        "rq1_csv": rq1_csv,
        "rq2_csv": rq2_csv,
        "rq3_csv": rq3_csv,
        "rq4_csv": rq4_csv,
        "rq5_csv": rq5_csv,
        "rq1_table": out_dir / "rq1_table.tex",
        "rq2_table": out_dir / "rq2_table.tex",
        "rq3_table": out_dir / "rq3_table.tex",
        "rq4_table": out_dir / "rq4_table.tex",
        "rq5_table": out_dir / "rq5_table.tex",
        "results_summary": summary_path,
        **figure_paths,
    }
    return paths


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate paper-ready artefacts from campaign summary CSV files.",
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
        help=f"Output directory (default: <run-dir>/{PAPER_RESULTS_DIR_NAME})",
    )
    args = parser.parse_args(argv)
    run_dir = args.run_dir.resolve()
    output_dir = (args.output_dir or (run_dir / PAPER_RESULTS_DIR_NAME)).resolve()

    paths = generate_paper_results(run_dir, output_dir)
    print(f"output_dir={paths['output_dir']}")
    for key, path in sorted(paths.items()):
        if key != "output_dir":
            print(f"{key}={path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
