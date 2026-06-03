"""Reusable helpers for Ollama behavioral FSM campaigns (offline testable)."""

from __future__ import annotations

import csv
import json
import platform
import re
import socket
import subprocess
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from framework.benchmark.loader import load_gold_fsm, load_requirement_spec, load_test_suite
from framework.evaluation import evaluate_case, evaluation_to_export
from framework.io.load_json import load_json
from framework.io.write_json import write_json
from framework.types import fsm_from_dict
from framework.validators.schema_validator import validate_against_schema

REPO_ROOT = Path(__file__).resolve().parents[1]

RUN_STATUS_PENDING = "pending"
RUN_STATUS_COMPLETED = "completed"
RUN_STATUS_FAILED = "failed"
RUN_STATUS_SKIPPED = "skipped"

RUN_OUTCOME_PASSED = "passed"
RUN_OUTCOME_FAILED = "failed"

FAILURE_STAGE_NONE = "none"
FAILURE_CATEGORY_NONE = "none"

UNEVALUABLE = None


@dataclass(frozen=True)
class CampaignConfig:
    campaign_id: str
    systems: list[str]
    models: list[str]
    replicates: int
    temperature: float
    structured_output: bool
    prompt_template_path: Path
    system_message: str
    schema_reference: Path
    output_base_dir: Path
    timestamp_policy: str
    ollama_host: str
    timeout_seconds: int
    num_ctx: int
    environment: dict[str, Any] = field(default_factory=dict)
    raw_config: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RunSpec:
    run_id: str
    campaign_id: str
    system_id: str
    model: str
    replicate: int
    index: int


@dataclass
class CandidateEvaluationOutcome:
    run_status: str
    failure_stage: str = FAILURE_STAGE_NONE
    failure_category: str = FAILURE_CATEGORY_NONE
    failure_reason: str = ""
    evaluation_export: dict[str, Any] | None = None
    metrics: dict[str, Any] = field(default_factory=dict)


@dataclass
class RunOutcome:
    run_spec: RunSpec
    status: str
    error: str | None = None
    metrics: dict[str, Any] = field(default_factory=dict)


def load_campaign_config(config_path: Path, *, repo_root: Path | None = None) -> CampaignConfig:
    root = repo_root or REPO_ROOT
    payload = load_json(config_path)
    inference = payload.get("inference", {})
    output = payload.get("output", {})
    prompt_ref = str(payload.get("prompt_template", ""))
    schema_ref = str(payload.get("schema_reference", ""))
    return CampaignConfig(
        campaign_id=str(payload["campaign_id"]),
        systems=[str(item) for item in payload.get("systems", [])],
        models=[str(item) for item in payload.get("models", [])],
        replicates=int(payload.get("replicates", 1)),
        temperature=float(inference.get("temperature", 0.0)),
        structured_output=bool(inference.get("structured_output", True)),
        prompt_template_path=(root / prompt_ref).resolve(),
        system_message=str(payload.get("system_message", "")),
        schema_reference=(root / schema_ref).resolve(),
        output_base_dir=(root / str(output.get("base_dir", "experiments/runs"))).resolve(),
        timestamp_policy=str(output.get("timestamp_policy", "utc_iso_compact")),
        ollama_host=str(inference.get("ollama_host", "http://localhost:11434")),
        timeout_seconds=int(inference.get("timeout_seconds", 600)),
        num_ctx=int(inference.get("num_ctx", 8192)),
        environment=dict(payload.get("environment", {})),
        raw_config=payload,
    )


def sanitize_model_name(model: str) -> str:
    return re.sub(r"[^a-zA-Z0-9._+-]+", "_", model)


def make_run_id(campaign_id: str, system_id: str, model: str, replicate: int) -> str:
    return f"{campaign_id}__{system_id}__{sanitize_model_name(model)}__r{replicate:02d}"


