# Evaluation Protocol — FSM-Behavior-Bench

**Project:** LLM-FSM Behavioral Benchmark  
**Artifact:** FSM-Behavior-Bench (extends FSM-Bench-20)  
**Runtime:** Ollama (local, no paid APIs)  
**Target venue:** Empirical Software Engineering (EMSE)  
**Status:** Draft — skeleton phase

---

## 1. Research questions

| ID | Research question |
|----|-------------------|
| **RQ1 (Structural)** | To what extent do local LLMs produce structurally valid and deterministic FSMs, replicating the FSM-Bench-20 gate findings? |
| **RQ2 (Behavioral)** | How often do structurally valid FSMs pass behavioral oracles derived from requirements and gold reference traces? |
| **RQ3 (Behavioral)** | Which failure modes dominate when LLM FSMs are structurally valid but behaviorally incorrect? |
| **RQ4 (Robustness)** | How sensitive is FSM generation quality to controlled requirement perturbations (paraphrase, omission, ordering)? |
| **RQ5 (Robustness)** | Do code-specialised models exhibit lower perturbation sensitivity than general chat models? |
| **RQ6 (Reproducibility)** | What is the run-to-run variance in FSM structure and behavioral scores under fixed temperature and prompts? |
| **RQ7 (Reproducibility)** | Which metrics are stable enough for cross-study comparison without full campaign replication? |

---

## 2. Hypotheses

| ID | Hypothesis |
|----|------------|
| **H1** | A substantial fraction of G2-passing FSMs fail at least one behavioral oracle (structural validity is insufficient). |
| **H2** | Oracle failures cluster on invariant (“must not”) and guard-heavy requirements. |
| **H3** | Paraphrase perturbations cause smaller quality degradation than omission or negation-flip perturbations. |
| **H4** | Code-specialised models show lower structural Jaccard variance across reproducibility repeats. |
| **H5** | Behavioral pass rate correlates more strongly with gold trace alignment than with requirement citation coverage alone. |
| **H6** | Null hypothesis (H0): no significant model differences in oracle pass rate — test with appropriate non-parametric tests. |

---

## 3. Evaluation pillars

| Pillar | Inherited from IST | EMSE extension |
|--------|-------------------|----------------|
| Structural | G1–G3 gates, coverage, determinism | Baseline replication on same 20 systems |
| Behavioral | Gold placeholders only | Oracle execution, trace simulation, gold alignment |
| Robustness | Not evaluated | Perturbation suite with fixed seeds |
| Reproducibility | Single-run (T=0) | Multi-run repeats with variance metrics |

Detailed protocols:

- Structural: inherit `docs/evaluation_protocol.md` gates from FSM-Bench-20 (see `docs/UPSTREAM_DEPENDENCY.md`)
- Behavioral: `docs/behavioral_evaluation_protocol.md`
- Robustness: `docs/robustness_protocol.md`
- Reproducibility: `docs/reproducibility_protocol.md`

---

## 4. Independent variables

| Variable | Type | Levels / values |
|----------|------|-----------------|
| **LLM model** | Categorical | TBD — inherit FSM-Bench-20 model set |
| **Application domain** | Categorical | 20 domains |
| **System** | Categorical | 20 systems |
| **Perturbation type** | Categorical | none, paraphrase, ordering, omission, ambiguity, negation_flip |
| **Reproducibility repeat** | Ordinal | 1…K (fixed K TBD) |
| **Structured output** | Boolean | true (primary) vs false (ablation, optional) |

---

## 5. Dependent variables

### 5.1 Structural (inherited)

| Variable | Description |
|----------|-------------|
| G1–G3 pass | Nested structural gates |
| `requirement_coverage` | Fraction of requirements cited |
| `determinism_rate` | No duplicate `(source, event)` pairs |

### 5.2 Behavioral (new)

| Variable | Description |
|----------|-------------|
| `oracle_pass_rate` | Fraction of oracles passed per FSM |
| `trace_simulation_success` | Fraction of positive traces executable |
| `invariant_violation_count` | Negative oracle failures |
| `gold_structural_similarity` | Graph similarity vs approved gold |
| `gold_behavioral_alignment` | Trace agreement vs gold FSM |

### 5.3 Robustness (new)

| Variable | Description |
|----------|-------------|
| `perturbation_delta_g3` | Change in G3 pass under perturbation |
| `perturbation_delta_oracle` | Change in oracle pass rate |
| `structural_jaccard_vs_base` | Structural similarity to unperturbed run |

### 5.4 Reproducibility (new)

| Variable | Description |
|----------|-------------|
| `cross_run_structural_jaccard` | Mean pairwise Jaccard across repeats |
| `cross_run_oracle_variance` | Variance of oracle pass rate |
| `exact_replication_rate` | Fraction of identical cleaned JSON outputs |

---

## 6. Campaign design (planned)

| Campaign | Purpose | Planned runs |
|----------|---------|--------------|
| `structural_baseline` | Replicate G1–G3 on 20×N models | TBD |
| `behavioral_oracles` | Oracle evaluation on G2+ outputs | TBD |
| `robustness_perturbations` | Perturbation variants × models | TBD |
| `reproducibility_repeats` | K repeats per (model, system) | TBD |

Campaign manifests: `experiments/campaigns/`

---

## 7. Statistical analysis plan (placeholder)

- Descriptive statistics for all primary metrics
- Non-parametric tests for model comparisons (Kruskal-Wallis, pairwise with correction)
- Effect sizes (Cliff's delta or rank-biserial) where applicable
- Robustness: mixed-effects or stratified comparison by perturbation type
- Reproducibility: ICC or coefficient of variation for continuous metrics

Analysis scripts: `analysis/` (separate from experiment driver)

---

## 8. Related documents

- `docs/behavioral_evaluation_protocol.md`
- `docs/robustness_protocol.md`
- `docs/reproducibility_protocol.md`
- `docs/experimental_prompts.md`
- `docs/UPSTREAM_DEPENDENCY.md`
- `experiments/README.md`
