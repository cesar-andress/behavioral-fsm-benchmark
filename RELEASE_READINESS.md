# Release Readiness Audit — v0.1.0

**Repository:** `behavioral-fsm-benchmark`  
**Target release:** `v0.1.0` (2026-06-03)  
**Audit date:** 2026-06-03  
**Auditor scope:** Read-only inspection of repository structure, tracked content, validation tooling, and local worktree hygiene. Benchmark assets were not modified.

---

## Executive summary

| Verdict | Detail |
|---------|--------|
| **Release-ready for v0.1.0 scope** | The evaluation framework, approved gold corpus (12 systems), validation tooling, tests, CI, and release-hygiene checks are in place and passing. |
| **Tracked content clean** | `python scripts/audit_public_release.py` → `release_audit=PASS` (181 tracked files; no manuscript, LaTeX, PDF, or local run outputs in Git). |
| **Local worktree hygiene** | Local experiment outputs and temporary logs exist on disk but are correctly gitignored; they must not be force-added before tagging. |
| **Deferred items** | Zenodo replication ZIP builder, Docker/environment pins, stretch-tier systems, and frozen campaign archival remain out of scope for this tag. |

---

## Release scope

`v0.1.0` is the **first public pre-release** of:

1. The offline Python evaluation framework (structural gates G1–G3a, behavioral oracles, gold comparison, coverage).
2. The **approved gold corpus**: 3 pilot + 9 core systems with requirement specs, reference FSMs, and behavioral test suites.
3. Study documentation, replication instructions, and release-hygiene automation.

**Not in scope for `v0.1.0`:**

- EMSE manuscript sources or submission materials (private repository).
- Frozen LLM campaign result archives (local runs remain gitignored).
- Stretch-tier benchmark systems (8 of 20 upstream systems).
- Zenodo replication package build (script is a placeholder).
- Post-submission `v1.0.0` campaign freeze described in `docs/release_policy.md`.

---

## Included components

### Repository structure

| Path | Status | Notes |
|------|--------|-------|
| `framework/` | ✅ Complete | 28 Python modules: validators, guards, behavioral simulator/runner, equivalence, coverage, evaluation, benchmark loader |
| `benchmark/` | ✅ Complete (v0.1.0 tier) | 12 systems across pilot + core tiers |
| `benchmark/schemas/` | ✅ Complete | 9 JSON Schema files |
| `scripts/` | ✅ Complete | 11 CLI entry points |
| `tests/` | ✅ Complete | 208 tests, 22 test modules |
| `docs/` | ✅ Complete | Study design, benchmark spec, evaluation protocol, artifact/release policies |
| `experiments/configs/` | ✅ Complete | C1 pilot config + 5 campaign templates |
| `experiments/manifests/` | ✅ Partial | Run registry schema only |
| `reproducibility/` | ⚠️ Partial | Guide present; build script and environment pins are placeholders |
| `prompts/` | ✅ Whitelisted | `behavioral_fsm_generation.md` (single tracked generation prompt) |
| `.github/workflows/` | ✅ Complete | `validate.yml`, `release-audit.yml` |

### README

| Check | Status |
|-------|--------|
| Purpose and v0.1.0 scope stated | ✅ |
| Installation (Python 3.11+, editable install) | ✅ |
| Validation commands (`pytest`, `ruff`, gold corpus) | ✅ |
| Manuscript exclusion policy | ✅ |
| Artifact tier table (12 systems) | ✅ |
| Governance links | ✅ |

**Documentation drift (non-blocking):** README states campaign execution is “planned for a later milestone,” but Ollama campaign scripts and configs are already present. `REPRODUCIBILITY.md` lists 6 models / 90 expected runs while `C1_pilot_ollama_behavioral.json` specifies 4 models / 60 runs.

### Benchmark assets

