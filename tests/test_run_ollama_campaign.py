"""Tests for Ollama campaign runner (no live Ollama required)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from ollama_campaign_lib import (  # noqa: E402
    RUN_STATUS_COMPLETED,
    build_metric_row,
    build_run_matrix,
    create_campaign_run_dir,
    detect_completed_run_ids,
    extract_json_object,
    load_campaign_config,
    make_run_id,
    render_prompt,
    run_campaign,
)

CONFIG_PATH = REPO_ROOT / "experiments/configs/C1_pilot_ollama_behavioral.json"


@pytest.fixture(scope="module")
def campaign_config():
    return load_campaign_config(CONFIG_PATH, repo_root=REPO_ROOT)


def test_load_campaign_config(campaign_config) -> None:
    assert campaign_config.campaign_id == "C1_pilot_ollama_behavioral"
    assert campaign_config.systems == ["vending_machine", "login_system", "atm"]
    assert len(campaign_config.models) == 6
    assert campaign_config.replicates == 5
    assert campaign_config.temperature == 0.0
    assert campaign_config.structured_output is True
    assert campaign_config.prompt_template_path.is_file()


def test_build_run_matrix_size(campaign_config) -> None:
    matrix = build_run_matrix(campaign_config)
    assert len(matrix) == 90
    assert matrix[0].system_id == "vending_machine"
    assert matrix[0].model == "qwen2.5-coder:7b"
    assert matrix[0].replicate == 1
    assert matrix[-1].replicate == 5


def test_make_run_id_sanitizes_model() -> None:
    run_id = make_run_id("C1", "atm", "qwen2.5-coder:7b", 3)
    assert "qwen2.5-coder_7b" in run_id
    assert run_id.endswith("__r03")


def test_create_campaign_run_dir(tmp_path: Path) -> None:
    payload = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    payload["output"] = {"base_dir": str(tmp_path / "runs"), "timestamp_policy": "utc_iso_compact"}
    cfg_path = tmp_path / "cfg.json"
    cfg_path.write_text(json.dumps(payload), encoding="utf-8")
    cfg = load_campaign_config(cfg_path, repo_root=tmp_path)

    run_dir = create_campaign_run_dir(cfg, timestamp="20260101T000000Z")
    assert run_dir.is_dir()
    for sub in ("raw", "candidates", "evaluations", "logs"):
        assert (run_dir / sub).is_dir()


def test_detect_completed_run_ids(tmp_path: Path) -> None:
    run_dir = tmp_path / "campaign"
    run_dir.mkdir()
    manifest = {
        "campaign_id": "C1",
        "runs": [
            {"run_id": "a", "status": RUN_STATUS_COMPLETED},
            {"run_id": "b", "status": "failed"},
        ],
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    completed = detect_completed_run_ids(run_dir)
    assert completed == {"a"}


def test_build_metric_row_from_evaluation() -> None:
    from ollama_campaign_lib import RunSpec

    run = RunSpec(
        run_id="test__vending__model__r01",
        campaign_id="C1",
        system_id="vending_machine",
        model="llama3.1:8b",
        replicate=1,
        index=1,
    )
    export = {
        "structural": {"schema_valid": True, "referential_valid": True},
        "determinism": {"strict_deterministic": True, "guard_aware_deterministic": True},
        "behavioral": {
            "behavioral_pass_rate": 0.5,
            "final_state_agreement_rate": 0.8,
            "trace_agreement_rate": 0.7,
            "rejected_event_agreement_rate": 1.0,
        },
        "equivalence": {"missing_transitions": ["A:e:B"], "extra_transitions": ["C:d:D"]},
        "coverage": {"requirement_coverage": 0.75},
    }
    row = build_metric_row(run, status=RUN_STATUS_COMPLETED, evaluation_export=export)
    assert row["schema_valid"] is True
    assert row["g3_pass"] is True
    assert row["behavioral_pass_rate"] == 0.5
    assert row["missing_transitions_count"] == 1
    assert row["extra_transitions_count"] == 1


def test_render_prompt_includes_requirements(campaign_config) -> None:
    template = campaign_config.prompt_template_path.read_text(encoding="utf-8")
    spec = {"system_name": "Vending Machine", "domain": "vending", "requirements": ["R1: idle"]}
    rendered = render_prompt(
        template,
        system_id="vending_machine",
        spec_payload=spec,
        schema_ref="schema.json",
    )
    assert "vending_machine" in rendered
    assert "R1: idle" in rendered


def test_extract_json_object_from_fenced_response() -> None:
    text = (
        'Here is output:\n```json\n'
        '{"states":["A"],"initial_state":"A","events":[],"transitions":[]}\n```'
    )
    payload, error = extract_json_object(text)
    assert error is None
    assert payload is not None
    assert payload["initial_state"] == "A"


def test_dry_run_planned_matrix(campaign_config, tmp_path: Path) -> None:
    payload = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    payload["output"] = {"base_dir": str(tmp_path / "runs"), "timestamp_policy": "utc_iso_compact"}
    cfg_path = tmp_path / "cfg.json"
    cfg_path.write_text(json.dumps(payload), encoding="utf-8")
    cfg = load_campaign_config(cfg_path, repo_root=tmp_path)

    result = run_campaign(cfg, repo_root=REPO_ROOT, dry_run=True, limit=3)
    assert result["dry_run"] is True
    assert result["planned_runs"] == 3
    assert len(result["runs"]) == 3


def test_resume_skips_completed_runs(campaign_config, tmp_path: Path, monkeypatch) -> None:
    run_dir = tmp_path / "campaign"
    for sub in ("raw", "candidates", "evaluations", "logs"):
        (run_dir / sub).mkdir(parents=True)

    matrix = build_run_matrix(campaign_config)[:1]
    run_id = matrix[0].run_id
    manifest = {
        "campaign_id": campaign_config.campaign_id,
        "runs": [
            {
                "run_id": run_id,
                "status": RUN_STATUS_COMPLETED,
                "metrics": {"run_id": run_id, "status": RUN_STATUS_COMPLETED},
            }
        ],
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    calls = {"count": 0}

    def fake_execute(*args, **kwargs):
        calls["count"] += 1
        raise AssertionError("execute_run should not be called for completed run")

    monkeypatch.setattr("ollama_campaign_lib.execute_run", fake_execute)
    result = run_campaign(campaign_config, repo_root=REPO_ROOT, run_dir=run_dir, limit=1)
    assert calls["count"] == 0
    assert result["failed_runs"] == 0
