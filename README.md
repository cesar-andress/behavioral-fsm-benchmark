# behavioral-fsm-benchmark

Research artifact and manuscript workspace for an empirical software engineering study on LLM-generated finite state machines.

## Working title

**Beyond Structural Validity: Evaluating Behavioral Correctness, Robustness, and Reproducibility of LLM-Generated Finite State Machines from Natural-Language Requirements**

## Target journal

**Empirical Software Engineering (EMSE)** — Springer Nature

## Relationship to prior work

This project extends the **IST 2026 FSM-Bench-20** study ([DOI 10.5281/zenodo.20516296](https://doi.org/10.5281/zenodo.20516296)) by moving beyond JSON/schema/determinism gates toward:

- **Behavioral correctness** — trace execution against approved gold reference FSMs
- **Guard semantics** — structured guard DSL and context-aware transition evaluation
- **Gold reference FSMs** — human-authored, reviewer-approved reference models
- **Test-suite agreement** — oracle pass rates, path coverage, and equivalence metrics
- **Robustness** — sensitivity to requirement perturbations
- **Reproducibility** — multi-run variance and metric stability

## Repository layout

```text
behavioral-fsm-benchmark/
├── benchmark/          # Datasets, gold FSMs, schemas, test suites, guards
├── experiments/        # Campaign configs, manifests, runs, logs
├── framework/          # Evaluation engine (behavioral, validators, equivalence, …)
├── analysis/           # Post-hoc analysis, notebooks, publication tables/figures
├── paper/              # EMSE manuscript (LaTeX)
├── reproducibility/    # Environment, Docker, replication scripts
├── docs/               # Study design, benchmark spec, protocols, release policy
├── releases/           # Versioned release artifacts
├── scripts/            # CLI entry points
└── tests/              # Unit and integration tests
```

## Status

**Bootstrap phase** — normalized project structure (2026-06-03). No experiments, benchmark data, or manuscript content implemented yet.

## Quick start

```bash
cd ~/papers/emse2026/behavioral-fsm-benchmark
python3.12 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

See [REPRODUCIBILITY.md](REPRODUCIBILITY.md) for the full replication protocol (pending implementation).

## Key documents

| Document | Path |
|----------|------|
| Study design | [docs/study_design.md](docs/study_design.md) |
| Benchmark specification | [docs/benchmark_specification.md](docs/benchmark_specification.md) |
| Evaluation protocol | [docs/evaluation_protocol.md](docs/evaluation_protocol.md) |
| Release policy | [docs/release_policy.md](docs/release_policy.md) |

## License

MIT — see [LICENSE](LICENSE).

## Citation

See [CITATION.cff](CITATION.cff).
