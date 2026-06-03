# Release Policy — behavioral-fsm-benchmark

Versioning, GitHub releases, and Zenodo archival for the EMSE study artifact.

---

## 1. Version scheme

| Tag | Meaning |
|-----|---------|
| `v0.x.y` | Pre-publication development |
| `v1.0.0` | First frozen campaign + manuscript submission snapshot |
| `v1.x.y` | Post-submission fixes (patch) or benchmark extensions (minor) |

Update `CITATION.cff` and `pyproject.toml` version on every release tag.

---

## 2. Release trigger checklist

Archive when **all** are true:

- [ ] Final campaign manifest frozen in `experiments/manifests/`
- [ ] Run registry complete in `experiments/runs/`
- [ ] Manuscript results exported to `paper/tables/`
- [ ] `REPRODUCIBILITY.md` validated end-to-end
- [ ] Git tag created and pushed
- [ ] GitHub Release published with changelog
- [ ] Zenodo record created or updated with DOI in `CITATION.cff`

---

## 3. GitHub release process

1. Merge freeze branch to `main`.
2. Run CI (`.github/workflows/validate.yml`, `release-audit.yml`).
3. Tag: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
4. Push tag: `git push origin vX.Y.Z`
5. Create GitHub Release with notes from `releases/CHANGELOG.md`.
6. Attach replication ZIP if size permits; otherwise link Zenodo.

---

## 4. Zenodo archival

| Include | Exclude |
|---------|---------|
| `framework/`, `scripts/`, `tests/` | `.venv/`, `__pycache__/` |
| `benchmark/schemas/`, manifests | Imported `benchmark/datasets/systems/` |
| Frozen campaign configs | Draft configs |
| `docs/`, `REPRODUCIBILITY.md` | Internal dev notes |
| Results snapshot CSV/JSON | Raw full logs (optional supplementary) |

Build: `reproducibility/build_replication_package.sh`

Dual-record strategy (recommended):

1. **Artifact record** — code + benchmark specs (early Zenodo deposit).
2. **Results snapshot** — frozen metrics at submission (linked from paper Data Availability).

---

## 5. Pre-release audit

Before tagging:

```bash
pytest
ruff check framework/ tests/ scripts/
python scripts/audit_public_release.py
python scripts/evaluate_gold_corpus.py
git status
```

Release audit checks tracked files for manuscript sources, LaTeX/PDF artifacts, submission/reviewer material, local experiment logs, and editor metadata paths. See `scripts/audit_public_release.py`.

Language policy: all tracked files in English.

---

## 6. Upstream dependency

FSM-Bench-20 pin: `benchmark/datasets/upstream_manifest.json`

Do not bundle upstream requirement files in release ZIP; document import procedure instead.
