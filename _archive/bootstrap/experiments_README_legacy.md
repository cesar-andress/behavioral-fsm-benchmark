# Experiment Tracking

Campaign manifests, run registry, and provenance for large-scale benchmark execution.

---

## Directory structure

```text
experiments/
├── README.md                 # This file
├── campaigns/                # Frozen campaign configurations (version controlled)
│   ├── TEMPLATE_structural.json
│   ├── TEMPLATE_behavioral.json
│   ├── TEMPLATE_robustness.json
│   └── TEMPLATE_reproducibility.json
└── registry/                 # Append-only run log (gitignored at scale)
    ├── run_index.jsonl       # One JSON object per run
    └── schema.json           # Run record schema
```

---

## Campaign lifecycle

```text
Draft manifest → Pilot run → Review metrics → Freeze manifest → Full campaign → Archive
```

| Stage | Action |
|-------|--------|
| Draft | Create `campaigns/<campaign_id>.json` from template |
| Pilot | Set `"pilot": true`, subset of models/systems |
| Freeze | Set `"frozen_at"`, `"frozen_by"`, pin git commit |
| Archive | Copy to Zenodo bundle; reference in paper |

---

## Campaign ID convention

`YYYYMMDDTHHMMSSZ_<purpose>`

Examples:

- `20260603T120000Z_structural_baseline`
- `20260610T080000Z_behavioral_oracles`
- `20260615T140000Z_reproducibility_v1`

---

## Run registry

Each experiment run appends one line to `experiments/registry/run_index.jsonl`:

```json
{
  "run_id": "uuid",
  "campaign_id": "20260603T120000Z_structural_baseline",
  "model": "qwen2.5-coder:14b",
  "system": "vending_machine",
  "repeat_index": 1,
  "git_commit": "abc123",
  "timestamp_utc": "2026-06-03T12:00:00Z",
  "status": "completed",
  "output_paths": {
    "raw": "outputs/raw/...",
    "cleaned": "outputs/cleaned/..."
  }
}
```

Schema: `experiments/registry/schema.json`

---

## Large-scale execution notes

- Batch runs by model to manage VRAM
- Resume from `run_index.jsonl` on failure
- Generate live summary: `scripts/generate_live_summary.py` (planned)
- Do not commit `run_index.jsonl` for full campaigns; include snapshot in Zenodo only

---

## Related documents

- `docs/evaluation_protocol.md`
- `docs/reproducibility_protocol.md`
- `docs/ZENODO_ARCHIVAL_PLAN.md`
