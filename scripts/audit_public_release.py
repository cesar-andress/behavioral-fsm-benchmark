#!/usr/bin/env python3
"""Audit the public repository for release-ineligible tracked content."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_PREFIXES = (
    "paper/",
    "../paper/",
    ".cursor/",
    ".claude/",
    ".aider/",
    ".continue/",
    ".windsurf/",
    "prompts/",
    "prompt_drafts/",
    "ai_prompts/",
    "cursor_rules/",
    "chat_logs/",
    "assistant_logs/",
    "scratch_prompts/",
    "local_notes/",
)

FORBIDDEN_SUFFIXES = (
    ".tex",
    ".pdf",
    ".aux",
    ".bbl",
    ".blg",
    ".out",
    ".toc",
    ".lof",
    ".lot",
    ".fls",
    ".fdb_latexmk",
    ".synctex.gz",
    ".prompt.txt",
    ".chat.txt",
    ".assistant.txt",
)

FORBIDDEN_BASENAMES = {
    "AGENTS.md",
    ".cursorrules",
    ".cursorignore",
    ".claude.json",
}

FORBIDDEN_EXPERIMENT_PATTERNS = (
    "experiments/logs/",
    "experiments/runs/",
    "outputs/",
    "results/",
    "campaign_reports/",
    "paper_results/",
    "manuscript_exports/",
)

# Matches .gitignore whitelist for the frozen C1 generation prompt (v0.1.0).
ALLOWED_TRACKED_PATHS = frozenset(
    {
        "prompts/behavioral_fsm_generation.md",
    }
)


def git_ls_files(repo_root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(repo_root), "ls-files"],
        check=True,
        capture_output=True,
        text=True,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def audit_tracked_paths(tracked_files: list[str]) -> list[str]:
    violations: list[str] = []

    for rel_path in tracked_files:
        normalized = rel_path.replace("\\", "/")
        basename = Path(normalized).name

        if normalized in ALLOWED_TRACKED_PATHS:
            continue

        if basename in FORBIDDEN_BASENAMES:
            violations.append(f"forbidden basename tracked: {rel_path}")
            continue

        if any(normalized.startswith(prefix) for prefix in FORBIDDEN_PREFIXES):
            violations.append(f"forbidden path prefix tracked: {rel_path}")
            continue

        if normalized.endswith(FORBIDDEN_SUFFIXES):
            violations.append(f"forbidden file extension tracked: {rel_path}")
            continue

        for pattern in FORBIDDEN_EXPERIMENT_PATTERNS:
            if normalized.startswith(pattern) and not normalized.endswith(".gitkeep"):
                violations.append(f"local experiment output tracked: {rel_path}")

    return violations


def audit_worktree(repo_root: Path) -> list[str]:
    violations: list[str] = []

    paper_dir = repo_root / "paper"
    if paper_dir.is_dir():
        violations.append(
            "paper/ directory present in repository root (must live outside public repo)"
        )

    return violations


def audit_public_release(*, repo_root: Path | None = None) -> tuple[bool, list[str]]:
    root = repo_root or REPO_ROOT
    tracked = git_ls_files(root)
    violations = audit_tracked_paths(tracked) + audit_worktree(root)
    return len(violations) == 0, violations


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit public repository release eligibility.")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=REPO_ROOT,
        help="Repository root to audit",
    )
    args = parser.parse_args(argv)

    ok, violations = audit_public_release(repo_root=args.repo_root)
    if ok:
        print("release_audit=PASS")
        print(f"tracked_files={len(git_ls_files(args.repo_root))}")
        return 0

    print("release_audit=FAIL")
    for item in violations:
        print(f"VIOLATION: {item}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
