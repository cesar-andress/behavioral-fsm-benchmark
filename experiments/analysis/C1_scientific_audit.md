# C1 Pilot — Scientific Audit

**Campaign run:** `experiments/runs/C1_pilot_ollama_behavioral/20260603T003118Z`  
**Audit date:** 2026-06-03  
**Scope:** Read-only synthesis of frozen campaign exports and prior methodology audits  
**Matrix:** 3 pilot systems × 4 Ollama models × 5 replicates = **60 runs**  
**Method:** No benchmark assets modified; no new campaigns executed.

**Related audits:** [C1_replicate_audit.md](C1_replicate_audit.md), [C1_negative_test_audit.md](C1_negative_test_audit.md)

---

## 1. Executive summary

| Question | Finding |
|----------|---------|
| Is C1 informative for RQ1–RQ5? | **Partially.** Strong signal on structural funnel and system difficulty; weak signal on replicate dispersion and rejection metrics. |
| Primary discriminators | `behavioral_pass_rate`, `final_state_agreement`, `trace_agreement`, missing/extra transitions, non-evaluable rate |
| Saturated / non-discriminative | `rejected_event_agreement` (100% on evaluable stratum); BPR replicate variance (0 in all evaluable cells) |
| Unstable under the hood | Raw Ollama text (5/5 unique per cell); candidate JSON drift in 3/12 cells masked by BPR in 2 cells |
| Recommended protocol changes (analysis only) | Report secondary variance metrics; treat REA as supplementary; retain ATM; keep K=5 but do not power on BPR variance alone |

---

## 2. Campaign snapshot

| Statistic | Value |
|-----------|-------|
| Total runs | 60 |
| Run status passed / failed | 54 / 6 |
| Evaluable / non-evaluable | 54 / 6 (10%) |
| G2-passing runs (schema + referential) | 49 / 60 |
| Unique BPR values (evaluable) | **3** — 0.3125, 0.5, 1.0 |
| Mean BPR (evaluable) | 0.497685 |
| Mean final-state agreement | 0.132479 |
| Mean trace agreement | 0.092593 |
| Mean rejected-event agreement | **1.0** |

---

## 3. Findings by research question

### RQ1 — Structural validity

Source: `summary/rq_summary.md`, `metrics.csv`.

| Gate | Pass rate | Interpretation |
|------|----------:|----------------|
| G1 (JSON parseable) | 0.917 | 5/60 fail at parsing (all `atm` × `qwen2.5-coder:7b`) |
| G2 (schema + referential) | 0.891 | 1 additional schema failure (`llama3.1:8b × atm` r1) |
| G3 (strict determinism) | 0.898 | Among G2-eligible rows |
| G3a (guard-aware) | 0.898 | **Identical to G3** — no guarded transitions exercised in pilot FSMs |

**Structural–behavioral gap (RQ1 core phenomenon):**

- Among 49 G2-passing runs, **100%** are evaluable and mean BPR = **0.497** — roughly half of structurally valid candidates fail behavioral oracles.
- G2 pass does **not** imply behavioral pass: BPR spans 0.3125–1.0 within the G2 stratum.

**RQ1 verdict:** C1 supports reporting a non-trivial funnel and structural–behavioral gap on pilot systems. G3a adds **no information** in C1 (pilot gold FSMs have zero non-empty guards).

---

### RQ2 — Behavioral correctness

| Metric | Campaign mean | Discriminatory? |
|--------|-------------:|:----------------|
| Mean BPR | 0.498 | **Yes** — three discrete levels |
| Mean final-state agreement (FSA) | 0.132 | **Yes** — co-varies with low BPR on `atm` |
| Mean trace agreement | 0.093 | **Yes** — often 0 when FSA low |
| Mean rejected-event agreement (REA) | 1.0 | **No** — saturated (see §5) |

**By model (mean BPR, evaluable runs only):**

