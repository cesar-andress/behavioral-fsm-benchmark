# Artifact Policy — behavioral-fsm-benchmark

What belongs in git versus what is regenerated locally or archived externally (Zenodo).

## Commit by default

| Category | Path | Condition |
|----------|------|-----------|
| Source code | `framework/`, `scripts/`, `tests/` | Reviewed PR |
| JSON schemas | `benchmark/schemas/` | Versioned with spec |
| Campaign templates | `experiments/configs/TEMPLATE_*.json` | Draft only until freeze |
| Frozen manifests | `experiments/manifests/` | After campaign freeze |
| Approved gold FSMs | `benchmark/gold_fsms/` | `status: approved` in metadata |
| Test suites | `benchmark/test_suites/` | Reviewer sign-off |
| Guard definitions | `benchmark/guards/` | Linked to perturbation protocol |
| Upstream pin | `benchmark/datasets/upstream_manifest.json` | Checksums after verified import |
| Documentation | `docs/`, `README.md`, `REPRODUCIBILITY.md` | English, peer-reviewed internally |
| Manuscript skeleton | `paper/sections/`, `paper/main.tex` | No fabricated results |
| Publication tables | `paper/tables/` | Exported from frozen analysis only |

## Gitignore by default (regeneratable)

| Category | Path |
|----------|------|
| Raw model outputs | `experiments/runs/` |
| Execution logs | `experiments/logs/` |
| Imported requirements | `benchmark/datasets/systems/*.json` |
| Analysis exports | `analysis/tables/`, `analysis/figures/` |
| LaTeX build | `paper/*.aux`, `paper/*.log`, `paper/*.pdf`, … |
| Virtual env | `.venv/` |
| Release ZIPs | `releases/*.zip`, `reproducibility/build/*` |

## Zenodo / GitHub release snapshot

At release tag, bundle:

- Framework source + schemas + frozen configs + results CSV/JSON snapshot
- Exclude: full raw logs (optional supplementary), imported dataset files (document import instead)

See [release_policy.md](release_policy.md).

## Placeholder artifacts

Files marked `status: placeholder` in metadata (e.g., `benchmark/gold_fsms/vending_machine.json`) must **not** be used in scoring until replaced and approved.

## Archive policy

Superseded bootstrap or migration files → `_archive/` (retained, not deleted).
