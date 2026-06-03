# Scripts

CLI entry points for validation, benchmark evaluation, and release hygiene.

| Script | Purpose |
|--------|---------|
| `validate_fsm.py` | Schema + structural + determinism validation for one FSM JSON file |
| `run_behavioral_tests.py` | Execute a behavioral test suite against an FSM |
| `compare_to_gold.py` | Compare a candidate FSM to a gold reference |
| `evaluate_case.py` | End-to-end evaluation of one candidate case |
| `evaluate_gold_corpus.py` | Corpus-level gold validation and coverage report |
| `run_ollama_campaign.py` | Ollama FSM generation + behavioral evaluation campaign |
| `audit_public_release.py` | Pre-release audit for manuscript and local-output leakage |
| `build_core_batch1.py` | Offline helper to regenerate core benchmark artifacts |

## Common commands

```bash
python scripts/audit_public_release.py
python scripts/evaluate_gold_corpus.py
python scripts/validate_fsm.py benchmark/gold_fsms/vending_machine.json --schema reference_fsm.schema.json
```

See [REPRODUCIBILITY.md](../REPRODUCIBILITY.md) for full replication steps.