| Asset | Count | Status |
|-------|------:|--------|
| Pilot systems | 3 | `vending_machine`, `login_system`, `atm` |
| Core systems | 9 | All approved in `benchmark/catalog.json` |
| Gold FSMs | 12 | `benchmark/gold_fsms/*.json` |
| Test suites | 12 | 177 tests total (31 negative / rejection-scored) |
| Requirement specs | 12 | Tracked under `benchmark/datasets/systems/` |
| Catalog / index | 2 | `benchmark/catalog.json`, `benchmark/index.json` |
| Upstream pin | 1 | `benchmark/datasets/upstream_manifest.json` → FSM-Bench-20 |

Gold corpus self-evaluation (`python scripts/evaluate_gold_corpus.py`):

```text
systems_total=12
systems_passed=12
all_passed=True
```

Pilot systems report requirement coverage below `1.000` (legacy transition-level traceability); all systems pass schema, G2, G3, G3a, and behavioral self-tests at `bta=1.000`.

### Schemas

All nine schemas under `benchmark/schemas/` parse as valid JSON in CI:

- `candidate_fsm.schema.json`, `generated_fsm.schema.json`, `reference_fsm.schema.json`
- `requirement_spec.schema.json`, `testsuite.schema.json`
- `catalog.schema.json`, `evaluation_report.schema.json`, `evaluation_result.schema.json`
- `experiment_manifest.schema.json`

### Validators

| Module | Gates / role |
|--------|----------------|
| `framework/validators/schema_validator.py` | G1 JSON + G2 schema |
| `framework/validators/fsm_validator.py` | Referential integrity, G3 strict determinism |
| `framework/validators/traceability_validator.py` | Requirement citation coverage |
| `framework/guards/` | G3a guard-aware determinism |

### Simulator and behavioral runner

| Module | Role |
|--------|------|
| `framework/behavioral/simulator.py` | Event-sequence FSM simulation |
| `framework/behavioral/oracle.py` | Oracle / path / negative test evaluation |
| `framework/behavioral/test_runner.py` | Test-suite execution |
| `framework/behavioral/metrics.py` | BPR, agreement, transition diagnostics |
| `framework/equivalence/` | Gold-vs-candidate transition matching |

### Campaign execution

| Component | Status |
|-----------|--------|
| `scripts/run_ollama_campaign.py` | ✅ Implemented with dry-run, limit, resume |
| `scripts/ollama_campaign_lib.py` | ✅ Metrics export, manifest, failure taxonomy |
| `experiments/configs/C1_pilot_ollama_behavioral.json` | ✅ Frozen config (60-run pilot) |
| Campaign outputs (`experiments/runs/`) | Gitignored by default |

Campaign tooling ships with the repository but **campaign results are not part of the v0.1.0 release artifact**. Operators run campaigns locally; outputs stay outside version control until explicitly frozen for a future tag.

### Aggregation utilities

| Script | Role |
|--------|------|
| `scripts/aggregate_campaign_results.py` | Campaign-level CSV summaries + `rq_summary.md` |
| `scripts/generate_paper_results.py` | Paper-ready CSV, LaTeX, figures from summaries (private manuscript pipeline; outputs gitignored via run directories) |

Both scripts have dedicated tests. They consume exported campaign metrics only; the evaluator is unchanged.

### Tests

| Check | Result |
|-------|--------|
| `pytest` | **208 passed** |
| `ruff check framework/ tests/ scripts/` | All checks passed |
| Gold corpus CI step | Passes on clean checkout |
| Release audit test | Passes on repository |
| Parametrized benchmark validation | All 12 systems |

`CHANGELOG.md` cites “172+” tests; the current suite has grown to 208 (campaign aggregation and paper-result generation tests added post-changelog freeze).

### Packaging

| Item | Status |
|------|--------|
| `pyproject.toml` version | `0.1.0` |
| `CITATION.cff` version | `0.1.0` |
| `LICENSE` | MIT |
| Runtime dependencies | `jsonschema`, `pyyaml` |
| Dev dependencies | `pytest`, `ruff`, `matplotlib` |
| Installable package | `framework*` via setuptools |
| Classifier | `Development Status :: 2 - Pre-Alpha` |

### Reproducibility assets

