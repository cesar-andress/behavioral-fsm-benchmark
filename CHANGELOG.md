# Changelog

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## v0.1.0 - 2026-06-03

First public pre-release of the behavioral evaluation stack and approved gold corpus.

### Framework

- Offline evaluation engine under `framework/` (structural validation, guard-aware determinism, behavioral simulator, test runner, gold comparison, coverage metrics).
- JSON schema validation for generated, reference, requirement, and test-suite artifacts.
- CLI scripts for FSM validation, behavioral test execution, gold comparison, and case evaluation.

### Benchmark

- Three pilot systems: `vending_machine`, `login_system`, `atm`.
- Nine core systems: `parking_gate`, `access_control`, `bike_rental`, `warehouse_inventory`, `smart_thermostat`, `elevator`, `hotel_booking`, `train_ticket_booking`, `package_locker`.
- Approved gold FSMs, requirement specs, and behavioral test suites for all twelve systems.
- Benchmark catalog and index metadata under `benchmark/catalog.json` and `benchmark/index.json`.

### Tests

- 172+ unit and integration tests covering validators, simulator, coverage, benchmark loading, and gold self-tests.
- Parametrized benchmark validation for all pilot and core systems.

### Reproducibility

- `REPRODUCIBILITY.md` with environment setup, validation commands, and gold corpus evaluation workflow.
- `scripts/evaluate_gold_corpus.py` for corpus-level schema, determinism, coverage, and self-test reporting.
- `scripts/audit_public_release.py` and CI release audit workflow to block manuscript and local-output leakage.
- Local outputs (`results/`, `experiments/runs/`, `experiments/logs/`) excluded from version control by default.
