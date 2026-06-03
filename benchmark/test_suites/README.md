# Behavioral Test Suites — behavioral-fsm-benchmark

Per-system executable behavioral test artifacts: oracles, multi-step paths, and negative (rejection) tests.

**Schema:** `../schemas/testsuite.schema.json`  
**Spec:** `../../docs/benchmark_specification.md` §5

## Pilot systems (approved)

| System ID | File | Tests |
|-----------|------|------:|
| `vending_machine` | `vending_machine.json` | 6 |
| `login_system` | `login_system.json` | 6 |

Load via `framework.benchmark.load_test_suite(system_id)` and execute with `framework.behavioral.test_runner.run_test_suite`.
