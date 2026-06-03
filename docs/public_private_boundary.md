# Public / Private Repository Boundary

This document defines what belongs in the **public benchmark repository** (`behavioral-fsm-benchmark`) versus the **private writing repository** (`~/papers/emse2026/paper/`).

---

## Public benchmark repository

**Purpose:** Reusable research software — evaluation framework, benchmark corpus, campaign tooling, and repository-neutral reporting.

### Tracked content

| Category | Examples |
|----------|----------|
| Framework code | `framework/`, `scripts/`, `tests/` |
| Benchmark assets | `benchmark/schemas/`, gold FSMs, test suites, approved requirement specs |
| Study documentation | `docs/`, `README.md`, `REPRODUCIBILITY.md` |
| Campaign templates | `experiments/configs/`, generation prompt whitelist |
| Neutral reporting scripts | `aggregate_campaign_results.py`, `generate_campaign_reports.py` |

### Allowed generated outputs (local, gitignored)

These formats are **repository-neutral** and may be produced locally from campaign summaries:

| Format | Typical path | Producer |
|--------|--------------|----------|
| CSV | `<run-dir>/summary/*.csv`, `<run-dir>/campaign_reports/*.csv` | `aggregate_campaign_results.py`, `generate_campaign_reports.py` |
| JSON | `<run-dir>/metrics.json`, `<run-dir>/campaign_reports/campaign_report.json` | Campaign runner, `generate_campaign_reports.py` |
| Markdown | `<run-dir>/summary/rq_summary.md`, `<run-dir>/campaign_reports/results_summary.md` | Aggregation and report scripts |

Copy CSV/JSON exports into the private repository when preparing prose tables and figures. Do **not** commit them to the public benchmark repository unless explicitly frozen for a tagged release snapshot.

### Never in the public repository

| Category | Patterns |
|----------|----------|
| LaTeX sources | `*.tex` |
| PDFs | `*.pdf` |
| Manuscript figures | `*.png`, `*.svg`, `*.eps` in analysis or export trees |
| Paper-specific export trees | `paper_results/`, `manuscript_exports/` |
| Submission artefacts | Cover letters, declarations, correspondence |
| Editor / AI metadata | `.cursor/`, `.claude/`, `.aider/`, etc. |

Enforced by `.gitignore` and `scripts/audit_public_release.py`.

---

## Private writing repository

**Location:** `~/papers/emse2026/paper/`

**Purpose:** Prose, LaTeX structure, bibliography, submission packaging, and presentation assets derived from benchmark exports.

### Belongs here

| Category | Typical paths |
|----------|---------------|
| LaTeX manuscript | `main.tex`, `sections/*.tex` |
| Result tables (LaTeX) | `tables/*.tex` |
| Figures for publication | `figures/` |
| Submission bundle | `submission/` |
| Writing notes | `notes/` |
| Table/figure generation scripts | `scripts/` (consume benchmark CSV/JSON) |

### Expected workflow

```text
behavioral-fsm-benchmark                    ~/papers/emse2026/paper/
─────────────────────────                   ────────────────────────
experiments/runs/<campaign>/<timestamp>/
  metrics.csv
  summary/                     ──copy CSV/JSON──▶  (local import)
  campaign_reports/
    rq*.csv
    campaign_report.json
                                              scripts/  →  tables/*.tex
                                                          →  figures/*
                                              sections/06_results.tex
```

1. Run campaigns locally; outputs stay under `experiments/runs/` (gitignored in the benchmark repo).
2. Aggregate: `python scripts/aggregate_campaign_results.py --run-dir <run-dir>`.
3. Export neutral reports: `python scripts/generate_campaign_reports.py --run-dir <run-dir>`.
4. Copy `campaign_reports/*.csv` and `campaign_report.json` into the private repository.
5. Generate LaTeX tables and publication figures **only** in `~/papers/emse2026/paper/` (see `paper/scripts/README.md`).

The former `generate_paper_results.py` script (LaTeX tables + matplotlib figures) was removed from the public repository. That presentation layer belongs in the private repository.

---

## Reporting script comparison

| Script | Repository | Outputs |
|--------|------------|---------|
| `aggregate_campaign_results.py` | Public benchmark | `summary/*.csv`, `summary/rq_summary.md` |
| `generate_campaign_reports.py` | Public benchmark | `campaign_reports/*.csv`, `campaign_report.json`, `results_summary.md` |
| Planned `update_results_artifacts.py` | Private paper | `tables/*.tex`, `figures/*` |

---

## Verification

Before tagging a public release:

```bash
python scripts/audit_public_release.py
git ls-files '*.tex' '*.pdf'
find . -path './.git' -prune -o -name 'paper_results' -print
```

Expected: audit passes; no tracked LaTeX or PDF; no `paper_results/` directories committed.

See also [repository_hygiene.md](repository_hygiene.md) and [artifact_policy.md](artifact_policy.md).
