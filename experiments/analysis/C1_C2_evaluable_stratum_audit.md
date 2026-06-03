# C1+C2 — Evaluable Stratum / G2 Consistency Audit

**Campaign runs:**

| Campaign | Frozen run directory | Runs |
|----------|---------------------|-----:|
| C1 pilot | `experiments/runs/C1_pilot_ollama_behavioral/20260603T003118Z` | 60 |
| C2 core | `experiments/runs/C2_core_ollama_behavioral/20260603T080817Z` | 180 |

**Audit date:** 2026-06-03  
**Scope:** Read-only check of `metrics.csv` exports against manuscript G2 / evaluable-stratum claims  
**Method:** Automated row scan of all 240 metrics rows; spot-check of `evaluations/*.json` for referential-failure cases; cross-read of campaign evaluator and aggregation code. **No evaluator behavior changed.**

**Related audits:** [C1_scientific_audit.md](C1_scientific_audit.md), [C1_replicate_audit.md](C1_replicate_audit.md)

**Terminology (v0.1.1):** See [docs/scoring_strata_and_campaign_freeze.md](../../docs/scoring_strata_and_campaign_freeze.md) for manuscript-aligned stratum names (behaviorally scored **n=209**; G2-pass behaviorally scored **n=189**).

---

## 1. Executive summary

| Question | Finding |
|----------|---------|
| Do schema-invalid runs receive behavioral metrics? | **No.** 31 schema-invalid runs; all have empty `behavioral_pass_rate`. |
| Do referential-invalid runs receive behavioral metrics? | **Yes — 20 runs (8.3%).** All have `schema_valid=true`, `referential_valid=false`, non-null BPR, `run_status=passed`, `failure_stage=none`. |
| Do failed runs receive behavioral metrics? | **No.** 31 failed runs; none have populated behavioral fields. |
| Do non-`none` failure stages carry downstream metrics? | **No.** All 31 non-evaluable failures have empty downstream fields. |
| Root cause class | **Expected implementation design + manuscript terminology mismatch** (not aggregation corruption). |
| Impact on reported means | Small numerically (mean BPR 0.487 on n=209 vs 0.489 on G2-pass evaluable n=189); conceptual stratum definition is the main issue. |

**Verdict:** The reviewer concern is **partially valid**. Twenty runs violate the manuscript’s stated rule that G2 failures (including `referential_valid=false`) should not receive behavioral metrics. This is **intentional campaign-pipeline behavior** today: JSON schema is the hard gate for oracle execution; referential closure is recorded but does not short-circuit evaluation. The manuscript and `analysis_plan.tex` describe a stricter contract than the exporter implements.

---

## 2. Audit criteria and results

Automated scan over C1+C2 `metrics.csv` (N=240).

| Criterion | Violations | Notes |
|-----------|----------:|-------|
| `schema_valid=false` ∧ `behavioral_pass_rate` non-null | **0** | Consistent with exporter and tests. |
| `referential_valid=false` ∧ `behavioral_pass_rate` non-null | **20** | All 20 also have all other behavioral fields populated. |
| `run_status=failed` ∧ any behavioral metric non-null | **0** | Failed runs are correctly blank downstream. |
| `failure_stage≠none` ∧ any downstream metric non-null | **0** | Downstream = behavioral fields + `referential_valid`. |

### Stratum counts (combined C1+C2)

| Stratum | Count | Share |
|---------|------:|------:|
| Total runs | 240 | 100% |
| G2-pass (`schema_valid` ∧ `referential_valid`) | 189 | 78.8% |
| Evaluable (`behavioral_pass_rate` non-null) | 209 | 87.1% |
| Evaluable but **not** G2-pass | **20** | **8.3%** |
| Non-evaluable (empty BPR) | 31 | 12.9% |

Non-evaluable breakdown (31 runs): 5 C1 parsing failures (`atm` × `qwen2.5-coder:7b`); 26 C2 JSON-schema failures (`schema_validation`, `schema_valid=false`).

---

## 3. Affected runs (referential-invalid with behavioral metrics)

All 20 violations share the same referential failure mode: **empty-string transition targets** (`transitions[k].target '' is not a declared state`). The candidate parses and passes JSON schema validation, but referential closure fails.

### 3.1 By model–system cell (summary)