| Asset | Status |
|-------|--------|
| `REPRODUCIBILITY.md` | ✅ Step-by-step replication guide |
| `reproducibility/build_replication_package.sh` | ❌ Placeholder (exits with error) |
| `reproducibility/environment/` | Empty placeholder (`.gitkeep`) |
| `reproducibility/docker/` | Empty placeholder (`.gitkeep`) |
| `reproducibility/CAMPAIGN_SUMMARY.md` | Present (campaign planning notes) |
| CI gold-corpus gate | ✅ Runs on push/PR and tag audit workflow |

---

## Excluded components

The following are **intentionally absent** from the public `v0.1.0` release:

| Category | Location / pattern | Exclusion mechanism |
|----------|-------------------|---------------------|
| Manuscript | `~/papers/emse2026/paper/` (external) | Not in this repository |
| LaTeX sources | `*.tex` | `.gitignore` + release audit |
| PDFs | `*.pdf` | `.gitignore` + release audit |
| Editorial / submission files | N/A in tracked tree | Release audit |
| Reviewer correspondence | N/A in tracked tree | Release audit |
| AI/editor metadata | `.cursor/`, `.claude/`, `AGENTS.md`, etc. | `.gitignore` + release audit |
| Local experiment runs | `experiments/runs/*` | `.gitignore` (only `.gitkeep` tracked) |
| Experiment logs | `experiments/logs/*`, `*.log` | `.gitignore` |
| Evaluation outputs | `results/` | `.gitignore` |
| Replication build output | `reproducibility/build/*` | `.gitignore` |
| Release archives | `releases/*.zip`, `*.tar.gz` | `.gitignore` |
| Imported upstream specs | `benchmark/datasets/systems/*.json` (except 12 approved) | `.gitignore` whitelist |
| Stretch-tier systems | 8 systems not in v0.1.0 corpus | Not yet authored |
| Model weights | `*.gguf`, `*.bin`, `*.safetensors` | `.gitignore` |

---

## Content verification

### Tracked Git index (2026-06-03)

```bash
python scripts/audit_public_release.py
# release_audit=PASS
# tracked_files=181
```

| Forbidden content | Tracked? | Worktree (untracked)? |
|-------------------|----------|------------------------|
| Manuscript files | No | No |
| LaTeX (`.tex`) | No | Only under gitignored `experiments/runs/.../paper_results/` |
| PDFs | No | No (outside gitignored run dirs) |
| Editorial material | No | No |
| Reviewer material | No | No |
| Local experiment artefacts | No (only `.gitkeep`) | Yes — `experiments/runs/C1_pilot_ollama_behavioral/20260603T003118Z/` (gitignored) |
| Temporary outputs | No | Yes — `x.log`, `overnight_C1.log` (gitignored via `*.log`) |

### Tracked study notes (acceptable)

Two read-only audit reports under `experiments/analysis/` reference the local C1 pilot run:

- `C1_replicate_audit.md`
- `C1_negative_test_audit.md`

These are methodology documentation, not manuscript or reviewer material. They cite gitignored run paths and do not embed private editorial content.

---

## Reproducibility status

| Step | Command | Expected | Status |
|------|---------|----------|--------|
| Install | `pip install -e ".[dev]"` | Import succeeds | ✅ |
| Unit tests | `pytest` | 208 passed | ✅ |
| Lint | `ruff check framework/ tests/ scripts/` | Clean | ✅ |
| Release audit | `python scripts/audit_public_release.py` | `PASS` | ✅ |
| Gold corpus | `python scripts/evaluate_gold_corpus.py` | `all_passed=True` | ✅ |
| CI validate workflow | Push/PR on `main` | All steps green | ✅ (configured) |
| Tag release audit | Push tag `v*` | Extended audit + gold corpus | ✅ (configured) |
| Replication ZIP | `reproducibility/build_replication_package.sh` | — | ❌ Not implemented |
| Zenodo DOI | `CITATION.cff` | — | ❌ Not yet assigned |

A clean clone can reproduce **framework validation and gold corpus self-tests** without local experiment data or Ollama.

---

## Known limitations

