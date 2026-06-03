#!/usr/bin/env python3
"""Evaluate the approved gold benchmark corpus across structural and behavioral gates."""

from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from framework.benchmark.validate import run_gold_self_test, validate_gold_fsm, validate_test_suite  # noqa: E402
from framework.coverage.path_coverage import compute_path_coverage  # noqa: E402
from framework.coverage.requirement_coverage import compute_requirement_coverage  # noqa: E402
from framework.coverage.transition_coverage import compute_transition_coverage  # noqa: E402
from framework.io.load_json import load_json  # noqa: E402
from framework.io.paths import REPO_ROOT as FRAMEWORK_REPO_ROOT  # noqa: E402
from framework.io.write_json import write_json  # noqa: E402
from framework.types import (  # noqa: E402
    fsm_from_dict,
    parse_test_suite,
    requirement_spec_from_dict,
)
from framework.validators.fsm_validator import validate_determinism, validate_fsm  # noqa: E402
from framework.validators.schema_validator import validate_against_schema  # noqa: E402

DEFAULT_INDEX_PATH = FRAMEWORK_REPO_ROOT / "benchmark" / "index.json"
DEFAULT_CATALOG_PATH = FRAMEWORK_REPO_ROOT / "benchmark" / "catalog.json"
DEFAULT_OUTPUT_DIR = FRAMEWORK_REPO_ROOT / "results" / "gold_corpus"

CSV_COLUMNS = [
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
    "transition_coverage_relaxed",
    "path_coverage",
    "tests_passed",
    "tests_total",
    "all_pass",
]


@dataclass(frozen=True)
class CorpusSystemEntry:
    system_id: str
    tier: str


@dataclass
class SystemCorpusMetrics:
    system_id: str
    tier: str
    schema_valid: bool
    g2_pass: bool
    g3_pass: bool
    g3a_pass: bool
    gold_self_test_pass: bool
    behavioral_pass_rate: float
    requirement_coverage: float
    transition_coverage_exact: float
    transition_coverage_relaxed: float
    path_coverage: float
    tests_passed: int
    tests_total: int
    all_pass: bool
    errors: list[str] = field(default_factory=list)

    def to_row(self) -> dict[str, object]:
        row = {key: getattr(self, key) for key in CSV_COLUMNS}
        row["errors"] = "; ".join(self.errors)
        return row


@dataclass
class CorpusEvaluationReport:
    generated_at: str
    benchmark_name: str
    systems_total: int
    systems_passed: int
    all_passed: bool
    systems: list[SystemCorpusMetrics]

    def to_dict(self) -> dict[str, object]:
        return {
            "generated_at": self.generated_at,
            "benchmark_name": self.benchmark_name,
            "systems_total": self.systems_total,
            "systems_passed": self.systems_passed,
            "all_passed": self.all_passed,
            "systems": [asdict(item) for item in self.systems],
        }


def load_corpus_systems(
    *,
    index_path: Path | None = None,
    catalog_path: Path | None = None,
) -> list[CorpusSystemEntry]:
    """Load benchmark systems from index.json, falling back to catalog.json tiers."""
    index_file = index_path or DEFAULT_INDEX_PATH
    catalog_file = catalog_path or DEFAULT_CATALOG_PATH

    if index_file.is_file():
        payload = load_json(index_file)
        entries = [
            CorpusSystemEntry(
                system_id=str(item["system_id"]),
                tier=str(item.get("tier", "unknown")),
            )
            for item in payload.get("systems", [])
            if item.get("system_id")
        ]
        if entries:
            return entries

    if not catalog_file.is_file():
        raise FileNotFoundError(
            f"No corpus index found at {index_file} or catalog at {catalog_file}"
        )

    payload = load_json(catalog_file)
    entries: list[CorpusSystemEntry] = []
    for tier_name, tier_payload in payload.get("tiers", {}).items():
        for item in tier_payload.get("systems", []):
            system_id = item.get("system_id")
            if system_id:
                entries.append(CorpusSystemEntry(system_id=str(system_id), tier=str(tier_name)))
    return entries


