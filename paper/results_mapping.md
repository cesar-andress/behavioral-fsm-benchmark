# Results Mapping — Metrics to Manuscript Artifacts

Maps benchmark outputs to LaTeX tables and figures. Updated at results freeze.

**Status:** Placeholder — no campaign data yet

---

## Structural (RQ1)

| Metric | CSV column | Table | Figure |
|--------|------------|-------|--------|
| G1 valid JSON rate | `g1_pass` | `table_structural_baseline` | F1 (funnel) |
| G2 schema valid rate | `g2_pass` | same | F1 |
| G3 deterministic rate | `g3_pass` | same | F1 |
| Requirement coverage | `requirement_coverage` | same | F3 (heatmap) |

**Source:** `results/structural/metrics.csv`

---

## Behavioral (RQ2, RQ3)

| Metric | CSV column | Table | Figure |
|--------|------------|-------|--------|
| Oracle pass rate | `oracle_pass_rate` | `table_oracle_results` | — |
| Gold behavioral alignment | `gold_behavioral_alignment` | same | — |
| Failure category | `primary_failure_mode` | — | F2 (taxonomy) |

**Source:** `results/behavioral/oracle_results.csv`

---

## Robustness (RQ4, RQ5)

| Metric | CSV column | Table | Figure |
|--------|------------|-------|--------|
| Δ G3 under perturbation | `perturbation_delta_g3` | `table_robustness` | F3 |
| Δ oracle pass rate | `perturbation_delta_oracle` | same | — |
| Structural Jaccard vs base | `structural_jaccard_vs_base` | same | — |

**Source:** `results/robustness/perturbation_results.csv`

---

## Reproducibility (RQ6, RQ7)

| Metric | JSON field | Table | Figure |
|--------|------------|-------|--------|
| Exact replication rate | `exact_replication_rate` | `table_reproducibility` | F4 |
| Cross-run structural Jaccard | `cross_run_structural_jaccard` | same | F4 |
| Oracle variance | `cross_run_oracle_variance` | same | — |

**Source:** `results/reproducibility/variance_summary.json`

---

## Statistical tests

| Test | Output | Table |
|------|--------|-------|
| Kruskal-Wallis (models × oracle rate) | `analysis/exports/statistical_tests.json` | `table_statistical_tests` |
| Perturbation type comparison | same | same |

---

## Results section mapping (manuscript §6)

| RQ | Results subsection | Label |
|----|-------------------|-------|
| RQ1 | §6.1 Structural--behavioral gap | `sec:results:gap` |
| RQ2 | §6.2 Behavioral failure taxonomy | `sec:results:failures` |
| RQ3 | §6.3 Proxy metrics and gold conformance | `sec:results:proxies` |
| RQ4 | §6.4 Overall perturbation sensitivity | `sec:results:perturbation-overall` |
| RQ5 | §6.5 Perturbation-type effects | `sec:results:perturbation-types` |
| RQ6 | §6.6 Run-to-run variance | `sec:results:variance` |
| RQ7 | §6.7 Metric stability classification | `sec:results:stability` |

## Freeze checklist

- [ ] Campaign manifests frozen in `experiments/campaigns/`
- [ ] All CSV/JSON sources archived
- [ ] `update_results_artifacts.py` run with `--force`
- [ ] `results_mapping.md` updated with actual column names
- [ ] Manuscript `\ref{}` labels verified
