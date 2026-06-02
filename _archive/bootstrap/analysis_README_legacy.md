# Analysis — Post-Hoc Statistical and Exploratory Analysis

**Status:** Placeholder — separated from experiment driver by design

---

## Rationale

Following IST 2026 architecture, **generation/evaluation** (`scripts/`) is separated from **post-hoc analysis** (`analysis/`) to:

- Keep the replication package minimal
- Allow analysis iteration without re-running LLM calls
- Support EMSE statistical reporting requirements

---

## Planned layout

```text
analysis/
├── README.md                       # This file
├── export_summary_tables.py        # Export CSV → paper-ready summaries
├── behavioral_failure_analysis.py  # Failure mode clustering
├── robustness_stats.py             # Perturbation sensitivity tests
├── reproducibility_stats.py        # Variance, ICC, exact replication
├── model_comparison_tests.py       # Non-parametric model comparisons
└── exports/                        # Generated analysis outputs (gitignored)
    └── .gitkeep
```

---

## Inputs

| Input | Source |
|-------|--------|
| Structural metrics | `results/structural/metrics.csv` |
| Oracle results | `results/behavioral/oracle_results.csv` |
| Perturbation results | `results/robustness/perturbation_results.csv` |
| Reproducibility summary | `results/reproducibility/variance_summary.json` |
| Campaign manifest | `experiments/campaigns/<id>.json` |

---

## Outputs

| Output | Consumer |
|--------|----------|
| `exports/summary_tables/` | `paper/scripts/update_results_artifacts.py` |
| `exports/statistical_tests.json` | `paper/tables/table_statistical_tests.tex` |
| `exports/behavioral_failure_taxonomy.csv` | Paper figures F2 (planned) |

---

## Related documents

- `docs/evaluation_protocol.md` §7 Statistical analysis plan
- `paper/scripts/README.md`
