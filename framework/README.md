# Framework — behavioral-fsm-benchmark

Python evaluation engine for milestone **M1** (framework validation). Install from repository root:

```bash
pip install -e ".[dev]"
```

## Modules

| Package | Responsibility |
|---------|----------------|
| `framework.types` | FSM datamodel, requirement specs, test suites, result types |
| `framework.io` | JSON load/write, repository path helpers |
| `framework.validators` | JSON schema validation (G1/G2), referential checks, strict determinism (G3), traceability |
| `framework.guards` | Guard DSL parse/evaluate, guard-aware duplicate detection scaffold (G3a) |
| `framework.behavioral` | Event-sequence simulator, oracle evaluation, test-suite runner |
| `framework.equivalence` | Gold-vs-generated transition matching and behavioral agreement scaffold |
| `framework.coverage` | Requirement, transition, and path coverage metrics |
| `framework.evaluation` | End-to-end single-case evaluation pipeline |
| `framework.repair` | Reserved for optional candidate normalization (post-M1) |

## Benchmark data vs framework code

| Location | Role |
|----------|------|
| `benchmark/guards/` | Guard **definitions** and perturbation variants (data) |
| `framework/guards/` | Guard **evaluation** logic (code) |
| `benchmark/schemas/` | JSON Schema for artifacts |
| `tests/fixtures/` | Deterministic pytest fixtures |

## CLI scripts

| Script | Purpose |
|--------|---------|
| `scripts/validate_fsm.py` | Structural and determinism validation |
| `scripts/run_behavioral_tests.py` | Execute a behavioral test suite |
| `scripts/compare_to_gold.py` | Gold comparison metrics |
| `scripts/evaluate_case.py` | Full evaluation pipeline |

## Status

M1 complete: core load/validate/simulate/compare pipeline implemented with pytest coverage per module. See `docs/implementation_roadmap.md`.
