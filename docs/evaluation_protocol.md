# Evaluation Protocol — behavioral-fsm-benchmark

**Document ID:** `evaluation_protocol_v2.0`  
**Repository:** `behavioral-fsm-benchmark`  
**Target venue:** Empirical Software Engineering (Springer)  
**Status:** Authoritative pre-registration protocol (no EMSE results claimed herein)  
**Companion:** `docs/study_design.md`, `docs/benchmark_specification.md`  
**Date:** 2026-06-03

---

## 1. Purpose

This protocol defines **dependent variables**, **metric computation**, **campaign structure**, and **RQ mapping** for the EMSE study *Beyond Structural Validity*. All metrics are computed by the offline evaluator (`framework/`, `scripts/evaluate_case.py`) against artifacts conforming to `benchmark/schemas/`.

**Freeze policy:** Numeric results are reported only after campaign freeze (M9). This document specifies *how* metrics are measured, not *what* values were observed.

---

## 2. Research questions

| RQ | Pillar | Question |
|----|--------|----------|
| **RQ1** | Behavioral | Among G2-passing FSMs, what proportion passes behavioral test suites, and how large is the structural–behavioral gap? |
| **RQ2** | Behavioral | What failure modes dominate when FSMs are structurally valid but behaviorally incorrect? |
| **RQ3** | Behavioral | How well do proxy metrics predict gold-backed behavioral agreement? |
| **RQ4** | Robustness | How sensitive are scores to controlled requirement perturbations overall? |
| **RQ5** | Robustness | Which perturbation types cause the largest score degradation? |
| **RQ6** | Reproducibility | What is run-to-run variance under fixed temperature and prompts? |
| **RQ7** | Reproducibility | Which metrics are stable enough for cross-study comparison? |

Structural replication (campaigns C0/C1) supports construct validity but is **not** an RQ.

---

## 3. Hypotheses (testable, no pre-specified effect sizes)

| ID | Hypothesis |
|----|------------|
| **H1** | A non-zero fraction of G2-passing FSMs fails at least one evaluable behavioral test |
| **H2** | Failures are more frequent on invariant/negative tests than on happy-path tests |
| **H3** | Requirement coverage is a weaker predictor of behavioral agreement than gold transition overlap |
| **H4** | Omission perturbations reduce behavioral agreement more than paraphrase |
| **H5** | Code-specialised models show lower structural Jaccard variance across repeats |
| **H6** | G3a pass rate exceeds strict G3 pass rate on the same candidates |

---

## 4. Independent variables

| Variable | Type | Levels / notes |
|----------|------|----------------|
| LLM model | Categorical | Local Ollama set; pinned in manifest |
| System | Categorical | Up to 20; **12 core** for primary inference |
| Domain | Categorical | From system metadata |
| Perturbation type | Categorical | `none`, `paraphrase`, `ordering`, `omission`, `ambiguity`, `negation_flip` |
| Repeat index | Ordinal | 1…K (set at C4 freeze) |
| Structured output | Boolean | Primary: JSON schema constrained |

**Unit of analysis:** one `(model, system, perturbation, repeat)` generation run and its evaluation export.

---

## 5. Metric families

### 5.1 Structural gates (L0–L1)

| Metric | Symbol | Type | Definition |
|--------|--------|------|------------|
| JSON validity | **G1** | Boolean | Candidate parses as JSON |
| Schema validity | **G2** | Boolean | Validates `generated_fsm.schema.json`; referential closure; no wildcard sources |
| Strict determinism | **G3** | Boolean | No duplicate `(source, event)` pairs |
| Guard-aware determinism | **G3a** | Boolean | No overlapping enabled guards to different targets (§4.3 of benchmark spec) |
| ND guard rate | `nd_guard_rate` | Continuous ∈ [0,1] | Fraction of transitions with non-decidable guards |

**Primary determinism endpoint:** G3a. G3 reported for IST replication.

### 5.2 Gold structural similarity and overlap (L3–L4)

| Metric | Symbol | Type | Definition |
|--------|--------|------|------------|
| Gold structural similarity | **GSS** | Continuous ∈ [0,1] | Relaxed transition overlap vs approved gold (ignores guards) |
| State overlap | `state_jaccard` | Continuous ∈ [0,1] | Jaccard similarity of state sets vs gold |
| Event overlap | `event_jaccard` | Continuous ∈ [0,1] | Jaccard similarity of event sets vs gold |
| Transition precision | `trans_precision` | Continuous ∈ [0,1] | \|matched candidate transitions\| / \|candidate transitions\| (relaxed tuple) |
| Transition recall | `trans_recall` | Continuous ∈ [0,1] | \|matched candidate transitions\| / \|gold transitions\| (relaxed tuple) |
| Transition F1 | `trans_f1` | Continuous ∈ [0,1] | Harmonic mean of precision and recall |
| Exact transition coverage | `tcov_exact` | Continuous ∈ [0,1] | Intersection over gold with guard_key in tuple |
| Relaxed transition coverage | `tcov_relaxed` | Continuous ∈ [0,1] | Intersection over gold on `(source, event, target)` only |

