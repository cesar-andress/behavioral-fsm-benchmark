# Changelog

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2026-06-03

Documentation patch aligning public repository terminology with the EMSE manuscript and frozen C1/C2 campaign records. **No evaluator logic, metrics, or campaign output changes.**

### Added

- [docs/scoring_strata_and_campaign_freeze.md](docs/scoring_strata_and_campaign_freeze.md) — authoritative definitions for:
  - scoring strata (behaviorally scored **n=209**; G2-pass behaviorally scored **n=189**);
  - **G2** = `schema_valid` ∧ `referential_valid`;
  - schema failure as behavioral hard stop vs `referential_valid=false` oracle-on-parsed-object scores;
  - **G3** and **G3a** as parallel post-G2 determinism checks;
  - approved gold FSM authorship and checklist workflow;
  - frozen C1/C2 run directories (`20260603T003118Z`, `20260603T080817Z`; N=240).

### Changed

- [README.md](README.md) — v0.1.1 release note, scoring strata summary, IST comparison table, governance link.
- [REPRODUCIBILITY.md](REPRODUCIBILITY.md) — scoring strata section, frozen C1/C2 paths, C2 replication notes, referential-invalid scoring clarification, corrected C1 run count (60).
- [docs/evaluation_protocol.md](docs/evaluation_protocol.md) — v0.1.1 alignment addendum (terminology only).
- [benchmark/gold_fsms/README.md](benchmark/gold_fsms/README.md) — pointer to gold approval workflow.
- [experiments/analysis/C1_C2_evaluable_stratum_audit.md](experiments/analysis/C1_C2_evaluable_stratum_audit.md) — cross-reference to scoring strata doc.
- [CITATION.cff](CITATION.cff) — version `0.1.1`.

### Unchanged

- Python evaluation framework (`framework/`, `scripts/`).
- JSON schemas, gold corpus artefacts, campaign configs.
- Frozen `metrics.csv` values and local run directories.

## [0.1.0] - 2026-06-03

First public release of the behavioral FSM evaluation framework and approved gold corpus.

**Zenodo:** [10.5281/zenodo.20522834](https://doi.org/10.5281/zenodo.20522834)

### Added

**Framework**

- Python evaluation engine under `framework/`: structural gates (G1–G3), guard-aware determinism (G3a), behavioral simulator, oracle and test-suite runner, gold comparison, transition diagnostics, and coverage metrics.
- Nine JSON Schema files under `benchmark/schemas/` for generated, reference, requirement, test-suite, catalog, and evaluation artifacts.
- End-to-end single-case evaluation pipeline (`framework/evaluation.py`).

**Benchmark**

- Three pilot systems with approved gold FSMs, requirement specs, and behavioral test suites: `vending_machine`, `login_system`, `atm`.
- Nine core systems: `parking_gate`, `access_control`, `bike_rental`, `warehouse_inventory`, `smart_thermostat`, `elevator`, `hotel_booking`, `train_ticket_booking`, `package_locker`.
- Benchmark catalog and system index (`benchmark/catalog.json`, `benchmark/index.json`).
- Upstream dataset pin to FSM-Bench-20 (`benchmark/datasets/upstream_manifest.json`).
- 177 behavioral tests across twelve test suites (oracle, path, and negative cases).

**CLI scripts**

- `validate_fsm.py` — schema, structural, and determinism validation.
- `run_behavioral_tests.py` — behavioral test-suite execution.
- `compare_to_gold.py` — gold reference comparison.
- `evaluate_case.py` — single-candidate end-to-end evaluation.
- `evaluate_gold_corpus.py` — corpus-level gold self-test and coverage reporting.
- `run_ollama_campaign.py` and `ollama_campaign_lib.py` — local Ollama FSM generation and evaluation campaigns with dry-run, resume, and failure recording.
- `aggregate_campaign_results.py` — campaign summary CSV and RQ-oriented markdown export.
- `generate_campaign_reports.py` — repository-neutral CSV, JSON, and Markdown export from campaign summaries.
- `audit_public_release.py` — tracked-content hygiene audit.

**Campaign configuration**

- C1 pilot config (`experiments/configs/C1_pilot_ollama_behavioral.json`) and five campaign templates under `experiments/configs/TEMPLATE_*.json`.
- Frozen generation prompt (`prompts/behavioral_fsm_generation.md`).

**Documentation**

- Study design, benchmark specification, evaluation protocol, artifact policy, release policy, and repository governance under `docs/`.
- `REPRODUCIBILITY.md` replication guide.
- `docs/repository_hygiene.md` public-release exclusion checklist.
- `RELEASE_READINESS.md` pre-tag audit report.
- Methodology audit notes for C1 pilot replicate stability and negative-test coverage (`experiments/analysis/`).

**Tooling and packaging**

- Editable install via `pyproject.toml` (Python 3.11+, runtime deps: `jsonschema`, `pyyaml`).
- Citation metadata (`CITATION.cff`, MIT `LICENSE`).
- CI workflows: `validate.yml` (push/PR) and `release-audit.yml` (version tags).

### Validation

- **208** pytest unit and integration tests across validators, simulator, coverage, benchmark loading, campaign utilities, and gold self-tests.
- `ruff check framework/ tests/ scripts/` passes on the release tree.
- `python scripts/audit_public_release.py` → `release_audit=PASS` (183 tracked files; no LaTeX, PDF, or local run outputs in Git).
- `python scripts/evaluate_gold_corpus.py` → `systems_total=12`, `systems_passed=12`, `all_passed=True`; behavioral pass rate `1.000` for every system.
- Parametrized benchmark validation for all twelve pilot and core systems.
- CI runs schema JSON checks, lint, tests, release audit, and gold corpus evaluation on every push to `main`.

### Reproducibility

- Step-by-step environment setup and validation commands in `REPRODUCIBILITY.md`.
- Gold corpus evaluation regenerates local reports under `results/gold_corpus/` (gitignored).
- Campaign outputs under `experiments/runs/` and `experiments/logs/` excluded from version control by default; only `.gitkeep` placeholders tracked.
- `.gitignore` and `docs/repository_hygiene.md` document exclusions for Python caches, virtual environments, editor metadata, temporary outputs, generated reports, and local PDFs.
- `reproducibility/build_replication_package.sh` stub present for future archival packaging.

### Known limitations

- **Corpus scope:** twelve of twenty FSM-Bench-20 systems; stretch tier not included.
- **Pilot requirement coverage:** legacy transition-level traceability yields requirement coverage below `1.000` on pilot systems despite passing behavioral self-tests.
- **Campaign archival:** Ollama campaign tooling and configs ship with the release, but timestamped run directories remain local and gitignored; no frozen campaign metrics bundle is included in this tag.
- **Replication packaging:** Zenodo ZIP builder and environment/Docker pins are placeholders (`reproducibility/environment/`, `reproducibility/docker/`).
- **PyPI classifier:** `Development Status :: 2 - Pre-Alpha`.
- **Dependency warning:** `jsonschema.RefResolver` deprecation notice during tests (non-blocking).

[0.1.1]: https://github.com/cesar-andress/behavioral-fsm-benchmark/releases/tag/v0.1.1

[0.1.0]: https://github.com/cesar-andress/behavioral-fsm-benchmark/releases/tag/v0.1.0

[0.1.0 Zenodo]: https://doi.org/10.5281/zenodo.20522834
