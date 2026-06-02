# Benchmark Catalog — Gold FSMs, Oracles, and Perturbations

This directory contains **reference artifacts** for behavioral, robustness, and structural comparison beyond the requirement-only dataset in `dataset/`.

---

## Directory structure

```text
benchmark/
├── README.md                 # This file
├── index.json                # Catalog metadata
├── gold/                     # Approved reference FSMs (one per system)
├── oracles/                  # Behavioral test traces and oracle specs
│   ├── schema.json           # Oracle file JSON schema
│   └── systems/              # Per-system oracle definitions
└── perturbations/            # Requirement perturbation variants
    ├── schema.json           # Perturbation spec JSON schema
    └── variants/             # Per-system perturbation sets
```

---

## Gold FSMs (`gold/`)

Approved reference FSMs for supervised behavioral comparison.

| Status | Meaning |
|--------|---------|
| `placeholder` | File exists; content not yet approved |
| `draft` | Under review |
| `approved` | Eligible for gold-aligned metrics |

Each gold file must:

- Be deterministic (unique `(source, event)` pairs)
- Include `requirement` traceability on every transition
- Declare `forbidden_behaviours` for negative test cases (planned)
- Match metadata in `index.json`

---

## Behavioral oracles (`oracles/`)

Oracle specifications define **executable traces** and **expected outcomes** for generated FSMs.

Example oracle categories (planned):

| Category | Description |
|----------|-------------|
| `positive_trace` | Valid event sequence must reach expected state |
| `negative_trace` | Forbidden sequence must be rejected or unreachable |
| `invariant_check` | Global property must hold after any valid prefix |
| `requirement_binding` | Specific requirement must be exercised |

See `docs/behavioral_evaluation_protocol.md`.

---

## Perturbations (`perturbations/`)

Requirement perturbation variants for robustness evaluation.

| Perturbation type | Description |
|-------------------|-------------|
| `paraphrase` | Semantically equivalent rewording |
| `ordering` | Requirement order shuffle (control: fixed seed) |
| ` omission` | Single requirement removed |
| `ambiguity_injection` | Controlled ambiguous phrasing |
| `negation_flip` | Invariant polarity change (stress test) |

See `docs/robustness_protocol.md`.

---

## Catalog index

`index.json` tracks approval status for all benchmark artifacts. Run validation after updates:

```bash
python3.12 scripts/validate_integrity.py   # planned
```

---

## Relationship to IST 2026

Gold FSM placeholders may be migrated from `~/papers/ist2026/llm-fsm-local-benchmark/benchmark/gold/` after independent review and approval for behavioral evaluation.

Do not copy gold files without updating `metadata.status` and oracle cross-references.