| Model | Mean BPR | Notes |
|-------|----------|-------|
| `gemma2:9b` | 0.625 | Only model reaching BPR 1.0 on `login_system` |
| `llama3.1:8b` | 0.458 | |
| `mistral-nemo:12b` | 0.458 | |
| `qwen2.5-coder:7b` | 0.417 | 0/5 evaluable on `atm` |

**Failure modes (evaluable stratum):** Low BPR driven by missing/extra transitions and oracle failures on positive paths; not by rejection-test failures (REA always passes).

**RQ2 verdict:** BPR, FSA, and trace agreement are usable primary endpoints. REA should not be interpreted as a quality differentiator in C1.

---

### RQ3 — Behavioral agreement (gold alignment)

| System | Mean missing trans. | Mean extra trans. | Mean BPR |
|--------|--------------------:|------------------:|---------:|
| `atm` | 4.07 | 4.36 | 0.3125 |
| `login_system` | 2.00 | 2.00 | 0.625 |
| `vending_machine` | 2.00 | 2.50 | 0.500 |

- Transition diagnostics **discriminate systems** (`atm` highest divergence).
- Within-system variance exists on `atm` (missing 3–5, extra 3–6 across runs) and `login_system` (0–4), but aggregate means are stable at pilot scale.
- `gemma2:9b × login_system` shows **metric collision**: two distinct candidate FSMs, identical exported agreement metrics (see replicate audit).

**RQ3 verdict:** Missing/extra transition counts are informative and should be retained. Per-run diagnostics are needed when candidates differ but means collide.

---

### RQ4 — Robustness / cross-run dispersion

| Statistic | Value |
|-----------|-------|
| Mean replicate variance (BPR, model×system cells) | **0.0** |
| Cells with BPR std > 0 | **0 / 11** evaluable cells |
| Cells with any secondary metric variance | **1** (`mistral-nemo:12b × atm`: rcov, extra_transitions) |
| Raw response uniqueness | **12/12** cells — 5 distinct payloads per cell |
| Candidate JSON uniqueness | **3/12** cells — two variants |

**First-replicate pattern:** Replicate 1 differs from replicates 2–5 in three cells (`gemma2:9b × login_system`, `llama3.1:8b × atm`, `mistral-nemo:12b × atm`).

**RQ4 verdict:** BPR-only replicate variance is **non-informative** in C1 (false stability). Raw-generation instability is real but often absorbed by JSON extraction. K=5 still detected one schema outlier and candidate drift invisible to BPR.

---

### RQ5 — System difficulty

| System | Mean BPR | Non-evaluable rate | Difficulty profile |
|--------|----------:|-------------------:|--------------------|
| `atm` | **0.3125** | **0.30** | Floor effect on BPR; parsing barrier for `qwen2.5-coder:7b` |
| `vending_machine` | 0.500 | 0.00 | Mid-range; zero cross-run BPR variance |
| `login_system` | 0.625 | 0.00 | Ceiling for `gemma2:9b` (BPR 1.0); bimodal 0.5 vs 1.0 across models |

**RQ5 verdict:** Pilot systems occupy **distinct difficulty bands** in C1. `atm` is the hardest and the only system with substantial non-evaluable mass.

---

## 4. Metric taxonomy

### 4.1 Saturated metrics

| Metric | Evidence | Implication |
|--------|----------|-------------|
| **`rejected_event_agreement`** | 54/54 evaluable runs = 1.0 | Cannot rank models or systems; see [C1_negative_test_audit.md](C1_negative_test_audit.md) |
| **G3a pass rate** (= G3) | 49/49 on eligible stratum | No guard-discrimination in pilot tier |
| **BPR replicate variance (aggregated)** | 0.0 campaign-wide | Misleading if reported alone as “perfect stability” |

### 4.2 Non-discriminative metrics (in C1 stratum)

