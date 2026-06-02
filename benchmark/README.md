# Benchmark artifacts

FSM-Bench-Next benchmark layout for the EMSE study.

| Directory | Contents |
|-----------|----------|
| `datasets/` | Upstream FSM-Bench-20 manifest and imported requirement sets |
| `gold_fsms/` | Approved human-authored reference FSMs |
| `schemas/` | JSON Schema for catalog, reference FSM, testsuite, candidate, evaluation report |
| `test_suites/` | Behavioral oracles, multi-step paths, forbidden traces |
| `guards/` | Guard DSL definitions and perturbation variants |

**Authority:** [docs/benchmark_specification.md](../docs/benchmark_specification.md)

Do not populate gold FSMs or test suites until the authoring phase begins.
