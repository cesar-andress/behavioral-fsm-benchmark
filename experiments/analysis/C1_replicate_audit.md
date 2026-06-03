# C1 pilot replicate stability audit

**Campaign run:** `experiments/runs/C1_pilot_ollama_behavioral/20260603T003118Z`  
**Audit date:** 2026-06-03  
**Protocol:** temperature `0.0`, 5 replicates per (model, system_id) cell  
**Runs audited:** 60 (12 cells × 5 replicates)  
**Method:** Read-only comparison of `raw/`, `candidates/`, and `metrics.csv` (campaign outputs not modified).

---

## Executive summary

| Question | Finding |
|----------|---------|
| Is replicate variance = 0 real? | **Yes for `behavioral_pass_rate`.** All 11 evaluable cells have zero cross-replicate variance on BPR. |
| Is variance = 0 an aggregation bug? | **No.** Aggregator and manual recomputation agree. Zero variance reflects identical BPR values per cell, not a coding error. |
| Is generation stable at T=0? | **No at the raw layer.** Every cell has **5 distinct** `response_text` payloads across replicates. |
| Is extraction stable? | **Mostly yes.** **9/12** cells produce one normalized candidate JSON across all five replicates; **3/12** cells show two candidate variants (replicate 1 vs replicates 2–5). |

**Conclusion:** Reported replicate variance of 0 on behavioral endpoints is **accurate but incomplete**. It correctly summarizes BPR stability while **under-reporting structural drift** in a subset of cells where candidates differ but BPR (or other exported fields) collide.

---

## 1. Aggregator cross-check

Source: `scripts/aggregate_campaign_results.py` → `replicate_variance_for_rows()`.

| Statistic | Aggregator output | Manual check |
|-----------|-------------------|--------------|
| Mean replicate variance (campaign) | `0.0` | `0.0` (population variance of BPR over 11 evaluable cells with ≥2 numeric BPR values) |
| Per-model replicate variance (`rq_summary.md`) | `0` for all four models | Confirmed |
| `model_system_summary.csv` `std_behavioral_pass_rate` | `0` or empty when min = max | Confirmed for all 12 cells |

**Cells excluded from BPR variance:** `qwen2.5-coder:7b × atm` — 0 evaluable runs (all five replicates failed at `failure_stage=parsing`).

**Aggregator limitation (not a bug):** `replicate_variance_for_rows()` uses **`behavioral_pass_rate` only**. It does not surface variance on `requirement_coverage`, `missing_transitions`, or `extra_transitions`. One cell (`mistral-nemo:12b × atm`) has non-zero variance on those fields while BPR remains constant (see §4).

---

## 2. Per-cell replicate comparison

Legend:

- **Raw identical:** all five `raw/<run_id>.json` `response_text` SHA-256 hashes equal  
- **Candidate identical:** all five normalized `candidates/<run_id>.json` equal  
- **Metrics identical:** all exported metric columns equal across replicates  
- **BPR values:** `behavioral_pass_rate` per replicate (empty = non-evaluable)

| Model | System | Raw u/5 | Cand u | Met u | BPR (r1–r5) | Classification |
|-------|--------|---------|--------|-------|-------------|----------------|
| gemma2:9b | atm | 5 | 1 | 1 | 0.3125 × 5 | Identical candidates + metrics |
| gemma2:9b | login_system | 5 | 2 | 1 | 1.0 × 5 | **Metric collision** (2 FSMs, same exports) |
| gemma2:9b | vending_machine | 5 | 1 | 1 | 0.5 × 5 | Identical candidates + metrics |
| llama3.1:8b | atm | 5 | 2 | 2 | ∅, 0.3125 × 4 | R1 schema fail; r2–5 identical |
| llama3.1:8b | login_system | 5 | 1 | 1 | 0.5 × 5 | Identical candidates + metrics |
| llama3.1:8b | vending_machine | 5 | 1 | 1 | 0.5 × 5 | Identical candidates + metrics |
| mistral-nemo:12b | atm | 5 | 2 | 2 | 0.3125 × 5 | **Structurally different, same BPR**; rcov/extra differ |
| mistral-nemo:12b | login_system | 5 | 1 | 1 | 0.5 × 5 | Identical candidates + metrics |
| mistral-nemo:12b | vending_machine | 5 | 1 | 1 | 0.5 × 5 | Identical candidates + metrics |
| qwen2.5-coder:7b | atm | 5 | 1 | 1 | ∅ × 5 | Identical parse-fail candidates; 5 distinct raw |
| qwen2.5-coder:7b | login_system | 5 | 1 | 1 | 0.5 × 5 | Identical candidates + metrics |
| qwen2.5-coder:7b | vending_machine | 5 | 1 | 1 | 0.5 × 5 | Identical candidates + metrics |

**Counts:**

| Category | Cells |
|----------|------:|
| Identical normalized candidates (all 5 replicates) | 9 |
| Two candidate variants | 3 |
| Identical exported metrics (all replicates) | 10 |
| Distinct metric signatures | 2 (`llama3.1:8b × atm`, `mistral-nemo:12b × atm`) |
| Metric collision (different candidates, identical evaluable metrics) | 1 |
| Structurally different, behaviorally equivalent (same BPR, different structure) | 2 |

