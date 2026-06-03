# Reproducibility Guide — behavioral-fsm-benchmark

Replication instructions for release **v0.1.0** (framework + approved gold corpus). LLM campaign execution is documented for future milestones.

## Overview

| Item | Value |
|------|-------|
| Release | `v0.1.0` (2026-06-03) |
| Upstream dataset | FSM-Bench-20 — [10.5281/zenodo.20516296](https://doi.org/10.5281/zenodo.20516296) |
| Import manifest | `benchmark/datasets/upstream_manifest.json` |
| Gold corpus | 12 systems (3 pilot + 9 core) — see `benchmark/index.json` |
| Structural gates | G1 (JSON), G2 (schema + referential), G3 (strict), G3a (guard-aware) |
| Behavioral layer | Oracle / path / negative test suites + gold self-tests |
| Local outputs | `results/`, `experiments/runs/`, `experiments/logs/` (gitignored) |

## Environment setup

### Prerequisites

```bash
python3.12 --version   # Python 3.11+ required
git --version
```

Optional for future LLM campaigns:

```bash
ollama --version
```

### Installation

```bash
git clone https://github.com/cesar-andress/behavioral-fsm-benchmark.git
cd behavioral-fsm-benchmark
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Verify import:

```bash
python -c "import framework; print('framework OK')"
```

## Exact commands — validation

From the repository root with the virtual environment activated:

```bash
pytest
ruff check framework/ tests/ scripts/
python scripts/audit_public_release.py
```

Expected:

```text
release_audit=PASS
```

All tests should pass (172+ as of v0.1.0).

## Exact commands — gold corpus evaluation

```bash
python scripts/evaluate_gold_corpus.py
```

Optional custom output directory:

```bash
python scripts/audit_public_release.py
python scripts/evaluate_gold_corpus.py --output-dir results/gold_corpus
```

### Expected console output

```text
systems_total=12
systems_passed=12
all_passed=True
metrics_csv=.../results/gold_corpus/metrics.csv
metrics_json=.../results/gold_corpus/metrics.json
summary_md=.../results/gold_corpus/summary.md
PASS vending_machine: bta=1.000 rcov=0.500 tcov=1.000 pcov=1.000
...
PASS package_locker: bta=1.000 rcov=1.000 tcov=1.000 pcov=1.000
```

Exit code: `0`.

### Expected output files

| File | Content |
|------|---------|
| `results/gold_corpus/metrics.csv` | One row per system: schema, G2, G3, G3a, self-test, RCov, TCov, PCov |
| `results/gold_corpus/metrics.json` | Full structured report with timestamps and per-system errors |
| `results/gold_corpus/summary.md` | Markdown table with corpus PASS/FAIL status |

Pilot systems may report requirement coverage below `1.000` (legacy traceability on transitions); core systems report `rcov=1.000`. All systems must pass schema, G2, G3, G3a, and behavioral self-tests at `bta=1.000`.

## Per-system validation (optional)

Validate one gold FSM:

```bash
python scripts/validate_fsm.py benchmark/gold_fsms/parking_gate.json \
  --schema reference_fsm.schema.json
```

Run one behavioral suite:

```bash
python scripts/run_behavioral_tests.py \
  benchmark/gold_fsms/parking_gate.json \
  benchmark/test_suites/parking_gate.json
```

Expected: `behavioral_pass_rate=1.000`, exit code `0`.

## Manuscript and private artifacts

The EMSE manuscript is **not** in this repository. It is maintained privately at:

```text
~/papers/emse2026/paper/
```

Do not commit manuscript sources, PDFs, submission files, or reviewer correspondence to the public repository. Run `python scripts/audit_public_release.py` before tagging releases.

## Ollama pilot campaign C1

Campaign config: `experiments/configs/C1_pilot_ollama_behavioral.json`

| Factor | Value |
|--------|-------|
| Systems | `vending_machine`, `login_system`, `atm` |
| Models | 6 local Ollama tags (see config) |
| Replicates | 5 per model-system pair |
| Expected runs | 90 |
| Temperature | 0.0 |
| Structured JSON | enabled when supported by Ollama |

### Prerequisites

```bash
ollama --version
ollama pull qwen2.5-coder:7b
# pull remaining models listed in the campaign config
```

### Dry run (no Ollama calls)

Prints the planned 90-run matrix:

```bash
python scripts/run_ollama_campaign.py \
  --config experiments/configs/C1_pilot_ollama_behavioral.json \
  --dry-run
```

### Limited smoke campaign

Execute the first two runs (requires Ollama; failures are recorded and the campaign continues):

```bash
python scripts/run_ollama_campaign.py \
  --config experiments/configs/C1_pilot_ollama_behavioral.json \
  --limit 2
```

### Full overnight campaign

```bash
python scripts/run_ollama_campaign.py \
  --config experiments/configs/C1_pilot_ollama_behavioral.json
```

### Output layout

Each campaign start creates a timestamped directory (never overwritten):

```text
experiments/runs/C1_pilot_ollama_behavioral/<timestamp>/
  manifest.json
  metrics.csv
  metrics.json
  raw/
  candidates/
  evaluations/
  logs/
```

### Resume interrupted campaigns

Re-run against the same timestamp directory:

```bash
python scripts/run_ollama_campaign.py \
  --config experiments/configs/C1_pilot_ollama_behavioral.json \
  --run-dir experiments/runs/C1_pilot_ollama_behavioral/<timestamp>
```

Completed runs (`status=completed` or `status=failed` in `manifest.json`) are skipped automatically. Both outcomes mean the run was executed and a metrics row was written; resume does not re-run failed candidates.

### Failed runs and metrics

Every executed run produces a row in `metrics.csv` and `metrics.json`, including malformed or unevaluable candidates. Failed runs are **not** repaired, discarded, or retried automatically.

| Field | Values | Meaning |
|-------|--------|---------|
| `run_status` | `passed`, `failed` | Whether the full evaluation pipeline completed |
| `failure_stage` | `generation`, `json_extraction`, `parsing`, `schema_validation`, `referential_validation`, `determinism_validation`, `behavioral_evaluation`, `none` | Last stage reached before failure |
| `failure_category` | `ollama_error`, `no_json_found`, `invalid_json`, `parse_error`, `schema_error`, `referential_error`, `determinism_error`, `behavioral_error`, `none` | Failure classifier |
| `failure_reason` | string | Human-readable error (empty when `run_status=passed`) |

When parsing or schema validation fails, downstream behavioral metrics are left empty in CSV and `null` in JSON — not `0`. A blank `behavioral_pass_rate` means *not evaluable*, not a behavioral score of zero.

Artifacts for failed runs (when available):

| Artifact | Typical failure stages |
|----------|------------------------|
| `raw/<run_id>.json` | JSON extraction, parsing, schema, evaluation |
| `candidates/<run_id>.json` | Parsing, schema, evaluation (extracted JSON saved before validation) |
| `evaluations/<run_id>.json` | All stages (failure stub or partial export) |
| `logs/<run_id>.log` | All stages |

Example metrics row for a parse error (missing transition `target`):

```csv
run_status,failed,failure_stage,parsing,failure_category,parse_error,failure_reason,"fsm parse error: 'target'",...,behavioral_pass_rate,
```

(`behavioral_pass_rate` and other downstream columns are empty in CSV.)

## Future campaigns

Additional templates remain under `experiments/configs/TEMPLATE_*.json` for parity, robustness, and reproducibility studies.

Outputs land in `experiments/runs/` and `experiments/logs/` (gitignored until explicitly frozen).

## Archival

Follow [docs/release_policy.md](docs/release_policy.md). Build script: `reproducibility/build_replication_package.sh` (when campaign data is frozen).

## Artifact policy

Raw experiment outputs and local evaluation reports are not committed by default. See [docs/artifact_policy.md](docs/artifact_policy.md).