### 5.3 Behavioral test-suite agreement (L2)

| Metric | Symbol | Type | Definition |
|--------|--------|------|------------|
| Oracle pass rate | `oracle_pass_rate` | Continuous ∈ [0,1] | Fraction of evaluable oracle tests passed |
| Path pass rate | `path_pass_rate` | Continuous ∈ [0,1] | Fraction of evaluable path tests passed |
| Combined behavioral agreement | **BTA** | Continuous ∈ [0,1] | Weighted combination of oracle and path pass rates (weights in catalog) |
| Forbidden false-accept rate | `forbidden_fpr` | Continuous ∈ [0,1] | Fraction of forbidden paths incorrectly accepted (lower is better) |
| Primary failure mode | `primary_failure_mode` | Categorical | Dominant BF-xx / SF-xx code per run |
| Structural–behavioral gap | `structural_behavioral_gap` | Derived | Indicator: G2 pass ∧ ¬BTA pass (per run); aggregated with Wilson CI on core stratum |

**Gold behavioral alignment (L4):**

| Metric | Symbol | Definition |
|--------|--------|------------|
| Gold behavioral alignment | **GBA** | Fraction of gold-derived positive path tests passing on candidate |
| Gold forbidden violation | **GFV** | Fraction of gold forbidden paths incorrectly accepted |
| Trace equivalence | **TEQ** | Composite of GBA, GFV, GSS (weights in `benchmark/catalog.json`) |

### 5.4 Coverage (L3)

| Metric | Symbol | Definition |
|--------|--------|------------|
| Requirement coverage | **RCov** | Fraction of requirements cited on transitions |
| Reference requirement recall | **RRef** | Recall of gold-cited requirements on candidate |
| Path coverage | **PCov** | Evaluable path tests passed / evaluable path tests |

### 5.5 Robustness deltas (C3)

Paired comparison vs unperturbed baseline for the same `(model, system)`:

| Metric | Symbol | Definition |
|--------|--------|------------|
| Δ G3 | `delta_g3` | G3_pass(perturbed) − G3_pass(baseline) |
| Δ G3a | `delta_g3a` | G3a_pass(perturbed) − G3a_pass(baseline) |
| Δ behavioral agreement | `delta_bta` | BTA(perturbed) − BTA(baseline) |
| Δ oracle pass | `delta_oracle` | oracle_pass_rate(perturbed) − baseline |
| Δ TEQ | `delta_teq` | TEQ(perturbed) − TEQ(baseline) |
| Structural Jaccard vs baseline | `struct_jaccard_vs_base` | Transition-set Jaccard between perturbed and baseline outputs |

### 5.6 Repair success rate (optional, exploratory)

When a repair pass is applied to G2-failing or G3a-failing candidates:

| Metric | Symbol | Definition |
|--------|--------|------------|
| Repair attempt rate | `repair_attempt_rate` | Fraction of eligible runs with repair invoked |
| Repair success rate | **RSR** | Fraction of repair attempts reaching G2 ∧ G3a ∧ BTA ≥ pre-repair baseline |
| Post-repair Δ BTA | `delta_bta_repair` | BTA after repair − BTA before repair |

Repair is **exploratory** unless pre-registered before C2 freeze.

### 5.7 Reproducibility metrics (C4)

Across K repeats per `(model, system)` at fixed prompt and T=0:

| Metric | Symbol | Definition |
|--------|--------|------------|
| Cross-run structural Jaccard | `cross_run_struct_jaccard` | Mean pairwise Jaccard of transition sets |
| Cross-run oracle variance | `cross_run_oracle_var` | Variance of oracle_pass_rate |
| Cross-run BTA variance | `cross_run_bta_var` | Variance of BTA |
| Exact replication rate | `exact_replication_rate` | Fraction of repeats with identical normalized JSON |
| Metric stability tier | `stability_tier` | Pre-specified CV thresholds → {high, medium, low} per metric |
| ICC (optional) | `metric_icc` | Intraclass correlation for continuous endpoints |

### 5.8 Composite index (L5, descriptive)

| Metric | Symbol | Role |
|--------|--------|------|
| FBNS | `fbns` | Weighted composite of structural, determinism, behavioral, coverage, equivalence sub-scores |
| Sub-scores | `s_structural`, `s_determinism`, `s_behavioral`, `s_coverage`, `s_equivalence` | Diagnostic decomposition |