def build_run_matrix(config: CampaignConfig) -> list[RunSpec]:
    runs: list[RunSpec] = []
    index = 0
    for system_id in config.systems:
        for model in config.models:
            for replicate in range(1, config.replicates + 1):
                index += 1
                runs.append(
                    RunSpec(
                        run_id=make_run_id(config.campaign_id, system_id, model, replicate),
                        campaign_id=config.campaign_id,
                        system_id=system_id,
                        model=model,
                        replicate=replicate,
                        index=index,
                    )
                )
    return runs


def make_campaign_timestamp(*, policy: str = "utc_iso_compact") -> str:
    now = datetime.now(tz=UTC).replace(microsecond=0)
    if policy == "utc_iso_compact":
        return now.strftime("%Y%m%dT%H%M%SZ")
    return now.isoformat()


def create_campaign_run_dir(config: CampaignConfig, timestamp: str | None = None) -> Path:
    stamp = timestamp or make_campaign_timestamp(policy=config.timestamp_policy)
    run_dir = config.output_base_dir / stamp
    for sub in ("raw", "candidates", "evaluations", "logs"):
        (run_dir / sub).mkdir(parents=True, exist_ok=True)
    return run_dir


def manifest_path(run_dir: Path) -> Path:
    return run_dir / "manifest.json"


def load_manifest(run_dir: Path) -> dict[str, Any]:
    path = manifest_path(run_dir)
    if path.is_file():
        return load_json(path)
    return {
        "campaign_id": None,
        "created_at": datetime.now(tz=UTC).replace(microsecond=0).isoformat(),
        "runs": [],
    }


def detect_completed_run_ids(run_dir: Path) -> set[str]:
    manifest = load_manifest(run_dir)
    executed: set[str] = set()
    for item in manifest.get("runs", []):
        run_id = item.get("run_id")
        if not run_id:
            continue
        status = item.get("status")
        if status in {RUN_STATUS_COMPLETED, RUN_STATUS_FAILED}:
            executed.add(str(run_id))
    return executed


