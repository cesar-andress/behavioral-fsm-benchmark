# Scripts — Experiment and Validation Pipeline

**Status:** Placeholder — no implementation yet

---

## Planned layout

```text
scripts/
├── README.md                      # This file
├── import_upstream_dataset.py     # Fetch FSM-Bench-20 systems
├── validate_integrity.py          # JSON, dataset, benchmark validation
├── validate_language.py           # English-only tracked files
├── check_models.py                # Ollama model availability
├── run_experiment.py              # Structural FSM generation
├── run_behavioral_evaluation.py   # Oracle execution
├── run_robustness_evaluation.py   # Perturbation campaign
├── run_reproducibility_campaign.py # Multi-run repeats
├── evaluate.py                    # Metrics aggregation → CSV
├── plot_results.py                # Diagnostic figures
├── generate_live_summary.py       # Campaign progress dashboard
└── fsm_benchmark/                 # Core library (schema, metrics, simulator)
    ├── __init__.py                # (planned)
    ├── config.py
    ├── schema.py
    ├── metrics.py
    ├── trace_simulator.py
    └── ollama_client.py
```

---

## Design principles (inherited from IST 2026)

1. **Single driver per campaign type** — clear entry points
2. **Library in `fsm_benchmark/`** — reusable validation and metrics
3. **Campaign-aware** — all runners accept `--campaign-id`
4. **Provenance logging** — append to `experiments/registry/run_index.jsonl`
5. **Idempotent** — skip completed runs unless `--force`

---

## Development order (recommended)

| Milestone | Scripts |
|-----------|---------|
| v0.2.0 | `import_upstream_dataset.py`, `validate_integrity.py`, `config.py`, `schema.py` |
| v0.3.0 | `run_experiment.py`, `evaluate.py` (structural only) |
| v0.4.0 | `run_behavioral_evaluation.py`, `trace_simulator.py` |
| v0.5.0 | `run_robustness_evaluation.py` |
| v0.6.0 | `run_reproducibility_campaign.py` |
| v1.0.0 | Full pipeline via `run_all.sh` |

---

## Usage (when implemented)

```bash
# Structural baseline
python3.12 scripts/run_experiment.py --campaign-id 20260603T120000Z_structural_baseline

# Behavioral oracles
python3.12 scripts/run_behavioral_evaluation.py --campaign-id 20260610T080000Z_behavioral_oracles

# Aggregate metrics
python3.12 scripts/evaluate.py --campaign-id 20260603T120000Z_structural_baseline
```

---

## Related documents

- `REPRODUCIBILITY.md`
- `docs/evaluation_protocol.md`
- `analysis/README.md`