| Metric | Why |
|--------|-----|
| **REA** | Simulation-failure ≡ pass on negative tests; C1 candidates fail by omission not false acceptance |
| **Mean REA in summaries** | Always 1.0 — adds no variance |
| **Std BPR** at system level | 0 for `atm` and `vending_machine` (all runs same BPR) |
| **G3 vs G3a** | Identical counts — guards absent on pilot FSMs |

### 4.3 Unstable metrics (hidden variance)

| Layer | Stability | Notes |
|-------|-----------|-------|
| Raw `response_text` | **Unstable** | 5/5 unique hashes every cell despite T=0 |
| Normalized candidate JSON | Mostly stable | 9/12 cells identical; 3/12 two variants |
| Exported BPR | **Over-stable** | Collapses distinct candidates in 2 cells |
| `requirement_coverage`, `extra_transitions` | Occasionally unstable | `mistral-nemo:12b × atm` |

### 4.4 Ceiling effects

| System / cell | Metric | Value |
|---------------|--------|------:|
| `login_system` × `gemma2:9b` | BPR | 1.0 (all 5 replicates) |
| All evaluable runs | REA | 1.0 |
| `login_system` × `gemma2:9b` | FSA, trace | 1.0 |

Ceiling on BPR is **model-specific**, not system-universal (`login_system` remains at 0.5 for three other models).

### 4.5 Floor effects

| System / cell | Metric | Value |
|---------------|--------|------:|
| `atm` (all evaluable models) | BPR | **0.3125** (14/14 runs) |
| `atm` × `qwen2.5-coder:7b` | Evaluable rate | **0/5** (parsing) |
| `vending_machine`, most models | BPR | **0.5** (sticky mid-floor) |
| Low-BPR runs | FSA | ~0.154 on `atm`; **0** on `vending_machine` / most `login_system` cells |
| Low-BPR runs | Trace | **0** except `gemma2:9b × login_system` |

`atm` is the canonical **floor system** — low BPR with high transition error counts and 30% non-evaluable rate.

---

## 5. Assessment of design choices

### 5.1 Is replicate count K = 5 justified?

| Criterion | K = 5 in C1 |
|-----------|-------------|
| BPR variance estimation | **Not justified** — zero variance in all evaluable cells; K=2 would suffice for BPR point estimates |
| Detecting first-run outliers | **Justified** — `llama3.1:8b × atm` r1 schema failure |
| Candidate drift detection | **Partially justified** — 3 cells show variant splits; K=3 might catch pattern |
| Statistical power (future inferential tests) | **Insufficient alone** — discrete BPR levels (3 values) need more systems/models, not more replicates |
| Operational cost | 5 × marginal value ≈ low for BPR, moderate for structural audits |

**Recommendation:** **Retain K = 5** for C2 protocol continuity and outlier detection, but **do not** justify K=5 by observed BPR variance. Supplement with candidate-hash equality rate and secondary metric variance. Consider reporting **effective independent samples** when candidates converge (often 1–2 per cell, not 5).

### 5.2 Should `atm` remain in the benchmark?

| Argument | Detail |
|----------|--------|
| **Keep** | Highest difficulty; separates evaluable from non-evaluable models; richest transition diagnostics; realistic parsing stress test |
| **Keep** | Only pilot system with 16 tests and 8 requirements — exercises larger suites |
| **Risk** | 30% non-evaluable rate inflates structural failures; `qwen2.5-coder:7b` total failure may dominate model comparisons |
| **Risk** | BPR floor at 0.3125 compresses dynamic range for behavioral endpoints |

**Recommendation:** **Retain `atm`.** It is the most informative system for RQ1 funnel drop-off and RQ5 difficulty in C1. Report non-evaluable rates separately; do not impute BPR = 0 for parsing failures. Flag `atm` as a **stress system** in cross-corpus comparisons when core systems are added in C2.

### 5.3 Should REA continue to be reported?

