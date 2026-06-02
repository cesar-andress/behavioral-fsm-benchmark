# Reproducibility Guide — behavioral-fsm-benchmark

How to reproduce the EMSE empirical study on your machine using **Ollama only** (no paid APIs).

> **Status:** Bootstrap phase — pipeline documented but not yet implemented.

---

## 1. Overview

| Item | Value |
|------|-------|
| Project | behavioral-fsm-benchmark |
| Upstream dataset | FSM-Bench-20 — [10.5281/zenodo.20516296](https://doi.org/10.5281/zenodo.20516296) |
| Evaluation pillars | Structural (G1–G3), behavioral, robustness, reproducibility |
| Primary inference | Ollama local API, temperature 0.0 |
| Hardware | NVIDIA RTX 4090 or equivalent (24 GB VRAM) recommended |

---

## 2. Prerequisites

```bash
python3.12 --version
ollama --version
ollama serve   # separate terminal if needed
```

---

## 3. Installation

```bash
git clone git@github.com-ucjc:cesar-andress/behavioral-fsm-benchmark.git
cd behavioral-fsm-benchmark
python3.12 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

---

## 4. Dataset import

Upstream manifest: `benchmark/datasets/upstream_manifest.json`

```bash
# Planned:
python scripts/import_upstream_dataset.py
```

Imported requirement JSON files are gitignored; regenerate from Zenodo.

---

## 5. Campaign execution (planned)

| Campaign | Config | Purpose |
|----------|--------|---------|
| C0 | `experiments/configs/TEMPLATE_parity.json` | Structural parity spot-check vs IST freeze |
| C1 | `experiments/configs/TEMPLATE_structural.json` | Structural baseline |
| C2 | `experiments/configs/TEMPLATE_behavioral.json` | Behavioral evaluation |
| C3 | `experiments/configs/TEMPLATE_robustness.json` | Perturbation sensitivity |
| C4 | `experiments/configs/TEMPLATE_reproducibility.json` | Multi-run variance |

Runs write to `experiments/runs/`; logs to `experiments/logs/`.

---

## 6. Analysis and paper tables

Post-hoc analysis scripts live in `analysis/scripts/`. Publication LaTeX tables are exported to `paper/tables/`.

---

## 7. Docker (optional)

See `reproducibility/docker/` when available.

---

## 8. Archival

Release packaging follows [docs/release_policy.md](docs/release_policy.md). Build script: `reproducibility/build_replication_package.sh`.
