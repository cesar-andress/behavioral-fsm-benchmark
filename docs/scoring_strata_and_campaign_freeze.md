# Scoring strata, structural gates, and frozen C1/C2 campaigns

**Document ID:** `scoring_strata_v0.1.1`  
**Repository:** `behavioral-fsm-benchmark`  
**Status:** Terminology alignment with the EMSE manuscript (*Beyond Structural Validity*) and frozen C1/C2 run records  
**Evaluator code:** unchanged since `v0.1.0` (documentation patch only)

---

## 1. Structural gates (recorded fields)

| Gate | Recorded field | Definition |
|------|----------------|------------|
| **G1** | (run eligibility) | Run reached JSON extraction / parsing without hard failure at generation or JSON extraction |
| **G2 pass** | `schema_valid` **and** `referential_valid` | JSON validates against `generated_fsm.schema.json` **and** `initial_state`, every transition `source`, and every transition `target` appear in `states` |
| **G3** | `strict_deterministic` | Strict `(source, event)` determinism (no duplicate pairs) |
| **G3a** | `guard_aware_deterministic` | Guard-aware determinism on `(source, event)` groups |

**G3 and G3a** are **post-G2 structural determinism checks** reported on **G2-pass runs**. They are evaluated **in parallel** on that stratum; **neither is a prerequisite for the other**. **G3a may exceed G3** when guard-aware analysis accepts transitions rejected by strict duplicate `(source, event)` checking.

G1–G2 describe population-wide or G1-conditioned pass rates in campaign summaries. G3/G3a proportions in manuscript-style tables use **G2-pass denominators** (e.g. `163/189` for G3 on the combined C1+C2 campaign).

---

## 2. Behavioral scoring hard stops

| Condition | Behavioral fields in `metrics.csv` |
|-----------|-----------------------------------|
| Parsing failure or JSON **schema** validation failure (`schema_valid=false`) | `behavioral_pass_rate` and related behavioral columns **empty / null** — run is **behaviorally non-scored** |
| `schema_valid=true` with `referential_valid=false` | Behavioral oracles **may still run** on the parsed FSM object; non-null BPR is an **oracle-on-parsed-object** reading (referential closure is recorded for G2 accounting but does not short-circuit evaluation in the Ollama campaign path) |

Referential-invalid simulation semantics: the simulator does not pre-filter transitions failing referential closure; see `experiments/analysis/C1_C2_evaluable_stratum_audit.md` §3 and the manuscript Empirical Setting (referential-oracle execution).

---

## 3. Named scoring strata (frozen C1+C2, N=240)

Combined campaign: **C1 pilot** (60 runs) + **C2 core** (180 runs).

| Stratum | Definition | Count (frozen exports) |
|---------|------------|------------------------|
| **Behaviorally scored** | Non-null `behavioral_pass_rate` after successful schema validation | **209** (87.1%) |
| **Behaviorally non-scored** | Null `behavioral_pass_rate` (parsing or schema failure) | **31** (12.9%) |
| **G2-pass behaviorally scored** | `schema_valid=true`, `referential_valid=true`, and non-null `behavioral_pass_rate` | **189** (78.8% of all runs; coincides with all G2-pass runs in this campaign) |
| **Referential-invalid but scored** | `referential_valid=false`, `schema_valid=true`, non-null BPR | **20** (subset of the behaviorally scored stratum) |

**Primary structural–behavioural gap (manuscript F1):** among the G2-pass behaviorally scored stratum (`n=189`), **30 runs (15.9%)** achieved `behavioral_pass_rate = 1.0`. Population-wide G2 pass **189/240 (78.8%)** is reported separately.

**G2 denominators:**

- Population-wide G2: **189/240 (78.8%)**
- G1-conditioned G2: **189/235 (80.4%)**

Do **not** impute null BPR as zero.

---

## 4. Frozen campaign run records

Timestamped exports used for manuscript statistics (local paths; gitignored under `experiments/runs/`):

| Campaign | Frozen directory | Runs |
|----------|------------------|-----:|
| C1 pilot | `experiments/runs/C1_pilot_ollama_behavioral/20260603T003118Z/` | 60 |
| C2 core | `experiments/runs/C2_core_ollama_behavioral/20260603T080817Z/` | 180 |

Each directory contains `manifest.json`, `metrics.csv`, `metrics.json`, and per-run artefacts under `raw/`, `candidates/`, `evaluations/`, and `logs/`.

Configs: `experiments/configs/C1_pilot_ollama_behavioral.json`, `experiments/configs/C2_core_ollama_behavioral.json` (four Ollama models, five replicates per model–system cell, temperature 0.0).

**Audit note:** `experiments/analysis/C1_C2_evaluable_stratum_audit.md` documents stratum counts and the 20 referential-invalid scored runs.

The private manuscript repository ingests these exports via `paper/scripts/results_config.json` and `paper/data/campaign/metrics_combined.csv` (not shipped in this public repository).

---

## 5. Approved gold FSMs and behavioural suites

Gold reference artefacts for the twelve study systems (3 pilot + 9 core):

1. Natural-language requirement specs imported from [FSM-Bench-20](https://doi.org/10.5281/zenodo.20516296) (`benchmark/datasets/systems/`).
2. Hand-authored reference FSMs (`benchmark/gold_fsms/`, schema `reference_fsm.schema.json`) with requirement IDs on transitions.
3. Paired behavioural test suites (`benchmark/test_suites/`: oracle, path, and negative tests).
4. **Reference self-test** before approval: G2, G3a, and full-suite behavioural pass on the paired suite.
5. **Gold approval checklist** (schema, DSL guards, requirement mapping, self-test, metadata sign-off) — see `docs/benchmark_specification.md` §3 and §8.1.

Candidate campaigns use the **same fixed suites** as oracles; gold diagnostics (`missing_transitions`, `extra_transitions`) count structural differences vs approved references.

---

## 6. RQ4 recorded-outcome consistency (descriptive)

On the frozen C1+C2 exports: among 42 model–system cells with at least one behaviorally scored replicate, **recorded BPR showed zero within-cell standard deviation (0/42)**. **Four cells** showed dispersion on `requirement_coverage` or `extra_transitions` with invariant BPR within the cell. This is a **descriptive** observation on recorded outcomes, not an inferential claim about generative stability.

---

## References

| Document | Content |
|----------|---------|
| [benchmark_specification.md](benchmark_specification.md) | Gold authorship, G3/G3a, test-suite requirements |
| [REPRODUCIBILITY.md](../REPRODUCIBILITY.md) | Environment setup, validation commands |
| [C1_C2_evaluable_stratum_audit.md](../experiments/analysis/C1_C2_evaluable_stratum_audit.md) | Automated stratum audit (N=240) |
| [gold_fsms/README.md](../benchmark/gold_fsms/README.md) | Approved reference FSM index |
