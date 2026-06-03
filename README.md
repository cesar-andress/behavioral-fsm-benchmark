# behavioral-fsm-benchmark

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20522834.svg)](https://doi.org/10.5281/zenodo.20522834)

Public **research-software repository** for an Empirical Software Engineering (EMSE) study on LLM-generated finite state machines.

**Release:** [`v0.1.1`](https://github.com/cesar-andress/behavioral-fsm-benchmark/releases/tag/v0.1.1) (2026-06-03) — documentation patch aligning terminology with the EMSE manuscript and frozen C1/C2 campaign records. Evaluator logic and metrics unchanged from [`v0.1.0`](https://github.com/cesar-andress/behavioral-fsm-benchmark/releases/tag/v0.1.0), archived on Zenodo as [10.5281/zenodo.20522834](https://doi.org/10.5281/zenodo.20522834).

## Purpose

This repository provides:

1. A **Python evaluation framework** for structural gates (G1–G2), post-G2 determinism checks (G3, G3a), behavioral oracles, gold comparison, and coverage metrics.
2. A **tiered behavioral benchmark** extending [FSM-Bench-20](https://doi.org/10.5281/zenodo.20516296) with human-approved gold FSMs and behavioral test suites.
3. **Study documentation** (design, benchmark specification, evaluation protocol, **scoring strata**) and replication instructions.
4. **Release hygiene** tooling to keep the public repository free of local experiment outputs and non-public content.

`v0.1.0` freezes the evaluation stack and approved gold corpus. **Frozen C1/C2 Ollama campaign exports** (N=240) are documented in [docs/scoring_strata_and_campaign_freeze.md](docs/scoring_strata_and_campaign_freeze.md); timestamped run directories remain local and gitignored.

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

## Scoring strata and frozen campaigns (v0.1.1)

Manuscript-aligned definitions for the combined **C1+C2** campaign (**N=240**):

| Stratum | Count |
|---------|------:|
| Behaviorally scored (`behavioral_pass_rate` non-null) | 209 |
| G2-pass behaviorally scored (`schema_valid` ∧ `referential_valid`, non-null BPR) | 189 |
| Behaviorally non-scored (schema/parsing hard stop) | 31 |

- **G2 pass** = `schema_valid` **and** `referential_valid`.
- **Schema failure** stops behavioral scoring; **`referential_valid=false` may still receive oracle scores** on the parsed object (20 runs in the frozen exports).
- **G3** (strict `(s,e)` determinism) and **G3a** (guard-aware determinism) are **post-G2 checks in parallel**, not sequential gates.

Frozen run records, gold approval workflow, and RQ4 descriptive notes: [docs/scoring_strata_and_campaign_freeze.md](docs/scoring_strata_and_campaign_freeze.md).

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
| G1 JSON, G2 schema + referential, G3 strict determinism | Post-G2 G3/G3a (parallel) + behavioral oracles |
| Requirement citation coverage as proxy | Test-suite agreement + gold reference conformance |
| Single-run descriptive campaign (140 runs) | Frozen C1+C2 descriptive campaign (240 runs; five replicates per cell) |
| Placeholder gold FSMs | Human-approved reference FSMs + paired suites |
| Zenodo DOI [10.5281/zenodo.20516296](https://doi.org/10.5281/zenodo.20516296) | Upstream import via `benchmark/datasets/upstream_manifest.json` |

## Governance

| Policy | Document |
|--------|----------|
| Study design | [docs/study_design.md](docs/study_design.md) |
| Scoring strata and frozen C1/C2 | [docs/scoring_strata_and_campaign_freeze.md](docs/scoring_strata_and_campaign_freeze.md) |
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

MIT — see [LICENSE](LICENSE).

**Zenodo archive (v0.1.0):** [10.5281/zenodo.20522834](https://doi.org/10.5281/zenodo.20522834)

Citation metadata and software record fields: [CITATION.cff](CITATION.cff).

```bibtex
@software{behavioral_fsm_bench_2026,
  author       = {Andr{\'e}s, C{\'e}sar},
  title        = {behavioral-fsm-benchmark: Behavioral Evaluation of LLM-Generated FSMs},
  version      = {0.1.0},
  date         = {2026-06-03},
  doi          = {10.5281/zenodo.20522834},
  url          = {https://github.com/cesar-andress/behavioral-fsm-benchmark}
}
```
