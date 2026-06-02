# Final Research Questions — EMSE 2026

**Document ID:** `research_questions_v1.0`  
**Status:** Authoritative RQ set for manuscript and analysis plan  
**Derived from:** `paper/notes/study_design.md` (v1.0)  
**Supersedes:** Draft RQs in `llm-fsm-behavioral-benchmark/docs/evaluation_protocol.md`  
**Date:** 2026-06-03

---

## Scope and positioning

### What FSM-Bench-20 (IST 2026) already answered

IST established a **descriptive structural funnel** on 140 runs: G1 98.6%, G2 78.6%, nested G3 31.4%, with coverage decoupled from determinism. Those questions — *Can LLMs emit valid JSON?*, *Which model ranks highest on coverage?*, *How often is output non-deterministic?* — are **closed** for the frozen IST campaign and must **not** be re-posed as EMSE research questions.

### What this study adds

EMSE research questions treat structural gates (G1–G3) as **stratification covariates**, not primary endpoints. Every RQ below targets **operational specification quality**: trace execution, gold conformance, perturbation sensitivity, and measurement stability.

### Design principles applied

| Principle | Implication |
|-----------|-------------|
| Behavioral over syntactic | No RQ whose sole endpoint is JSON parse rate or schema pass rate |
| Non-trivial | No model-leaderboard or "can LLMs generate FSMs?" questions |
| Measurable | Each RQ maps to CSV/JSON columns and a frozen campaign |
| EMSE rigor | Effect sizes, confidence intervals, and pre-registered tests where applicable |
| Analysis traceability | Each RQ maps to one Results subsection (§8.x) |

### RQ count

**Seven primary research questions (RQ1–RQ7)** covering three empirical pillars: behavioral correctness (RQ1–RQ3), robustness (RQ4–RQ5), reproducibility (RQ6–RQ7).

Structural replication of IST is **experimental infrastructure** (campaign C0/C1), not a research question.

---

## Summary table

| RQ | Pillar | One-line question | Primary metrics | Campaign | Results section |
|----|--------|-------------------|-----------------|----------|-----------------|
| **RQ1** | Behavioral | Structural–behavioral gap | `oracle_pass_rate`, `structural_behavioral_gap` | C2 | §8.1 |
| **RQ2** | Behavioral | Dominant failure modes | `primary_failure_mode`, category rates | C2 | §8.2 |
| **RQ3** | Behavioral | Proxy vs gold behavioral predictors | `GBA`, `GSS`, `GRR`, correlations | C2 | §8.3 |
| **RQ4** | Robustness | Perturbation sensitivity (overall) | `Δ_oracle`, `Δ_G3`, `Jaccard_trans` | C3 | §8.4 |
| **RQ5** | Robustness | Perturbation-type ranking | \|`Δ_oracle`\| by type, Cliff's δ | C3 | §8.5 |
| **RQ6** | Reproducibility | Run-to-run variance | `exact_replication_rate`, `oracle_pass_variance` | C4 | §8.6 |
| **RQ7** | Reproducibility | Cross-study metric stability | `metric_stability_tier` | C4 | §8.7 |

---

## RQ1 — Structural–behavioral gap

### Question

**Among LLM-generated FSMs that pass schema validation (G2), what proportion satisfies requirement-derived behavioral oracles, and how large is the gap between structural acceptance and behavioral correctness?**

### Rationale

IST showed that **78.6%** of runs pass G2 yet only **31.4%** pass nested G3, and citation coverage is a weak quality proxy (|r| ≤ 0.16 vs G3). Neither metric establishes that an FSM **behaves** as specified. MBT adoption requires knowing whether structurally "usable" artefacts are operationally safe.

This RQ quantifies the **structural–behavioral gap** — the study's central empirical phenomenon — on a fixed oracle battery, stratified by G2 and G3 pass status.

**Why stronger than FSM-Bench-20:** IST measured gate attrition; this RQ measures **semantic adequacy** via executable traces on the same population.

**Why non-trivial:** A high G2 pass rate does not imply high oracle pass rate; the gap magnitude is unknown and may be large.

### Expected metric families

| Family | Metrics | Stratum |
|--------|---------|---------|
| **Behavioral pass** | `oracle_pass_rate`, `oracle_pass_count`, `oracle_evaluable_count` | S2 (G2 pass), S3 (G3 pass) |
| **Gap** | `structural_behavioral_gap` = P(G2 pass) − P(all oracles pass \| G2) | S2 |
| **Structural covariates** | `schema_valid`, `deterministic`, `requirement_coverage` | S0–S3 |
| **Sensitivity** | `deterministic_guard_aware` (G3′), gap recomputed on S4 | S4 |

