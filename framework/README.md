# Framework

Python evaluation engine for structural gates, behavioral oracles, equivalence, coverage, and repair.

| Package | Role |
|---------|------|
| `behavioral/` | Trace simulator and oracle execution |
| `validators/` | G1–G3 structural gates, schema validation |
| `equivalence/` | Reference FSM comparison (FBNS, bisimulation tiers) |
| `coverage/` | TCov, PCov, TEQ metrics |
| `repair/` | Optional candidate FSM normalization |
| `io/` | JSON I/O, manifest readers, report writers |

Implementation pending. Install with `pip install -e .` from repository root.