| Campaign | `system_id` | Model | Replicates | BPR | FSA | TA | REA | ReqCov | Miss / Extra | G3 | G3a |
|----------|-------------|-------|:----------:|----:|----:|---:|----:|-------:|-------------:|:--:|:---:|
| C1 | `vending_machine` | `llama3.1:8b` | 5 | 0.500 | 0.000 | 0.000 | 1.000 | 0.667 | 2 / 3 | ✓ | ✓ |
| C2 | `warehouse_inventory` | `llama3.1:8b` | 5 | 0.250 | 0.143 | 0.000 | 1.000 | 0.875 | 5 / 7 | ✓ | ✓ |
| C2 | `hotel_booking` | `qwen2.5-coder:7b` | 5 | 0.875 | 1.000 | 1.000 | 0.000 | 0.875 | 0 / 2 | ✓ | ✓ |
| C2 | `hotel_booking` | `gemma2:9b` | 5 | 0.250 | 0.143 | 0.000 | 1.000 | 0.875 | 5 / 7 | ✓ | ✓ |

Export metadata for these runs: `run_status=passed`, `failure_stage=none`, `failure_category=none`, empty `failure_reason` in CSV (referential errors appear only under `structural.errors` in `evaluations/<run_id>.json`).

### 3.2 Full `run_id` list

**C1 (5 runs)**

- `C1_pilot_ollama_behavioral__vending_machine__llama3.1_8b__r01` … `r05`

**C2 (15 runs)**

- `C2_core_ollama_behavioral__warehouse_inventory__llama3.1_8b__r01` … `r05`
- `C2_core_ollama_behavioral__hotel_booking__qwen2.5-coder_7b__r01` … `r05`
- `C2_core_ollama_behavioral__hotel_booking__gemma2_9b__r01` … `r05`

**Example evaluation export** (`C2_core_ollama_behavioral__hotel_booking__gemma2_9b__r01`):

```json
"structural": {
  "schema_valid": true,
  "referential_valid": false,
  "errors": [
    "transitions[2].target '' is not a declared state",
    "transitions[3].target '' is not a declared state"
  ]
},
"run_status": "passed",
"failure_stage": "none"
```

---

## 4. Root-cause analysis

### 4.1 What the manuscript states

In `paper/sections/analysis_plan.tex` (Handling failed runs → Schema failures):

> Runs reaching schema evaluation with `schema_valid=false` **or `referential_valid=false`** contribute to G2 fail counts. **Behavioral metrics are not populated** for these runs in the exporter.

In `paper/sections/experimental_protocol.tex`:

> Layers may record skipped or unevaluable status when upstream parsing **or schema validation** fails; downstream behavioral metrics are left empty…

The G2 definition in the analysis plan pairs `schema_valid` and `referential_valid`, implying both are upstream gates for behavioral evaluation.

### 4.2 What the campaign evaluator does

In `scripts/ollama_campaign_lib.py`, `evaluate_candidate_payload()`:

1. **JSON schema failure** → early return, `run_status=failed`, `failure_stage=schema_validation`, `evaluation_export=None`, behavioral fields empty via `unevaluable_metric_fields()`. ✓ Matches manuscript.
2. **Parse failure** → same pattern with `failure_stage=parsing`. ✓
3. **JSON schema pass** → calls `evaluate_case()` unconditionally, then **forces** `run_status=passed`, `failure_stage=none`, and exports full metrics regardless of `referential_valid`.

`framework/evaluation.py::evaluate_case()` always runs `run_test_suite()` when a test suite is present; `validate_fsm()` sets `referential_valid` on the structural result but does not block behavioral execution.

Regression test `tests/test_run_ollama_campaign.py::test_evaluate_candidate_schema_invalid_still_produces_metrics_row` covers schema-invalid → empty BPR only; there is **no** test asserting referential-invalid → empty BPR.

### 4.3 What aggregation does

`scripts/aggregate_campaign_results.py`:

- `is_evaluable(row)` → `behavioral_pass_rate` is non-null (does **not** require G2).
- `is_g2_pass(row)` → `schema_valid` ∧ `referential_valid`.

Aggregation faithfully reflects exported CSV values. The 20 inconsistent rows are included in campaign “evaluable” summaries (n=209) but excluded from G2-pass counts (n=189). **This is not an aggregation bug.**

### 4.4 Classification

| Hypothesis | Assessment |
|------------|------------|
| Evaluator bug (wrong metrics exported) | **Rejected** for schema/parse/failed paths — behavior matches tests and REPRODUCIBILITY.md. **Partially applicable** for referential: implementation diverges from manuscript contract but is stable and reproducible. |
| Aggregation / reporting bug | **Rejected** — `is_evaluable` and `is_g2_pass` are applied consistently to exported data. |
| Terminology / manuscript mismatch | **Confirmed** — manuscript equates “G2 fail” with “no behavioral metrics”; exporter equates “JSON schema pass” with “run behavioral oracles”. |
| Expected design choice needing documentation | **Confirmed** — referential closure is diagnostic for the G2 funnel, not a pipeline abort in the Ollama campaign path. Empty-target transitions can still be simulated partially, yielding meaningful (if structurally invalid) behavioral scores. |

