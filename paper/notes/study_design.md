# Formal Study Design — FSM-Behavior-Bench (EMSE 2026)

**Document ID:** `study_design_v1.0`  
**Status:** Authoritative design specification — implement from this document  
**Target venue:** Empirical Software Engineering (Springer)  
**Predecessor study:** FSM-Bench-20 (IST 2026) — DOI [10.5281/zenodo.20516296](https://doi.org/10.5281/zenodo.20516296)  
**Working title:** *Beyond Structural Validity: Evaluating Behavioral Correctness, Robustness, and Reproducibility of LLM-Generated Finite State Machines from Natural-Language Requirements*  
**Author:** Cesar Andres Sanchez  
**Date:** 2026-06-03

---

## Document control

| Field | Value |
|-------|-------|
| Supersedes | `llm-fsm-behavioral-benchmark/docs/evaluation_protocol.md` (draft RQs only) |
| Implementation repo | `~/papers/emse2026/llm-fsm-behavioral-benchmark/` |
| Manuscript repo | `~/papers/emse2026/paper/` |
| Freeze policy | Campaign manifests in `experiments/campaigns/` become immutable at `frozen_at` |
| Change control | Material design changes require new `study_design_vX.Y` and changelog entry |

**How to use this document:** Each section maps to repository paths and scripts listed in §18. Do not begin full-scale campaigns until §16 pre-registration checklist is complete and pilot campaigns (§15) pass acceptance criteria.

---

## 1. Executive summary

FSM-Bench-20 (IST 2026) established that local open-weight LLMs can often produce parseable, schema-valid FSM JSON, yet only **31.4%** of runs (44/140) pass nested structural determinism (G3), and requirement citation coverage (**69.2%** mean) is a **weak proxy** for operational quality (|r| ≤ 0.16 vs G3). Gold-standard behavioural comparison (RQ5) was **not executed**; reproducibility was assumed from temperature 0.0 without multi-run verification; robustness to requirement variation was **not studied**.

This follow-up study closes those gaps with a **three-pillar empirical design**:

1. **Behavioral correctness** — requirement-derived oracles, gold FSM trace equivalence, and invariant checking on G2-passing outputs.
2. **Robustness** — controlled requirement perturbations with paired baselines.
3. **Reproducibility** — multi-run variance measurement and metric stability classification.

The study **reuses** FSM-Bench-20 requirements and structural gates as a **baseline stratum**, enabling direct quantification of the **structural–behavioral gap** — the central empirical phenomenon IST identified qualitatively but could not measure.

---

## 2. Research motivation

### 2.1 Problem context

Model-based testing (MBT), requirements traceability, and formal specification pipelines increasingly treat LLM-generated finite state machines (FSMs) as draft artefacts. Practitioners and researchers need to know whether a generated FSM is **safe to use** — not merely syntactically valid.

FSM-Bench-20 demonstrated a **quality funnel**:

```text
140 runs → G1 98.6% → G2 78.6% → G3 31.4%
```

The dominant attrition (66/140 runs, 47.1%) occurs at **G3 (determinism)**, not at JSON parsing. Yet determinism in FSM-Bench-20 is **guard-blind** and counts duplicate `(source, event)` rows without evaluating guard mutual exclusivity — a known construct threat (IST guard-aware audit: a non-trivial fraction of G3 failures may be *apparent* non-determinism).

More importantly, IST documented **coverage–quality decoupling**: e.g., `qwen2.5-coder:14b × medical_appointment_booking` achieved **92.3%** requirement coverage while failing G3; `atm` and `login_system` showed **0%** nested G3 across all seven models despite moderate coverage. **Structural gates cannot answer whether an FSM behaves as specified.**

### 2.2 Why EMSE (and why now)

Empirical Software Engineering expects:

- **Replicable** experimental packages with explicit provenance.
- **Construct-valid** metrics tied to operational semantics, not proxy citations alone.
- **Sensitivity analysis** (robustness) when studying generative AI artefacts.
- **Variance reporting** when claiming reproducibility at temperature 0.

IST positioned FSM-Bench-20 as a **benchmark introduction** with a descriptive 140-run campaign. EMSE allows a **deeper empirical study** that treats the IST freeze as **prior evidence** and extends it with inferential analysis, oracle-based behavioural endpoints, and explicit reproducibility instrumentation — without re-claiming the benchmark artefact as the primary contribution.

### 2.3 Stakeholder utility

| Stakeholder | Utility |
|-------------|---------|
| MBT researchers | Evidence on when LLM FSMs are behaviourally trustworthy |
| Requirements engineers | Robustness bounds under paraphrase/omission |
| Benchmark designers | Metric stability guidance for cross-study comparison |
| Tool builders | Failure taxonomy beyond structural validation |

---

## 3. Research gap

### 3.1 Gap relative to prior literature (general)

| Gap | Evidence in literature / practice |
|-----|-----------------------------------|
| **G-L1** Structural validity dominates LLM SE evaluations; behavioural oracles for generated specifications are rare | Most code/FSM LLM benchmarks report parse rate, BLEU, or schema compliance |
| **G-L2** Requirement citation coverage used as correctness proxy without validation | IST freeze: coverage weakly/negatively associated with determinism among G2 passers |
| **G-L3** Robustness of *specification* generation (vs code) under NL variation is under-studied | Perturbation studies focus on code translation, not FSM synthesis |
| **G-L4** Reproducibility of LLM outputs at T=0 often assumed, rarely measured with repeated runs | IST: single run per cell; no variance quantification |
| **G-L5** Gold/reference models for LLM FSM evaluation seldom published with executable oracles | IST gold FSMs remained placeholders; RQ5 unexecuted |

### 3.2 Gap relative to FSM-Bench-20 (IST 2026) — **primary anchor**

| IST finding | Limitation | EMSE addresses |
|-------------|------------|----------------|
| 31.4% nested G3 pass | No behavioural verification of the 44 G3 passers | Oracle pass rate on G2+ and G3+ strata |
| 66 G3 failures (47.1%) | Guard-blind determinism metric | Guard-aware reclassification + behavioural traces |
| 69.2% mean coverage; 97.9% missing R1 | Citation ≠ behaviour | Trace execution vs requirements |
| RQ5 gold comparison planned | **Not executed** | Approved gold + GBS/GSS/oracle endpoints |
| RQ4 structured-output ablation | **Not executed** | Optional secondary campaign (see §15.5) |
| Single run, T=0 | Reproducibility unverified | K-repeat reproducibility campaign |
| Descriptive only | No inferential model comparisons on behaviour | Pre-registered non-parametric tests |
| Failure taxonomy structural | No invariant-violation or negative-trace testing | Behavioral failure taxonomy |

### 3.3 Core empirical question (study thesis)

> **How large is the gap between structural validity and behavioral correctness for LLM-generated FSMs, and how stable are quality measurements under requirement perturbation and repeated generation?**

---

## 4. Relationship to IST 2026 (explicit scope boundary)

| Aspect | IST 2026 | EMSE 2026 (this study) |
|--------|----------|------------------------|
| Primary contribution | Benchmark artefact + descriptive gate study | Behavioral/robustness/reproducibility empirical study |
| Dataset authorship | FSM-Bench-20 creation | Reuse via pinned import (`dataset/upstream_manifest.json`) |
| Structural baseline | Authoritative 140-run freeze | **Replicate** on same model×system grid OR **cite IST freeze** for structural stratum (see §15.2) |
| Gold FSMs | Placeholders | **Author and approve** (minimum 12 systems) |
| New benchmark content | — | Oracles, perturbations, reproducibility harness |
| Venue narrative | "How good are local LLMs at FSM JSON?" | "Is structural validity sufficient for MBT use?" |

**Design decision (structural baseline):** To conserve compute, the structural stratum MAY use the **frozen IST metrics** as the authoritative baseline for G1–G3 on the identical manifest (`20260602T195520Z`), re-validated by checksum against imported outputs. A **partial replication** (20 randomly selected runs, 10% spot-check) MUST confirm metric parity before citing IST numbers. If parity fails (>2% absolute deviation on any gate rate), run full structural replication campaign `structural_replication_v1`.

---

## 5. Expected contributions

### 5.1 Primary contributions (target for EMSE)

| ID | Contribution | Evidence type |
|----|--------------|---------------|
| **C1** | **Quantification of the structural–behavioral gap** — proportion of G2/G3 passers failing requirement oracles | Descriptive + inferential |
| **C2** | **FSM-Behavior-Bench extension** — approved gold FSMs, behavioral oracles, perturbation suite with schemas and replication package | Artefact |
| **C3** | **Behavioral failure taxonomy** — oracle-level failure modes (invariant violation, wrong terminal state, forbidden trace accepted, etc.) | Qualitative + counts |
| **C4** | **Robustness characterization** — effect sizes of perturbation types on structural and behavioral endpoints | Inferential |
| **C5** | **Reproducibility profile** — run-to-run variance and metric stability classification for FSM generation at T=0 | Descriptive + guidance |

### 5.2 Secondary contributions

| ID | Contribution |
|----|--------------|
| **C6** | Guard-aware determinism reanalysis of IST G3 failures (construct refinement) |
| **C7** | Guidance on which metrics are stable enough for cross-paper comparison without full replication |

### 5.3 Non-contributions (explicitly out of scope)

- New requirement systems beyond FSM-Bench-20 (unless pilot extension ≤2 systems documented).
- Cloud/paid API models (local Ollama only — continuity with IST).
- Automatic repair/refinement loops (single-shot generation only).
- Human developer studies (offline benchmark only).

---

## 6. Threats to novelty

| Threat | Severity | Mitigation in design |
|--------|----------|---------------------|
| **N1: "Incremental extension of own prior work"** | High | Frame EMSE paper as **empirical study** with new endpoints (behavior, robustness, reproducibility), not a benchmark paper; IST is **prior baseline**, not duplicate contribution |
| **N2: Oracle engineering perceived as ad hoc** | Medium | Dual-source oracles (requirement-derived + gold-derived); inter-rater oracle review; publish oracle specs |
| **N3: Gold FSMs authored by same researcher** | Medium | Independent reviewer sign-off; forbidden-behaviour coverage; negative traces; report Cohen's κ on oracle agreement pilot |
| **N4: Perturbation study overlaps NL robustness literature** | Medium | Domain-specific perturbations tied to MBT requirements (invariant flip, omission); FSM-specific metrics |
| **N5: Reproducibility results may be trivial at T=0** | Medium | Report **exact replication rate** honestly even if high; focus on **behavioral** and **structural Jaccard** variance |
| **N6: Structural findings replicate IST without new insight** | Low–Medium | Structural stratum is **covariate**, not headline; headline is gap between structural pass and oracle pass |
| **N7: Competing LLM FSM benchmarks emerge** | Medium | Cite comprehensively; emphasize integrated three-pillar protocol on shared dataset |
| **N8: EMSE reviewers expect human subjects or industrial case study** | Medium | Justify offline benchmark rigor; large N runs; pre-registration; industrial **domains** without proprietary data |

---

## 7. Research questions

### 7.1 Primary research questions

| ID | Research question | Primary endpoint | Section |
|----|-------------------|------------------|---------|
| **RQ1** | What proportion of LLM-generated FSMs that pass structural validation (G2, G3) also pass requirement-derived behavioral oracles? | `oracle_pass_rate` | Behavioral |
| **RQ2** | Which behavioral failure modes dominate among structurally valid FSMs? | Failure category frequencies | Behavioral |
| **RQ3** | How do LLM-generated FSMs align with approved gold reference FSMs on structural and behavioral metrics? | `gold_behavioral_alignment`, `gold_structural_similarity` | Behavioral |
| **RQ4** | To what extent does FSM generation quality degrade under controlled requirement perturbations? | `Δ oracle_pass_rate`, `Δ G3_pass` | Robustness |
| **RQ5** | Which perturbation types (paraphrase, ordering, omission, negation-flip) produce the largest degradation? | Perturbation-type stratified effects | Robustness |
| **RQ6** | What is the run-to-run variance in structural and behavioral metrics under fixed temperature (T=0) and prompts? | `exact_replication_rate`, `cross_run_oracle_variance` | Reproducibility |
| **RQ7** | Which metrics exhibit sufficient stability to support cross-study comparison without full campaign replication? | Metric stability tier classification | Reproducibility |

### 7.2 Secondary research questions

| ID | Research question |
|----|-------------------|
| **RQ8** | Does guard-aware determinism reclassification materially change the G3 pass rate reported in IST? |
| **RQ9** | Do code-specialised models outperform general models on **behavioral** endpoints after controlling for structural pass status? |
| **RQ10** | Are systems with security/invariant-heavy requirements (e.g., `login_system`, `access_control`) disproportionately represented among behavioral failures? |

### 7.3 RQ dependency graph

```text
IST structural baseline (G1–G3)
        │
        ├─► RQ1, RQ2, RQ3 (behavioral layer on G2+ / G3+)
        │
        ├─► RQ4, RQ5 (perturbation vs baseline pairs)
        │
        └─► RQ6, RQ7 (repeats on baseline conditions)

RQ8 ──► construct refinement (parallel to RQ1)
RQ9 ──► model factor (cross-cutting)
RQ10 ── system/domain stratification
```

---

## 8. Hypotheses

All hypotheses tested at α = 0.05 with multiple-comparison correction (Benjamini–Hochberg FDR) within each family.

### 8.1 Behavioral hypotheses

| ID | Hypothesis | Test | RQ |
|----|------------|------|-----|
| **H1** | Among G2-passing FSMs, oracle pass rate < 0.85 (majority fail at least one oracle) | One-sample proportion test vs 0.85 | RQ1 |
| **H2** | Oracle pass rate \| G3 pass < oracle pass rate \| G2 pass (determinism necessary but insufficient) | McNemar / stratified comparison | RQ1 |
| **H3** | `gold_behavioral_alignment` correlates more strongly with `oracle_pass_rate` than `requirement_coverage` does | Williams test for dependent correlations | RQ3 |
| **H4** | Invariant-related oracles fail more often than positive-trace oracles | χ² or Fisher exact on oracle category | RQ2 |
| **H5** | Systems with 0% IST nested G3 (`atm`, `login_system`, etc.) have oracle pass rate ≤ systems with 71.4% IST G3 | Mann–Whitney on system aggregates | RQ10 |

### 8.2 Robustness hypotheses

| ID | Hypothesis | Test | RQ |
|----|------------|------|-----|
| **H6** | \|Δ oracle pass rate\| (omission) > \|Δ oracle pass rate\| (paraphrase) | Paired Wilcoxon on system-model pairs | RQ5 |
| **H7** | \|Δ G3 pass\| (negation-flip) ≥ \|Δ G3 pass\| (ordering) | Paired Wilcoxon | RQ5 |
| **H8** | Code-specialised models (Qwen-Coder family) exhibit lower mean \|Δ oracle\| across perturbations than general models | Kruskal–Wallis + post-hoc | RQ4, RQ9 |

### 8.3 Reproducibility hypotheses

| ID | Hypothesis | Test | RQ |
|----|------------|------|-----|
| **H9** | `exact_replication_rate` < 1.0 for at least 50% of (model, system) cells | Descriptive + binomial CI | RQ6 |
| **H10** | Behavioral metrics (`oracle_pass_rate`) have higher cross-run variance than structural binary gates (G1, G2) | Compare ICC or coefficient of variation | RQ7 |
| **H11** | Structural Jaccard across K repeats ≥ 0.90 median for code-specialised models | Descriptive stability tier | RQ7 |

### 8.4 Construct refinement hypothesis

| ID | Hypothesis | Test | RQ |
|----|------------|------|-----|
| **H12** | Guard-aware G3 pass rate ≥ IST nested G3 pass rate + 10 pp (apparent ND reclassification) | Descriptive + bootstrap CI on difference | RQ8 |

### 8.5 Null hypotheses (explicit)

| ID | Null | Rejection criterion |
|----|------|---------------------|
| **H0-M** | No difference in oracle pass rate across models | Kruskal–Wallis p < 0.05 |
| **H0-P** | No difference in perturbation sensitivity across perturbation types | Friedman test p < 0.05 |

Report **effect sizes** (Cliff's δ, rank-biserial) regardless of p-values.

---

## 9. Benchmark requirements

### 9.1 Inherited requirements (FSM-Bench-20)

| Requirement | Specification | Source |
|-------------|---------------|--------|
| **BR-01** | 20 software systems, 12–13 requirements each, numbered R1…Rn | `dataset/systems/*.json` (imported) |
| **BR-02** | FSM JSON output schema (states, events, transitions with guards, actions, requirement refs) | Port `scripts/fsm_benchmark/schema.py` from IST |
| **BR-03** | Structural gates G1 (JSON), G2 (schema + referential closure), G3 (nested determinism) | Inherited metric definitions |
| **BR-04** | Prompt specification byte-compatible with IST for baseline comparison | `docs/experimental_prompts.md` |
| **BR-05** | Local Ollama inference, T=0 primary, structured JSON output default | `scripts/fsm_benchmark/config.py` |
| **BR-06** | Upstream pin with SHA-256 checksums | `dataset/upstream_manifest.json` |

### 9.2 New requirements (FSM-Behavior-Bench)

| Requirement | Specification | Path |
|-------------|---------------|------|
| **BR-07** | **Approved gold FSM** per evaluated system — deterministic, full requirement traceability, `forbidden_behaviours` | `benchmark/gold/<system>.json` |
| **BR-08** | **Behavioral oracle file** per evaluated system — min 8 oracles (see §10.3) | `benchmark/oracles/systems/<system>.json` |
| **BR-09** | **Perturbation variant file** per evaluated system — 5 types × 1 variant minimum | `benchmark/perturbations/variants/<system>.json` |
| **BR-10** | JSON schemas for oracle and perturbation files | `benchmark/oracles/schema.json`, `benchmark/perturbations/schema.json` |
| **BR-11** | Trace simulator with guard evaluation semantics (see §10.4) | `scripts/fsm_benchmark/trace_simulator.py` |
| **BR-12** | Campaign manifest schema with `frozen_at`, provenance | `experiments/campaigns/*.json` |
| **BR-13** | Append-only run registry | `experiments/registry/run_index.jsonl` |
| **BR-14** | Replication package builder | `replication/build_replication_package.sh` |

### 9.3 Gold FSM coverage target

| Tier | Systems | Count | Rationale |
|------|---------|------:|-----------|
| **Tier A (mandatory)** | `vending_machine`, `atm`, `login_system`, `access_control`, `elevator`, `ticket_machine` | 6 | Span transactional, security, concurrent; IST difficulty extremes |
| **Tier B (required)** | `ecommerce_checkout`, `medical_appointment_booking`, `hotel_booking`, `smart_thermostat`, `library_loan`, `parking_gate` | 6 | Invariant-heavy and booking flows |
| **Tier C (stretch)** | Remaining 8 systems | 8 | Full-domain coverage for EMSE comprehensiveness |
| **Minimum for inference** | Tier A + B | **12** | Power analysis anchor (§14) |
| **Target** | All 20 | **20** | Full benchmark parity |

**Approval gate:** `metadata.status = "approved"` + reviewer sign-off + automated `validate_gold.py` score = 100.

### 9.4 Oracle coverage requirements (per system)

| Oracle category | Min count | Description |
|-----------------|----------:|-------------|
| `positive_trace` | 3 | Valid sequences → expected state |
| `negative_trace` | 2 | Forbidden sequences → must reject or remain in safe state |
| `invariant_check` | 2 | Global properties after valid prefixes |
| `requirement_binding` | 1 | Specific Rn must be exercised |
| **Total** | **8** | Minimum per system in Tier A/B |

For Tier C systems: minimum 5 oracles (3 positive, 2 negative) acceptable.

### 9.5 Perturbation requirements (per system)

| Perturbation type | Variants | Seed control |
|-------------------|----------|--------------|
| `paraphrase` | 1 | Fixed template + seed |
| `ordering` | 1 | Fixed permutation seed |
| `omission` | 1 | Rotate which Rn omitted (document which) |
| `negation_flip` | 1 | Single invariant Rn |
| `ambiguity_injection` | 0–1 | Optional for Tier A only |

Each variant MUST include `expected_behavior_change` hypothesis field for interpretability.

---

## 10. Behavioral evaluation design

### 10.1 Eligibility strata

Behavioral evaluation runs on **cleaned FSM JSON** from generation campaigns. Report results in strata:

| Stratum | Filter | Purpose |
|---------|--------|---------|
| **S0** | All runs | Population overview |
| **S1** | G1 pass | Parsed FSMs |
| **S2** | G2 pass | Schema-valid (primary behavioral input) |
| **S3** | G3 pass (nested) | Structurally deterministic |
| **S4** | G3′ pass (guard-aware) | Construct-refined determinism |

Primary RQ1–RQ3 reported on **S2** (G2 pass) to measure behavioral failure among "usable" structural artefacts. Sensitivity analysis on S3 and S4.

### 10.2 Oracle execution algorithm

```
INPUT:  FSM F, oracle file O, guard semantics G
OUTPUT: per-oracle pass/fail + failure code

for each oracle o in O:
    if o.category == positive_trace:
        state ← simulate(F, o.trace, G)
        PASS iff state == o.expected.final_state
    if o.category == negative_trace:
        result ← simulate(F, o.trace, G)
        PASS iff result.rejected OR NOT o.expected.forbidden_state_reached
    if o.category == invariant_check:
        PASS iff invariant holds after all prefixes of o.trace
    if o.category == requirement_binding:
        PASS iff trace fires ≥1 transition citing o.requirement_refs

oracle_pass_rate = |passed| / |O|
```

Implement in `scripts/run_behavioral_evaluation.py`; core logic in `scripts/fsm_benchmark/trace_simulator.py`.

### 10.3 Guard semantics (G)

| Guard type | Evaluation rule |
|------------|-----------------|
| Empty guard | Always enabled |
| Boolean literal | Parse true/false |
| Comparison | Parse `var op value` when decidable |
| Natural language | **Conservative:** if not decidable, mark oracle **not evaluable** (exclude from denominator with reporting) |

Document non-decidable rate per system. This addresses IST guard-aware threat.

### 10.4 Gold alignment metrics

| Metric | Symbol | Definition |
|--------|--------|------------|
| Gold structural similarity | `GSS` | Normalised Jaccard on `(source, event, target)` tuples after name normalisation |
| Gold behavioral alignment | `GBA` | Fraction of gold positive traces accepted by generated FSM |
| Gold forbidden violation rate | `GFV` | Fraction of gold forbidden traces incorrectly accepted |
| Gold requirement recall | `GRR` | Gold requirements cited in generated FSM / total gold requirements |

Port composite definitions from IST `docs/gold_standard_strategy.md` §5.

### 10.5 Behavioral failure taxonomy

| Code | Label | Detection |
|------|-------|-----------|
| `BF-01` | Wrong terminal state | positive_trace failure |
| `BF-02` | Forbidden trace accepted | negative_trace failure |
| `BF-03` | Invariant violated | invariant_check failure |
| `BF-04` | Requirement not exercised | requirement_binding failure |
| `BF-05` | Trace stuck (no transition) | simulator rejection |
| `BF-06` | Non-deterministic resolution | multiple enabled transitions |
| `BF-07` | Not evaluable (guard) | excluded from rate |

Primary failure mode per run = most severe code by order BF-02 > BF-03 > BF-01 > BF-04 > BF-05 > BF-06.

---

## 11. Robustness evaluation design

### 11.1 Paired design

For each `(model m, system s, perturbation type p)`:

1. **Baseline** FSM: generated from unperturbed requirements (reuse IST output if available in imported freeze).
2. **Perturbed** FSM: generate from `perturbations/variants/<s>.json` variant of type `p`.
3. Compute **paired deltas** on same metrics.

| Delta metric | Formula |
|--------------|---------|
| `Δ_G3` | G3_pass(perturbed) − G3_pass(baseline) |
| `Δ_oracle` | oracle_pass_rate(perturbed) − oracle_pass_rate(baseline) |
| `Δ_GSS` | GSS(perturbed) − GSS(baseline) |
| `Jaccard_trans` | \|T(perturbed) ∩ T(baseline)\| / \|T(perturbed) ∪ T(baseline)\| |

### 11.2 Experimental unit

**Unit of analysis:** `(model, system, perturbation_type)` with paired baseline.

### 11.3 Factorial structure (robustness campaign)

```
MODELS (6 mandatory) × SYSTEMS (12 min) × PERT_TYPES (4 core) = 288 cells
Each cell: 1 perturbed generation (+ baseline from store)
```

Optional: `ambiguity_injection` on Tier A only (+36 cells).

### 11.4 Controls

| Control | Value |
|---------|-------|
| Same prompt version | Yes |
| Same model digest | Yes |
| Same temperature | 0.0 |
| Same structured output | true |
| Perturbation seed | Fixed in JSON spec |

---

## 12. Reproducibility evaluation design

### 12.1 Rationale

IST assumed T=0.0 yields deterministic outputs. Empirical SE requires **evidence**. Some Ollama backends may still exhibit variability (sampling implementation, floating kernels, batch effects).

### 12.2 Repeat protocol

| Parameter | Value |
|-----------|-------|
| Temperature | 0.0 |
| Repeats (K) | **5** per (model, system) |
| Prompt | Identical bytes |
| Model | 6 mandatory models |
| Systems | **10** stratified sample (see §12.3) |
| Total runs | 6 × 10 × 5 = **300** |

### 12.3 System sample for reproducibility (n=10)

Stratified by IST nested G3 difficulty:

| Stratum | Systems | Count |
|---------|---------|------:|
| Zero G3 (IST) | `atm`, `login_system`, `ticket_machine` | 3 |
| Mid G3 | `elevator`, `medical_appointment_booking`, `hotel_booking` | 3 |
| High G3 (71.4%) | `vending_machine`, `access_control`, `bike_rental` | 3 |
| Outlier | `phi3:14b`-sensitive: `restaurant_reservation` | 1 |

### 12.4 Reproducibility metrics

| Metric | Definition | Stability tier (RQ7) |
|--------|------------|----------------------|
| `exact_replication_rate` | Fraction of K runs with identical cleaned JSON hash | High if ≥ 0.95 |
| `structural_jaccard_mean` | Mean pairwise Jaccard on transition sets | High if ≥ 0.90 |
| `oracle_pass_variance` | Variance of oracle_pass_rate across K runs | Low if ≤ 0.01 |
| `G3_flip_rate` | Fraction of cells where G3 pass differs across K runs | Low if = 0 |
| `token_length_cv` | CV of output token count | Informational |

**Stability classification (RQ7):**

| Tier | Criteria | Cross-study use |
|------|----------|-----------------|
| **Stable** | exact_replication ≥ 0.95 AND oracle variance ≤ 0.01 | Comparable without replication |
| **Moderate** | structural_jaccard ≥ 0.90 | Requires same manifest |
| **Unstable** | otherwise | Full replication required |

---

## 13. Experimental factors

### 13.1 Independent variables

| Factor | Symbol | Type | Levels | Campaign |
|--------|--------|------|--------|----------|
| LLM model | `M` | Categorical | 6 mandatory (+ optional 32B exploratory) | All |
| System | `S` | Categorical | 12–20 | All |
| Perturbation type | `P` | Categorical | none, paraphrase, ordering, omission, negation_flip [, ambiguity] | Robustness |
| Repeat index | `R` | Ordinal | 1…K=5 | Reproducibility |
| Structural stratum | — | Derived | S1–S4 | Analysis |
| Domain | `D` | Categorical | 20 domain labels | Covariate |
| Model family | — | Derived | code-specialised vs general | RQ9 |
| Invariant density | `I` | Continuous | # "must not" reqs / total | Covariate |

**Model family classification:**

| Family | Models |
|--------|--------|
| Code-specialised | `qwen2.5-coder:7b`, `qwen2.5-coder:14b` [, `qwen2.5-coder:32b`] |
| General | `llama3.1:8b`, `mistral-nemo:12b`, `gemma2:9b`, `phi3:14b` |

### 13.2 Controlled variables (fixed)

| Variable | Value | Record in manifest |
|----------|-------|-------------------|
| Temperature | 0.0 | Yes |
| `num_ctx` | 8192 | Yes |
| Structured output | true (primary) | Yes |
| Prompt version | `experimental_prompts.md` hash | Yes |
| Ollama version | `ollama --version` | Yes |
| Model digest | `ollama show <model>` | Yes |
| Git commit | `git rev-parse HEAD` | Yes |
| Upstream dataset pin | `upstream_manifest.json` hash | Yes |

### 13.3 Blocking and randomisation

- **Block by model** during execution (VRAM management).
- **System order** within model: alphabetical (replicable; not random — intentional for resume).
- **Perturbation order:** fixed (paraphrase → ordering → omission → negation_flip).
- No randomisation needed for reproducibility repeats (same condition).

---

## 14. Dependent variables

### 14.1 Structural (inherited / replicated)

| Variable | Type | Range | Source |
|----------|------|-------|--------|
| `valid_json` (G1) | Binary | {0,1} | evaluate.py |
| `schema_valid` (G2) | Binary | {0,1} | evaluate.py |
| `deterministic` (G3 strict) | Binary | {0,1} | evaluate.py |
| `deterministic_guard_aware` (G3′) | Binary | {0,1} | guard_relabel.py |
| `requirement_coverage` | Continuous | [0,1] | metrics.py |
| `nondeterministic_pairs` | Count | ≥0 | metrics.py |
| `unreachable_states` | Count | ≥0 | metrics.py |
| `num_states`, `num_events`, `num_transitions` | Count | ≥0 | metrics.py |

### 14.2 Behavioral

| Variable | Type | Range | Source |
|----------|------|-------|--------|
| `oracle_pass_rate` | Continuous | [0,1] | behavioral eval |
| `oracle_pass_count` | Count | ≥0 | behavioral eval |
| `oracle_evaluable_count` | Count | ≥0 | behavioral eval |
| `primary_failure_mode` | Categorical | BF-01…BF-07 | behavioral eval |
| `GSS` | Continuous | [0,1] | gold compare |
| `GBA` | Continuous | [0,1] | gold compare |
| `GFV` | Continuous | [0,1] | gold compare |
| `GRR` | Continuous | [0,1] | gold compare |
| `structural_behavioral_gap` | Continuous | G3_pass − oracle_pass (on S2) | derived |

### 14.3 Robustness

| Variable | Type | Source |
|----------|------|--------|
| `Δ_G3`, `Δ_G2`, `Δ_oracle`, `Δ_GSS` | Continuous [-1,1] | paired compare |
| `Jaccard_trans` | Continuous [0,1] | paired compare |
| `perturbation_success` | Binary | generation succeeded |

### 14.4 Reproducibility

| Variable | Type | Source |
|----------|------|--------|
| `exact_replication_rate` | Continuous [0,1] | reproducibility_stats.py |
| `structural_jaccard_mean` | Continuous [0,1] | reproducibility_stats.py |
| `oracle_pass_variance` | Continuous | reproducibility_stats.py |
| `G3_flip_rate` | Continuous [0,1] | reproducibility_stats.py |
| `metric_stability_tier` | Ordinal {Stable, Moderate, Unstable} | reproducibility_stats.py |

### 14.5 Primary study endpoints (pre-registered)

| Priority | Endpoint | RQ |
|----------|----------|-----|
| **Primary** | `oracle_pass_rate` on S2 (G2 pass) | RQ1 |
| **Primary** | `structural_behavioral_gap` (G2_pass rate − oracle_pass rate on S2) | RQ1 |
| **Primary** | Mean \|Δ_oracle\| by perturbation type | RQ5 |
| **Primary** | `exact_replication_rate` distribution | RQ6 |
| Secondary | `GBA`, failure taxonomy counts | RQ2, RQ3 |
| Secondary | G3′ vs G3 difference | RQ8 |

---

## 15. Campaign design and execution plan

### 15.1 Campaign overview

| Campaign ID | Purpose | Runs (est.) | Depends on |
|-------------|---------|------------:|------------|
| `C0_spot_check` | Validate IST metric parity (10% sample) | 14 | IST freeze import |
| `C1_behavioral_baseline` | Generate if not reusing IST outputs; else evaluate oracles on imported cleaned JSON | 0–140 | C0 |
| `C2_oracle_eval` | Run oracles on all G2+ FSMs for Tier A+B systems | ≤ 72×6 = 432 oracle executions | C1, gold+oracles approved |
| `C3_robustness` | Perturbed generation | 288–324 | C1 baseline pairs |
| `C4_reproducibility` | K=5 repeats | 300 | — |
| `C5_guard_relabel` | Guard-aware G3 on IST/all outputs | offline | C1 |
| `C6_structured_ablation` | Optional RQ extension | 120 | separate prompt condition |

### 15.2 Campaign C1 — Behavioral baseline

**Preferred path (compute-efficient):**

1. Import IST cleaned outputs (`outputs/cleaned/`) with manifest `20260602T195520Z`.
2. Run C0 spot-check (14 runs): re-generate and compare metrics.
3. If spot-check passes, **do not re-generate** full 140; use IST outputs as C1.

**Fallback:** Full regeneration if spot-check fails or IST outputs unavailable.

Record decision in `experiments/campaigns/C1_behavioral_baseline.json`.

### 15.3 Campaign C2 — Oracle evaluation

```bash
python3.12 scripts/run_behavioral_evaluation.py \
  --campaign-id C2_oracle_eval \
  --systems-tier AB \
  --input-stratum G2
```

Output: `results/behavioral/oracle_results.csv`

### 15.4 Campaign C3 — Robustness

```bash
python3.12 scripts/run_robustness_evaluation.py \
  --campaign-id C3_robustness \
  --perturbation-types paraphrase,ordering,omission,negation_flip \
  --models mandatory \
  --systems-tier AB
```

### 15.5 Campaign C4 — Reproducibility

```bash
python3.12 scripts/run_reproducibility_campaign.py \
  --campaign-id C4_reproducibility \
  --repeats 5 \
  --systems reproducibility_sample_10.txt \
  --models mandatory
```

### 15.6 Campaign C6 — Structured output ablation (optional)

Execute only if page budget and compute allow. Supports comparison to IST RQ4 gap.

| Condition | Structured output |
|-----------|-------------------|
| A | true (default) |
| B | false |

120 runs (6×20). Not required for primary EMSE claims.

### 15.7 Pilot acceptance criteria (before full campaigns)

| Pilot | Scope | Pass criterion |
|-------|-------|----------------|
| Gold authoring | Tier A, 2 systems | Reviewer approved; validate_gold.py = 100 |
| Oracle engine | Tier A, 2 systems | ≥95% agreement with manual trace adjudication on 20 traces |
| Perturbation gen | 1 system, all types | Deterministic regeneration given seed |
| Reproducibility | 1 model × 2 systems × K=5 | Pipeline completes; variance metrics computed |

---

## 16. Reproducibility strategy (open science)

### 16.1 Pre-registration checklist

Before freezing any campaign:

- [ ] This `study_design.md` committed at tag `study-design-v1.0`
- [ ] Primary endpoints listed in §14.5 unchanged
- [ ] Analysis script paths documented in §18
- [ ] Hypothesis families and α correction method fixed
- [ ] System tier lists frozen in campaign manifest

Optional: OSF or Zenodo pre-registration of analysis plan (recommended for EMSE).

### 16.2 Provenance capture (every run)

Append to `experiments/registry/run_index.jsonl`:

```json
{
  "run_id": "uuid",
  "campaign_id": "C3_robustness",
  "model": "qwen2.5-coder:14b",
  "system": "atm",
  "perturbation_variant": "omission_R7",
  "repeat_index": 1,
  "git_commit": "...",
  "ollama_version": "...",
  "model_digest": "...",
  "prompt_hash": "sha256:...",
  "upstream_manifest_hash": "sha256:...",
  "timestamp_utc": "...",
  "status": "completed",
  "output_paths": { "raw": "...", "cleaned": "..." }
}
```

### 16.3 Artifact publication tiers

| Tier | Content | When |
|------|---------|------|
| **T1 (Git)** | Code, schemas, oracles, perturbations, docs, campaign manifests | Continuous |
| **T2 (Zenodo v1.0.0)** | Frozen metrics CSV, selected cleaned outputs, replication zip | Submission |
| **T3 (Supplementary)** | Full run registry, raw outputs (optional) | Reviewer request |

### 16.4 Independent replication path

Document in `REPRODUCIBILITY.md`:

1. Install from Git tag `v1.0.0`
2. Import FSM-Bench-20 requirements
3. Pull Ollama models with digest verification
4. Recreate prompts from spec hash
5. Run `./run_all.sh` OR step-through campaigns
6. Compare checksums to `replication/MANIFEST.txt`

### 16.5 Metric parity with IST

When citing IST structural numbers:

- Reference manifest `20260602T195520Z` explicitly
- Report whether values are **imported** or **replicated**
- Include C0 spot-check results in appendix

---

## 17. Statistical analysis plan

### 17.1 Software

- **Python 3.12:** `pandas`, `scipy`, `statsmodels`, `numpy`
- Scripts: `analysis/behavioral_failure_analysis.py`, `analysis/robustness_stats.py`, `analysis/reproducibility_stats.py`, `analysis/model_comparison_tests.py`

### 17.2 Descriptive analysis (all RQs)

- Rates with **95% Wilson confidence intervals**
- Report **n** at every aggregation level
- Stratify by S2/S3/S4 for RQ1

### 17.3 Inferential tests

| Comparison | Test | Effect size |
|------------|------|-------------|
| Oracle pass vs 0.85 (H1) | One-proportion z-test | Cohen's h |
| Paired perturbation deltas (H6, H7) | Wilcoxon signed-rank | Rank-biserial r |
| Model differences in oracle rate (H0-M) | Kruskal–Wallis | ε² |
| Perturbation type differences (H0-P) | Friedman | Kendall's W |
| Correlation oracle vs coverage (H3) | Williams test | — |
| Oracle category failures (H4) | χ² or Fisher exact | Cramér's V |

**Multiple comparisons:** Benjamini–Hochberg FDR within each hypothesis family.

### 17.4 Power and sample size justification

| Analysis | n | Justification |
|----------|---|---------------|
| RQ1 (G2 stratum) | ~110 FSMs from IST (86 expected G2 on Tier A+B subset) | Binomial CI width ~±10 pp at n=86 |
| RQ4/RQ5 robustness | 288 paired cells | Detect δ=0.15 oracle delta with power >0.80 (paired Wilcoxon sim) |
| RQ6 reproducibility | 60 cells × K=5 | Characterise variance; not powered for tiny effects |
| RQ9 model comparison | 6 models × 12 systems | EMSE norm: descriptive + non-parametric; avoid claiming equivalence |

### 17.5 Handling missing/failed runs

| Case | Rule |
|------|------|
| Invalid JSON | Exclude from S2+; report in S0 |
| Oracle not evaluable (guard) | Exclude from denominator; report count |
| Perturbation generation fail | Record status=failed; impute not allowed |
| phi3:14b known instability | Include in mandatory set with explicit sensitivity analysis excluding phi3 |

---

## 18. Implementation mapping

### 18.1 Repository structure → study components

| Study component | Path |
|-----------------|------|
| Study design (this doc) | `paper/notes/study_design.md` |
| Operational protocols | `llm-fsm-behavioral-benchmark/docs/*_protocol.md` |
| Gold FSMs | `benchmark/gold/` |
| Oracles | `benchmark/oracles/systems/` |
| Perturbations | `benchmark/perturbations/variants/` |
| Campaign configs | `experiments/campaigns/C*.json` |
| Run log | `experiments/registry/run_index.jsonl` |
| Structural metrics | `results/structural/metrics.csv` |
| Behavioral results | `results/behavioral/oracle_results.csv` |
| Robustness results | `results/robustness/perturbation_results.csv` |
| Reproducibility | `results/reproducibility/variance_summary.json` |
| Analysis exports | `analysis/exports/` |
| Paper tables | `paper/tables/table_*.tex` |
| Paper figures | `paper/figures/` |

### 18.2 Script development order

| Phase | Deliverable | Acceptance |
|-------|-------------|------------|
| 1 | `import_upstream_dataset.py`, `validate_integrity.py`, `schema.py` | CI green |
| 2 | `validate_gold.py`, gold Tier A (6 systems) | Reviewer sign-off |
| 3 | `trace_simulator.py`, oracle schemas, Tier A oracles | Pilot 95% adjudication |
| 4 | `run_behavioral_evaluation.py`, `evaluate.py` extensions | C2 on pilot |
| 5 | `generate_perturbations.py`, `run_robustness_evaluation.py` | C3 pilot |
| 6 | `run_reproducibility_campaign.py`, `reproducibility_stats.py` | C4 pilot |
| 7 | `guard_relabel.py` | RQ8 report |
| 8 | `analysis/export_summary_tables.py`, `paper/scripts/update_results_artifacts.py` | Tables regenerate |
| 9 | `replication/build_replication_package.sh` | Zenodo dry run |

### 18.3 Manuscript section mapping

| Section | Content source |
|---------|----------------|
| §4 Methodology | §9–§16 of this document |
| §5 Behavioral design | §10 |
| §6 Robustness design | §11 |
| §7 Reproducibility design | §12 |
| §8 Results | `results/*`, `analysis/exports/*` |
| §10 Threats | §19 below |

---

## 19. Threats to validity

### 19.1 Internal validity

| Threat | Mitigation |
|--------|------------|
| Oracle bias from same author | Independent oracle review; dual gold/requirement oracles |
| Guard semantics ambiguity | Report not-evaluable rate; conservative rules |
| Baseline–perturbation pairing errors | Manifest links variant_id → baseline run_id |
| Instrumentation drift | Frozen campaign; git tag on freeze |

### 19.2 External validity

| Threat | Mitigation |
|--------|------------|
| 20 English systems only | Explicit language/domain limitation |
| Local Ollama quantisation | Record model digests; no cloud generalisation claim |
| Single-shot generation | Discuss iterative refinement as future work |
| MBT practitioner variance | Offline study; user study out of scope |

### 19.3 Construct validity

| Threat | Mitigation |
|--------|------------|
| G3 guard-blind (IST) | G3′ guard-aware reanalysis (RQ8) |
| Coverage as proxy | Demonstrate decoupling with behavioral endpoints (H3) |
| Oracle completeness | Minimum 8 oracles/system; forbidden traces |
| Gold FSM correctness | Dual review + automated consistency score 100 |

### 19.4 Conclusion validity

| Threat | Mitigation |
|--------|------------|
| Multiple comparisons | FDR correction; pre-registered families |
| Clustering by system/model | Report hierarchical aggregates; system as blocking factor in discussion |
| Optional 32B exploratory | Separate exploratory subsection; not primary inference |
| phi3 outlier | Sensitivity analysis excluding phi3 |

---

## 20. Publication risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **R1: Reviewers view as incremental over IST** | High | Desk reject | EMSE framing: behavioral gap study; IST as baseline; new endpoints |
| **R2: Insufficient gold/oracle rigor** | Medium | Major revision | 12+ approved gold; reviewer sign-off; κ reporting |
| **R3: Negative result (oracles mostly pass)** | Low–Medium | Weakened narrative | Still publishable: tightens practitioner confidence; report CIs |
| **R4: Reproducibility variance too low to interest** | Medium | Section weakness | Focus on behavioral variance; honest reporting |
| **R5: Compute limits → incomplete Tier C** | Medium | Scope criticism | Pre-commit to Tier A+B (12 systems) as minimum |
| **R6: Guard semantics dispute** | Medium | Construct attack | Conservative evaluability; sensitivity appendix |
| **R7: Zenodo/package incomplete at review** | Medium | Transparency rejection | Dry-run replication package before submission |
| **R8: EMSE length limits** | Medium | Cut robustness or reproducibility | Prioritise behavioral (RQ1–3) in main text; robustness/repro in dedicated sections |
| **R9: Simultaneous IST publication confusion** | Medium | Citation overlap | Cross-cite clearly; different RQs and contributions |
| **R10: Statistical power insufficient for model ranking** | High | Overclaim risk | **Avoid** "best model" claims; report descriptive ranks + CIs only |

---

## 21. Success criteria

| Criterion | Target | Measurement |
|-----------|--------|-------------|
| Gold FSMs approved | ≥ 12 (Tier A+B) | `metadata.status` |
| Oracle coverage | ≥ 8 oracles/system (Tier A+B) | oracle JSON validation |
| C0 IST parity | ≤ 2 pp deviation on G1–G3 | spot-check report |
| Behavioral gap quantified | `structural_behavioral_gap` reported with 95% CI | C2 results |
| Robustness campaign complete | ≥ 95% cells succeeded | C3 manifest |
| Reproducibility campaign complete | 300/300 runs | C4 manifest |
| Replication package | Zenodo dry-run passes checksum audit | replication/MANIFEST.txt |
| Pre-registered analysis executed | All §8 hypotheses tested or marked exploratory | analysis log |
| Manuscript traceability | Every figure/table maps to `results_mapping.md` | audit |

---

## 22. Timeline and milestones

| Milestone | Deliverable | Gate |
|-----------|-------------|------|
| **M1** | Study design frozen (this document v1.0) | CP-010 |
| **M2** | Import IST outputs + C0 spot-check | Parity report |
| **M3** | Tier A gold + oracles (6 systems) | Pilot pass |
| **M4** | Tier B gold + oracles (6 systems) | 12 systems ready |
| **M5** | C2 oracle evaluation complete | oracle_results.csv frozen |
| **M6** | C3 robustness complete | perturbation_results.csv frozen |
| **M7** | C4 reproducibility complete | variance_summary.json frozen |
| **M8** | Analysis + inferential tests | analysis/exports/ |
| **M9** | Results freeze + replication package | CP-080 |
| **M10** | Manuscript draft | CP-090 |
| **M11** | Submission | CP-100 |

---

## 23. Ethical and resource considerations

- **No human subjects** — synthetic requirements and LLM outputs only.
- **No proprietary data** — open benchmark inherited from FSM-Bench-20.
- **Compute estimate:** ~750–900 generation runs (C3+C4+contingency) + oracle/simulation (CPU-bound) on 1× RTX 4090; ~80–120 GPU-hours.
- **Energy reporting:** Log total GPU wall time per campaign in manifest.
- **Model licenses:** MIT artifact; Ollama model licenses documented in replication package.

---

## 24. Key quantitative predictions (from IST — directional, not claims)

Used for pilot sanity checks only:

| Prediction | IST evidence | EMSE test |
|------------|--------------|-----------|
| G2 pass rate ≈ 75–80% | 78.6% at 140 runs | C0/C1 |
| G3 pass rate ≈ 28–35% | 31.4% nested | C0/C1 |
| Oracle pass < G2 pass on S2 | Qualitative decoupling | RQ1/H1 |
| `atm`, `login_system` behavioral failure | 0% IST G3 | RQ10/H5 |
| Coverage weakly predicts oracle pass | \|r\| ≤ 0.16 vs G3 | H3 |

If pilot diverges >15 pp from predictions, investigate prompt/import drift before scaling.

---

## 25. Document approval

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Primary investigator | Cesar Andres Sanchez | 2026-06-03 | — |
| Oracle reviewer | TBD | — | — |
| Gold reviewer | TBD | — | — |

---

## Appendix A — IST 2026 reference statistics (frozen)

Authoritative source: `~/papers/ist2026/paper/final_results_freeze_140.md`

| Metric | Value (n=140) |
|--------|---------------|
| G1 valid JSON | 98.6% (138/140) |
| G2 schema-valid | 78.6% (110/140) |
| G3 nested deterministic | 31.4% (44/140) |
| Mean requirement coverage | 69.2% |
| G3 failures among G2 passers | 60.0% (66/110) |
| Missing R1 citation | 97.9% (137/140) |
| Hardest systems (0% G3) | atm, login_system, online_examination, package_locker, restaurant_reservation, ticket_machine |

## Appendix B — Model × system grid (mandatory)

6 models × 20 systems = 120 runs (IST completed). EMSE behavioral/robustness focuses on Tier A+B = 12 systems × 6 models = 72 baseline cells minimum.

## Appendix C — Oracle authorship worksheet (template)

For each system, complete before approval:

| Field | Value |
|-------|-------|
| system_id | |
| gold_author | |
| gold_reviewer | |
| oracle_author | |
| oracle_reviewer | |
| manual_adjudication_sample_size | ≥ 20 traces |
| agreement_rate | ≥ 95% target |
| approved_date | |

---

*End of study design v1.0. Implement from §18. Do not modify primary endpoints after campaign freeze without versioning this document.*
