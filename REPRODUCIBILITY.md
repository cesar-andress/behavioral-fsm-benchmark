# Reproducibility Guide — behavioral-fsm-benchmark

End-to-end replication of the EMSE empirical study using **local Ollama inference** (no paid APIs required for the primary campaign).

> **Status:** Bootstrap — framework skeleton in place; pipeline entry points not yet implemented.

## Overview

| Item | Value |
|------|-------|
| Upstream dataset | FSM-Bench-20 — [10.5281/zenodo.20516296](https://doi.org/10.5281/zenodo.20516296) |
| Import manifest | `benchmark/datasets/upstream_manifest.json` |
| Structural gates | G1–G3 (IST-compatible baseline) |
| Behavioral layers | Oracles, gold conformance, equivalence (planned) |
| Robustness | Requirement perturbations (`benchmark/guards/`) |
| Reproducibility | Multi-run variance (campaign C4) |
| Temperature | 0.0 (primary); variance study uses repeated runs |

## Prerequisites

```bash
python3.11 --version   # or 3.12
ollama --version
```

## Installation

```bash
git clone git@github.com-ucjc:cesar-andress/behavioral-fsm-benchmark.git
cd behavioral-fsm-benchmark
python3.12 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## Dataset import (planned)

```bash
python scripts/import_upstream_dataset.py
```

Imported files land in `benchmark/datasets/systems/` (gitignored).

## Campaign workflow (planned)

| ID | Config | Purpose |
|----|--------|---------|
| C0 | `experiments/configs/TEMPLATE_parity.json` | Structural parity vs IST freeze |
| C1 | `experiments/configs/TEMPLATE_structural.json` | Structural baseline |
| C2 | `experiments/configs/TEMPLATE_behavioral.json` | Behavioral evaluation |
| C3 | `experiments/configs/TEMPLATE_robustness.json` | Perturbation sensitivity |
| C4 | `experiments/configs/TEMPLATE_reproducibility.json` | Multi-run variance |

Outputs: `experiments/runs/` (artifacts), `experiments/logs/` (logs).

## Analysis export

Post-hoc scripts in `analysis/scripts/` export tables and figures for manuscript use (private, outside this repository).

## Archival

Follow [docs/release_policy.md](docs/release_policy.md). Build script: `reproducibility/build_replication_package.sh`.

## Artifact policy

Raw outputs are not committed. See [docs/artifact_policy.md](docs/artifact_policy.md).
