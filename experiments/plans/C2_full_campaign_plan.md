# C2 Full Campaign Plan — Behavioral Evaluation (EMSE Primary Dataset)

**Campaign ID:** `C2_core_ollama_behavioral`  
**Config:** `experiments/configs/C2_core_ollama_behavioral.json`  
**Document date:** 2026-06-03  
**Status:** Config frozen; execution not started  
**Benchmark release:** v0.1.0 — [10.5281/zenodo.20522834](https://doi.org/10.5281/zenodo.20522834)  
**Prior campaign:** C1 pilot (`C1_pilot_ollama_behavioral`, 60 runs, frozen locally)

---

## 1. Purpose

C2 is the **first full-scale behavioral generation campaign** on the approved v0.1.0 gold corpus. It is intended to become the **primary empirical dataset** for the EMSE study: structural funnel (RQ1), behavioral correctness and agreement (RQ2–RQ3), cross-run dispersion (RQ4), and system difficulty (RQ5).

C1 validated the Ollama pipeline on three pilot systems. C2 extends coverage to **all twelve approved systems** while preserving C1-compatible inference settings for comparability and reproducibility.

**This document describes the C2 design.** Campaign configuration is frozen at `experiments/configs/C2_core_ollama_behavioral.json` (180 runs). Full campaign execution is not implied by this plan alone.

---

## 2. Benchmark system audit (v0.1.0)

Read-only audit of approved gold FSMs, requirement specs, and behavioral test suites under `benchmark/`. Counts derived from tracked JSON artefacts (2026-06-03).

| system_id | tier | states | transitions | guards | requirements | tests | negative tests |
|-----------|------|-------:|------------:|-------:|-------------:|------:|---------------:|
| vending_machine | pilot | 3 | 3 | 0 | 6 | 6 | 3 |
| login_system | pilot | 3 | 4 | 0 | 6 | 6 | 3 |
| atm | pilot | 4 | 6 | 0 | 8 | 16 | 3 |
| parking_gate | core | 4 | 4 | 0 | 8 | 17 | 3 |
| access_control | core | 2 | 2 | 1 | 8 | 18 | 6 |
| bike_rental | core | 4 | 5 | 0 | 8 | 17 | 2 |
| warehouse_inventory | core | 4 | 5 | 0 | 8 | 16 | 2 |
| smart_thermostat | core | 3 | 6 | 0 | 8 | 16 | 2 |
| elevator | core | 4 | 4 | 0 | 8 | 16 | 2 |
| hotel_booking | core | 4 | 5 | 0 | 8 | 16 | 2 |
| train_ticket_booking | core | 4 | 5 | 0 | 8 | 16 | 2 |
| package_locker | core | 4 | 4 | 1 | 8 | 17 | 4 |
| **Totals** | | **43** | **53** | **2** | **92** | **177** | **34** |

### Count definitions

| Metric | Definition |
|--------|------------|
| **states** | Length of `states[]` in the gold FSM |
| **transitions** | Length of `transitions[]` in the gold FSM |
| **guards** | Transitions with non-empty `guard` string (`access_control`, `package_locker` only in v0.1.0) |
| **requirements** | Length of `requirements[]` in the requirement spec |
| **tests** | Length of `tests[]` in the behavioral test suite |
| **negative tests** | Tests with `kind == "negative"` **plus** path tests with `expected_final_state == null` (rejection-scored set used by `rejected_event_agreement`; corpus total **34**, of which **31** are strict `negative` kind) |

### Audit observations

- **Corpus size:** 12 systems (3 pilot + 9 core); stretch tier empty in v0.1.0.
- **Complexity spread:** `login_system` and `vending_machine` are smallest (6 tests, 6 requirements); `access_control` has the richest rejection coverage (6 rejection-scored tests).
- **Guard coverage:** Only two guarded transitions in the entire corpus — G3a discrimination will rely primarily on these two systems unless candidates introduce spurious guards elsewhere.
- **Negative-test density:** Pilot systems skew high (50% negative/rejection-scored on `login_system` and `vending_machine`); six core systems have only **2** strict negative tests each (12.5% of suite).
- **C1 overlap:** Pilot trio (`vending_machine`, `login_system`, `atm`) already has a frozen 60-run C1 matrix; C2 should **reuse** those runs rather than regenerate them.

---

## 3. Recommended campaign design

### 3.1 Systems — include all twelve

| Decision | Rationale |
|----------|-----------|
| **Include all 12 approved systems** | Only evaluable corpus in v0.1.0; required for system-level RQ5 and cross-domain coverage |
| **Reuse C1 pilot runs** | Avoid duplicate cost for 12 model×system cells already executed; merge by timestamp directory |
| **No stretch-tier systems** | Not present in v0.1.0; defer until gold + suites exist |

**New generation required:** 9 core systems × 4 models × 5 replicates = **180 runs**  
**Reused from C1:** 3 pilot systems × 4 models × 5 replicates = **60 runs**  
**Combined primary dataset:** **240 runs**

### 3.2 Models — four local Ollama tags (C1-validated)

| Model | Role in C2 |
|-------|------------|
| `qwen2.5-coder:7b` | Code-specialised baseline (C1) |
| `llama3.1:8b` | General-purpose baseline (C1) |
| `mistral-nemo:12b` | Mid-size instruct model (C1) |
| `gemma2:9b` | Compact instruct model (C1) |

**Recommendation:** Keep the **same four models** as C1 for continuity, overnight feasibility, and direct pilot-to-full comparison. Expanding to six models (as sketched in early replication notes) would add **+120 runs** (12×2×5) and is **deferred** to a follow-up campaign unless hardware budget allows a second wave.

### 3.3 Replicates — five per (model, system) cell

| Factor | Value | Rationale |
|--------|------:|-----------|
| Replicates (K) | **5** | Matches C1; supports RQ4 dispersion estimates with K≥3; C1 audit showed BPR variance often collapses to 0 but raw/candidate drift still varies |
| Temperature | **0.0** | Fixed across C1 and C2 for reproducibility |
| Structured JSON | **enabled** | Same as C1 |

Alternative considered: **K = 3** (144 new runs) for a single overnight — rejected as primary plan because it weakens RQ4 and diverges from the validated C1 protocol.

### 3.4 Estimated run budget

| Scenario | Systems | Models | K | New runs | + C1 reuse | Total dataset |
|----------|--------:|-------:|--:|---------:|-----------:|--------------:|
| **Recommended (C2 primary)** | 12 | 4 | 5 | 180 | 60 | **240** |
| Reduced replicate (not primary) | 12 | 4 | 3 | 108 | 60 | 168 |
| Expanded models (deferred) | 12 | 6 | 5 | 360 | 0* | 360 |

\*Expanded-model scenario would rerun pilots unless C1 merge rules are applied.

### 3.5 Overnight execution feasibility

C1 pilot: **60 runs** completed in one overnight session (4 models × 3 systems × 5 replicates).

Scaling assumptions (conservative):

| Metric | Estimate |
|--------|----------|
| Mean wall time per run (C1 experience) | ~6–10 min (generation + evaluation; `timeout_seconds=600`) |
| **180 new runs** | ~18–30 h wall time sequential |
| Suggested execution | **2–3 overnight sessions** with `--run-dir` resume, or **2 nights** if splitting by core batch (5 systems + 4 systems) |
| Failure tolerance | Campaign runner records failures; no auto-retry (same as C1) |

**Balancing trade-off:** 240 total runs fits **two to three local overnights** with resume — large enough for descriptive RQ1–RQ5 tables per model and system, without the cost of a six-model or K=10 design.

---

## 4. Inference and protocol (inherit from C1)

Frozen config: `experiments/configs/C2_core_ollama_behavioral.json` (mirrors C1 unless a protocol version bump is documented):

| Parameter | C1 value | C2 recommendation |
|-----------|----------|-------------------|
| Backend | Ollama | Ollama |
| Temperature | 0.0 | 0.0 |
| `num_ctx` | 8192 | 8192 |
| `timeout_seconds` | 600 | 600 |
| Prompt | `prompts/behavioral_fsm_generation.md` | Unchanged |
| Repair loop | off | off |
| Post-processing | JSON extraction + validation only | unchanged |

Output layout (unchanged):

```text
experiments/runs/C2_core_ollama_behavioral/<timestamp>/
  manifest.json
  metrics.csv
  summary/              # via aggregate_campaign_results.py
  campaign_reports/     # via generate_campaign_reports.py
```

---

## 5. Statistical and reproducibility considerations

| Goal | C2 design choice |
|------|------------------|
| **RQ1 structural funnel** | 240 runs → stable G1–G3a rate estimates; compare G2 pass vs mean BPR |
| **RQ2–RQ3 behavioral** | 12 systems × 4 models → 48 model×system cells; all cells ≥5 evaluable replicates target |
| **RQ4 robustness / dispersion** | K=5 replicates per cell; report std/min/max BPR and replicate variance |
| **RQ5 system difficulty** | 12 system strata with unequal non-evaluable rates expected (C1: parsing failures on `atm` for some models) |
| **Reproducibility** | Pin Ollama model digests in manifest `environment`; record git commit of benchmark repo at campaign start |
| **C1 merge** | Document C1 timestamp (`20260603T003118Z`) in C2 manifest `notes` and combined analysis registry |

Minimum cell sizes after merge:

- **48** distinct model×system cells (12×4)
- **5** replicates per cell when C1+C2 complete
- Expect **non-evaluable cells** (parsing/schema failures); report rates separately — do not impute BPR=0

---

## 6. Execution phases (planned, not scheduled)

| Phase | Scope | Runs | Dependency |
|-------|-------|-----:|------------|
| **P0** | Config frozen at `experiments/configs/C2_core_ollama_behavioral.json` | 0 | Done |
| **P1** | Register C1 pilot runs in combined analysis manifest | 0 | C1 frozen |
| **P2** | Generate core systems only (9×4×5) | 180 | Ollama models pulled |
| **P3** | Aggregate + `campaign_reports` on merged 240-run registry | 0 | P1 + P2 |
| **P4** | Optional spot-check: 10% manual raw/candidate audit | 0 | P3 |

---

## 7. Risks and mitigations

| Risk | Mitigation |
|------|------------|
| Overnight overrun (>30 h for 180 runs) | Resume support; split P2 into two batches by system list |
| Model pull / Ollama drift | Record model IDs in manifest; pin versions in `reproducibility/environment/` before execution |
| Low evaluable rate on complex systems (`atm`) | Already observed in C1; report non-evaluable rate explicitly in RQ5 |
| Duplicate pilot work | Merge C1 metrics; do not rerun pilot cells |
| Weak guard corpus (2 guarded transitions) | Report G3 vs G3a gap honestly; do not over-claim guard-aware findings |

---

## 8. Deliverables after execution (future)

| Artefact | Location |
|----------|----------|
| Frozen config | `experiments/configs/C2_core_ollama_behavioral.json` |
| Run directory | `experiments/runs/C2_core_ollama_behavioral/<timestamp>/` |
| Combined registry | `experiments/manifests/` (run registry entry linking C1 + C2) |
| Neutral reports | `<run-dir>/campaign_reports/` (CSV, JSON, Markdown only) |
| Analysis import | Private writing repository (`~/papers/emse2026/paper/`) |

See [docs/public_private_boundary.md](../docs/public_private_boundary.md).

---

## 9. Summary recommendation

| Parameter | Recommended value |
|-----------|-------------------|
| **Systems** | All **12** approved (merge **3** pilot runs from C1) |
| **Models** | **4** Ollama tags (same as C1) |
| **Replicates** | **5** per model×system cell |
| **New runs to execute** | **180** |
| **Total primary dataset** | **240** runs |
| **Estimated wall time** | **2–3 overnight sessions** (resume-enabled) |

This design maximises corpus coverage and replicate depth for RQ1–RQ5 while staying within local sequential execution constraints validated by C1.

---

## References

- C1 config: `experiments/configs/C1_pilot_ollama_behavioral.json`
- C2 config: `experiments/configs/C2_core_ollama_behavioral.json`
- C1 audits: `experiments/analysis/C1_replicate_audit.md`, `experiments/analysis/C1_negative_test_audit.md`
- Study design campaigns: `docs/study_design.md` §10
- Evaluation protocol: `docs/evaluation_protocol.md`
