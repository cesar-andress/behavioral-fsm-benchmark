# behavioral-fsm-benchmark

Public **research-software repository** for an Empirical Software Engineering (EMSE) study on LLM-generated finite state machines.

## Public scope

This repository contains:

1. **Evaluation framework** — Python packages for structural validation, behavioral oracles, gold comparison, coverage, and guard-aware checks.
2. **Benchmark artifacts** — JSON schemas, pilot gold FSMs, behavioral test suites, guard definitions, and dataset import manifests.
3. **Study documentation** — pre-registered study design, benchmark specification, evaluation protocol, and reproducibility guides.
4. **Experiment infrastructure** — campaign templates and manifest schemas (raw run outputs are not committed by default).

## Private manuscript (not in this repository)

The EMSE manuscript is maintained **separately** in a private directory outside this public repository (`~/papers/emse2026/paper`). Draft prose, submission files, reviewer correspondence, and LaTeX build outputs are **not** part of this GitHub project.

Future **Zenodo** releases will archive only:

- reproducible software (framework, scripts, tests),
- benchmark schemas and approved pilot artifacts,
- documentation and replication instructions.

No private draft manuscript files are included in public releases.

## Working title

**Beyond Structural Validity: Evaluating Behavioral Correctness, Robustness, and Reproducibility of LLM-Generated Finite State Machines from Natural-Language Requirements**

## Target journal

**Empirical Software Engineering (EMSE)** — Springer Nature

## Relationship to FSM-Bench-20 (IST 2026)

| IST 2026 (structural) | This study (behavioral extension) |
|-----------------------|-----------------------------------|
| G1 JSON, G2 schema, G3 guard-blind determinism | Guard-aware determinism (G3a) + behavioral oracles |
| Requirement citation coverage as proxy | Test-suite agreement + gold reference conformance |
| Single-run descriptive campaign (140 runs) | Multi-run reproducibility + perturbation robustness |
| Placeholder gold FSMs | Tiered human-approved reference FSMs |
| Zenodo DOI [10.5281/zenodo.20516296](https://doi.org/10.5281/zenodo.20516296) | Upstream import via `benchmark/datasets/upstream_manifest.json` |

## Repository layout

```text
behavioral-fsm-benchmark/
├── benchmark/       schemas, gold_fsms, test_suites, datasets, guards
├── framework/       Python evaluation engine
├── experiments/     configs, manifests, runs/, logs/
├── analysis/        post-hoc scripts, tables/, figures/
├── docs/            study design, protocols, policies
├── reproducibility/ environment, docker, replication scripts
├── releases/        versioned release artifacts
├── scripts/         CLI entry points
└── tests/           unit and integration tests
```

## Governance

| Policy | Document |
|--------|----------|
| Study design | [docs/study_design.md](docs/study_design.md) |
| Benchmark specification | [docs/benchmark_specification.md](docs/benchmark_specification.md) |
| Evaluation protocol | [docs/evaluation_protocol.md](docs/evaluation_protocol.md) |
| Artifact policy | [docs/artifact_policy.md](docs/artifact_policy.md) |
| Release policy | [docs/release_policy.md](docs/release_policy.md) |
| Repository governance | [docs/repository_governance.md](docs/repository_governance.md) |
| Reproducibility | [REPRODUCIBILITY.md](REPRODUCIBILITY.md) |
| Contributing | [CONTRIBUTING.md](CONTRIBUTING.md) |

## Quick start

```bash
cd ~/papers/emse2026/behavioral-fsm-benchmark
python3.12 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
ruff check framework/ tests/ scripts/
```

## Status

Pilot benchmark systems (`vending_machine`, `login_system`) with approved gold FSMs and behavioral test suites. Framework M1–M2 implemented; campaign execution pending.

## License

MIT — see [LICENSE](LICENSE). Citation metadata: [CITATION.cff](CITATION.cff).