1. **Pre-Alpha classifier** — PyPI metadata marks development status as Pre-Alpha; appropriate for v0.1.0 but should be revisited before `v1.0.0`.
2. **Partial corpus** — 12 of 20 FSM-Bench-20 systems; stretch tier not included.
3. **Pilot requirement coverage** — Legacy traceability on pilot transitions yields `rcov < 1.000` despite passing behavioral self-tests.
4. **Replication packaging** — `build_replication_package.sh` is a stub; Zenodo archival requires manual curation or future implementation.
5. **Environment pinning** — No committed lock files or Docker images under `reproducibility/environment/` or `reproducibility/docker/`.
6. **Campaign results not archived** — C1 pilot completed locally (60 runs); outputs are gitignored and not bundled in v0.1.0.
7. **Documentation inconsistencies** — README vs. REPRODUCIBILITY.md vs. C1 config on campaign maturity and run counts; `scripts/README.md` omits aggregation scripts; `framework/README.md` milestone notes lag core completion.
8. **jsonschema deprecation** — `RefResolver` deprecation warning in tests (non-blocking).
9. **Paper-result tooling** — `generate_paper_results.py` produces LaTeX/figures for the private manuscript; outputs belong in gitignored run directories, not in public releases.

---

## Release requirements checklist

### Mandatory (v0.1.0 tag)

- [x] Version aligned in `pyproject.toml` and `CITATION.cff` (`0.1.0`)
- [x] `CHANGELOG.md` entry for v0.1.0
- [x] `README.md` describes scope, install, and validation
- [x] `REPRODUCIBILITY.md` with replication commands
- [x] Gold corpus (12 systems) passes self-evaluation
- [x] `pytest` passes (208 tests)
- [x] `ruff check` passes
- [x] `python scripts/audit_public_release.py` passes
- [x] CI workflows present (`validate.yml`, `release-audit.yml`)
- [x] No tracked manuscript, LaTeX, PDF, or local run outputs
- [x] `.gitignore` covers experiments, results, logs, and editor metadata
- [x] `LICENSE` (MIT) and `CITATION.cff` present
- [x] Benchmark schemas valid JSON

### Recommended before public announcement

- [ ] Resolve README / REPRODUCIBILITY.md / C1 config documentation drift (models, run counts, campaign maturity wording)
- [ ] Update `CHANGELOG.md` test count (172+ → 208)
- [ ] Update `scripts/README.md` to list aggregation and paper-result scripts
- [ ] Remove or relocate local log files (`x.log`, `overnight_C1.log`) from working copies used for tagging
- [ ] Confirm `git status` is clean with no force-added run outputs

### Deferred (post–v0.1.0 / v1.0.0)

- [ ] Implement `reproducibility/build_replication_package.sh`
- [ ] Pin Ollama model versions and Python lock files
- [ ] Freeze and optionally publish C1 (or final) campaign metrics snapshot
- [ ] Assign Zenodo DOI and update `CITATION.cff`
- [ ] Complete stretch-tier gold FSMs and test suites (8 systems)
- [ ] GitHub Release notes and tag push (`git tag -a v0.1.0`)
- [ ] Manuscript results export to private `paper/tables/` (per `docs/release_policy.md` v1.0.0 checklist)

---

## Pre-tag command sequence

Run from a clean working tree (no staged experiment outputs):

```bash
pytest
ruff check framework/ tests/ scripts/
python scripts/audit_public_release.py
python scripts/evaluate_gold_corpus.py
git status
```

Expected: all commands succeed; `git status` shows no untracked files that should be committed (ignored local runs and logs are acceptable on disk).

Tag when ready:

```bash
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0
```

The `Release Audit` workflow runs automatically on tag push.

---

## Audit conclusion

**`v0.1.0` is ready to tag** for its declared scope: public release of the behavioral evaluation framework and approved twelve-system gold corpus, with automated hygiene checks and CI validation. Local experiment artefacts and temporary logs present in development working copies are correctly excluded from Git and must remain so.

Items marked deferred do not block the v0.1.0 software-and-corpus release but should be tracked for `v1.0.0` (frozen campaign + manuscript submission snapshot).
