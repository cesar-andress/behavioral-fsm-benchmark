# Repository Governance — behavioral-fsm-benchmark

## Purpose

Single authoritative git repository for the EMSE follow-up study extending FSM-Bench-20.

## Decision authority

| Topic | Authoritative source |
|-------|---------------------|
| Research questions, campaigns, analysis | `docs/study_design.md` |
| Benchmark artifacts and metrics | `docs/benchmark_specification.md` |
| Execution procedures | `docs/evaluation_protocol.md` |
| Versioning and Zenodo | `docs/release_policy.md` |
| What may be committed | `docs/artifact_policy.md` |

## Branching (recommended)

| Branch | Use |
|--------|-----|
| `main` | Stable, reviewable artifact + docs |
| `dev/*` | Feature branches for framework and benchmark authoring |
| `freeze/*` | Immutable campaign snapshots before paper export |

## Change control

1. Material study-design changes → bump `study_design.md` version + changelog in `releases/`.
2. Schema changes → update `benchmark/schemas/` and cross-check `docs/benchmark_specification.md`.
3. Gold FSM approval → metadata `status: approved` before use in scoring.

## Language

All tracked files: **English only**.

## What not to commit

See [artifact_policy.md](artifact_policy.md). In brief: raw outputs, run logs, imported requirement JSON, `.venv/`, LaTeX intermediates, secrets.

## CI

`.github/workflows/validate.yml` — schema JSON validity, pytest smoke tests.  
`.github/workflows/release-audit.yml` — pre-tag audit on `v*` tags.

## Related repositories

- **Upstream:** [FSM-Bench-20](https://doi.org/10.5281/zenodo.20516296) (IST 2026 structural benchmark)
- **This repo:** behavioral extension + EMSE empirical study