def evaluate_system(
    entry: CorpusSystemEntry,
    *,
    repo_root: Path | None = None,
) -> SystemCorpusMetrics:
    """Evaluate one gold benchmark system across schema, structural, and behavioral gates."""
    root = repo_root or FRAMEWORK_REPO_ROOT
    errors: list[str] = []

    gold_path = root / "benchmark" / "gold_fsms" / f"{entry.system_id}.json"
    suite_path = root / "benchmark" / "test_suites" / f"{entry.system_id}.json"
    req_path = root / "benchmark" / "datasets" / "systems" / f"{entry.system_id}.json"

    gold_payload = load_json(gold_path)
    suite_payload = load_json(suite_path)
    req_payload = load_json(req_path)

    gold_schema_ok, gold_schema_errors = validate_against_schema(
        gold_payload, "reference_fsm.schema.json"
    )
    suite_schema_ok, suite_schema_errors = validate_test_suite(suite_payload)
    req_schema_ok, req_schema_errors = validate_against_schema(
        req_payload, "requirement_spec.schema.json"
    )
    schema_valid = gold_schema_ok and suite_schema_ok and req_schema_ok
    if not schema_valid:
        errors.extend(gold_schema_errors + suite_schema_errors + req_schema_errors)

    gold = fsm_from_dict(gold_payload)
    structural = validate_fsm(gold, schema_valid=gold_schema_ok)
    g2_pass = gold_schema_ok and structural.referential_valid
    if not g2_pass:
        errors.extend(structural.errors)

    determinism = validate_determinism(gold)
    g3_pass = determinism.strict_deterministic
    g3a_pass = determinism.guard_aware_deterministic
    if not g3_pass:
        errors.append(
            "G3 strict determinism failed: "
            f"{determinism.duplicate_source_event_pairs} duplicate (source, event) pairs"
        )
    if not g3a_pass:
        errors.extend(f"G3a conflict: {item}" for item in determinism.guard_aware_conflicts)

    spec = requirement_spec_from_dict(req_payload)
    suite = parse_test_suite(suite_payload)

    req_cov = compute_requirement_coverage(gold, spec)
    trans_cov = compute_transition_coverage(gold, gold)
    path_cov = compute_path_coverage(gold, suite)

    gold_ok, gold_validate_errors = validate_gold_fsm(gold_payload)
    if not gold_ok:
        errors.extend(gold_validate_errors)

    self_ok, behavioral = run_gold_self_test(gold, suite)
    if not self_ok:
        for result in behavioral.test_results:
            if not result.passed:
                errors.append(f"self-test failed: {result.test_id}: {result.message}")

    all_pass = schema_valid and g2_pass and g3_pass and g3a_pass and self_ok and gold_ok

    return SystemCorpusMetrics(
        system_id=entry.system_id,
        tier=entry.tier,
        schema_valid=schema_valid,
        g2_pass=g2_pass,
        g3_pass=g3_pass,
        g3a_pass=g3a_pass,
        gold_self_test_pass=self_ok,
        behavioral_pass_rate=behavioral.behavioral_pass_rate,
        requirement_coverage=req_cov.coverage,
        transition_coverage_exact=trans_cov.exact,
        transition_coverage_relaxed=trans_cov.relaxed,
        path_coverage=path_cov,
        tests_passed=behavioral.tests_passed,
        tests_total=behavioral.tests_total,
        all_pass=all_pass,
        errors=sorted(set(errors)),
    )


def evaluate_corpus(
    *,
    index_path: Path | None = None,
    catalog_path: Path | None = None,
    repo_root: Path | None = None,
) -> CorpusEvaluationReport:
    """Evaluate every system listed in the benchmark corpus index."""
    entries = load_corpus_systems(index_path=index_path, catalog_path=catalog_path)
    systems = [evaluate_system(entry, repo_root=repo_root) for entry in entries]

    benchmark_name = "behavioral-fsm-benchmark"
    index_file = index_path or DEFAULT_INDEX_PATH
    if index_file.is_file():
        benchmark_name = str(load_json(index_file).get("benchmark_name", benchmark_name))

    systems_passed = sum(1 for item in systems if item.all_pass)
    return CorpusEvaluationReport(
        generated_at=datetime.now(tz=UTC).replace(microsecond=0).isoformat(),
        benchmark_name=benchmark_name,
        systems_total=len(systems),
        systems_passed=systems_passed,
        all_passed=systems_passed == len(systems) and len(systems) > 0,
        systems=systems,
    )


