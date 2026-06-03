# C2 Runtime Estimation — Execution Cost

**Baseline campaign:** C1 pilot (`C1_pilot_ollama_behavioral/20260603T003118Z`)  
**Document date:** 2026-06-03  
**Status:** Planning estimate (no new runs executed)  
**Related plan:** [C2_full_campaign_plan.md](C2_full_campaign_plan.md)

---

## 1. Purpose

Estimate wall-clock cost for the planned C2 behavioral campaign using **observed C1 timings** as baseline, then scale to **120**, **240**, and **360** run scenarios.

This document supports overnight scheduling for C2. It does **not** launch or resume any campaign.

---

## 2. C1 baseline summary

| Item | Value |
|------|-------|
| Runs in frozen directory | 60 |
| Matrix | 3 systems × 4 models × 5 replicates |
| Manifest final state | 49 completed, 6 failed, 5 skipped (resume pass) |
| Config timeout ceiling | 600 s per Ollama call |
| Active execution window | 2026-06-03 05:47:26 → 05:56:23 UTC (**8.9 min**) |

### 2.1 What C1 timestamps measure

Per-run `started_at` / `finished_at` in `metrics.csv` and run logs bracket **Ollama generation through pre-evaluation hand-off** in the current campaign runner (evaluation completes before the log is flushed, but the recorded `finished_at` stamp precedes evaluation in the metric row). Empirically, these deltas match log line timestamps and reflect **short LLM calls on small pilot specs**, not the 600 s timeout ceiling.

**Implication:** C1 per-run metrics are a **lower bound** for end-to-end perceived latency; use scaled planning envelopes for overnight buffers.

### 2.2 C1 per-run duration (observed)

Source: `metrics.csv`, all 60 runs (2026-06-03).

| Statistic | Seconds | Minutes |
|-----------|--------:|--------:|
| Mean | 6.3 | **0.11** |
| Median | 6.0 | **0.10** |
| Min | 3.0 | 0.05 |
| Max | 12.0 | 0.20 |
| p90 | 10.8 | **0.18** |
| p95 | 12.0 | **0.20** |
| Sequential sum (60 runs) | 379 s | **6.3 min** |

### 2.3 C1 active wall-clock throughput

| Metric | Value |
|--------|-------|
| First start → last finish | **8.9 min** (535 s) |
| Effective wall per run (535 s ÷ 60) | **0.15 min** (~8.9 s) |
| Inter-run gaps (59 intervals) | median 0 s, mean 2.7 s, max 158 s |

The 158 s gap is a single outlier (likely model load or system scheduling); 58/59 gaps were 0 s (back-to-back runs).

### 2.4 C1 average runtime per model

Per-run mean duration from `metrics.csv` (15 runs each):

| Model | Mean per run | Median per run | Sequential total (15 runs) |
|-------|-------------:|---------------:|---------------------------:|
| `gemma2:9b` | **0.16 min** (9.6 s) | 0.17 min | **2.5 min** |
| `llama3.1:8b` | **0.08 min** (4.8 s) | 0.07 min | **1.2 min** |
| `mistral-nemo:12b` | **0.09 min** (5.4 s) | 0.08 min | **1.4 min** |
| `qwen2.5-coder:7b` | **0.09 min** (5.4 s) | 0.07 min | **1.3 min** |
| **Campaign mean** | **0.11 min** | 0.10 min | **6.3 min** |

`gemma2:9b` was ~2× slower than the fastest model on pilot systems (`atm` mean 0.13 min vs `vending_machine` 0.08 min per system).

### 2.5 C1 vs manifest creation time (not used for scaling)

Manifest `created_at` → first run start includes **~5.3 h idle** (directory prepared at 00:31 UTC, execution at 05:47 UTC). Overnight feasibility estimates **must not** use manifest creation time; use active execution window or per-run statistics instead.

---

## 3. Scaling assumptions for C2

| Factor | C1 | C2 (planned) | Scale note |
|--------|----|--------------|------------|
| Systems | 3 pilot | 12 all-tier | 4× system count |
| New runs | 60 | 180 new (+ 60 C1 reuse → 240 total) | — |
| Mean tests per system | 9.3 | 14.8 corpus-wide | **~1.6×** evaluation load on core |
| Mean requirements | 6.7 | 7.7 | Slightly longer prompts |
| Models | 4 | 4 (recommended) | unchanged |

**C2 complexity uplift (planning):** apply **1.5×** to C1 per-run percentiles when estimating core-only workloads (larger test suites, especially `access_control` and `atm`-class systems).

---

## 4. Estimation methods

Two complementary views:

| Method | Optimistic | Conservative |
|--------|------------|--------------|
| **A — C1 extrapolation** | C1 median/mean per-run × run count | C1 p90 × 1.5 × run count |
| **B — Overnight planning envelope** | 2 min/run (≈10× C1 max; headroom for core + eval) | 6 min/run (mid-range from feasibility planning; below timeout) |

Method A reflects **observed C1 hardware behaviour**. Method B reflects **operator-safe scheduling** when core systems, cold model loads, and occasional slow generations occur.

---

## 5. Expected runtime by run count