---

## 3. Raw Ollama responses

- **0/12** cells have identical raw `response_text` across replicates.  
- **12/12** cells have **5/5 unique** raw payloads per cell.

Temperature was `0.0` (`experiments/configs/C1_pilot_ollama_behavioral.json`), yet byte-level generation output still varies. Normalized candidate JSON often converges after JSON extraction despite raw divergence.

---

## 4. Detailed findings for divergent cells

### 4.1 `gemma2:9b × login_system` — metric collision

| Replicate | Candidate group | BPR | rcov | missing | extra |
|-----------|-----------------|-----|------|---------|-------|
| 1 | A (unique) | 1.0 | 0.667 | 0 | 0 |
| 2–5 | B (shared) | 1.0 | 0.667 | 0 | 0 |

- Two structurally distinct FSMs (same state count; transition/guard details differ).  
- All exported evaluable metrics **identical**.  
- **Interpretation:** BPR alone masks structural replicate instability; gold diagnostics would not separate these variants at this export granularity.

### 4.2 `llama3.1:8b × atm` — first-replicate outlier

| Replicate | failure_stage | Candidate group | BPR |
|-----------|---------------|-----------------|-----|
| 1 | `schema_validation` | A | non-evaluable |
| 2–5 | `none` | B (shared) | 0.3125 |

- R1 produces a schema-invalid candidate; r2–5 converge.  
- Metric signatures differ because r1 is non-evaluable (expected funnel behavior, not aggregation error).

### 4.3 `mistral-nemo:12b × atm` — structural drift, constant BPR

| Replicate | Candidate group | BPR | rcov | missing | extra |
|-----------|-----------------|-----|------|---------|-------|
| 1 | A | 0.3125 | 0.75 | 5 | 5 |
| 2–5 | B (shared) | 0.3125 | 0.875 | 5 | 6 |

- BPR variance = **0**; `requirement_coverage` variance = **0.0025**; `extra_transitions` variance = **0.16**.  
- **Interpretation:** behaviorally equivalent under the authored suite, structurally divergent; confirmatory BPR-only robustness metrics miss this.

### 4.4 `qwen2.5-coder:7b × atm` — stable failure

- All five replicates: `failure_stage=parsing`, reason `fsm parse error: 'target'`.  
- Five distinct raw responses → **one** normalized candidate JSON (identical invalid structure).  
- Confirms identical failure artifact despite generation jitter.

---

## 5. First-replicate pattern

Three cells show **replicate 1 candidate ≠ replicates 2–5** (same pattern):

1. `gemma2:9b × login_system`  
2. `llama3.1:8b × atm`  
3. `mistral-nemo:12b × atm`

Possible causes (descriptive, not confirmed): cold-start/model load, cache warmup, or ordering effect in the campaign matrix. Worth noting in RQ4 reporting; not evidence of an aggregation defect.

---

## 6. Aggregation assessment

| Check | Result |
|-------|--------|
| BPR variance = 0 when all BPR equal | Correct |
| Null BPR excluded from mean/std | Correct |
| `std_behavioral_pass_rate` empty when &lt;2 evaluable values | Correct (`qwen2.5-coder:7b × atm`) |
| Failure rates use full run denominator | Correct |
| Possible false stability from BPR-only variance | **Yes** — design limitation |
| Metric collision undetected by summaries | **Yes** — 1 cell (`gemma2:9b × login_system`) |
| Structural variance hidden when BPR equal | **Yes** — 1 cell (`mistral-nemo:12b × atm`) |

**No evidence** that zero replicate variance is caused by incorrect grouping, deduplication, or averaging bugs in `aggregate_campaign_results.py`.

**Recommendations for paper/analysis (future, not applied here):**

1. Report **candidate JSON equality rate** alongside BPR variance for RQ4.  
2. Include **secondary variance** on `requirement_coverage`, `missing_transitions`, `extra_transitions`.  
3. Flag **metric collisions** when normalized candidate hash diversity &gt; 1 but behavioral exports match.

---

## 7. Artefacts referenced

| Path | Role |
|------|------|
| `metrics.csv` | Per-run exported metrics (60 rows) |
| `raw/*.json` | Stored Ollama `response_text` |
| `candidates/*.json` | Extracted FSM JSON |
| `summary/rq_summary.md` | Reports replicate variance = 0 |
| `summary/model_system_summary.csv` | Per-cell BPR min/max/std |

---

## 8. Audit procedure (reproducible)

Analysis performed with read-only Python over the frozen run directory:

1. Group `metrics.csv` rows by (`model`, `system_id`).  
2. SHA-256 hash of `response_text` in `raw/`, normalized JSON in `candidates/`.  
3. Compare metric tuples across replicates.  
4. Recompute `pvariance(behavioral_pass_rate)` per cell and compare to `replicate_variance_for_rows()`.

No files under `20260603T003118Z/` were modified during this audit.
