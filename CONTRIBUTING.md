# Contributing — behavioral-fsm-benchmark

Thank you for your interest in this research artifact.

## Scope

This repository supports an EMSE empirical study. Contributions should align with the study design in [docs/study_design.md](docs/study_design.md).

## Before you start

1. Read [docs/benchmark_specification.md](docs/benchmark_specification.md).
2. Read [docs/evaluation_protocol.md](docs/evaluation_protocol.md).
3. Do not commit raw model outputs, imported datasets, or LaTeX build artifacts.

## Development setup

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## Pull requests

- English only for tracked files.
- One logical change per PR.
- Update docs when changing protocols or schemas.
- No experimental results in PRs until campaign freeze is documented.

## Gold FSM authoring

Reference FSMs require reviewer approval before use in scoring. See `benchmark/gold_fsms/` README and [docs/benchmark_specification.md](docs/benchmark_specification.md).

## Questions

Open a GitHub issue with label `question`.
