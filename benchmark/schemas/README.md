# JSON Schemas — behavioral-fsm-benchmark

| Schema | Purpose |
|--------|---------|
| `requirement_spec.schema.json` | Natural-language requirement sets |
| `generated_fsm.schema.json` | LLM-generated / candidate FSM (FSMOutput-compatible) |
| `reference_fsm.schema.json` | Gold / reference FSM metadata |
| `testsuite.schema.json` | Behavioral test suites |
| `evaluation_result.schema.json` | Structured evaluation export |
| `experiment_manifest.schema.json` | Campaign / experiment manifests |

Legacy placeholders (`catalog.schema.json`, `candidate_fsm.schema.json`, `evaluation_report.schema.json`) remain for migration; prefer the schemas above.