def write_metrics_csv(report: CorpusEvaluationReport, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = CSV_COLUMNS + ["errors"]
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for item in report.systems:
            writer.writerow(item.to_row())


def write_summary_markdown(report: CorpusEvaluationReport, output_path: Path) -> None:
    lines = [
        "# Gold corpus evaluation summary",
        "",
        f"- Benchmark: `{report.benchmark_name}`",
        f"- Generated at: `{report.generated_at}`",
        f"- Systems evaluated: **{report.systems_total}**",
        f"- Systems passed all gates: **{report.systems_passed}**",
        f"- Corpus status: **{'PASS' if report.all_passed else 'FAIL'}**",
        "",
        "## Per-system metrics",
        "",
        "| System | Tier | Schema | G2 | G3 | G3a | Self-test | RCov | TCov | PCov | Status |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]

    for item in report.systems:
        status = "PASS" if item.all_pass else "FAIL"
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{item.system_id}`",
                    item.tier,
                    _bool_mark(item.schema_valid),
                    _bool_mark(item.g2_pass),
                    _bool_mark(item.g3_pass),
                    _bool_mark(item.g3a_pass),
                    _bool_mark(item.gold_self_test_pass),
                    f"{item.requirement_coverage:.3f}",
                    f"{item.transition_coverage_exact:.3f}",
                    f"{item.path_coverage:.3f}",
                    status,
                ]
            )
            + " |"
        )

    failing = [item for item in report.systems if not item.all_pass]
    if failing:
        lines.extend(["", "## Failures", ""])
        for item in failing:
            lines.append(f"### `{item.system_id}`")
            if item.errors:
                for error in item.errors:
                    lines.append(f"- {error}")
            else:
                lines.append("- No error details recorded.")
            lines.append("")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def export_corpus_report(report: CorpusEvaluationReport, output_dir: Path) -> dict[str, Path]:
    """Write CSV, JSON, and Markdown corpus reports."""
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "metrics.csv"
    json_path = output_dir / "metrics.json"
    summary_path = output_dir / "summary.md"

    write_metrics_csv(report, csv_path)
    write_json(json_path, report.to_dict())
    write_summary_markdown(report, summary_path)
    return {"csv": csv_path, "json": json_path, "summary": summary_path}


def _bool_mark(value: bool) -> str:
    return "yes" if value else "no"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate the approved gold benchmark corpus.")
    parser.add_argument(
        "--index",
        type=Path,
        default=DEFAULT_INDEX_PATH,
        help="Path to benchmark/index.json",
    )
    parser.add_argument(
        "--catalog",
        type=Path,
        default=DEFAULT_CATALOG_PATH,
        help="Fallback path to benchmark/catalog.json",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for metrics.csv, metrics.json, and summary.md",
    )
    args = parser.parse_args(argv)

    report = evaluate_corpus(index_path=args.index, catalog_path=args.catalog)
    paths = export_corpus_report(report, args.output_dir)

    print(f"systems_total={report.systems_total}")
    print(f"systems_passed={report.systems_passed}")
    print(f"all_passed={report.all_passed}")
    print(f"metrics_csv={paths['csv']}")
    print(f"metrics_json={paths['json']}")
    print(f"summary_md={paths['summary']}")

    for item in report.systems:
        status = "PASS" if item.all_pass else "FAIL"
        print(
            f"{status} {item.system_id}: "
            f"bta={item.behavioral_pass_rate:.3f} "
            f"rcov={item.requirement_coverage:.3f} "
            f"tcov={item.transition_coverage_exact:.3f} "
            f"pcov={item.path_coverage:.3f}"
        )

    return 0 if report.all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