### Required experimental evidence

| Evidence | Source | Minimum *n* |
|----------|--------|-------------|
| Cleaned FSM JSON for 6 mandatory models × 12 systems (Tier A+B) | Campaign C1 (import IST freeze or replicate) | 72 runs |
| Approved oracle specs (≥8 oracles/system) | `benchmark/oracles/systems/` | 12 systems |
| Oracle execution log per run | Campaign C2 → `results/behavioral/oracle_results.csv` | 72 × ≥8 oracles |
| Wilson 95% CIs on pass rates | `analysis/behavioral_failure_analysis.py` | — |
| McNemar or stratified comparison: oracle pass \| G3 vs \| G2 only | Pre-registered test (H2 in study design) | S2 vs S3 |

### Analysis section mapping

| Manuscript | Content |
|------------|---------|
| **Design** | `sections/05_behavioral_evaluation.tex` — oracle protocol, strata S2/S3 |
| **Results** | **`sections/08_results.tex` → §8.1 Structural–behavioral gap** |
| **Tables/Figures** | `table_oracle_results.tex`; **F1** `structural_behavioral_gap` (bar or funnel: G2 → oracle pass → G3) |
| **Discussion hook** | §9 — implications for trusting schema-valid FSMs in MBT pipelines |

---

## RQ2 — Behavioral failure characterization

### Question

**When structurally valid LLM-generated FSMs fail behavioral oracles, which failure modes predominate, and do failure profiles differ by oracle category (positive trace, negative trace, invariant, requirement binding)?**

### Rationale

Structural failure taxonomies (non-determinism, wildcards, undeclared states) do not explain **why** an FSM misbehaves relative to requirements. Oracle-level failure codes (wrong terminal state, forbidden trace accepted, invariant violated) connect errors to **MBT-relevant semantics** and guide prompt or validation hardening.

**Why stronger than FSM-Bench-20:** IST ranked structural failure categories; this RQ ranks **behavioral** failures tied to test oracles.

**Why non-trivial:** Failure distribution may reveal that invariant violations dominate over trace errors — a non-obvious pattern with design implications.

### Expected metric families

| Family | Metrics |
|--------|---------|
| **Primary failure mode** | `primary_failure_mode` ∈ {BF-01…BF-07} per run |
| **Category pass rates** | Pass rate by `oracle.category` (positive, negative, invariant, binding) |
| **Severity-weighted counts** | Frequency table ranked by BF-02 > BF-03 > BF-01 > … |
| **Co-occurrence** | Structural flags (e.g., G3 fail) × behavioral failure code |

### Required experimental evidence

| Evidence | Source |
|----------|--------|
| Per-oracle pass/fail with failure code | C2 → `results/behavioral/details/<model>/<system>.json` |
| Aggregated taxonomy | `analysis/exports/behavioral_failure_taxonomy.csv` |
| Category comparison | χ² or Fisher exact across oracle categories (H4) |
| Qualitative exemplars | 3–5 cross-model failure traces per top-3 BF codes |

### Analysis section mapping

| Manuscript | Content |
|------------|---------|
| **Design** | `sections/05_behavioral_evaluation.tex` — failure code definitions (§10.5 study design) |
| **Results** | **`sections/08_results.tex` → §8.2 Behavioral failure taxonomy** |
| **Tables/Figures** | Failure frequency table; **F2** `oracle_failure_taxonomy` |
| **Discussion hook** | §9 — which failures are detectable by structural gates alone (answer: subset) |

---

## RQ3 — Construct validity of proxy metrics

### Question

**To what extent do structural proxy metrics (requirement citation coverage, nested G3 pass, structural similarity to gold) predict gold-aligned behavioral conformance, and which proxy best explains oracle pass rate?**

### Rationale

Practitioners and benchmarks often use **coverage** or **schema pass** as correctness shortcuts. IST demonstrated coverage–determinism decoupling. This RQ tests **construct validity** empirically: if proxies poorly predict `GBA` (gold behavioral alignment) and `oracle_pass_rate`, their use as quality indicators is unjustified.