def format_metric_csv_value(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def resolve_resume_run_dir(config: CampaignConfig, run_dir: Path | None) -> Path:
    if run_dir is not None:
        run_dir.mkdir(parents=True, exist_ok=True)
        for sub in ("raw", "candidates", "evaluations", "logs"):
            (run_dir / sub).mkdir(parents=True, exist_ok=True)
        return run_dir

    if not config.output_base_dir.is_dir():
        return create_campaign_run_dir(config)

    existing = sorted(
        [path for path in config.output_base_dir.iterdir() if path.is_dir()],
        key=lambda path: path.name,
    )
    if existing:
        latest = existing[-1]
        if manifest_path(latest).is_file():
            return latest
    return create_campaign_run_dir(config)


def render_prompt(
    template_text: str,
    *,
    system_id: str,
    spec_payload: dict[str, Any],
    schema_ref: str,
) -> str:
    requirements = spec_payload.get("requirements", [])
    req_text = (
        "\n".join(f"- {item}" for item in requirements)
        if isinstance(requirements, list)
        else str(requirements)
    )
    replacements = {
        "{{SYSTEM_ID}}": system_id,
        "{{SYSTEM_NAME}}": str(spec_payload.get("system_name", system_id)),
        "{{DOMAIN}}": str(spec_payload.get("domain", "")),
        "{{REQUIREMENTS}}": req_text,
        "{{SCHEMA_REFERENCE}}": schema_ref,
    }
    rendered = template_text
    for key, value in replacements.items():
        rendered = rendered.replace(key, value)
    return rendered


def extract_json_object(text: str) -> tuple[dict[str, Any] | None, str | None]:
    stripped = text.strip()
    if not stripped:
        return None, "empty model response"

    candidates = [stripped]
    fence_match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", stripped, flags=re.DOTALL | re.IGNORECASE)
    if fence_match:
        candidates.insert(0, fence_match.group(1).strip())
    brace_match = re.search(r"(\{.*\})", stripped, flags=re.DOTALL)
    if brace_match:
        candidates.append(brace_match.group(1).strip())

    last_error = "unable to parse JSON from model response"
    for candidate in candidates:
        try:
            payload = json.loads(candidate)
        except json.JSONDecodeError as exc:
            last_error = str(exc)
            continue
        if isinstance(payload, dict):
            return payload, None
        last_error = "parsed JSON is not an object"
    return None, last_error


def classify_json_extraction_error(error: str | None) -> tuple[str, str]:
    message = (error or "").lower()
    if "empty" in message:
        return "json_extraction", "no_json_found"
    if "not an object" in message:
        return "json_extraction", "invalid_json"
    if "expect" in message or "decode" in message or "json" in message:
        return "json_extraction", "invalid_json"
    return "json_extraction", "no_json_found"


def unevaluable_metric_fields() -> dict[str, Any]:
    return {
        "schema_valid": UNEVALUABLE,
        "referential_valid": UNEVALUABLE,
        "strict_deterministic": UNEVALUABLE,
        "guard_aware_deterministic": UNEVALUABLE,
        "requirement_coverage": UNEVALUABLE,
        "behavioral_pass_rate": UNEVALUABLE,
        "final_state_agreement": UNEVALUABLE,
        "trace_agreement": UNEVALUABLE,
        "rejected_event_agreement": UNEVALUABLE,
        "missing_transitions": UNEVALUABLE,
        "extra_transitions": UNEVALUABLE,
    }


def build_metric_row(
    run_spec: RunSpec,
    *,
    run_status: str,
    failure_stage: str = FAILURE_STAGE_NONE,
    failure_category: str = FAILURE_CATEGORY_NONE,
    failure_reason: str = "",
    evaluation_export: dict[str, Any] | None = None,
    schema_valid_override: bool | None = None,
    started_at: str | None = None,
    finished_at: str | None = None,
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "run_id": run_spec.run_id,
        "campaign_id": run_spec.campaign_id,
        "system_id": run_spec.system_id,
        "model": run_spec.model,
        "replicate": run_spec.replicate,
        "run_index": run_spec.index,
        "run_status": run_status,
        "failure_stage": failure_stage,
        "failure_category": failure_category,
        "failure_reason": failure_reason or "",
        "started_at": started_at or "",
        "finished_at": finished_at or "",
        **unevaluable_metric_fields(),
    }

    if evaluation_export is None:
        if schema_valid_override is not None:
            row["schema_valid"] = schema_valid_override
        return row

    structural = evaluation_export.get("structural", {})
    determinism = evaluation_export.get("determinism", {})
    behavioral = evaluation_export.get("behavioral") or {}
    equivalence = evaluation_export.get("equivalence") or {}
    coverage = evaluation_export.get("coverage") or {}

    row.update(
        {
            "schema_valid": bool(structural.get("schema_valid")),
            "referential_valid": bool(structural.get("referential_valid")),
            "strict_deterministic": bool(determinism.get("strict_deterministic")),
            "guard_aware_deterministic": bool(determinism.get("guard_aware_deterministic")),
            "requirement_coverage": float(coverage.get("requirement_coverage", 0.0)),
            "behavioral_pass_rate": float(
                behavioral.get("behavioral_pass_rate", behavioral.get("oracle_pass_rate", 0.0))
            ),
            "final_state_agreement": float(behavioral.get("final_state_agreement_rate", 0.0)),
            "trace_agreement": float(behavioral.get("trace_agreement_rate", 0.0)),
            "rejected_event_agreement": float(
                behavioral.get("rejected_event_agreement_rate", 0.0)
            ),
            "missing_transitions": len(equivalence.get("missing_transitions", [])),
            "extra_transitions": len(equivalence.get("extra_transitions", [])),
        }
    )
    if schema_valid_override is not None:
        row["schema_valid"] = schema_valid_override
    return row


def build_failure_export(
    *,
    failure_stage: str,
    failure_category: str,
    failure_reason: str,
    schema_valid: bool | None = None,
    schema_errors: list[str] | None = None,
) -> dict[str, Any]:
    export: dict[str, Any] = {
        "run_status": RUN_OUTCOME_FAILED,
        "failure_stage": failure_stage,
        "failure_category": failure_category,
        "failure_reason": failure_reason,
    }
    if schema_valid is not None:
        export["structural"] = {
            "schema_valid": schema_valid,
            "referential_valid": False,
            "errors": list(schema_errors or []),
            "warnings": [],
        }
    return export


def evaluate_candidate_payload(
    payload: dict[str, Any],
    *,
    system_id: str,
    repo_root: Path,
    candidate_label: str,
    run_spec: RunSpec,
) -> CandidateEvaluationOutcome:
    schema_ok, schema_errors = validate_against_schema(payload, "generated_fsm.schema.json")

    try:
        candidate = fsm_from_dict(payload)
    except (KeyError, TypeError, ValueError) as exc:
        reason = f"fsm parse error: {exc}"
        export = build_failure_export(
            failure_stage="parsing",
            failure_category="parse_error",
            failure_reason=reason,
            schema_valid=schema_ok,
            schema_errors=schema_errors,
        )
        metrics = build_metric_row(
            run_spec,
            run_status=RUN_OUTCOME_FAILED,
            failure_stage="parsing",
            failure_category="parse_error",
            failure_reason=reason,
            evaluation_export=None,
            schema_valid_override=schema_ok,
        )
        return CandidateEvaluationOutcome(
            run_status=RUN_OUTCOME_FAILED,
            failure_stage="parsing",
            failure_category="parse_error",
            failure_reason=reason,
            evaluation_export=export,
            metrics=metrics,
        )

    if not schema_ok:
        reason = "; ".join(schema_errors) if schema_errors else "schema validation failed"
        export = build_failure_export(
            failure_stage="schema_validation",
            failure_category="schema_error",
            failure_reason=reason,
            schema_valid=False,
            schema_errors=schema_errors,
        )
        metrics = build_metric_row(
            run_spec,
            run_status=RUN_OUTCOME_FAILED,
            failure_stage="schema_validation",
            failure_category="schema_error",
            failure_reason=reason,
            evaluation_export=None,
            schema_valid_override=False,
        )
        return CandidateEvaluationOutcome(
            run_status=RUN_OUTCOME_FAILED,
            failure_stage="schema_validation",
            failure_category="schema_error",
            failure_reason=reason,
            evaluation_export=export,
            metrics=metrics,
        )

    spec = load_requirement_spec(system_id, datasets_dir=repo_root / "benchmark/datasets/systems")
    gold = load_gold_fsm(system_id, validate=False, gold_dir=repo_root / "benchmark/gold_fsms")
    suite = load_test_suite(system_id, validate=False, suite_dir=repo_root / "benchmark/test_suites")

    result = evaluate_case(
        candidate,
        candidate_label=candidate_label,
        spec=spec,
        gold=gold,
        test_suite=suite,
        schema_valid=True,
    )
    export = evaluation_to_export(result)
    export["run_status"] = RUN_OUTCOME_PASSED
    export["failure_stage"] = FAILURE_STAGE_NONE
    export["failure_category"] = FAILURE_CATEGORY_NONE
    export["failure_reason"] = ""

    metrics = build_metric_row(
        run_spec,
        run_status=RUN_OUTCOME_PASSED,
        evaluation_export=export,
    )
    return CandidateEvaluationOutcome(
        run_status=RUN_OUTCOME_PASSED,
        evaluation_export=export,
        metrics=metrics,
    )


def populate_environment_metadata(config: CampaignConfig, *, repo_root: Path) -> dict[str, Any]:
    env = dict(config.environment)
    env.setdefault("hostname", socket.gethostname())
    env.setdefault("platform", platform.platform())
    env.setdefault("python_version", platform.python_version())
    if not env.get("git_commit"):
        try:
            result = subprocess.run(
                ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
                check=True,
                capture_output=True,
                text=True,
            )
            env["git_commit"] = result.stdout.strip()
        except (OSError, subprocess.CalledProcessError):
            env["git_commit"] = "unknown"
    return env


def call_ollama_chat(
    *,
    host: str,
    model: str,
    system_message: str,
    user_prompt: str,
    temperature: float,
    structured_output: bool,
    num_ctx: int,
    timeout_seconds: int,
) -> tuple[str | None, str | None]:
    payload: dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_ctx": num_ctx,
        },
    }
    if structured_output:
        payload["format"] = "json"

    request = urllib.request.Request(
        f"{host.rstrip('/')}/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        return None, f"ollama request failed: {exc}"
    except TimeoutError:
        return None, "ollama request timed out"
    except json.JSONDecodeError as exc:
        return None, f"ollama response decode error: {exc}"

    message = body.get("message", {})
    content = message.get("content")
    if not isinstance(content, str) or not content.strip():
        return None, "ollama returned empty content"
    return content, None


METRIC_CSV_COLUMNS = [
    "run_id",
    "campaign_id",
    "system_id",
    "model",
    "replicate",
    "run_index",
    "run_status",
    "failure_stage",
    "failure_category",
    "failure_reason",
    "started_at",
    "finished_at",
    "schema_valid",
    "referential_valid",
    "strict_deterministic",
    "guard_aware_deterministic",
    "requirement_coverage",
    "behavioral_pass_rate",
    "final_state_agreement",
    "trace_agreement",
    "rejected_event_agreement",
    "missing_transitions",
    "extra_transitions",
]


def write_metrics_files(run_dir: Path, rows: list[dict[str, Any]]) -> None:
    csv_path = run_dir / "metrics.csv"
    json_path = run_dir / "metrics.json"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=METRIC_CSV_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    key: format_metric_csv_value(row.get(key))
                    for key in METRIC_CSV_COLUMNS
                }
            )
    write_json(
        json_path,
        {
            "generated_at": datetime.now(tz=UTC).replace(microsecond=0).isoformat(),
            "runs_total": len(rows),
            "runs_passed": sum(
                1 for row in rows if row.get("run_status") == RUN_OUTCOME_PASSED
            ),
            "runs_failed": sum(
                1 for row in rows if row.get("run_status") == RUN_OUTCOME_FAILED
            ),
            "metrics": rows,
        },
    )


