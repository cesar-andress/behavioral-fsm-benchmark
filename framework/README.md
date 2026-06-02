# Framework — behavioral-fsm-benchmark

Python evaluation engine. Install from repository root: `pip install -e ".[dev]"`.

## Modules

| Package | Responsibility |
|---------|----------------|
| `framework.validators` | G1–G3 structural gates, JSON schema validation |
| `framework.behavioral` | Trace simulator, oracle execution |
| `framework.equivalence` | Reference FSM comparison (FBNS, bisimulation tiers) |
| `framework.coverage` | TCov, PCov, TEQ metrics |
| `framework.guards` | Guard DSL parse/evaluate, guard-aware determinism |
| `framework.io` | Artifact loading, manifest I/O, report writers |
| `framework.repair` | Optional candidate normalization |
| `framework.types` | Shared dataclasses (placeholder) |

## Benchmark data vs framework code

| Location | Role |
|----------|------|
| `benchmark/guards/` | Guard **definitions** and perturbation variants (data) |
| `framework/guards/` | Guard **evaluation** logic (code) |

## Status

Package skeleton only — implementations pending per [docs/evaluation_protocol.md](../docs/evaluation_protocol.md).
