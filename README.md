# behavioral-fsm-benchmark

Public **research-software repository** for an Empirical Software Engineering (EMSE) study on LLM-generated finite state machines.

**Release:** `v0.1.0` — framework, approved gold corpus (pilot + core), corpus evaluation, and reproducibility documentation.

## Purpose

This repository provides:

1. A **Python evaluation framework** for structural gates (G1–G3), guard-aware determinism (G3a), behavioral oracles, gold comparison, and coverage metrics.
2. A **tiered behavioral benchmark** extending [FSM-Bench-20](https://doi.org/10.5281/zenodo.20516296) with human-approved gold FSMs and behavioral test suites.
3. **Study documentation** (design, benchmark specification, evaluation protocol) and replication instructions.
4. **Release hygiene** tooling to keep the public repository free of local experiment outputs and non-public content.

`v0.1.0` freezes the evaluation stack and approved gold corpus. Ollama campaign scripts and configs are included; timestamped run outputs remain local and gitignored until explicitly frozen in a future release.

## Repository layout

```text
behavioral-fsm-benchmark/
├── benchmark/           JSON schemas, gold FSMs, test suites, requirement specs, guards
│   ├── catalog.json     tier registry (pilot / core / stretch)
│   ├── index.json       system index with artifact paths
│   ├── gold_fsms/       approved reference FSMs
│   ├── test_suites/     behavioral oracle / path / negative tests
│   └── datasets/systems/ requirement specifications (tracked for pilot + core)
├── framework/           Python evaluation engine
├── scripts/             CLI entry points (validation, corpus evaluation, release audit)
├── tests/               unit and integration tests
├── docs/                study design, protocols, artifact and release policies
├── experiments/         campaign templates (raw runs gitignored)
├── reproducibility/     replication packaging scripts
├── REPRODUCIBILITY.md   step-by-step replication guide
└── CHANGELOG.md         release history
```

## Installation

Requires **Python 3.11+** (3.12 recommended).

```bash
git clone https://github.com/cesar-andress/behavioral-fsm-benchmark.git
cd behavioral-fsm-benchmark
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Validation commands

Run the full test suite and linter:

```bash
pytest
ruff check framework/ tests/ scripts/
```

Validate a single gold FSM (schema + structural + determinism):

```bash
python scripts/validate_fsm.py benchmark/gold_fsms/vending_machine.json \
  --schema reference_fsm.schema.json
```

Run a behavioral test suite against a gold FSM:

```bash
python scripts/run_behavioral_tests.py \
  benchmark/gold_fsms/vending_machine.json \
  benchmark/test_suites/vending_machine.json
```

## Gold corpus evaluation

Evaluate all systems listed in `benchmark/index.json` (12 systems in `v0.1.0`):

```bash
python scripts/audit_public_release.py
python scripts/evaluate_gold_corpus.py
```

Reports are written to `results/gold_corpus/` (gitignored):

| Output | Description |
|--------|-------------|
| `metrics.csv` | Per-system gate and coverage metrics |
| `metrics.json` | Structured corpus report |
| `summary.md` | Human-readable pass/fail summary |

Expected result for the released corpus: `all_passed=True` with behavioral pass rate `1.000` for every system.

## Artifact scope (v0.1.0)

| Tier | Systems | Status |
|------|---------|--------|
| Pilot | `vending_machine`, `login_system`, `atm` | Approved gold + test suites |
| Core | `parking_gate`, `access_control`, `bike_rental`, `warehouse_inventory`, `smart_thermostat`, `elevator`, `hotel_booking`, `train_ticket_booking`, `package_locker` | Approved gold + test suites |

Each system provides:

- `benchmark/datasets/systems/<system>.json` — requirements
- `benchmark/gold_fsms/<system>.json` — reference FSM
- `benchmark/test_suites/<system>.json` — behavioral tests

See [docs/artifact_policy.md](docs/artifact_policy.md) and [docs/benchmark_specification.md](docs/benchmark_specification.md).

## Manuscript exclusion policy

The EMSE **manuscript is private** and lives **outside** this repository:

```text
~/papers/emse2026/paper/
```

This public repository must **not** contain:

- Manuscript drafts, LaTeX sources, or PDFs
- Submission files or editorial correspondence
- Reviewer materials or private research notes
- Local experiment logs or editor/tooling metadata (`.cursor/`, `.claude/`, `.venv/`, etc.)

Enforced by `.gitignore`, `scripts/audit_public_release.py`, and the [Release Audit](.github/workflows/release-audit.yml) CI workflow. Reporting scripts emit CSV, JSON, and Markdown only — LaTeX tables and publication figures belong in the private writing repository. See [docs/public_private_boundary.md](docs/public_private_boundary.md).

## Relationship to FSM-Bench-20 (IST 2026)

| IST 2026 (structural) | This study (behavioral extension) |
|-----------------------|-----------------------------------|
| G1 JSON, G2 schema, G3 guard-blind determinism | Guard-aware determinism (G3a) + behavioral oracles |
| Requirement citation coverage as proxy | Test-suite agreement + gold reference conformance |
| Single-run descriptive campaign (140 runs) | Multi-run reproducibility + perturbation robustness (planned) |
| Placeholder gold FSMs | Tiered human-approved reference FSMs |
| Zenodo DOI [10.5281/zenodo.20516296](https://doi.org/10.5281/zenodo.20516296) | Upstream import via `benchmark/datasets/upstream_manifest.json` |

## Governance

| Policy | Document |
|--------|----------|
| Study design | [docs/study_design.md](docs/study_design.md) |
| Benchmark specification | [docs/benchmark_specification.md](docs/benchmark_specification.md) |
| Evaluation protocol | [docs/evaluation_protocol.md](docs/evaluation_protocol.md) |
| Artifact policy | [docs/artifact_policy.md](docs/artifact_policy.md) |
| Repository hygiene | [docs/repository_hygiene.md](docs/repository_hygiene.md) |
| Public / private boundary | [docs/public_private_boundary.md](docs/public_private_boundary.md) |
| Release policy | [docs/release_policy.md](docs/release_policy.md) |
| Reproducibility | [REPRODUCIBILITY.md](REPRODUCIBILITY.md) |
| Changelog | [CHANGELOG.md](CHANGELOG.md) |
| Contributing | [CONTRIBUTING.md](CONTRIBUTING.md) |

## License and citation

MIT — see [LICENSE](LICENSE). Citation metadata: [CITATION.cff](CITATION.cff).
