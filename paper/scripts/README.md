# Paper scripts

Utilities for synchronising the LaTeX manuscript with FSM-Behavior-Bench outputs.

**Status:** Placeholder — scripts not yet implemented

---

## Planned pipeline

```bash
# 1. Evaluate benchmark campaigns
cd ~/papers/emse2026/llm-fsm-behavioral-benchmark
python3.12 scripts/evaluate.py

# 2. Export analysis summaries
python3.12 analysis/export_summary_tables.py

# 3. Generate paper tables and figures
cd ~/papers/emse2026/paper/scripts
python3.12 update_results_artifacts.py
```

---

## Planned modules

| Module | Role |
|--------|------|
| `benchmark_results.py` | Load CSV/JSON from benchmark `results/` |
| `update_results_artifacts.py` | Generate tables + figures |
| `update_result_tables.py` | Tables-only wrapper |

---

## Planned outputs

| File | Label |
|------|-------|
| `tables/table_structural_baseline.tex` | `tab:structural-baseline` |
| `tables/table_oracle_results.tex` | `tab:oracle-results` |
| `tables/table_robustness.tex` | `tab:robustness` |
| `tables/table_reproducibility.tex` | `tab:reproducibility` |
| `tables/table_statistical_tests.tex` | `tab:statistical-tests` (manual) |

See `../results_mapping.md` and `../figures/FIGURES.md`.

---

## Auto-generation markers

Tables start with:

```latex
% Auto-generated from FSM-Behavior-Bench results. Do not edit manually.
```

Use `--force` to overwrite protected files.
