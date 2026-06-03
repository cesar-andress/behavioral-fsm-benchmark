# Repository Hygiene — behavioral-fsm-benchmark

Pre-public-release checklist for keeping the **public** repository free of local artefacts, private manuscript material, and editor metadata.

**Related:** [artifact_policy.md](artifact_policy.md), [release_policy.md](release_policy.md), [RELEASE_READINESS.md](../RELEASE_READINESS.md)

---

## Purpose

This document records what must **never** be committed to the public GitHub / Zenodo archive, how exclusions are enforced, and how maintainers verify hygiene before tagging a release.

The benchmark assets under `benchmark/` (schemas, gold FSMs, test suites, approved requirement specs) are **intentionally tracked** and must not be removed during hygiene passes.

---

## Enforcement layers

| Layer | Mechanism |
|-------|-----------|
| `.gitignore` | Blocks accidental `git add` of local outputs and tooling metadata |
| `scripts/audit_public_release.py` | Fails CI if forbidden paths are already tracked |
| `.github/workflows/validate.yml` | Runs audit on every push/PR |
| `.github/workflows/release-audit.yml` | Extended audit on version tags |

---

## Exclusion checklist

### Python build and runtime artefacts

| Pattern | Status | Notes |
|---------|--------|-------|
| `__pycache__/` | ✅ Ignored | Bytecode directories |
| `*.pyc`, `*.pyo`, `*.pyd` | ✅ Ignored | Compiled Python (`*.py[cod]` + explicit `*.pyc`) |
| `*.egg-info/` | ✅ Ignored | Editable-install metadata (e.g. `behavioral_fsm_benchmark.egg-info/`) |
| `*.egg` | ✅ Ignored | Legacy setuptools eggs |
| `dist/`, `build/` | ✅ Ignored | Wheel/sdist build trees |
| `.eggs/` | ✅ Ignored | Setuptools cache |
| `.venv/`, `venv/`, `env/` | ✅ Ignored | Local virtual environments |
| `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/` | ✅ Ignored | Tool caches |
| `.coverage`, `htmlcov/` | ✅ Ignored | Coverage reports |

### Editor and AI assistant metadata

| Pattern | Status | Notes |
|---------|--------|-------|
| `.cursor/` | ✅ Ignored | Cursor IDE project state |
| `.cursorignore`, `.cursorindexingignore`, `.cursorrules` | ✅ Ignored | Cursor config (also blocked if tracked by audit) |
| `.claude/`, `.claude.json` | ✅ Ignored | Claude / Anthropic tooling |
| `.aider/`, `.aider*` | ✅ Ignored | Aider assistant |
| `.continue/`, `.windsurf/` | ✅ Ignored | Other assistant integrations |
| `.chatgpt/`, `.openai/` | ✅ Ignored | OpenAI tooling paths |
| `*.code-workspace` | ✅ Ignored | Multi-root editor workspaces |
| `AGENTS.md` | ✅ Ignored | Agent instruction files |
| `prompt_drafts/`, `ai_prompts/`, `cursor_rules/` | ✅ Ignored | Draft prompt trees |
| `chat_logs/`, `assistant_logs/`, `scratch_prompts/`, `local_notes/` | ✅ Ignored | Local assistant transcripts |
| `*.prompt.txt`, `*.chat.txt`, `*.assistant.txt` | ✅ Ignored | Ad-hoc assistant exports |

**Whitelisted exception:** `prompts/behavioral_fsm_generation.md` — frozen C1 generation prompt required for campaign replication.

### Temporary and scratch outputs

| Pattern | Status | Notes |
|---------|--------|-------|
| `tmp/`, `temp/`, `.tmp/` | ✅ Ignored | Scratch directories |
| `*.tmp` | ✅ Ignored | Temporary files |
| `outputs/` | ✅ Ignored | Generic script output root |

### Campaign and experiment outputs

| Pattern | Status | Notes |
|---------|--------|-------|
| `experiments/runs/*` | ✅ Ignored | Timestamped campaign directories (`raw/`, `candidates/`, `evaluations/`, `logs/`, `metrics.csv`, `summary/`) |
| `experiments/logs/*` | ✅ Ignored | Standalone campaign logs |
| `!experiments/runs/.gitkeep` | ✅ Tracked | Placeholder only |
| `!experiments/logs/.gitkeep` | ✅ Tracked | Placeholder only |

Campaign configs under `experiments/configs/` and methodology notes under `experiments/analysis/` **are tracked** (templates and read-only audits, not raw run data).

### Generated reports and paper exports

| Pattern | Status | Notes |
|---------|--------|-------|
| `results/` | ✅ Ignored | Gold corpus reports, local evaluation exports |
| `campaign_reports/` | ✅ Ignored | CSV/JSON/Markdown from `scripts/generate_campaign_reports.py` |
| `paper_results/` | ✅ Ignored | Legacy paper-export directory name (removed from tooling) |
| `manuscript_exports/` | ✅ Ignored | Private writing-repository staging copies |
| `analysis/figures/*.{png,pdf,svg}` | ✅ Ignored | Manuscript figure exports |
| `analysis/tables/*.{tex,csv}` | ✅ Ignored | Manuscript table exports |
| `reproducibility/build/*` | ✅ Ignored | Replication ZIP staging |
| `releases/*.zip`, `releases/*.tar.gz` | ✅ Ignored | Release bundles built locally |

