# Manuscript Plan — EMSE 2026

**Repository:** `behavioral-fsm-benchmark`  
**Working title:** *Beyond Structural Validity: Evaluating Behavioral Correctness, Robustness, and Reproducibility of LLM-Generated Finite State Machines from Natural-Language Requirements*  
**Status:** Skeleton — prose populated after M9 (results freeze)  
**Date:** 2026-06-03

---

## 1. Document map

| Manuscript section | LaTeX file | Authority document(s) |
|--------------------|------------|------------------------|
| Abstract | `paper/main.tex` | All docs (no numeric results pre-freeze) |
| §1 Introduction | `paper/sections/01_introduction.tex` | `docs/study_design.md` §1–2 |
| §2 Related Work | `paper/sections/02_related_work.tex` | `paper/references/references.bib` |
| §3 Study Design | `paper/sections/03_study_design.tex` | `docs/study_design.md`, `docs/evaluation_protocol.md` §2–4 |
| §4 Benchmark | `paper/sections/04_benchmark.tex` | `docs/benchmark_specification.md` |
| §5 Experimental Setup | `paper/sections/05_experimental_setup.tex` | `docs/evaluation_protocol.md` §7, `REPRODUCIBILITY.md` |
| §6 Results | `paper/sections/06_results.tex` | `analysis/exports/` (post-M9 only) |
| §7 Discussion | `paper/sections/07_discussion.tex` | Results + `docs/study_design.md` §13 |
| §8 Threats | `paper/sections/08_threats_to_validity.tex` | `docs/study_design.md` §13 |
| §9 Conclusion | `paper/sections/09_conclusion.tex` | Results summary (post-M9) |

Extended design notes (non-authoritative for submission): `paper/notes/study_design.md`.

---

## 2. Research questions → sections

| RQ | Primary section | Subsection label |
|----|-----------------|------------------|
| RQ1 | §6.1 | `\ref{sec:results:gap}` |
| RQ2 | §6.2 | `\ref{sec:results:failures}` |
| RQ3 | §6.3 | `\ref{sec:results:proxies}` |
| RQ4 | §6.4 | `\ref{sec:results:perturbation-overall}` |
| RQ5 | §6.5 | `\ref{sec:results:perturbation-types}` |
| RQ6 | §6.6 | `\ref{sec:results:variance}` |
| RQ7 | §6.7 | `\ref{sec:results:stability}` |

Hypotheses H1–H6: introduced in §3.2; tested in §6 with analysis per `docs/evaluation_protocol.md` §8.

---

## 3. Metrics → sections

| Metric family | Defined in | Reported in |
|---------------|------------|-------------|
| G1, G2, G3, G3a | `docs/benchmark_specification.md` §4, §9 | §4.4, §6.1 |
| BTA, oracle/path rates | `docs/evaluation_protocol.md` §5.3 | §6.1–§6.2 |
| GSS, GBA, TEQ, transition P/R | `docs/evaluation_protocol.md` §5.2–§5.3 | §6.3 |
| RCov, PCov | `docs/benchmark_specification.md` §9.3 | §6.3 |
| Perturbation Δ | `docs/evaluation_protocol.md` §5.5 | §6.4–§6.5 |
| Reproducibility variance | `docs/evaluation_protocol.md` §5.7 | §6.6–§6.7 |
| RSR (optional) | `docs/evaluation_protocol.md` §5.6 | §7 (exploratory) |

---

## 4. Milestone gates → manuscript

| Milestone | Manuscript impact |
|-----------|-------------------|
| M1 | §3–§5 skeleton authoritative; framework validated; no Results prose |
| M2–M3 | §4.2–§4.3 may cite approved gold/test-suite counts (descriptive, not campaign results) |
| M4–M7 | Metrics and campaigns; still no §6 prose until M8 |
| M8 | Populate §6, §9; replace "Reported after campaign freeze" in abstract Results/Conclusions |
| M9 | Release package; final DOI in Declarations |

Roadmap detail: `docs/implementation_roadmap.md`.

---

## 5. Tables and figures (planned slots)

| ID | Content | Source (post-freeze) | Section |
|----|---------|----------------------|---------|
| T1 | System tiers (20 systems) | `docs/benchmark_specification.md` §2 | §4.2 |
| T2 | Evaluation layers L0–L5 | `docs/benchmark_specification.md` §9 | §4.5 |
| T3 | Campaign overview C0–C4 | `docs/evaluation_protocol.md` §7 | §5.4 |
| T4 | RQ1 structural–behavioral gap | `behavioral_results.csv` | §6.1 |
| T5 | RQ2 failure mode taxonomy | BF-xx aggregates | §6.2 |
| T6 | RQ3 proxy correlations | Analysis exports | §6.3 |
| T7 | RQ4–RQ5 perturbation Δ | `perturbation_results.csv` | §6.4–§6.5 |
| T8 | RQ6–RQ7 stability | `variance_summary.json` | §6.6–§6.7 |
| F1 | Evaluation pipeline | Benchmark spec §10 layout | §4 |
| F2 | Quality funnel G1→G3a→BTA | Analysis exports | §6.1 |

**Rule:** No fabricated numbers in table cells until M9 exports exist.

---

## 6. Citation clusters (related work)

| Topic | Indicative keys in `references.bib` |
|-------|-------------------------------------|
| FSM-Bench-20 predecessor | `fsm_bench_20_2026` |
| RE from NL / conceptual models | `dalpiaz2021`, `aysolmaz2018` |
| NLP in RE | `mendez2016`, `alhoshan2023` |
| Empirical SE methods | `wohlin2012`, `carro2020` |
| RE empirical surveys | `carro2020` |

---

## 7. Writing conventions

- Use **G3a** (not G3′ or `g3_prime`) for guard-aware determinism.
- Cite IST descriptive rates only as **background** from FSM-Bench-20 Zenodo artifact; EMSE claims require frozen campaigns.
- §6 and §9 conclusion summary: **"Reported after campaign freeze"** until M9.
- Repository name in prose: `behavioral-fsm-benchmark`.
- Schema paths: `benchmark/schemas/`.

---

## 8. Build

```bash
cd paper && ./compile.sh
```

Class: `paper/latex-class/sn-jnl.cls` (Springer Nature).

---

## 9. Version history

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-06-03 | Initial manuscript map |

---

*End of paper plan*
