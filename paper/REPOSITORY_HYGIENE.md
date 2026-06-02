# Paper Repository Hygiene — EMSE 2026

**Path:** `~/papers/emse2026/paper/`  
**Related:** `llm-fsm-behavioral-benchmark/docs/RESEARCH_REPOSITORY_POLICY.md`

---

## 1. What belongs in the paper tree

| Include | Path | Git |
|---------|------|-----|
| LaTeX manuscript | `main.tex`, `sections/` | Yes |
| Bibliography | `references.bib`, `references/` | Yes |
| Auto-generated tables | `tables/table_*.tex` | Yes (with autogen header) |
| Publication figures | `figures/` (whitelist) | Yes — see `figures/FIGURES.md` |
| Analysis notes | `notes/`, audit reports | Yes (review before commit) |
| Artifact scripts | `scripts/` | Yes |

| Exclude | Reason |
|---------|--------|
| Raw LLM JSON | Regeneratable; benchmark `outputs/` |
| Metrics CSV / manifests | Regeneratable; benchmark `results/` |
| LaTeX build products | `*.aux`, `*.log`, `main.pdf` |
| Virtual environments | `scripts/.venv/` |

---

## 2. Figure policy

1. Track only publication figures **F1–F4** listed in `figures/FIGURES.md`
2. Do not track `figures/*.autogen` sidecar markers
3. Do not track benchmark diagnostic plots from `llm-fsm-behavioral-benchmark/figures/`
4. Regenerate from `scripts/update_results_artifacts.py` after each metrics freeze

---

## 3. Tables policy

| Table | Source | Auto-generated |
|-------|--------|----------------|
| `table_structural_baseline.tex` | Structural campaign | Yes |
| `table_oracle_results.tex` | Behavioral campaign | Yes |
| `table_robustness.tex` | Robustness campaign | Yes |
| `table_reproducibility.tex` | Reproducibility campaign | Yes |
| `table_statistical_tests.tex` | Inferential analysis | Manual |

---

## 4. Pre-commit checklist

1. No `outputs/`, `results/`, or benchmark duplicates staged
2. Only whitelisted files under `paper/figures/`
3. Tables carry auto-generation header when regenerated
4. `figures/FIGURES.md` updated for new publication figures

---

## 5. Regeneration (when implemented)

```bash
cd ~/papers/emse2026/llm-fsm-behavioral-benchmark
python3.12 scripts/evaluate.py

cd ~/papers/emse2026/paper/scripts
python3.12 update_results_artifacts.py --force
```
