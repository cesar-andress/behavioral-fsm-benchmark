"""Tests for scripts/audit_public_release.py."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "audit_public_release.py"


def _load_audit_module():
    spec = importlib.util.spec_from_file_location("audit_public_release", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_audit_public_release_passes_on_repository() -> None:
    audit = _load_audit_module()
    ok, violations = audit.audit_public_release(repo_root=REPO_ROOT)
    assert ok, violations


def test_audit_detects_forbidden_tracked_path() -> None:
    audit = _load_audit_module()
    violations = audit.audit_tracked_paths(
        [
            "framework/types.py",
            "paper/main.tex",
            "experiments/logs/run001.log",
        ]
    )
    assert any("paper/main.tex" in item for item in violations)
    assert any("experiments/logs/run001.log" in item for item in violations)
    assert not any("framework/types.py" in item for item in violations)


def test_audit_cli_exit_code() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH)],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "release_audit=PASS" in result.stdout
