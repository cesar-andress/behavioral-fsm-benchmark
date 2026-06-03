# Artifact Policy — behavioral-fsm-benchmark

What belongs in this **public** research-software repository versus what is kept private or regenerated locally.

## Public — committed to GitHub / Zenodo

| Category | Path | Notes |
|----------|------|-------|
| Framework source | `framework/`, `scripts/`, `tests/` | Reviewed changes only |
| JSON schemas | `benchmark/schemas/` | Versioned with benchmark spec |
| Study documentation | `docs/`, `README.md`, `REPRODUCIBILITY.md` | English, authoritative design docs |
| Pilot gold FSMs | `benchmark/gold_fsms/` | `metadata.status = approved` |
| Behavioral test suites | `benchmark/test_suites/` | Paired with gold FSMs |
| Test fixtures | `tests/fixtures/` | Deterministic unit-test inputs |
| Guard definitions | `benchmark/guards/` | Data artifacts for perturbation design |
| Campaign templates | `experiments/configs/TEMPLATE_*.json` | Not executed runs |
| Manifest schemas | `experiments/manifests/` | Registry and experiment metadata |
| Upstream pin | `benchmark/datasets/upstream_manifest.json` | FSM-Bench-20 import reference |
| Pilot requirement specs | `benchmark/datasets/systems/vending_machine.json`, `login_system.json` | Authored pilot systems |
| Reproducibility docs | `reproducibility/` | Replication packaging scripts and guides |
| Citation metadata | `CITATION.cff`, `LICENSE` | Release identification |

## Private / not archived in this repository

| Category | Location | Reason |
|----------|----------|--------|
| Manuscript drafts | Private `~/papers/emse2026/paper/` | Submission prose, not public software |
| Submission files | Private manuscript tree | Cover letters, declarations, correspondence |
| Reviewer correspondence | Private | Confidential peer review |
| Private research notes | Outside public repo | Working notes not needed for replication |
| LaTeX build outputs | Private manuscript tree | Regeneratable (`*.aux`, `*.log`, `*.pdf`, …) |
| AI / editor metadata | `.cursor/`, `.claude/`, etc. | Local tooling; gitignored |
| Raw large experiment outputs | `experiments/runs/`, `experiments/logs/` | Regeneratable; released only when explicitly frozen |

## Gitignored by default (regeneratable)

| Category | Path |
|----------|------|
| Python caches | `__pycache__/`, `*.pyc`, `*.egg-info/` |
| Virtual environments | `.venv/`, `venv/` |
| Experiment outputs | `experiments/runs/`, `experiments/logs/` |
| Analysis exports | `analysis/figures/*.{png,pdf,svg}`, `analysis/tables/*.{tex,csv}` |
| Release bundles | `releases/*.zip`, `releases/*.tar.gz` |
| Bulk imported datasets | `benchmark/datasets/systems/*.json` (except tracked pilots) |
| Manuscript directory | `paper/` (must not exist inside public repo) |

## Zenodo / GitHub release snapshot

At release tag, bundle:

- Framework source, tests, schemas, approved pilot benchmark artifacts
- Frozen evaluation exports and manifest pins (when campaigns complete)
- Documentation and replication instructions

Exclude:

- Manuscript sources and submission materials
- Private notes and reviewer correspondence
- Full raw logs unless explicitly designated as supplementary material
- AI/editor metadata and local environment files

See [release_policy.md](release_policy.md).

## Placeholder artifacts

Files with `metadata.status = placeholder` must not be used in official scoring until replaced and approved.
