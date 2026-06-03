# Study Design — EMSE 2026

**Document ID:** `study_design_v2.0`  
**Repository:** `behavioral-fsm-benchmark`  
**Target venue:** Empirical Software Engineering (Springer)  
**Working title:** *Beyond Structural Validity: Evaluating Behavioral Correctness, Robustness, and Reproducibility of LLM-Generated Finite State Machines from Natural-Language Requirements*  
**Predecessor artefact:** FSM-Bench-20 (IST 2026) — [10.5281/zenodo.20516296](https://doi.org/10.5281/zenodo.20516296)  
**Status:** Authoritative pre-registration design (no EMSE results claimed herein)

---

## 1. Motivation

Practitioners increasingly use large language models (LLMs) to draft finite state machines (FSMs) from natural-language requirements for model-based testing, simulation, and traceability. A structurally valid artefact—parseable JSON, closed state/event references, no duplicate `(source, event)` pairs—is necessary but not sufficient for safe downstream use.

FSM-Bench-20 (IST 2026) demonstrated a **structural quality funnel** on 140 local-LLM runs: most outputs parse and many pass schema checks, yet nested strict determinism (G3) passes in a minority of runs, and requirement citation coverage correlates weakly with structural quality among schema-valid outputs. Behavioral gold comparison, robustness under requirement change, and multi-run reproducibility were **not empirically closed** in that study.

This EMSE study treats FSM-Bench-20 as **prior descriptive evidence** and asks whether operational correctness, robustness, and reproducibility can be measured with construct-valid instruments: approved reference FSMs, executable behavioral test suites, guard-aware determinism (G3a), and repeated generation under fixed prompts.

---

## 2. Research gap

### 2.1 Relative to literature

| Gap | Description |
|-----|-------------|
| **Behavioral endpoints** | LLM specification benchmarks emphasize syntax and schema; executable oracles against requirements are uncommon. |
| **Construct validity** | Requirement citation in transition metadata is used as a proxy without behavioral verification. |
| **Guard semantics** | Determinism checks often ignore conditional transitions; apparent conflicts may be resolvable with guard analysis. |
| **Specification robustness** | Perturbation studies target code translation more often than FSM/requirements synthesis. |
| **Reproducibility** | Single-run temperature-0 campaigns do not quantify run-to-run variance or metric stability. |

### 2.2 Relative to FSM-Bench-20 (primary anchor)

| IST finding | Limitation addressed by EMSE |
|-------------|------------------------------|
| Structural funnel (G1–G3) reported | No behavioral verification of passing runs |
| Coverage as quality signal | Coverage decoupled from determinism; not validated against traces |
| Gold FSM placeholders | No approved reference models or oracle batteries executed |
| Single run per model×system | No variance or stability classification |
| Guard-blind G3 | No guard-aware determinism (G3a) or overlap analysis |

**Central phenomenon:** the **structural–behavioral gap** — the difference between passing structural gates and passing executable behavioral tests.

---

## 3. Relationship to FSM-Bench-20

| Component | FSM-Bench-20 (IST) | This study |
|-----------|-------------------|------------|
| Requirement texts | 20 systems, frozen NL specs | **Reused** via `benchmark/datasets/upstream_manifest.json` |
| Candidate format | FSMOutput JSON | **Unchanged** (`generated_fsm.schema.json`) |
| Structural gates | G1, G2, G3 | **Inherited** (C0 parity, C1 baseline) |
| Reference FSMs | Placeholders only | **New:** approved gold FSMs |
| Behavioral tests | None shipped | **New:** test suites |
| Determinism | G3 strict only | **Extended:** G3a guard-aware |
| Paper type | Benchmark introduction | **Empirical study** |

IST descriptive rates may be cited as **background**; EMSE claims require **new frozen campaigns**.

---

## 4. Contribution claims (intended)

| ID | Claim |
|----|-------|
| **C1** | Quantify the structural–behavioral gap using executable oracles (RQ1). |
| **C2** | Taxonomy of behavioral failure modes beyond structural gates (RQ2). |
| **C3** | Compare proxy metrics against gold-backed behavioral agreement (RQ3). |
| **C4** | Measure sensitivity to controlled requirement perturbations (RQ4–RQ5). |
| **C5** | Report run-to-run variance and metric stability (RQ6–RQ7). |
| **C6** | Release reproducible evaluation framework and campaign manifests. |

---

## 5. Novelty risks and mitigations

| Risk | Mitigation |
|------|------------|
| Incremental over IST | Behavioral, robustness, reproducibility as primary endpoints |
| Small gold budget | Pilot 3 → core 12 → stretch 8 |
| Construct validity | Reviewer-approved gold; G3 vs G3a dual reporting |
| Single-author gold bias | Checklist approval workflow |
| Local LLM generalization | External validity threat documented |
| Hypothesis fishing | Pre-registered analysis plan; confirmatory vs exploratory labeled |

---

## 6. Research questions

| RQ | Pillar | Question |
|----|--------|----------|
| **RQ1** | Behavioral | Among G2-passing FSMs, what proportion passes behavioral oracles, and how large is the structural–behavioral gap? |
| **RQ2** | Behavioral | What failure modes dominate when FSMs are structurally valid but behaviorally incorrect? |
| **RQ3** | Behavioral | How well do proxy metrics predict gold-backed behavioral agreement? |
| **RQ4** | Robustness | How sensitive are scores to requirement perturbations overall? |
| **RQ5** | Robustness | Which perturbation types cause the largest degradation? |
| **RQ6** | Reproducibility | What is run-to-run variance at temperature 0 with fixed prompts? |
| **RQ7** | Reproducibility | Which metrics are stable enough for cross-study comparison? |

Structural replication (C0/C1) is **infrastructure**, not an RQ.

---

## 7. Hypotheses (measurable only)

| ID | Hypothesis |
|----|------------|
| **H1** | A non-zero fraction of G2-passing FSMs fail at least one evaluable behavioral oracle |
| **H2** | Oracle failures are more frequent on invariant/negative tests than happy-path tests |
| **H3** | Requirement coverage is a weaker predictor of oracle pass than gold transition overlap |
| **H4** | Omission perturbations reduce oracle pass more than paraphrase |
| **H5** | Code-specialised models show lower structural Jaccard variance across repeats |
| **H6** | G3a pass rate exceeds strict G3 pass rate on the same candidates |

No pre-specified numeric effect sizes.

---

## 8. Independent variables

| Variable | Type | Notes |
|----------|------|-------|
| LLM model | Categorical | Local Ollama set; pinned in manifest |
| System | Categorical | Up to 20; **12 core** for inference |
| Domain | Categorical | From system metadata |
| Perturbation type | Categorical | none, paraphrase, ordering, omission, ambiguity, negation_flip |
| Repeat index | Ordinal | 1…K (C4 freeze sets K) |
| Structured output | Boolean | Primary JSON schema constrained |

---

## 9. Dependent variables

See `docs/evaluation_protocol.md`. Families: structural (G1–G3a), behavioral (oracle pass), equivalence (transition P/R, overlap), coverage (RCov, TCov, PCov), robustness (Δ metrics), reproducibility (variance, stability tier), repair success (optional).

---

## 10. Experimental factors and campaigns

| Campaign | Purpose | RQs |
|----------|---------|-----|
| **C0** | IST structural parity spot-check | — |
| **C1** | Structural baseline | Infrastructure |
| **C2** | Behavioral evaluation | RQ1–RQ3 |
| **C3** | Perturbation robustness | RQ4–RQ5 |
| **C4** | Multi-run reproducibility | RQ6–RQ7 |

**Unit of analysis:** one `(model, system, perturbation, repeat)` run and its evaluation export.

Templates: `experiments/configs/TEMPLATE_*.json`.

---

## 11. Data collection plan

1. Import FSM-Bench-20 requirements (upstream manifest).
2. Author and approve gold FSMs and test suites per benchmark spec.
3. Generate candidates via Ollama (M6); store under `experiments/runs/` (gitignored).
4. Evaluate offline with `scripts/evaluate_case.py`.
5. Aggregate to `analysis/` → `paper/tables/` after freeze.
6. Record provenance: git commit, manifest ID, prompt hash, model tag.

---

## 12. Analysis plan

| RQ | Analysis |
|----|----------|
| RQ1 | Oracle pass rates with Wilson CIs; structural–behavioral gap on G2 stratum |
| RQ2 | Failure taxonomy frequencies |
| RQ3 | Rank correlations: coverage vs oracle; overlap vs oracle |
| RQ4 | Paired Δ vs baseline |
| RQ5 | Compare \|Δ\| across perturbation types |
| RQ6 | Variance; exact replication rate |
| RQ7 | Stability tiers from pre-specified CV thresholds |

Holm correction for confirmatory tests per pillar.

---

## 13. Validity threats

| Threat | Mitigation |
|--------|------------|
| Internal | Fixed prompts, T=0, pinned models, deterministic evaluator |
| External | Local open-weight models; FSM-Bench-20 domains |
| Construct | Gold + oracles; G3 vs G3a; no coverage-as-correctness claim |
| Conclusion | Pre-specified tests; CIs; exploratory labeled |
| Reliability | Multi-run campaign; pytest on framework |

---

## 14. Reproducibility plan

| Mechanism | Location |
|-----------|----------|
| Repository | `behavioral-fsm-benchmark` |
| Upstream pin | `benchmark/datasets/upstream_manifest.json` |
| Schemas | `benchmark/schemas/` |
| Manifests | `experiments/manifests/` |
| Guide | `REPRODUCIBILITY.md` |
| Archival | `docs/release_policy.md` |

**Freeze gate:** No Results population until C2 manifest frozen.