def update_manifest(run_dir: Path, manifest: dict[str, Any]) -> None:
    write_json(manifest_path(run_dir), manifest)


def execute_run(
    run_spec: RunSpec,
    *,
    config: CampaignConfig,
    run_dir: Path,
    repo_root: Path,
    prompt_template: str,
) -> RunOutcome:
    started_at = datetime.now(tz=UTC).replace(microsecond=0).isoformat()
    spec_payload = load_json(repo_root / "benchmark/datasets/systems" / f"{run_spec.system_id}.json")
    user_prompt = render_prompt(
        prompt_template,
        system_id=run_spec.system_id,
        spec_payload=spec_payload,
        schema_ref=str(config.schema_reference.relative_to(repo_root)),
    )

    raw_path = run_dir / "raw" / f"{run_spec.run_id}.json"
    candidate_path = run_dir / "candidates" / f"{run_spec.run_id}.json"
    evaluation_path = run_dir / "evaluations" / f"{run_spec.run_id}.json"
    log_path = run_dir / "logs" / f"{run_spec.run_id}.log"

    response_text, ollama_error = call_ollama_chat(
        host=config.ollama_host,
        model=run_spec.model,
        system_message=config.system_message,
        user_prompt=user_prompt,
        temperature=config.temperature,
        structured_output=config.structured_output,
        num_ctx=config.num_ctx,
        timeout_seconds=config.timeout_seconds,
    )

    log_lines = [
        f"run_id={run_spec.run_id}",
        f"system_id={run_spec.system_id}",
        f"model={run_spec.model}",
        f"replicate={run_spec.replicate}",
        f"started_at={started_at}",
    ]
    finished_at = datetime.now(tz=UTC).replace(microsecond=0).isoformat()

    def finish_failed(
        *,
        failure_stage: str,
        failure_category: str,
        failure_reason: str,
        evaluation_export: dict[str, Any] | None = None,
        schema_valid_override: bool | None = None,
    ) -> RunOutcome:
        log_lines.extend(
            [
                f"run_status={RUN_OUTCOME_FAILED}",
                f"failure_stage={failure_stage}",
                f"failure_category={failure_category}",
                f"failure_reason={failure_reason}",
                f"finished_at={finished_at}",
            ]
        )
        log_path.write_text("\n".join(log_lines) + "\n", encoding="utf-8")
        if evaluation_export is not None:
            write_json(evaluation_path, evaluation_export)
        metrics = build_metric_row(
            run_spec,
            run_status=RUN_OUTCOME_FAILED,
            failure_stage=failure_stage,
            failure_category=failure_category,
            failure_reason=failure_reason,
            evaluation_export=None,
            schema_valid_override=schema_valid_override,
            started_at=started_at,
            finished_at=finished_at,
        )
        return RunOutcome(
            run_spec=run_spec,
            status=RUN_STATUS_FAILED,
            error=failure_reason,
            metrics=metrics,
        )

    if ollama_error:
        export = build_failure_export(
            failure_stage="generation",
            failure_category="ollama_error",
            failure_reason=ollama_error,
        )
        return finish_failed(
            failure_stage="generation",
            failure_category="ollama_error",
            failure_reason=ollama_error,
            evaluation_export=export,
        )

    write_json(
        raw_path,
        {
            "run_id": run_spec.run_id,
            "model": run_spec.model,
            "system_id": run_spec.system_id,
            "response_text": response_text,
        },
    )

    payload, extract_error = extract_json_object(response_text or "")
    if payload is None:
        failure_stage, failure_category = classify_json_extraction_error(extract_error)
        reason = extract_error or "json extraction failed"
        export = build_failure_export(
            failure_stage=failure_stage,
            failure_category=failure_category,
            failure_reason=reason,
        )
        return finish_failed(
            failure_stage=failure_stage,
            failure_category=failure_category,
            failure_reason=reason,
            evaluation_export=export,
        )

    write_json(candidate_path, payload)
    eval_outcome = evaluate_candidate_payload(
        payload,
        system_id=run_spec.system_id,
        repo_root=repo_root,
        candidate_label=run_spec.run_id,
        run_spec=run_spec,
    )

    if eval_outcome.run_status == RUN_OUTCOME_FAILED:
        log_lines.extend(
            [
                f"run_status={RUN_OUTCOME_FAILED}",
                f"failure_stage={eval_outcome.failure_stage}",
                f"failure_category={eval_outcome.failure_category}",
                f"failure_reason={eval_outcome.failure_reason}",
                f"finished_at={finished_at}",
            ]
        )
        log_path.write_text("\n".join(log_lines) + "\n", encoding="utf-8")
        if eval_outcome.evaluation_export is not None:
            write_json(evaluation_path, eval_outcome.evaluation_export)
        eval_outcome.metrics["started_at"] = started_at
        eval_outcome.metrics["finished_at"] = finished_at
        return RunOutcome(
            run_spec=run_spec,
            status=RUN_STATUS_FAILED,
            error=eval_outcome.failure_reason,
            metrics=eval_outcome.metrics,
        )

    write_json(evaluation_path, eval_outcome.evaluation_export)
    log_lines.extend(
        [
            f"run_status={RUN_OUTCOME_PASSED}",
            f"failure_stage={FAILURE_STAGE_NONE}",
            f"failure_category={FAILURE_CATEGORY_NONE}",
            f"finished_at={finished_at}",
        ]
    )
    log_path.write_text("\n".join(log_lines) + "\n", encoding="utf-8")
    eval_outcome.metrics["started_at"] = started_at
    eval_outcome.metrics["finished_at"] = finished_at
    return RunOutcome(
        run_spec=run_spec,
        status=RUN_STATUS_COMPLETED,
        metrics=eval_outcome.metrics,
    )


