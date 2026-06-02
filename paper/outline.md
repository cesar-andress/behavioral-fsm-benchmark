# Manuscript Outline — EMSE 2026

**Title (working):** Beyond Structural Validity: Evaluating Behavioral Correctness, Robustness, and Reproducibility of LLM-Generated Finite State Machines from Natural-Language Requirements

**Status:** Skeleton — content not yet written

---

## Contribution summary (planned)

1. **Extension** of FSM-Bench-20 with behavioral oracle evaluation beyond structural gates
2. **Robustness** methodology for requirement perturbations in LLM FSM generation
3. **Reproducibility** analysis of run-to-run variance under fixed local inference
4. **Empirical evidence** on the gap between structural validity and behavioral correctness

---

## Section plan

| Section | File | Content |
|---------|------|---------|
| 1. Introduction | `sections/01_introduction.tex` | Motivation, gap, contributions |
| 2. Related Work | `sections/02_related_work.tex` | LLM specs, MBT benchmarks, robustness, reproducibility |
| 3. Study Design | `sections/03_study_design.tex` | RQ1–RQ7, hypotheses, factors, analysis plan |
| 4. Benchmark | `sections/04_benchmark.tex` | FSM-Bench-Next artifact, metrics, pipeline |
| 5. Experimental Setup | `sections/05_experimental_setup.tex` | Models, campaigns C0–C4, provenance |
| 6. Results | `sections/06_results.tex` | §6.1–6.8 by RQ (reporting plans until freeze) |
| 7. Discussion | `sections/07_discussion.tex` | Interpretation themes by pillar |
| 8. Threats to Validity | `sections/08_threats_to_validity.tex` | Internal, external, construct, conclusion |
| 9. Conclusion | `sections/09_conclusion.tex` | Summary, future work |

---

## Research question mapping

| RQ | Primary section | Tables/Figures |
|----|-----------------|----------------|
| RQ1–RQ3 Behavioral | §6.1–§6.3 | `table_oracle_results`, F1, F2 |
| RQ4–RQ5 Robustness | §6.4–§6.5 | `table_robustness`, F3 |
| RQ6–RQ7 Reproducibility | §6.6–§6.7 | `table_reproducibility`, F4 |

See `results_mapping.md` for detailed artifact mapping.

---

## Data availability statement (draft)

> All requirement specifications are imported from FSM-Bench-20 (DOI: 10.5281/zenodo.20516296). The behavioral evaluation artifact, campaign manifests, analysis scripts, and frozen result snapshots are archived at [Zenodo DOI TBD]. Replication instructions are in the companion repository `llm-fsm-behavioral-benchmark`.

---

## Timeline (placeholder)

| Milestone | Target |
|-----------|--------|
| Oracle pilot (3 systems) | TBD |
| Structural baseline campaign | TBD |
| Full behavioral + robustness + reproducibility | TBD |
| Results freeze | TBD |
| Manuscript draft | TBD |
| Submission | TBD |
