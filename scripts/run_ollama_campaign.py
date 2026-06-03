#!/usr/bin/env python3
"""Run a local Ollama FSM generation and behavioral evaluation campaign."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

from ollama_campaign_lib import load_campaign_config, run_campaign  # noqa: E402

DEFAULT_CONFIG = REPO_ROOT / "experiments/configs/C1_pilot_ollama_behavioral.json"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run an Ollama behavioral FSM campaign.")
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help="Path to campaign config JSON",
    )
    parser.add_argument(
        "--run-dir",
        type=Path,
        default=None,
        help="Existing campaign run directory for resume (timestamp subdirectory)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned run matrix without calling Ollama",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Execute only the first N planned runs",
    )
    args = parser.parse_args(argv)

    config = load_campaign_config(args.config.resolve(), repo_root=REPO_ROOT)
    result = run_campaign(
        config,
        repo_root=REPO_ROOT,
        run_dir=args.run_dir,
        dry_run=args.dry_run,
        limit=args.limit,
    )

    if result.get("dry_run"):
        print("dry_run=true")
        print(f"planned_runs={result['planned_runs']}")
        print(f"run_dir={result['run_dir']}")
        for run_id in result.get("runs", []):
            print(f"PLAN {run_id}")
        return 0

    print(f"run_dir={result['run_dir']}")
    print(f"planned_runs={result['planned_runs']}")
    print(f"executed_runs={result['executed_runs']}")
    print(f"failed_runs={result['failed_runs']}")
    print(f"all_passed={result['all_passed']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
