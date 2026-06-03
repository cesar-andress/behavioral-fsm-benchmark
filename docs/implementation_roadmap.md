# Implementation Roadmap — behavioral-fsm-benchmark

**Document ID:** `implementation_roadmap_v1.0`  
**Repository:** `behavioral-fsm-benchmark`  
**Status:** Authoritative milestone plan (pre-campaign)  
**Companion:** `docs/study_design.md`, `docs/benchmark_specification.md`, `docs/evaluation_protocol.md`  
**Date:** 2026-06-03

---

## 1. Overview

This roadmap sequences engineering deliverables from framework validation through release packaging. Milestones **M1–M9** gate EMSE campaign execution and manuscript population.

**Rule:** No inferential EMSE results are published until **M9** completes and **M8** may populate the manuscript only from frozen exports.

---

## 2. Milestones M1–M9

| Milestone | Deliverable | Acceptance gate | Primary artifacts |
|-----------|-------------|-----------------|-------------------|
| **M1** | Framework validation | `pytest` green; G1–G3a validators and simulator self-tested on fixtures | `framework/`, `tests/`, `benchmark/schemas/` |
| **M2** | Gold FSM format | Gold checklist (§8 of benchmark spec) operational; pilot drafts pass L2 self-test | `benchmark/gold_fsms/`, gold authoring guide |
| **M3** | Behavioral test suites | Pilot systems have ≥8 oracles and ≥6 path tests; reference self-test passes | `benchmark/test_suites/` |
| **M4** | Gold comparison metrics | GSS, BTA, transition P/R, RCov, PCov computed and exported per case | `framework/equivalence/`, `framework/coverage/`, evaluation exports |
| **M5** | Robustness experiments | C3 manifest frozen; perturbation deltas (Δ BTA, Δ G3a) computed | `experiments/manifests/C3_*.json`, `perturbation_results.csv` |
| **M6** | LLM generation pipeline | C1–C4 generation scripts reproducible from manifests; no evaluator coupling | `experiments/configs/`, generation scripts, run logs |
| **M7** | Analysis scripts | Pre-registered tests and descriptive tables/figures exported | `analysis/scripts/`, `analysis/exports/` |
| **M8** | Paper population | §6–§9 populated from frozen exports only; abstract Results/Conclusions updated | `paper/sections/06_results.tex` … `09_conclusion.tex` |
| **M9** | Release package | Checkpoint **CP-080**; Zenodo dry-run checksum audit; replication bundle | `reproducibility/`, release manifest, tagged version |

---

## 3. Phase detail by milestone

### M1 — Framework validation

**Objective:** Confirm the offline evaluator is correct before benchmark authoring at scale.

| Task | Output |
|------|--------|
| Schema validation against JSON Schema drafts | `framework/validators/schema_validator.py` |
| FSM structural gates G1, G2, G3, G3a | `framework/validators/fsm_validator.py`, `framework/guards/` |
| Behavioral simulator and oracle runner | `framework/behavioral/` |
| CLI entry points smoke-tested | `scripts/evaluate_case.py`, etc. |
| Unit and integration tests | `tests/test_framework.py`, `tests/test_smoke.py` |

**Exit criteria:** `pytest tests/ -q` passes; fixture cases produce deterministic evaluation reports.

**Status:** Core framework v1 implemented; re-validate after each schema or metric change.

---

### M2 — Gold FSM format

**Objective:** Define and populate human-approved reference FSMs with traceability and guard DSL.

| Task | Output |
|------|--------|
| Import 20 requirement specs from FSM-Bench-20 | `benchmark/datasets/systems/*.json` |
| Author pilot gold FSMs (3 systems) | `benchmark/gold_fsms/pilot/` |
| Scale to 12 core + 8 stretch | `benchmark/gold_fsms/core/`, `stretch/` |
| Peer review and `metadata.status = approved` | Gold acceptance checklist (benchmark spec §8) |

**Exit criteria:** Pilot gold passes L2 self-test; core tier complete before C2 behavioral campaign.

---

### M3 — Behavioral test suites

**Objective:** Executable oracles that operationalise requirements independently of gold structure.

| Task | Output |
|------|--------|
| Oracle tests (state/event sequences + expected outcomes) | Per-system `test_suites/*.json` |
| Path and forbidden-transition tests | Coverage of happy paths and invariant violations |
| Reference self-test (gold FSM must pass own suite) | CI gate before `approved` status |