**Why stronger than FSM-Bench-20:** IST planned gold comparison (RQ5) but **never executed it**. This RQ completes that gap with approved gold FSMs and inferential comparison of predictors.

**Why non-trivial:** The winning predictor is not predetermined; behavioral alignment may be only weakly explained by structural proxies.

### Expected metric families

| Family | Metrics |
|--------|---------|
| **Gold behavioral** | `GBA`, `GFV` (forbidden trace violation rate), `GRR` |
| **Gold structural** | `GSS` (transition-set Jaccard vs gold) |
| **Proxies** | `requirement_coverage`, `deterministic` (G3), `schema_valid` |
| **Association** | Pearson/Spearman ρ; Williams test for dependent correlations (H3) |
| **Variance explained** | Rank proxy by \|ρ\| with `oracle_pass_rate` and `GBA` |

### Required experimental evidence

| Evidence | Source | Minimum *n* |
|----------|--------|-------------|
| Approved gold FSMs | `benchmark/gold/` (`metadata.status = approved`) | 12 systems |
| Gold positive/forbidden traces | Embedded in gold + oracle cross-check | per system |
| Per-run gold metrics | C2 + `scripts/fsm_benchmark/gold_compare.py` | 72 runs |
| Correlation matrix with CIs | `analysis/behavioral_failure_analysis.py` | — |
| Sensitivity excluding non-evaluable oracles | Guard-decidability filter reported | — |

### Analysis section mapping

| Manuscript | Content |
|------------|---------|
| **Design** | `sections/05_behavioral_evaluation.tex` — gold alignment metrics |
| **Results** | **`sections/08_results.tex` → §8.3 Proxy metrics vs gold behavioral conformance** |
| **Tables/Figures** | Correlation table (proxies × `GBA` × `oracle_pass_rate`); scatter panels optional in appendix |
| **Threats hook** | `sections/10_threats_to_validity.tex` — construct validity paragraph |

---

## RQ4 — Robustness to requirement perturbation (overall)

### Question

**How much do structural and behavioral quality metrics change when requirements are perturbed under controlled, seeded transformations, relative to unperturbed baselines for the same (model, system) pair?**

### Rationale

Requirements in practice are **revised, reordered, paraphrased, or incomplete**. A specification generator that only works on pristine FSM-Bench-20 text is fragile. Paired perturbation analysis measures **engineering resilience** of LLM FSM synthesis — not addressed in IST.

**Why stronger than FSM-Bench-20:** IST used fixed requirement text; this RQ introduces **controlled independent manipulation** of the input specification.

**Why non-trivial:** Degradation may be asymmetric (behavioral metrics may drop more than structural gates suggest).

### Expected metric families

| Family | Metrics |
|--------|---------|
| **Paired deltas (behavioral)** | `Δ_oracle` = oracle_pass_rate(pert) − oracle_pass_rate(base) |
| **Paired deltas (structural)** | `Δ_G3`, `Δ_G2`, `Δ_coverage` |
| **Structural drift** | `Jaccard_trans` on transition sets vs baseline |
| **Success** | `perturbation_success` (generation completed) |

### Required experimental evidence

| Evidence | Source | Minimum *n* |
|----------|--------|-------------|
| Perturbation specs with fixed seeds | `benchmark/perturbations/variants/` | 12 systems × 4 types |
| Baseline FSM per (model, system) | C1 imported/cached outputs | 72 cells |
| Perturbed generation | Campaign C3 | 288 cells (6×12×4) |
| Paired delta CSV | `results/robustness/perturbation_results.csv` | — |
| Mean \|Δ_oracle\| with 95% CI | `analysis/robustness_stats.py` | — |

### Analysis section mapping

| Manuscript | Content |
|------------|---------|
| **Design** | `sections/06_robustness_evaluation.tex` — paired design, perturbation types |
| **Results** | **`sections/08_results.tex` → §8.4 Overall perturbation sensitivity** |
| **Tables/Figures** | `table_robustness.tex` (summary deltas); **F3** panel: Δ oracle by model (not leaderboard — distribution) |
| **Discussion hook** | §9 — requirements volatility as deployment risk |

---

## RQ5 — Perturbation-type effects

### Question

**Which requirement perturbation classes (paraphrase, ordering, omission, negation-flip) induce the largest paired degradation in behavioral correctness, and do effect sizes differ beyond what structural gate changes alone would predict?**

### Rationale