Regenerate locally:

```bash
python scripts/evaluate_gold_corpus.py          # → results/gold_corpus/
python scripts/aggregate_campaign_results.py  # → <run-dir>/summary/
python scripts/generate_campaign_reports.py      # → <run-dir>/campaign_reports/
```

### Manuscript, editorial, and reviewer material

| Pattern | Status | Notes |
|---------|--------|-------|
| `paper/`, `../paper/` | ✅ Ignored | Manuscript tree must live outside this repo |
| `manuscript/`, `submission/` | ✅ Ignored | Defence-in-depth path names |
| `reviewer/`, `editorial/` | ✅ Ignored | Peer-review correspondence paths |
| `*.tex` | ✅ Ignored | LaTeX sources |
| `*.pdf` | ✅ Ignored | Local PDFs |
| LaTeX intermediates (`*.aux`, `*.bbl`, `*.log`, …) | ✅ Ignored | Build artefacts |

Private manuscript location (not in this repository):

```text
~/papers/emse2026/paper/
```

### Secrets and large binaries

| Pattern | Status |
|---------|--------|
| `.env`, `.env.*`, `*.secret`, `*.key` | ✅ Ignored |
| `*.gguf`, `*.bin`, `*.safetensors` | ✅ Ignored |

---

## Tracked public content (do not delete)

These paths **belong** in the public release and are excluded from hygiene removal:

| Category | Paths |
|----------|-------|
| Benchmark corpus | `benchmark/schemas/`, `benchmark/gold_fsms/`, `benchmark/test_suites/`, `benchmark/catalog.json`, `benchmark/index.json` |
| Approved requirement specs | `benchmark/datasets/systems/{pilot,core}.json` (12 files) |
| Framework and tests | `framework/`, `tests/`, `tests/fixtures/` |
| CLI scripts | `scripts/*.py` |
| Study documentation | `docs/`, `README.md`, `REPRODUCIBILITY.md`, `CHANGELOG.md` |
| Campaign templates | `experiments/configs/`, `experiments/manifests/` |
| CI and packaging | `.github/workflows/`, `pyproject.toml`, `CITATION.cff`, `LICENSE` |

Imported upstream requirement JSON for non-release systems remains gitignored via the whitelist in `.gitignore` (regeneratable from FSM-Bench-20).

---

## Repository structure (public layout)

```text
behavioral-fsm-benchmark/
├── benchmark/              Tracked benchmark assets (schemas, gold, tests, specs)
├── framework/              Tracked evaluation engine
├── scripts/                Tracked CLI entry points + release audit
├── tests/                  Tracked unit and integration tests
├── docs/                   Tracked study and hygiene documentation
├── experiments/
│   ├── configs/            Tracked campaign templates
│   ├── analysis/           Tracked methodology audits (no raw runs)
│   ├── runs/               Gitignored ( .gitkeep only )
│   └── logs/               Gitignored ( .gitkeep only )
├── reproducibility/        Tracked replication docs; build/ gitignored
├── prompts/                Single whitelisted generation prompt
├── results/                Gitignored local reports
├── analysis/               Gitignored figure/table exports; README tracked
└── releases/               Gitignored ZIP/TAR; README tracked
```

---

## Pre-release verification

Run from a clean working tree before tagging:

```bash
# 1. Automated checks
pytest
ruff check framework/ tests/ scripts/
python scripts/audit_public_release.py
python scripts/evaluate_gold_corpus.py

# 2. Confirm no forbidden paths are tracked
git ls-files '*.tex' '*.pdf' 'paper/*' 'experiments/runs/*' 'results/*'
# Expected: no output (except experiments/runs/.gitkeep is tracked as experiments/runs/.gitkeep)

# 3. Confirm local-only dirs are ignored
git check-ignore -v .venv __pycache__ tmp/ paper_results/ behavioral_fsm_benchmark.egg-info

# 4. Working tree status
git status
```

Expected audit output:

```text
release_audit=PASS
```

### Local artefacts on disk (acceptable if ignored)

Development clones may contain gitignored directories such as `.venv/`, `experiments/runs/C1_pilot_.../`, `results/gold_corpus/`, or `*.log` files. These must **not** be force-added (`git add -f`) before a public release.

---

## Audit history (2026-06-03)

| Check | Result |
|-------|--------|
| `release_audit=PASS` | 182 tracked files, no forbidden extensions |
| No tracked `.tex` / `.pdf` | Confirmed |
| No tracked `experiments/runs/` outputs | Confirmed (`.gitkeep` only) |
| `__pycache__/` / `.venv/` ignored | Confirmed |
| `.cursor/` / `.claude/` / `.aider/` ignored | Confirmed |
| New exclusions added | `tmp/`, `paper_results/`, `dist/`, `build/`, `manuscript/`, `submission/`, `reviewer/`, `editorial/`, explicit `*.pyc` |

---

## Maintainer actions before `v0.1.0` tag

1. Run the verification commands above.
2. Delete or leave untracked any local `*.log` scratch files in the repository root.
3. Do not commit campaign run directories under `experiments/runs/`.
4. Push only after `release_audit=PASS` and CI green.

See [public_private_boundary.md](public_private_boundary.md) for what belongs in the private writing repository.