**Primary label:** *Expected design choice that needs documentation*, with a secondary *terminology problem in the manuscript* (analysis plan overstates exporter behavior for referential failures).

---

## 5. Impact on manuscript results

| Statistic | All evaluable (current `is_evaluable`) | G2-pass evaluable (manuscript-aligned) |
|-----------|---------------------------------------:|-----------------------------------------:|
| n | 209 | 189 |
| Mean BPR | 0.487 | 0.489 |

The 20 referential-invalid runs shift means slightly but change **stratum interpretation**:

- Abstract / Results use “evaluable stratum (n=209)” for primary BPR summaries.
- Some sentences reference “G2-pass evaluable runs” (n=189) for ceiling statistics — internally inconsistent with n=209 headline unless explicitly dual-stratum.

Notable cell: `hotel_booking` × `qwen2.5-coder:7b` shows **BPR=0.875** despite referential failure (empty targets on two transitions). This is the clearest example motivating stratum clarification.

---

## 6. Recommendations

### 6.1 Manuscript (preferred near-term — no code change)

1. **Define two strata explicitly:**
   - **Behaviorally scored** (`behavioral_pass_rate` non-null): JSON parseable + JSON schema valid; oracles executed.
   - **G2-pass evaluable** (`schema_valid` ∧ `referential_valid` ∧ BPR non-null): stratum for structural–behavioral gap claims.
2. **Revise** `analysis_plan.tex` §Handling failed runs: state that `referential_valid=false` with `schema_valid=true` **may still** receive behavioral metrics in campaign exports; such runs count toward G2 fail but remain in the behaviorally scored stratum unless re-filtered.
3. **Align** Abstract/Results captions: either report RQ2–RQ3 on G2-pass evaluable only, or report both n=209 and n=189 with clear labels.
4. **Add Threats to Validity** note: referential-invalid FSMs can yield non-null BPR because simulators operate on partial graph structure; interpret as “oracle-on-parsed-object” not “oracle-on-G2-closed FSM”.

### 6.2 Code (future — out of scope for this audit)

If the manuscript contract should become normative in the exporter:

1. In `evaluate_candidate_payload()`, after `evaluate_case()`, if `not result.structural.referential_valid`: return failed outcome with `failure_stage=referential_validation`, `failure_category=referential_error`, and `unevaluable_metric_fields()` for behavioral columns (mirror schema-invalid path).
2. Add regression test: referential-invalid candidate → empty BPR, `run_status=failed`.
3. Optionally add `is_g2_evaluable()` in aggregation and use it for RQ2–RQ3 tables.

**Do not implement item 6.2 until the study team chooses the normative stratum definition** — re-running campaigns would change n=209 summaries.

---

## 7. Reproducing this audit

From the repository root:

```bash
python3 - <<'PY'
import csv
from pathlib import Path

paths = [
    Path("experiments/runs/C1_pilot_ollama_behavioral/20260603T003118Z/metrics.csv"),
    Path("experiments/runs/C2_core_ollama_behavioral/20260603T080817Z/metrics.csv"),
]

def pb(v):
    if v is None or str(v).strip() == "":
        return None
    return str(v).lower() in ("true", "1", "yes")

beh = ["behavioral_pass_rate", "final_state_agreement", "trace_agreement",
       "rejected_event_agreement", "requirement_coverage",
       "missing_transitions", "extra_transitions"]

rows = []
for p in paths:
    rows.extend(csv.DictReader(p.open(newline="", encoding="utf-8")))

ref_bpr = [r for r in rows if pb(r.get("referential_valid")) is False
           and r.get("behavioral_pass_rate", "").strip() != ""]
print("referential_invalid_with_bpr", len(ref_bpr))
for r in ref_bpr:
    print(r["run_id"], r["behavioral_pass_rate"])
PY
```

Expected output: `referential_invalid_with_bpr 20` and the run IDs listed in §3.2.

---

## 8. Conclusion

The G2 / evaluable-stratum inconsistency flagged in review is **real but narrow**: exactly **20 referential-invalid runs** across four model–system cells carry behavioral metrics, while all schema-invalid and hard-failed runs do not. This reflects a **documented-in-code pipeline choice** (JSON schema gates oracles; referential closure is recorded post-hoc) that **contradicts the manuscript’s G2-fail handling paragraph**. Fix by clarifying dual strata in the paper; optionally tighten the exporter in a future protocol revision after a deliberate design decision.
