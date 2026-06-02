# Publication-ready figures

**Directory:** `paper/figures/`  
**Regenerate:** `cd paper/scripts && python3.12 update_results_artifacts.py --figures-only --force`  
**Source data:** `llm-fsm-behavioral-benchmark/results/`

**Status:** Planned — no figures generated yet

---

## Planned assets (F1–F4)

| ID | File(s) | Narrative role | LaTeX label |
|----|---------|----------------|-------------|
| **F1** | `structural_behavioral_gap.{png,svg}` | Gap between G3 pass and oracle pass | `fig:structural-behavioral-gap` |
| **F2** | `oracle_failure_taxonomy.{png,svg}` | Behavioral failure categories | `fig:oracle-failure-taxonomy` |
| **F3** | `perturbation_sensitivity.{png,svg}` | Robustness by perturbation type | `fig:perturbation-sensitivity` |
| **F4** | `reproducibility_variance.{png,svg}` | Cross-run stability by model | `fig:reproducibility-variance` |

**Style:** Grayscale-friendly, single-panel, suitable for Springer EMSE print.

**Not tracked:** `*.autogen` sidecar markers.

---

## Inclusion checklist

1. Regenerated from frozen campaign CSV/JSON
2. Referenced in `sections/08_results.tex`
3. Listed in this file before adding to Git whitelist in `.gitignore`