| Argument | Detail |
|----------|--------|
| **Report (secondary)** | Pre-specified in evaluation protocol; transparent completeness |
| **Do not emphasize** | 100% saturation in C1; weak correlation with BPR; oracle semantics reward omission failures |
| **Future** | Core systems with more negative tests may show REA < 1.0; C1 alone cannot validate discriminatory power |

**Recommendation:** **Continue reporting REA in export tables** for reproducibility, but classify it as **non-discriminative in C1** and **not suitable as a primary RQ2/RQ3 endpoint**. Pair with negative-test pass counts and explicit false-accept cases if evaluator semantics are refined later.

---

## 6. Cross-RQ synthesis

```text
Generation (raw)     → unstable (5/5 unique texts)
        ↓ extraction
Candidate JSON       → mostly stable; drift in 3/12 cells
        ↓ G1–G2
Structural pass      → 91.7% G1, 89.1% G2
        ↓ behavioral eval
BPR / FSA / trace    → discriminative; 3 BPR levels
        ↓
REA                  → saturated at 1.0
        ↓
Replicate variance   → 0 on BPR; non-zero on structure in 1 cell
```

**Systems ranking (behavioral difficulty, C1):**  
`atm` (floor, high non-evaluable) → `vending_machine` (mid-floor) → `login_system` (highest mean BPR, model-dependent ceiling).

**Models ranking (mean BPR):**  
`gemma2:9b` > `llama3.1:8b` ≈ `mistral-nemo:12b` > `qwen2.5-coder:7b` (penalized by `atm` parsing).

---

## 7. Implications for C2 full campaign

| C1 lesson | C2 action (planning) |
|-----------|----------------------|
| BPR variance = 0 | Add candidate-hash and secondary-variance reporting; expand to 12 systems |
| REA saturated | Do not expect REA to differentiate in core tier without oracle changes |
| G3a = G3 on pilots | Expect G3a lift only on `access_control` / `package_locker` (guarded transitions) |
| ATM stress | Include in corpus; monitor non-evaluable rate in RQ5 |
| K = 5 | Keep; re-evaluate after C2 if BPR variance remains zero |
| Discrete BPR levels | Larger system count needed for continuous-looking distributions |

See [C2_full_campaign_plan.md](../plans/C2_full_campaign_plan.md) and [C2_runtime_estimation.md](../plans/C2_runtime_estimation.md).

---

## 8. Limitations of this audit

1. **Pilot scope only** — 3 systems, 4 models; no core-tier systems or guarded FSMs in C1 matrix.  
2. **Temperature 0.0** — raw instability may differ at T > 0.  
3. **Local Ollama** — external validity limited to pinned local models.  
4. **Metric collision** — exported summaries under-report structural diversity.  
5. **No causal claims** — patterns are descriptive associations from one frozen run directory.

---

## 9. Artefacts referenced

| Path | Role |
|------|------|
| `metrics.csv` | 60-run primary data |
| `summary/rq_summary.md` | RQ1–RQ5 aggregated exports |
| `summary/campaign_summary.csv` | Campaign-level means |
| `summary/system_summary.csv` | RQ5 system strata |
| `summary/model_system_summary.csv` | Per-cell dispersion |
| `raw/*.json`, `candidates/*.json` | Replicate stability (replicate audit) |
| `benchmark/test_suites/*.json` | Negative-test inventory (negative audit) |

No files under the run directory or benchmark tree were modified.

---

## 10. Audit procedure

1. Load `metrics.csv` (60 rows) and `summary/*` exports.  
2. Cross-check with [C1_replicate_audit.md](C1_replicate_audit.md) and [C1_negative_test_audit.md](C1_negative_test_audit.md).  
3. Classify metrics by variance, saturation, and system-level floors/ceilings.  
4. Map findings to RQ1–RQ5 reporting slots used by `aggregate_campaign_results.py`.

Analysis performed with read-only Python over the frozen run directory (2026-06-03).