def run_campaign(
    config: CampaignConfig,
    *,
    repo_root: Path | None = None,
    run_dir: Path | None = None,
    dry_run: bool = False,
    limit: int | None = None,
) -> dict[str, Any]:
    root = repo_root or REPO_ROOT
    matrix = build_run_matrix(config)
    if limit is not None:
        matrix = matrix[: max(limit, 0)]

    if dry_run:
        return {
            "dry_run": True,
            "planned_runs": len(matrix),
            "runs": [run.run_id for run in matrix],
            "run_dir": str(resolve_resume_run_dir(config, run_dir)),
        }

    campaign_dir = resolve_resume_run_dir(config, run_dir)
    completed = detect_completed_run_ids(campaign_dir)
    prompt_template = config.prompt_template_path.read_text(encoding="utf-8")

    manifest = load_manifest(campaign_dir)
    manifest["campaign_id"] = config.campaign_id
    manifest["environment"] = populate_environment_metadata(config, repo_root=root)
    manifest.setdefault("runs", [])

    existing_by_id = {str(item.get("run_id")): item for item in manifest.get("runs", [])}
    metric_rows: list[dict[str, Any]] = []

    for run_spec in matrix:
        if run_spec.run_id in completed:
            existing = existing_by_id.get(run_spec.run_id)
            if existing and existing.get("metrics"):
                metric_rows.append(dict(existing["metrics"]))
            else:
                eval_path = campaign_dir / "evaluations" / f"{run_spec.run_id}.json"
                if eval_path.is_file():
                    export = load_json(eval_path)
                    metric_rows.append(
                        build_metric_row(
                            run_spec,
                            run_status=str(
                                export.get("run_status", RUN_OUTCOME_PASSED)
                            ),
                            failure_stage=str(
                                export.get("failure_stage", FAILURE_STAGE_NONE)
                            ),
                            failure_category=str(
                                export.get("failure_category", FAILURE_CATEGORY_NONE)
                            ),
                            failure_reason=str(export.get("failure_reason", "")),
                            evaluation_export=export
                            if export.get("run_status", RUN_OUTCOME_PASSED)
                            == RUN_OUTCOME_PASSED
                            else None,
                        )
                    )
            manifest_entry = existing or {"run_id": run_spec.run_id, "status": RUN_STATUS_SKIPPED}
            manifest_entry["status"] = RUN_STATUS_SKIPPED
            existing_by_id[run_spec.run_id] = manifest_entry
            continue

        outcome = execute_run(
            run_spec,
            config=config,
            run_dir=campaign_dir,
            repo_root=root,
            prompt_template=prompt_template,
        )
        manifest_entry = {
            "run_id": run_spec.run_id,
            "system_id": run_spec.system_id,
            "model": run_spec.model,
            "replicate": run_spec.replicate,
            "status": outcome.status,
            "error": outcome.error,
            "metrics": outcome.metrics,
        }
        existing_by_id[run_spec.run_id] = manifest_entry
        metric_rows.append(outcome.metrics)

    manifest["runs"] = [existing_by_id[run.run_id] for run in matrix if run.run_id in existing_by_id]
    manifest["updated_at"] = datetime.now(tz=UTC).replace(microsecond=0).isoformat()
    update_manifest(campaign_dir, manifest)
    metric_rows.sort(key=lambda row: int(row.get("run_index", 0)))
    write_metrics_files(campaign_dir, metric_rows)

    failed = sum(1 for row in metric_rows if row.get("run_status") == RUN_OUTCOME_FAILED)
    passed = sum(1 for row in metric_rows if row.get("run_status") == RUN_OUTCOME_PASSED)
    return {
        "dry_run": False,
        "run_dir": str(campaign_dir),
        "planned_runs": len(matrix),
        "executed_runs": len(metric_rows),
        "passed_runs": passed,
        "failed_runs": failed,
        "all_passed": failed == 0,
    }