RQ4 establishes *that* sensitivity exists; RQ5 identifies *which edits* are harmful — actionable for requirements engineering (e.g., paraphrase may be safe; omission or invariant flip may be catastrophic). FSM-specific perturbations (negation-flip on "must not" clauses) differentiate this from generic NL robustness benchmarks.

**Why non-trivial:** Ordering-only changes might preserve semantics but alter LLM output substantially; empirical ranking is required.

### Expected metric families

| Family | Metrics |
|--------|---------|
| **By-type effect** | Mean \|`Δ_oracle`\| stratified by `perturbation_type` |
| **Structural–behavioral divergence** | \|`Δ_oracle`\| − \|`Δ_G3`\| per type (behavioral drop exceeds structural) |
| **Inferential** | Friedman test across types; paired Wilcoxon paraphrase vs omission (H6); Cliff's δ |
| **Model family covariate** | Code-specialised vs general: mean \|Δ_oracle\| (descriptive + Kruskal–Wallis, H8) |

### Required experimental evidence

| Evidence | Source |
|----------|--------|
| Same C3 paired data as RQ4 | `perturbation_results.csv` grouped by `perturbation_type` |
| Type-stratified effect size table | `analysis/exports/robustness_summary.json` |
| FDR-corrected pairwise comparisons | `analysis/robustness_stats.py` |

### Analysis section mapping

| Manuscript | Content |
|------------|---------|
| **Design** | `sections/06_robustness_evaluation.tex` — perturbation taxonomy |
| **Results** | **`sections/08_results.tex` → §8.5 Perturbation-type effects** |
| **Tables/Figures** | Type-effect table in `table_robustness.tex`; **F3** `perturbation_sensitivity` by type |
| **Discussion hook** | §9 — guidance on safe vs risky requirement edits before FSM generation |

---

## RQ6 — Run-to-run generation variance

### Question

**Under fixed temperature (T=0), identical prompts, and pinned model digests, what run-to-run variance appears in structural form and behavioral scores across repeated generations of the same (model, system) specification?**

### Rationale

IST treated T=0 as deterministic and ran **one shot** per cell. Reproducibility is a core EMSE expectation. Non-zero variance in `oracle_pass_rate` or `G3` pass would imply that single-run benchmarks — including IST — under-report uncertainty.

**Why stronger than FSM-Bench-20:** First **quantified variance profile** for local LLM FSM generation at T=0.

**Why non-trivial:** Variance may concentrate in behavioral metrics even when structural JSON is stable.

### Expected metric families

| Family | Metrics |
|--------|---------|
| **Exact stability** | `exact_replication_rate` (identical cleaned JSON hash across K repeats) |
| **Structural stability** | `structural_jaccard_mean` (pairwise transition-set Jaccard) |
| **Behavioral stability** | `oracle_pass_variance`, `G3_flip_rate` |
| **Auxiliary** | `token_length_cv` |

### Required experimental evidence

| Evidence | Source | Minimum *n* |
|----------|--------|-------------|
| K=5 repeats per cell | Campaign C4 | 6 models × 10 systems × 5 = **300 runs** |
| Stratified system sample | `reproducibility_sample_10.txt` (study design §12.3) | 10 systems |
| Variance summary JSON | `results/reproducibility/variance_summary.json` | — |
| Per-cell distribution plots | `analysis/reproducibility_stats.py` | 60 cells |

### Analysis section mapping

| Manuscript | Content |
|------------|---------|
| **Design** | `sections/07_reproducibility.tex` — repeat protocol, K=5 |
| **Results** | **`sections/08_results.tex` → §8.6 Run-to-run variance** |
| **Tables/Figures** | `table_reproducibility.tex`; **F4** `reproducibility_variance` |
| **Threats hook** | §10 — conclusion validity of single-run studies |

---

## RQ7 — Metric stability for cross-study comparison

### Question

**Which FSM evaluation metrics are sufficiently stable across repeated generation to permit cross-study comparison without full campaign replication, and which require mandatory replication?**

### Rationale

RQ6 measures variance; RQ7 **translates** variance into **guidance** for benchmark consumers — an EMSE-style actionable outcome. Directly addresses IST's single-run freeze and the field's habit of comparing numbers across incompatible studies.

**Why non-trivial:** Stability may differ by metric family (binary gates vs continuous oracle rates); blanket "replicate everything" or "T=0 is enough" claims are both testable and likely false in parts.

### Expected metric families