FBNS is **not** a primary confirmatory endpoint; layer metrics above are.

---

## 6. RQ → metric mapping

| RQ | Primary metrics | Secondary / supporting |
|----|-----------------|------------------------|
| **RQ1** | `structural_behavioral_gap`, `oracle_pass_rate`, `bta` on G2 stratum | G2 pass rate, G3/G3a rates (context) |
| **RQ2** | `primary_failure_mode` distribution, BF-xx frequencies | Breakdown by oracle category |
| **RQ3** | Rank correlations: RCov vs BTA; `trans_recall` vs BTA; GSS vs BTA | `trans_f1`, `state_jaccard`, `event_jaccard` |
| **RQ4** | `delta_bta`, `delta_oracle`, `delta_teq` (paired vs baseline) | `delta_g3`, `delta_g3a` |
| **RQ5** | \|Δ\| compared across perturbation types | `struct_jaccard_vs_base` by type |
| **RQ6** | `cross_run_oracle_var`, `cross_run_bta_var`, `exact_replication_rate` | `cross_run_struct_jaccard` |
| **RQ7** | `stability_tier` per metric family | `metric_icc`, coefficient of variation |

---

## 7. Campaigns

| Campaign | Purpose | RQs | Output artifact (frozen) |
|----------|---------|-----|--------------------------|
| **C0** | IST structural parity spot-check | — | Parity report |
| **C1** | Structural baseline replication | Infrastructure | `structural_baseline.csv` |
| **C2** | Behavioral evaluation | RQ1–RQ3 | `behavioral_results.csv` |
| **C3** | Perturbation robustness | RQ4–RQ5 | `perturbation_results.csv` |
| **C4** | Multi-run reproducibility | RQ6–RQ7 | `variance_summary.json` |

Manifest templates: `experiments/configs/TEMPLATE_*.json`  
Frozen manifests: `experiments/manifests/` (immutable after `frozen_at`).

---

## 8. Statistical analysis plan

| Analysis | Method |
|----------|--------|
| Descriptive rates | Wilson score intervals (95%) on core stratum |
| Model comparisons | Non-parametric tests (Kruskal–Wallis; pairwise with Holm correction) |
| Effect size | Cliff's delta or rank-biserial where applicable |
| RQ3 correlations | Spearman ρ; compare proxy vs gold-backed predictors |
| RQ4–RQ5 perturbation | Paired Δ vs baseline; compare \|Δ\| across perturbation types |
| RQ6–RQ7 variance | CV, stability tiers; optional ICC |
| System blocking | Systems treated as blocking factors; avoid unpooled model ranking as primary claim |

Confirmatory tests are labeled in analysis log; unplanned analyses are **exploratory**.

Analysis scripts: `analysis/` (separate from experiment driver).

---

## 9. Reporting conventions

### 9.1 Strata

| Stratum | Filter | Use |
|---------|--------|-----|
| All runs | — | Descriptive context |
| G2+ | G2 pass | Primary behavioral stratum (RQ1–RQ3) |
| G3a+ | G3a pass | Guard-resolved determinism stratum |
| Core | 12 core systems | Primary inference |
| Stretch | 8 stretch systems | Extension only |

### 9.2 CSV export columns (minimum)

`run_id`, `campaign_id`, `model`, `system_id`, `g1`, `g2`, `g3`, `g3a`, `nd_guard_rate`, `oracle_pass_rate`, `path_pass_rate`, `bta`, `forbidden_fpr`, `rcov`, `rref`, `tcov_exact`, `tcov_relaxed`, `pcov`, `gss`, `gba`, `gfv`, `teq`, `trans_precision`, `trans_recall`, `state_jaccard`, `event_jaccard`, `primary_failure_mode`, `fbns`

Perturbation and reproducibility exports add columns defined in §5.5–§5.7.

### 9.3 Prohibited in pre-freeze documents

- Invented pass rates or effect sizes for this study
- Model ranking as primary conclusion before C2/C4 freeze
- Using stretch-only systems for confirmatory claims

---

## 10. Related documents

| Document | Role |
|----------|------|
| `docs/study_design.md` | RQs, validity threats, contribution claims |
| `docs/benchmark_specification.md` | Gold requirements, G3/G3a, L0–L5, schemas |
| `docs/implementation_roadmap.md` | Milestones M1–M9 |
| `docs/artifact_policy.md` | What is committed vs gitignored |
| `REPRODUCIBILITY.md` | Replication package |
| `benchmark/schemas/` | Authoritative JSON schemas |

---

## 11. Version history

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-06-03 | Draft skeleton |
| **2.0** | 2026-06-03 | Full metric catalog; G3a; RQ mapping; repair/repro/robustness deltas |

---

*End of evaluation protocol v2.0*
