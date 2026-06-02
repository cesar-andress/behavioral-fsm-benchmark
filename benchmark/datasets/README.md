# FSM-Bench-20 Dataset (Upstream Import)

This directory holds **imported** FSM-Bench-20 requirement sets. System JSON files are **not version controlled** in this repository; they are fetched at setup time from the upstream artifact.

---

## Upstream source

| Field | Value |
|-------|-------|
| Name | FSM-Bench-20 |
| DOI | [10.5281/zenodo.20516296](https://doi.org/10.5281/zenodo.20516296) |
| Repository | [llm-fsm-local-benchmark](https://github.com/cesar-andress/llm-fsm-local-benchmark) |
| Pin | See `upstream_manifest.json` |

---

## Directory structure

```text
dataset/
├── README.md                 # This file
├── upstream_manifest.json    # Pinned upstream version and checksums
├── index.json                # Local catalog (generated after import)
└── systems/                  # Imported system JSON (gitignored)
    ├── vending_machine.json
    ├── atm.json
    └── ... (20 systems total)
```

---

## Import procedure (planned)

```bash
python3.12 scripts/import_upstream_dataset.py \
  --manifest dataset/upstream_manifest.json \
  --output dataset/
```

The import script will:

1. Resolve the upstream Zenodo record or Git tag
2. Verify checksums against `upstream_manifest.json`
3. Copy `dataset/systems/*.json` into this tree
4. Generate `dataset/index.json` with import metadata

---

## System file schema

Each file in `systems/` follows the FSM-Bench-20 schema:

```json
{
  "system_name": "Human-readable name of the system",
  "domain": "Application domain label",
  "requirements": [
    "R1: ...",
    "R2: ..."
  ]
}
```

See upstream `dataset/README.md` for full field descriptions.

---

## EMSE extensions (optional, future)

If this study adds requirement variants beyond FSM-Bench-20:

| Extension | Path | Version control |
|-----------|------|-----------------|
| Extended systems | `dataset/extensions/` | Yes (if added) |
| Perturbation bases | `benchmark/perturbations/` | Yes |

Extensions must not modify upstream files in place; derive variants under `benchmark/perturbations/`.

---

## Citation

When using the requirement dataset, cite FSM-Bench-20 (see `upstream_manifest.json` for BibTeX).