| Family | Metrics |
|--------|---------|
| **ICC / CV** | Intraclass correlation or coefficient of variation per metric across K repeats |
| **Stability tier** | `metric_stability_tier` ∈ {Stable, Moderate, Unstable} per study design §12.4 |
| **Classification rules** | Stable: exact_replication ≥ 0.95 AND oracle_variance ≤ 0.01; etc. |
| **Recommendations** | Tabular guidance for G1, G2, G3, coverage, oracle_pass_rate, GBA |

### Required experimental evidence

| Evidence | Source |
|----------|--------|
| C4 repeat data (same as RQ6) | `variance_summary.json` |
| Tier assignment per metric | `analysis/reproducibility_stats.py` |
| Cross-metric comparison | Behavioral vs structural stability ranking (H10) |

### Analysis section mapping

| Manuscript | Content |
|------------|---------|
| **Design** | `sections/07_reproducibility.tex` — tier definitions |
| **Results** | **`sections/08_results.tex` → §8.7 Metric stability classification** |
| **Tables/Figures** | Stability tier table in `table_reproducibility.tex`; optional appendix decision tree |
| **Discussion hook** | §9 — recommendations for benchmark authors and systematic reviews |

---

## Explicitly excluded questions (not RQs)

These were considered but **rejected** to avoid IST duplication or trivial benchmarking:

| Rejected question | Reason |
|-------------------|--------|
| How accurately do LLMs generate syntactically valid FSM JSON? | Closed by IST (G1 98.6%) |
| Which model achieves the highest coverage or G3 pass rate? | Leaderboard framing; EMSE contribution is not model ranking |
| Does structured JSON output improve validity? | IST RQ4 ablation not executed; optional C6 — report as sensitivity, not core RQ |
| Does guard-aware G3 reclassification change pass rates? | Construct refinement; report as **sensitivity analysis under RQ1** (stratum S4), not standalone RQ |
| Which application domain is hardest? | IST RQ6 descriptive; fold as **covariate stratification** in RQ2/RQ3 discussion, not primary RQ |
| Can LLMs generate FSMs from requirements? | Trivially yes; no longer research-worthy |

---

## Cross-RQ dependency structure

```text
                    IST structural baseline (C0/C1)
                    G1, G2, G3, coverage — covariates only
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
   RQ1 Gap              RQ4 Overall          RQ6 Variance
   RQ2 Failures         RQ5 By-type          RQ7 Stability
   RQ3 Proxies
         │                    │                    │
         └────────────────────┴────────────────────┘
                              ▼
              sections/08_results.tex (§8.1–§8.7)
                              ▼
              sections/09_discussion.tex (integrated interpretation)
```

---

## Hypothesis alignment (from study design)

| RQ | Primary hypotheses tested |
|----|---------------------------|
| RQ1 | H1 (majority of G2 passers fail ≥1 oracle), H2 (oracle \| G3 ≤ oracle \| G2) |
| RQ2 | H4 (invariant oracles fail more than positive traces) |
| RQ3 | H3 (GBA correlates more with oracle pass than coverage does) |
| RQ4 | — (descriptive + CI; no directional pre-registration required) |
| RQ5 | H6 (omission > paraphrase), H7 (negation-flip ≥ ordering), H8 (model family sensitivity) |
| RQ6 | H9 (exact_replication < 1.0 for ≥50% cells) |
| RQ7 | H10 (behavioral variance > structural gate variance), H11 (structural Jaccard ≥ 0.90 median for code-specialised models) |

---

## Manuscript integration checklist

Before drafting Results prose, verify:

- [ ] Each RQ1–RQ7 has a matching **§8.x** subsection heading in `sections/08_results.tex`
- [ ] `results_mapping.md` updated to map metrics → RQ → §8.x
- [ ] `outline.md` RQ table replaced with this document's summary table
- [ ] Campaign manifests C2, C3, C4 reference RQ IDs in `notes` field
- [ ] No Results subsection reports model leaderboard as primary answer to any RQ

---

## Document control

| Version | Date | Change |
|---------|------|--------|
| v1.0 | 2026-06-03 | Final RQ set derived from study_design v1.0; 7 primary RQs; IST structural questions demoted to infrastructure |

**Authority:** This document defines the RQs stated in `sections/04_methodology.tex` and answered in `sections/08_results.tex`. Changes after campaign freeze require v1.1 and manifest amendment.

---

*End of research_questions_v1.0*
