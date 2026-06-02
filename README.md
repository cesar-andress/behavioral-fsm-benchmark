# behavioral-fsm-benchmark

Research artifact and evaluation framework for an **Empirical Software Engineering (EMSE)** study on LLM-generated finite state machines.

## Project scope

This repository provides:

1. **Benchmark artifacts** — datasets, gold reference FSMs, test suites, guard definitions, JSON schemas.
2. **Evaluation framework** — Python packages for structural validation, behavioral oracles, equivalence, coverage, and guard-aware checks.
3. **Experiment infrastructure** — campaign configs, manifests, run registry (no executed campaigns in bootstrap phase).
4. **Manuscript sources** — LaTeX skeleton for the EMSE submission (`paper/`).
5. **Reproducibility packaging** — environment pins, replication scripts, release workflow.

**Out of scope (bootstrap phase):** executed experiments, populated gold FSMs, manuscript prose, published results.

## Working title

**Beyond Structural Validity: Evaluating Behavioral Correctness, Robustness, and Reproducibility of LLM-Generated Finite State Machines from Natural-Language Requirements**

## Target journal

**Empirical Software Engineering (EMSE)** — Springer Nature

## Relationship to FSM-Bench-20 (IST 2026)

| IST 2026 (structural) | This study (behavioral extension) |
|-----------------------|-----------------------------------|
| G1 JSON, G2 schema, G3 guard-blind determinism | Guard-aware determinism + behavioral oracles |
| Requirement citation coverage as proxy | Test-suite agreement + gold reference conformance |
| Single-run descriptive campaign (140 runs) | Multi-run reproducibility + perturbation robustness |
| Placeholder gold FSMs | Tiered human-approved reference FSMs |
| Zenodo DOI [10.5281/zenodo.20516296](https://doi.org/10.5281/zenodo.20516296) | Upstream import via `benchmark/datasets/upstream_manifest.json` |

## Repository layout

```text
behavioral-fsm-benchmark/
├── benchmark/       datasets, gold_fsms, schemas, test_suites, guards
├── framework/       Python evaluation engine
├── experiments/     configs, manifests, runs, logs
├── analysis/        post-hoc scripts, tables, figures
├── paper/           EMSE manuscript (LaTeX skeleton)
├── docs/            study design, protocols, policies
├── reproducibility/ environment, docker, replication scripts
├── releases/        versioned release artifacts
├── scripts/         CLI entry points (planned)
└── tests/           unit and integration tests
```

## Governance

| Policy | Document |
|--------|----------|
| Study design | [docs/study_design.md](docs/study_design.md) |
| Benchmark specification | [docs/benchmark_specification.md](docs/benchmark_specification.md) |
| Evaluation protocol | [docs/evaluation_protocol.md](docs/evaluation_protocol.md) |
| Release policy | [docs/release_policy.md](docs/release_policy.md) |
| Artifact policy | [docs/artifact_policy.md](docs/artifact_policy.md) |
| Repository governance | [docs/repository_governance.md](docs/repository_governance.md) |
| Reproducibility | [REPRODUCIBILITY.md](REPRODUCIBILITY.md) |
| Contributing | [CONTRIBUTING.md](CONTRIBUTING.md) |

**Artifact policy (summary):** Raw model outputs, experiment runs, logs, imported datasets, and LaTeX build artifacts are **gitignored by default**. Only frozen manifests, schemas, approved gold FSMs, and publication exports are committed after review.

## Quick start

```bash
cd ~/papers/emse2026/behavioral-fsm-benchmark
python3.12 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
ruff check framework/ tests/
```

## Status

Bootstrap phase — framework package skeleton and governance docs in place. No experiments or benchmark data yet.

## License

MIT — see [LICENSE](LICENSE). Citation metadata: [CITATION.cff](CITATION.cff).
