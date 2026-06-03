# Reference FSMs — behavioral-fsm-benchmark

Human-approved gold (reference) finite state machines for behavioral evaluation.

| Status | Meaning |
|--------|---------|
| `draft` | Under authoring |
| `review` | Pending reviewer sign-off |
| `approved` | Eligible for gold comparison and L4 scoring |
| `placeholder` | Bootstrap stub only |
| `deprecated` | Superseded |

**Schema:** `../schemas/reference_fsm.schema.json`  
**Spec:** `../../docs/benchmark_specification.md` §3

## Pilot systems (approved)

| System ID | File |
|-----------|------|
| `vending_machine` | `vending_machine.json` |
| `login_system` | `login_system.json` |

Each approved gold FSM MUST pass its paired test suite at 100% (reference self-test).