**Exit criteria:** Pilot suites pass on gold; core suites complete before M5/C2 freeze.

---

### M4 — Gold comparison metrics

**Objective:** Implement and validate construct-valid similarity and coverage metrics.

| Task | Output |
|------|--------|
| Gold structural similarity (GSS), state/event overlap | `framework/equivalence/` |
| Behavioral test-suite agreement (BTA) | `framework/behavioral/test_runner.py` |
| Transition precision/recall vs gold | Equivalence module |
| Requirement and path coverage (RCov, PCov) | `framework/coverage/` |
| C0 parity spot-check vs IST cached outputs | Parity report (G1–G3) |

**Exit criteria:** Metrics reproducible on fixtures; evaluation report schema validated.

---

### M5 — Robustness experiments

**Objective:** Execute C3 perturbation campaign and compute score deltas.

| Task | Output |
|------|--------|
| Define perturbation types (omission, paraphrase, constraint shift) | `experiments/configs/perturbations/` |
| Freeze C3 manifest (models × systems × perturbations) | `experiments/manifests/C3_*.json` |
| Run generation + evaluation (offline analysis only) | `perturbation_results.csv` |

**Exit criteria:** Δ BTA, Δ G3a, Δ GSS exported per (system, model, perturbation type).

---

### M6 — LLM generation pipeline

**Objective:** Reproducible local-LLM generation decoupled from evaluation.

| Task | Output |
|------|--------|
| Ollama (or equivalent) invocation from frozen prompts | Generation scripts |
| Campaign manifests C1 (structural), C2 (behavioral), C4 (reproducibility) | `experiments/manifests/` |
| Run logging with prompt/model/seed hashes | `experiments/logs/` (gitignored until freeze) |

**Exit criteria:** Re-run from manifest reproduces candidate FSM set within documented LLM non-determinism bounds.

**Note:** LLM experiments are **not** executed during study-design phase; pipeline is implemented and dry-run only until campaign authorization.

---

### M7 — Analysis scripts

**Objective:** Pre-registered statistical and descriptive analysis on frozen CSV/JSON exports.

| Task | Output |
|------|--------|
| RQ1–RQ7 analysis notebooks/scripts | `analysis/scripts/` |
| Hypothesis tests H1–H6 per evaluation protocol §8 | Analysis log |
| Tables and figures (no fabricated cells) | `analysis/exports/`, `paper/tables/` |

**Exit criteria:** Analysis reproducible from exports + manifest pins alone.

---

### M8 — Paper population

**Objective:** Populate manuscript from M7 exports after results freeze gate.

| Task | Output |
|------|--------|
| §6 Results subsections per RQ | `paper/sections/06_results.tex` |
| §7 Discussion and §9 Conclusion | Updated prose |
| Abstract Results/Conclusions replace freeze placeholder | `paper/main.tex` |

**Exit criteria:** No numeric claims without corresponding export file; build via `paper/compile.sh`.

---

### M9 — Release package

**Objective:** Public replication bundle aligned with EMSE data/code availability policy.

| Task | Output |
|------|--------|
| Freeze results bundle and checksum manifest | `reproducibility/` |
| Zenodo dry-run upload | DOI candidate |
| Tag release; update README and governance docs | `releases/` |

**Exit criteria:** Independent replicator can reproduce tables from bundle using documented commands.

---

## 4. Dependencies

```
M1 ──► M2 ──► M3 ──► M4 ──► M5
                  └──────────► M6 (parallel after M3)
M5 + M6 ──► M7 ──► M8 ──► M9
```

| Blocker | Blocks |
|---------|--------|
| M1 failing tests | M2–M9 |
| Incomplete core gold (M2) | C2, M5 |
| Missing test suites (M3) | C2, M4 behavioral endpoints |
| Unfrozen C3 manifest (M5) | RQ4–RQ5 analysis |
| Unfrozen exports (M7) | M8 |

---

## 5. Checkpoint alignment

| Checkpoint | Milestone | Description |
|------------|-----------|-------------|
| CP-010 | M1 + design docs | Study design and protocol frozen |
| CP-040 | M2 + M3 core | Core gold + suites approved |
| CP-060 | M5 + M6 | Campaigns complete |
| CP-080 | M9 | Results freeze + replication package |

Governance detail: `docs/repository_governance.md`, `docs/release_policy.md`.

---

## 6. Version history

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-06-03 | Initial M1–M9 roadmap |

---

*End of implementation roadmap*
