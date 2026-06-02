# Contributing — behavioral-fsm-benchmark

## Scope

Contributions must align with [docs/study_design.md](docs/study_design.md) and [docs/repository_governance.md](docs/repository_governance.md).

## Setup

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
ruff check framework/ tests/
```

## Pull request checklist

- [ ] English only for tracked files
- [ ] No raw experiment outputs or imported datasets committed
- [ ] Schemas updated if artifact formats change
- [ ] `docs/benchmark_specification.md` updated if metrics or layers change
- [ ] Tests pass (`pytest`)
- [ ] Lint clean (`ruff check`)

## Gold FSM and test-suite authoring

Requires reviewer approval documented in artifact metadata. See [docs/artifact_policy.md](docs/artifact_policy.md).

## Campaign execution

Do not merge executed run data until campaign manifest is frozen per [docs/release_policy.md](docs/release_policy.md).