### 5.1 Method A — C1 extrapolation

Per-run rates:

| Tier | Per run | Derivation |
|------|--------:|------------|
| Optimistic | **0.10 min** | C1 median |
| Baseline | **0.11 min** | C1 mean |
| Conservative | **0.27 min** | C1 p90 (0.18 min) × 1.5 core uplift |

| Runs | Optimistic | Baseline | Conservative |
|-----:|-----------:|---------:|-------------:|
| **120** | **0.20 h** (12 min) | **0.22 h** (13 min) | **0.54 h** (32 min) |
| **240** | **0.40 h** (24 min) | **0.44 h** (26 min) | **1.08 h** (65 min) |
| **360** | **0.60 h** (36 min) | **0.66 h** (40 min) | **1.62 h** (97 min) |

Wall-clock variant (C1 effective throughput **0.15 min/run**, includes inter-run gaps):

| Runs | Wall-style estimate |
|-----:|--------------------:|
| 120 | **0.30 h** (18 min) |
| 240 | **0.60 h** (36 min) |
| 360 | **0.90 h** (54 min) |

### 5.2 Method B — Overnight planning envelope

| Runs | Optimistic (2 min/run) | Conservative (6 min/run) |
|-----:|-----------------------:|-------------------------:|
| **120** | **4.0 h** | **12.0 h** |
| **240** | **8.0 h** | **24.0 h** |
| **360** | **12.0 h** | **36.0 h** |

### 5.3 Recommended interpretation for C2 primary design (240 runs)

| Scenario | Runs | Optimistic | Conservative |
|----------|-----:|-----------:|-------------:|
| C2 new core only | 180 | 18–32 min (A) / **6 h** (B) | 49–81 min (A) / **18 h** (B) |
| C2 merged dataset | **240** | 24–36 min (A) / **8 h** (B) | 65–97 min (A) / **24 h** (B) |
| Expanded six-model | 360 | 36–54 min (A) / **12 h** (B) | 97–146 min (A) / **36 h** (B) |

**Scheduling recommendation:** Plan **one overnight session (~8–10 h)** for 180 new core runs under Method B optimistic, or **two overnights** under Method B conservative. Method A suggests the same hardware may finish much faster if C1-like latencies persist on core systems—validate with a **10-run smoke batch** before committing calendar time.

---

## 6. Per-model cost (240-run C2 design)

240 runs = **60 runs per model** (12 systems × 5 replicates).

| Model | Optimistic (A, mean rate) | Conservative (A, p90×1.5) | Planning envelope (B, 2–6 min) |
|-------|--------------------------:|----------------------------:|-------------------------------:|
| `gemma2:9b` | **6.6 min** | **16 min** | **2.0–6.0 h** |
| `llama3.1:8b` | **5.3 min** | **16 min** | **2.0–6.0 h** |
| `mistral-nemo:12b` | **5.4 min** | **16 min** | **2.0–6.0 h** |
| `qwen2.5-coder:7b` | **5.4 min** | **16 min** | **2.0–6.0 h** |
| **All four models** | **~22 min** | **~65 min** | **8–24 h** |

Per-model optimistic (A) uses each model’s C1 mean (gemma 0.16 min/run, others ~0.09 min/run) × 60. Conservative (A) applies the uniform uplifted p90 to all models.

---

## 7. Cost drivers and risks

| Driver | Effect on C2 |
|--------|--------------|
| Larger core test suites (16–18 tests) | Increases evaluation CPU time (minor vs generation if C1-like) |
| `atm`-class systems | C1 slowest pilot system; expect similar or higher latency |
| Parsing failures | Short failed runs still consume generation time (C1: failed mean 0.12 min) |
| Model cold start | Up to 158 s inter-run gap observed once in C1 |
| Resume / skip | Re-runs cost ~0 s if artefacts exist — do not rely on for first C2 pass |
| Timeout hits (600 s) | Not observed in C1; would dominate if network/model hangs |

---

## 8. Summary table (decision-ready)

| Runs | Role | Optimistic | Conservative |
|-----:|------|------------|--------------|
| **120** | Half corpus × 4 models × 5 reps | **12 min – 4 h** | **32 min – 12 h** |
| **240** | **C2 primary dataset** | **24 min – 8 h** | **65 min – 24 h** |
| **360** | Six-model expansion | **36 min – 12 h** | **97 min – 36 h** |

Ranges span Method A (C1 extrapolation) through Method B (overnight envelope).

---

## 9. Data sources

| Source | Path |
|--------|------|
| C1 metrics | `experiments/runs/C1_pilot_ollama_behavioral/20260603T003118Z/metrics.csv` |
| C1 manifest | `…/manifest.json` |
| C1 run logs | `…/logs/*.log` |
| C1 config | `experiments/configs/C1_pilot_ollama_behavioral.json` |
| C2 plan | [C2_full_campaign_plan.md](C2_full_campaign_plan.md) |

---

## 10. Next step before execution

Run a **smoke batch** (e.g. `--limit 10` on core systems) and recompute per-run mean/p90 before locking overnight calendar slots. Update this document with smoke timings; do not modify benchmark assets.
