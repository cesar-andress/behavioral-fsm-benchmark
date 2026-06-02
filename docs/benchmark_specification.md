# FSM-Bench-Next — Benchmark Specification

**Document ID:** `fsm_bench_next_spec_v1.0`  
**Status:** Authoritative benchmark design  
**Extends:** FSM-Bench-20 (IST 2026) — DOI [10.5281/zenodo.20516296](https://doi.org/10.5281/zenodo.20516296)  
**Target study:** EMSE 2026 — *Beyond Structural Validity*  
**Date:** 2026-06-03

---

## 1. Overview

### 1.1 Name and purpose

**FSM-Bench-Next** is the behavioral evaluation layer that extends FSM-Bench-20. It adds **reference FSMs**, **behavioral test suites**, **guard-aware semantics**, **transition and path coverage**, **trace equivalence checking**, and **deterministic validation** on top of the existing 20-system requirement dataset.

FSM-Bench-20 answers: *Is the output structurally valid?*  
FSM-Bench-Next answers: *Does the FSM behave correctly, deterministically, and equivalently to an approved reference under executable tests?*

### 1.2 Design constraints (single-researcher feasibility)

| Constraint | Design response |
|------------|-----------------|
| Limited authoring time | **Tiered system rollout** — 12 core systems required, 8 stretch; reuse FSM-Bench-20 requirements unchanged |
| No manual run adjudication at scale | **Fully automated** trace simulator + guard DSL (decidable subset) |
| No full formal verification | **Trace equivalence** vs reference, not bisimulation or model checking |
| Compute budget | Evaluate **cached** candidate FSMs offline; generation is separate |
| Reviewer burden for gold | One reference FSM + one test suite per system; checklist-driven approval |
| Reproducibility | Pinned schemas, deterministic simulator, manifest hashes |

### 1.3 Relationship to FSM-Bench-20

```text
FSM-Bench-20                          FSM-Bench-Next (this spec)
─────────────────                     ───────────────────────────
dataset/systems/*.json        ───────► requirements/ (imported, read-only)
FSMOutput schema              ───────► candidate FSM format (unchanged)
G1, G2, G3 gates              ───────► Layer L0 (inherited)
—                             ───────► reference/<id>.json
—                             ───────► testsuites/<id>.json
—                             ───────► L1–L5 evaluation layers
```

### 1.4 Benchmark tiers

| Tier | Systems | Reference + test suite | Use |
|------|--------:|------------------------|-----|
| **Core** | 12 | Required, `status=approved` | All reported EMSE metrics |
| **Stretch** | 8 | Optional phase 2 | Full 20-system parity |
| **Pilot** | 3 | First authoring target | Pipeline shake-down |

**Core 12:** `vending_machine`, `atm`, `login_system`, `access_control`, `elevator`, `ticket_machine`, `ecommerce_checkout`, `medical_appointment_booking`, `hotel_booking`, `smart_thermostat`, `library_loan`, `parking_gate`.

---

## 2. Benchmark specification

### 2.1 Evaluation layers

Evaluation proceeds in **six ordered layers**. A candidate FSM that fails layer *L* still runs layers *L+1…* where defined, but layers may mark tests **not applicable** (e.g., behavioral layers on G1 failures record `status=skipped` with reason).

| Layer | ID | Name | Input | Output |
|-------|-----|------|-------|--------|
| L0 | Structural | JSON + schema + referential closure | Candidate FSM | G1, G2 |
| L1 | Deterministic | Guard-aware determinism | G2 passers | G3, G3′ |
| L2 | Behavioral | Test suite execution | G2 passers | Oracle results, path results |
| L3 | Coverage | Transition + requirement coverage | G2 passers | TCov, RCov, PCov |
| L4 | Equivalence | Reference FSM comparison | G2 passers + approved reference | GSS, GBA, GFV, TEQ |
| L5 | Composite | Weighted scoring | All layer outputs | FBNS, sub-scores |

### 2.2 Guard semantics

FSM-Bench-Next defines a **Guard DSL** (decidable subset) for determinism and trace simulation. Natural-language guards in candidate FSMs are parsed when possible; otherwise marked **non-decidable** (ND).

#### 2.2.1 Guard DSL (evaluable forms)

| Form | Syntax example | Semantics |
|------|----------------|-----------|
| **Empty** | `""` | Always enabled |
| **Boolean literal** | `true`, `false` | Constant |
| **Variable compare** | `balance >= 10`, `attempts < 3` | Numeric/string literal compare |
| **Negation** | `not invalid_pin` | Boolean variable negation |
| **Conjunction** | `balance >= 10 and card_valid` | All must hold |
| **Named predicate** | `pin_valid` | Lookup in `context` supplied by test case |

Variables and predicates are declared in the **test suite** (`testsuites/*.json` → `guard_contexts`). Reference FSM guards MUST use DSL forms only.

#### 2.2.2 Guard-aware determinism (G3′)

Two transitions with the same `(source, event)` are **compatible** iff:

1. **Same target** and guards are **provably mutually exclusive**, or  
2. Guards are **identical** and targets are equal (duplicate row — hygiene violation, not ND).

**G3′ pass:** no `(source, event)` group contains two transitions with overlapping enabled guards reaching **different** targets.

**G3 pass (strict, inherited):** no duplicate `(source, event)` pairs regardless of guards (FSM-Bench-20 nested gate).

Both are reported; G3′ is primary for behavioral interpretation; G3 is retained for IST comparability.

#### 2.2.3 Non-decidable guards

If a guard string is not parseable as DSL and is not empty:

- Determinism check: group marked **ND** → transition pair treated as potentially overlapping (conservative).
- Trace simulation: test marked `evaluable=false` → excluded from path coverage denominator.

Report `nd_guard_rate` = ND transitions / total transitions.

### 2.3 Behavioral test suite concepts

Each system has one **test suite** JSON file containing:

| Component | Purpose |
|-----------|---------|
| **Oracle tests** | Single trace + expected outcome (positive, negative, invariant, binding) |
| **Path tests** | Multi-step scenarios with `guard_context` sequences |
| **Forbidden behaviours** | Negative paths that must be rejected (may mirror reference) |
| **Guard contexts** | Variable bindings per test step |

**Path coverage (PCov):** fraction of path tests with `evaluable=true` that pass.  
**Oracle pass rate (OPR):** fraction of oracle tests that pass (evaluable only).

### 2.4 Transition coverage (TCov)

Transition coverage measures overlap between **candidate transition set** *T(c)* and **reference transition set** *T(r)*.

Normalized transition tuple:

```text
τ = (normalize(source), normalize(event), normalize(target), guard_key)
```

where `guard_key` is canonical DSL string or `"_"` if empty.

```text
TCov_exact   = |T(c) ∩ T(r)| / |T(r)|
TCov_relaxed = |{(s,e,t) matched}| / |{(s,e,t) in T(r)}|
```

Report both: **exact** (includes guard) and **relaxed** (ignores guard — structural overlap).

### 2.5 Requirement coverage (RCov)

Inherited from FSM-Bench-20:

```text
RCov = |{ Rn cited in any transition.requirement }| / |{ R1…Rn in requirements }|
```

Additionally report **reference-aligned requirement recall**:

```text
RRef = |{ Rn cited in candidate ∩ Rn cited in reference }| / |{ Rn cited in reference }|
```

### 2.6 Path coverage (PCov)

For each path test *p* with steps `[(event, context), …]`:

1. Initialise simulator at `initial_state` with empty context.
2. For each step, merge `guard_context`; fire event if enabled transition exists.
3. **Pass** iff final state equals `expected.final_state` and no step is `rejected` when acceptance expected.

```text
PCov = |{ p : pass(p) ∧ evaluable(p) }| / |{ p : evaluable(p) }|
```

Minimum **6 path tests** per core system (see §4.3).

### 2.7 Equivalence checking

Full bisimulation is out of scope. FSM-Bench-Next defines **trace equivalence (TEQ)** against the reference FSM:

| Check | Symbol | Definition |
|-------|--------|------------|
| **Gold structural similarity** | GSS | Relaxed TCov (guard ignored) |
| **Gold behavioral alignment** | GBA | Fraction of reference **positive path tests** that pass on candidate |
| **Gold forbidden violation** | GFV | Fraction of reference **forbidden** paths incorrectly accepted by candidate |
| **Trace equivalence score** | TEQ | `0.4·GBA + 0.3·(1−GFV) + 0.3·GSS` |

TEQ ∈ [0, 1]. Equivalence **pass** threshold (reporting): TEQ ≥ 0.80 (configurable in `catalog.json`).

### 2.8 Deterministic validation summary

| Gate | Rule | Layer |
|------|------|-------|
| G1 | Valid JSON | L0 |
| G2 | FSMOutput schema + referential closure + no wildcards | L0 |
| G3 | Unique `(source, event)` among all transitions | L1 |
| G3′ | Guard-aware: no overlapping enabled transitions to different targets | L1 |
| DET_pass | G3′ pass (primary) | L1 |

---

## 3. Artifact format

### 3.1 Repository layout

```text
llm-fsm-behavioral-benchmark/          # implementation root
├── catalog.json                       # Benchmark manifest
├── dataset/                           # FSM-Bench-20 import (requirements)
│   ├── upstream_manifest.json
│   └── systems/*.json                 # gitignored after import
├── reference/                         # FSM-Bench-Next reference FSMs
│   ├── index.json
│   └── <system_id>.json
├── testsuites/                        # Behavioral test suites
│   ├── index.json
│   └── <system_id>.json
├── schemas/                           # JSON Schema documents
│   ├── catalog.schema.json
│   ├── reference_fsm.schema.json
│   ├── testsuite.schema.json
│   ├── candidate_fsm.schema.json      # = FSMOutput (+ optional meta)
│   └── evaluation_report.schema.json
├── scripts/
│   ├── evaluate_next.py               # Main pipeline entry
│   └── fsm_benchmark/
│       ├── schema.py
│       ├── structural.py              # L0
│       ├── determinism.py             # L1
│       ├── simulator.py               # L2–L4
│       ├── coverage.py                # L3
│       ├── equivalence.py             # L4
│       └── scoring.py                 # L5
├── outputs/cleaned/                   # Candidate FSMs (gitignored)
└── results/next/                      # Evaluation outputs (gitignored)
    ├── metrics.csv
    ├── details/<run_id>.json
    └── manifest_<campaign>.json
```

### 3.2 Catalog file (`catalog.json`)

```json
{
  "benchmark_id": "fsm-bench-next",
  "schema_version": "1.0.0",
  "extends": {
    "name": "FSM-Bench-20",
    "doi": "10.5281/zenodo.20516296"
  },
  "tiers": {
    "core_systems": ["vending_machine", "atm", "..."],
    "stretch_systems": ["bike_rental", "..."],
    "pilot_systems": ["vending_machine", "atm", "login_system"]
  },
  "thresholds": {
    "teq_pass": 0.80,
    "fbns_pass": 0.70
  },
  "scoring_weights": {
    "structural": 0.15,
    "determinism": 0.15,
    "behavioral": 0.30,
    "coverage": 0.20,
    "equivalence": 0.20
  },
  "guard_dsl_version": "1.0"
}
```

### 3.3 Reference FSM artifact (`reference/<system_id>.json`)

Human-authored, **approved** reference model. Extends candidate schema with metadata and authoring provenance.

**Naming:** PascalCase states, `snake_case` events, DSL guards only.

**Approval:** `metadata.status = "approved"` required for L4 equivalence in official scoring.

### 3.4 Test suite artifact (`testsuites/<system_id>.json`)

Machine-executable tests bound to the same `system_id`. Authored alongside reference FSM; cross-validated so every reference positive path passes on the reference FSM (self-test).

### 3.5 Candidate FSM artifact (`outputs/cleaned/<model>/<system_id>.json`)

Unchanged FSM-Bench-20 LLM output format. Optional envelope for evaluation:

```json
{
  "candidate_metadata": {
    "model": "qwen2.5-coder:14b",
    "system_id": "vending_machine",
    "campaign_id": "C1_behavioral_baseline",
    "run_id": "uuid",
    "generated_at": "2026-06-03T12:00:00Z"
  },
  "fsm": { "... FSMOutput ..." }
}
```

Evaluator accepts bare `FSMOutput` or enveloped form.

### 3.6 Evaluation report artifact (`results/next/details/<run_id>.json`)

Per-run structured report (see §6.4).

---

## 4. JSON schemas

### 4.1 Candidate FSM (`candidate_fsm.schema.json`)

Compatible with FSM-Bench-20 `FSMOutput`:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "fsm-bench-next/candidate-fsm/v1",
  "title": "Candidate FSM (LLM output)",
  "type": "object",
  "required": ["states", "initial_state", "events", "transitions"],
  "properties": {
    "states": {
      "type": "array",
      "items": { "type": "string", "pattern": "^[A-Za-z][A-Za-z0-9_]*$" },
      "minItems": 1
    },
    "initial_state": { "type": "string" },
    "events": {
      "type": "array",
      "items": { "type": "string", "pattern": "^[a-z][a-z0-9_]*$" }
    },
    "transitions": {
      "type": "array",
      "items": { "$ref": "#/$defs/transition" },
      "minItems": 1
    },
    "forbidden_behaviours": {
      "type": "array",
      "items": { "$ref": "#/$defs/forbidden" },
      "default": []
    }
  },
  "$defs": {
    "transition": {
      "type": "object",
      "required": ["source", "event", "target"],
      "properties": {
        "source": { "type": "string" },
        "event": { "type": "string" },
        "guard": { "type": "string", "default": "" },
        "action": { "type": "string", "default": "" },
        "target": { "type": "string" },
        "requirement": { "type": "string", "default": "" }
      },
      "additionalProperties": false
    },
    "forbidden": {
      "type": "object",
      "required": ["trace", "requirement"],
      "properties": {
        "trace": { "type": "array", "items": { "type": "string" } },
        "reason": { "type": "string" },
        "requirement": { "type": "string" }
      }
    }
  },
  "additionalProperties": false
}
```

### 4.2 Reference FSM (`reference_fsm.schema.json`)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "fsm-bench-next/reference-fsm/v1",
  "title": "Reference FSM",
  "allOf": [
    { "$ref": "candidate_fsm.schema.json" },
    {
      "type": "object",
      "required": ["metadata"],
      "properties": {
        "metadata": {
          "type": "object",
          "required": [
            "status",
            "system_id",
            "version",
            "requirement_source",
            "authors",
            "created"
          ],
          "properties": {
            "status": {
              "type": "string",
              "enum": ["draft", "review", "approved", "deprecated"]
            },
            "system_id": { "type": "string" },
            "version": { "type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$" },
            "requirement_source": { "type": "string" },
            "authors": { "type": "array", "items": { "type": "string" } },
            "reviewers": { "type": "array", "items": { "type": "string" } },
            "created": { "type": "string", "format": "date" },
            "approved_at": { "type": ["string", "null"], "format": "date" },
            "completions": {
              "type": "array",
              "description": "Documented (state,event) omissions",
              "items": {
                "type": "object",
                "required": ["state", "event", "reason"],
                "properties": {
                  "state": { "type": "string" },
                  "event": { "type": "string" },
                  "reason": { "type": "string" }
                }
              },
              "default": []
            }
          },
          "additionalProperties": false
        }
      }
    }
  ]
}
```

**Authoring rule:** All guards in approved reference FSMs MUST parse as Guard DSL v1.0.

### 4.3 Test suite (`testsuite.schema.json`)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "fsm-bench-next/testsuite/v1",
  "title": "Behavioral Test Suite",
  "type": "object",
  "required": ["system_id", "schema_version", "reference_id", "oracles", "paths"],
  "properties": {
    "system_id": { "type": "string" },
    "schema_version": { "type": "string", "const": "1.0.0" },
    "reference_id": {
      "type": "string",
      "description": "Stem of reference/<reference_id>.json"
    },
    "guard_predicates": {
      "type": "object",
      "description": "Named boolean predicates used in guards",
      "additionalProperties": {
        "type": "object",
        "required": ["type"],
        "properties": {
          "type": { "type": "string", "enum": ["boolean", "number", "string"] },
          "default": {}
        }
      },
      "default": {}
    },
    "oracles": {
      "type": "array",
      "minItems": 8,
      "items": { "$ref": "#/$defs/oracle" }
    },
    "paths": {
      "type": "array",
      "minItems": 6,
      "items": { "$ref": "#/$defs/path" }
    },
    "forbidden_paths": {
      "type": "array",
      "items": { "$ref": "#/$defs/forbidden_path" },
      "default": []
    }
  },
  "$defs": {
    "guard_context": {
      "type": "object",
      "description": "Variable bindings for guard evaluation",
      "additionalProperties": {
        "oneOf": [
          { "type": "boolean" },
          { "type": "number" },
          { "type": "string" }
        ]
      }
    },
    "oracle": {
      "type": "object",
      "required": ["oracle_id", "category", "trace", "expected"],
      "properties": {
        "oracle_id": { "type": "string", "pattern": "^O[0-9]+$" },
        "category": {
          "type": "string",
          "enum": [
            "positive_trace",
            "negative_trace",
            "invariant_check",
            "requirement_binding"
          ]
        },
        "description": { "type": "string" },
        "trace": {
          "type": "array",
          "items": { "type": "string" },
          "minItems": 1
        },
        "step_contexts": {
          "type": "array",
          "description": "Optional per-step guard_context; length = len(trace)",
          "items": { "$ref": "#/$defs/guard_context" }
        },
        "initial_context": { "$ref": "#/$defs/guard_context" },
        "expected": {
          "type": "object",
          "oneOf": [
            {
              "required": ["final_state"],
              "properties": {
                "final_state": { "type": "string" },
                "accept": { "type": "boolean", "const": true }
              }
            },
            {
              "required": ["reject"],
              "properties": {
                "reject": { "type": "boolean", "const": true },
                "reason": { "type": "string" }
              }
            },
            {
              "required": ["invariant"],
              "properties": {
                "invariant": { "type": "string" },
                "holds": { "type": "boolean", "const": true }
              }
            }
          ]
        },
        "requirement_refs": {
          "type": "array",
          "items": { "type": "string", "pattern": "^R[0-9]+$" }
        }
      },
      "additionalProperties": false
    },
    "path": {
      "type": "object",
      "required": ["path_id", "steps", "expected"],
      "properties": {
        "path_id": { "type": "string", "pattern": "^P[0-9]+$" },
        "description": { "type": "string" },
        "steps": {
          "type": "array",
          "minItems": 2,
          "items": {
            "type": "object",
            "required": ["event"],
            "properties": {
              "event": { "type": "string" },
              "context": { "$ref": "#/$defs/guard_context" }
            }
          }
        },
        "initial_context": { "$ref": "#/$defs/guard_context" },
        "expected": {
          "type": "object",
          "required": ["final_state"],
          "properties": {
            "final_state": { "type": "string" }
          }
        },
        "covers_transitions": {
          "type": "array",
          "description": "Reference transition tuples this path is intended to cover",
          "items": { "type": "string" }
        },
        "requirement_refs": {
          "type": "array",
          "items": { "type": "string" }
        }
      },
      "additionalProperties": false
    },
    "forbidden_path": {
      "type": "object",
      "required": ["forbidden_id", "trace", "requirement_ref"],
      "properties": {
        "forbidden_id": { "type": "string", "pattern": "^F[0-9]+$" },
        "trace": { "type": "array", "items": { "type": "string" } },
        "initial_context": { "$ref": "#/$defs/guard_context" },
        "requirement_ref": { "type": "string" }
      }
    }
  },
  "additionalProperties": false
}
```

#### Minimum test counts (core tier)

| Component | Min | Category mix (oracles) |
|-----------|----:|------------------------|
| Oracles | 8 | ≥3 positive, ≥2 negative, ≥2 invariant, ≥1 binding |
| Paths | 6 | Each ≥2 steps; cover ≥50% reference transitions collectively |
| Forbidden paths | 2 | From "must not" requirements |

### 4.4 Evaluation report (`evaluation_report.schema.json`)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "fsm-bench-next/evaluation-report/v1",
  "title": "FSM-Bench-Next Evaluation Report",
  "type": "object",
  "required": ["run_id", "system_id", "schema_version", "layers", "scores"],
  "properties": {
    "run_id": { "type": "string" },
    "system_id": { "type": "string" },
    "model": { "type": "string" },
    "campaign_id": { "type": "string" },
    "evaluated_at": { "type": "string", "format": "date-time" },
    "schema_version": { "type": "string", "const": "1.0.0" },
    "layers": {
      "type": "object",
      "properties": {
        "L0_structural": { "$ref": "#/$defs/layer_l0" },
        "L1_determinism": { "$ref": "#/$defs/layer_l1" },
        "L2_behavioral": { "$ref": "#/$defs/layer_l2" },
        "L3_coverage": { "$ref": "#/$defs/layer_l3" },
        "L4_equivalence": { "$ref": "#/$defs/layer_l4" }
      }
    },
    "scores": { "$ref": "#/$defs/scores" }
  },
  "$defs": {
    "layer_l0": {
      "type": "object",
      "properties": {
        "g1_valid_json": { "type": "boolean" },
        "g2_schema_valid": { "type": "boolean" },
        "g2_errors": { "type": "array", "items": { "type": "string" } }
      }
    },
    "layer_l1": {
      "type": "object",
      "properties": {
        "g3_strict": { "type": "boolean" },
        "g3_guard_aware": { "type": "boolean" },
        "nondeterministic_pairs": { "type": "integer" },
        "overlapping_guard_groups": { "type": "integer" },
        "nd_guard_rate": { "type": "number" }
      }
    },
    "layer_l2": {
      "type": "object",
      "properties": {
        "oracle_pass_rate": { "type": "number" },
        "oracle_evaluable": { "type": "integer" },
        "oracle_pass": { "type": "integer" },
        "path_pass_rate": { "type": "number" },
        "forbidden_pass_rate": { "type": "number" },
        "primary_failure_mode": { "type": "string" }
      }
    },
    "layer_l3": {
      "type": "object",
      "properties": {
        "rcov": { "type": "number" },
        "rref": { "type": "number" },
        "tcov_exact": { "type": "number" },
        "tcov_relaxed": { "type": "number" },
        "pcov": { "type": "number" }
      }
    },
    "layer_l4": {
      "type": "object",
      "properties": {
        "gss": { "type": "number" },
        "gba": { "type": "number" },
        "gfv": { "type": "number" },
        "teq": { "type": "number" },
        "teq_pass": { "type": "boolean" }
      }
    },
    "scores": {
      "type": "object",
      "properties": {
        "s_structural": { "type": "number" },
        "s_determinism": { "type": "number" },
        "s_behavioral": { "type": "number" },
        "s_coverage": { "type": "number" },
        "s_equivalence": { "type": "number" },
        "fbns": { "type": "number" },
        "fbns_pass": { "type": "boolean" }
      }
    }
  }
}
```

### 4.5 Example reference + testsuite excerpt (`vending_machine`)

**Reference** (`reference/vending_machine.json`) — abbreviated:

```json
{
  "metadata": {
    "status": "approved",
    "system_id": "vending_machine",
    "version": "1.0.0",
    "requirement_source": "dataset/systems/vending_machine.json",
    "authors": ["..."],
    "reviewers": ["..."],
    "created": "2026-06-03"
  },
  "states": ["Idle", "CreditAvailable", "Dispensing", "SoldOut"],
  "initial_state": "Idle",
  "events": ["coin_inserted", "select_item", "dispense", "cancel"],
  "transitions": [
    {
      "source": "Idle",
      "event": "coin_inserted",
      "guard": "amount > 0",
      "action": "accept_coin",
      "target": "CreditAvailable",
      "requirement": "R2"
    }
  ],
  "forbidden_behaviours": [
    {
      "trace": ["dispense"],
      "reason": "Cannot dispense from Idle without credit",
      "requirement": "R5"
    }
  ]
}
```

**Test suite** (`testsuites/vending_machine.json`) — abbreviated:

```json
{
  "system_id": "vending_machine",
  "schema_version": "1.0.0",
  "reference_id": "vending_machine",
  "guard_predicates": {
    "amount": { "type": "number", "default": 0 }
  },
  "oracles": [
    {
      "oracle_id": "O1",
      "category": "positive_trace",
      "trace": ["coin_inserted", "select_item", "dispense"],
      "initial_context": { "amount": 100 },
      "step_contexts": [{}, {}, {}],
      "expected": { "final_state": "Idle", "accept": true },
      "requirement_refs": ["R2", "R3", "R4"]
    },
    {
      "oracle_id": "O2",
      "category": "negative_trace",
      "trace": ["dispense"],
      "expected": { "reject": true, "reason": "no_credit" },
      "requirement_refs": ["R5"]
    }
  ],
  "paths": [
    {
      "path_id": "P1",
      "description": "Happy path purchase",
      "steps": [
        { "event": "coin_inserted", "context": { "amount": 50 } },
        { "event": "select_item", "context": {} },
        { "event": "dispense", "context": {} }
      ],
      "expected": { "final_state": "Idle" },
      "covers_transitions": ["Idle:coin_inserted:CreditAvailable"]
    }
  ],
  "forbidden_paths": [
    {
      "forbidden_id": "F1",
      "trace": ["select_item"],
      "requirement_ref": "R5"
    }
  ]
}
```

---

## 5. Evaluation pipeline

### 5.1 Pipeline overview

```text
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ Candidate FSM   │────►│ L0 Structural    │────►│ L1 Determinism  │
│ (cleaned JSON)  │     │ G1, G2           │     │ G3, G3′         │
└─────────────────┘     └────────┬─────────┘     └────────┬────────┘
                                 │ G2 fail               │ G2 pass
                                 ▼                       ▼
                        ┌────────────────────────────────────────┐
                        │ L2 Behavioral (testsuite)              │
                        │ L3 Coverage (T, R, P)                  │
                        │ L4 Equivalence (reference)             │
                        └────────────────────┬───────────────────┘
                                             ▼
                                    ┌─────────────────┐
                                    │ L5 Scoring FBNS │
                                    └────────┬────────┘
                                             ▼
                              results/next/details/<run_id>.json
                              results/next/metrics.csv
```

### 5.2 Entry point

```bash
# Single candidate
python3.12 scripts/evaluate_next.py \
  --candidate outputs/cleaned/qwen2.5-coder:14b/vending_machine.json \
  --system vending_machine \
  --campaign C2_oracle_eval

# Batch (all cleaned outputs for tier)
python3.12 scripts/evaluate_next.py \
  --batch outputs/cleaned/ \
  --tier core \
  --campaign C2_oracle_eval \
  --manifest results/next/manifest_C2.json
```

### 5.3 Stage definitions

#### Stage 0 — Load and validate inputs

| Step | Action | Fail behaviour |
|------|--------|----------------|
| 0.1 | Load `catalog.json`, `reference/<id>.json`, `testsuites/<id>.json` | Abort if missing for tier |
| 0.2 | Load candidate FSM; unwrap envelope if present | G1=false |
| 0.3 | Self-test: run testsuite on reference FSM (CI only) | Block approval if reference fails own tests |

#### Stage 1 — L0 Structural (`structural.py`)

Identical to FSM-Bench-20:

- JSON parse (G1)
- Pydantic `FSMOutput` validation
- Referential closure (states, events)
- Reject wildcard sources (`*`, `any_state`)

Output: `g1_valid_json`, `g2_schema_valid`, `g2_errors[]`

#### Stage 2 — L1 Determinism (`determinism.py`)

1. **G3 strict:** duplicate `(source, event)` detection  
2. **G3′ guard-aware:** group by `(source, event)`; pairwise guard overlap analysis via DSL  
3. Compute `nd_guard_rate`

If G2=false: set L1 fields to `null`, `skipped=true`.

#### Stage 3 — L2 Behavioral (`simulator.py`)

For each oracle, path, forbidden_path:

1. Parse guard contexts  
2. Simulate trace step-by-step  
3. Record pass/fail + failure code (BF-01…BF-07)  
4. Mark `evaluable=false` if guard ND blocks step

Output: `oracle_pass_rate`, `path_pass_rate`, `forbidden_pass_rate`, `primary_failure_mode`

#### Stage 4 — L3 Coverage (`coverage.py`)

- `rcov`, `rref` from requirement fields  
- `tcov_exact`, `tcov_relaxed` vs reference transitions  
- `pcov` from path tests

#### Stage 5 — L4 Equivalence (`equivalence.py`)

Requires `reference.metadata.status = approved`.

- `gss` ← `tcov_relaxed`  
- `gba` ← fraction of reference-derived positive paths passing on candidate  
- `gfv` ← forbidden acceptance rate  
- `teq` ← composite (§2.7)

If reference not approved: L4 skipped, `teq=null`.

#### Stage 6 — L5 Scoring (`scoring.py`)

Compute sub-scores and FBNS (§6).

#### Stage 7 — Manifest and export

Append to `run_index.jsonl`; aggregate row to `metrics.csv`.

### 5.4 Reproducibility requirements

| Requirement | Implementation |
|-------------|----------------|
| Deterministic simulator | Pure Python; no randomness; fixed tie-break: first matching transition in list order |
| Pinned schemas | `catalog.schema_version`; hash in manifest |
| Version logging | `evaluate_next.py --version` prints schema + simulator version |
| Input hashing | SHA-256 of candidate JSON + testsuite + reference stored in report |
| CI validation | `.github/workflows/validate.yml` runs reference self-tests |

### 5.5 Self-test (reference validation)

Before marking reference `approved`:

```bash
python3.12 scripts/evaluate_next.py \
  --candidate reference/vending_machine.json \
  --system vending_machine \
  --self-test
```

**Pass criteria:** G2, G3′, OPR=1.0, PCov=1.0, TEQ=1.0 on reference against its own testsuite.

### 5.6 Performance (single researcher)

| Operation | Expected time |
|-----------|---------------|
| Evaluate one candidate | < 100 ms (CPU) |
| Batch 72 candidates (core tier) | < 10 s |
| Full core tier generation (6×12 LLM) | GPU-bound; evaluation offline |

---

## 6. Scoring methodology

### 6.1 Sub-scores

All sub-scores ∈ [0, 1]. Binary gates map to {0, 1}.

| Sub-score | Symbol | Formula |
|-----------|--------|---------|
| **Structural** | `S_structural` | `1.0` if G2 else `0.5` if G1 else `0.0` |
| **Determinism** | `S_determinism` | `1.0` if G3′ else `0.5` if G3 else `0.0` |
| **Behavioral** | `S_behavioral` | `0.5·OPR + 0.3·PCov + 0.2·(1−FPR)` where FPR = forbidden path accept rate |
| **Coverage** | `S_coverage` | `0.35·RCov + 0.35·TCov_relaxed + 0.30·RRef` |
| **Equivalence** | `S_equivalence` | TEQ if reference approved; else `S_behavioral` (fallback, flagged) |

When G2=false: `S_behavioral`, `S_coverage`, `S_equivalence` = 0.

### 6.2 FSM-Bench-Next Score (FBNS)

Weighted composite from `catalog.json` (default weights):

```text
FBNS = w_s·S_structural + w_d·S_determinism + w_b·S_behavioral
     + w_c·S_coverage + w_e·S_equivalence

Default: w_s=0.15, w_d=0.15, w_b=0.30, w_c=0.20, w_e=0.20  (Σ=1.0)
```

**FBNS pass:** FBNS ≥ 0.70 (configurable `thresholds.fbns_pass`).

### 6.3 Reporting metrics (CSV columns)

`results/next/metrics.csv` — one row per (campaign, model, system):

| Column | Layer | Description |
|--------|-------|-------------|
| `run_id` | — | UUID |
| `campaign_id` | — | Campaign manifest ID |
| `model` | — | LLM identifier |
| `system_id` | — | System stem |
| `g1` | L0 | bool |
| `g2` | L0 | bool |
| `g3` | L1 | bool strict |
| `g3_prime` | L1 | bool guard-aware |
| `opr` | L2 | oracle pass rate |
| `pcov` | L2/L3 | path coverage |
| `fpr` | L2 | forbidden pass rate (lower better) |
| `rcov` | L3 | requirement coverage |
| `rref` | L3 | reference-aligned recall |
| `tcov_exact` | L3 | transition coverage exact |
| `tcov_relaxed` | L3 | transition coverage relaxed |
| `gss` | L4 | gold structural similarity |
| `gba` | L4 | gold behavioral alignment |
| `gfv` | L4 | gold forbidden violation rate |
| `teq` | L4 | trace equivalence |
| `fbns` | L5 | composite score |
| `primary_failure_mode` | L2 | BF-xx |
| `nd_guard_rate` | L1 | non-decidable guard fraction |

### 6.4 Layer-gated reporting (EMSE alignment)

For paper RQs, report **primary endpoints** separately from FBNS:

| RQ (EMSE) | Primary metrics from FSM-Bench-Next |
|-----------|-------------------------------------|
| RQ1 gap | `g2`, `opr`, `g2 ∧ ¬opr` |
| RQ2 failures | `primary_failure_mode` distribution |
| RQ3 proxies | `rcov`, `g3_prime`, `gss`, `gba`, correlations |
| RQ4–RQ5 | Perturbation deltas (outside FBNS; same pipeline on perturbed candidates) |
| RQ6–RQ7 | Repeat variance on `opr`, `fbns`, `g3_prime` |

FBNS is a **summary index** for benchmark consumers; EMSE analysis uses layer-specific metrics.

### 6.5 Failure mode codes

| Code | Label | Layer |
|------|-------|-------|
| BF-01 | Wrong terminal state | L2 |
| BF-02 | Forbidden trace accepted | L2 |
| BF-03 | Invariant violated | L2 |
| BF-04 | Requirement not exercised | L2 |
| BF-05 | Trace stuck (no transition) | L2 |
| BF-06 | Non-deterministic resolution | L2 |
| BF-07 | Not evaluable (guard ND) | L2 |
| SF-01 | Invalid JSON | L0 |
| SF-02 | Schema invalid | L0 |
| SF-03 | Strict non-determinism | L1 |
| SF-04 | Guard-aware non-determinism | L1 |

### 6.6 Aggregation rules

| Level | Aggregation |
|-------|-------------|
| Per (model, system) | Single evaluation report |
| Per model | Mean FBNS, mean OPR over core tier; Wilson CI on gate rates |
| Per system | Mean OPR over models |
| Global | Mean over all core (model, system) pairs |

**Do not** rank models as primary EMSE outcome; report distributions and CIs.

---

## 7. Authoring workflow (single researcher)

### 7.1 Phase schedule

| Phase | Deliverable | Effort estimate |
|-------|-------------|-----------------|
| **P0** | Pipeline skeleton + pilot 3 systems | 2 weeks |
| **P1** | Core 12 reference + testsuite | 4–6 weeks (~3–4 h/system) |
| **P2** | Stretch 8 systems | 3–4 weeks |
| **P3** | Zenodo package + CI self-tests | 1 week |

### 7.2 Per-system authoring checklist

1. Import requirements from FSM-Bench-20  
2. Draft reference FSM (DSL guards only)  
3. Map every Rn to transition or forbidden_behaviour  
4. Author ≥8 oracles + ≥6 paths covering ≥50% transitions  
5. Run `--self-test` on reference  
6. Peer or deferred self-review after 48 h  
7. Set `metadata.status = approved`  
8. Commit reference + testsuite + update `reference/index.json`

### 7.3 Quality gates before campaign freeze

- [ ] All core references pass self-test  
- [ ] CI validates schemas and reference self-tests  
- [ ] `catalog.json` tier lists match committed files  
- [ ] Simulator version pinned in campaign manifest  

---

## 8. Mapping to repository paths

| Spec path | Current EMSE repo path | Action |
|-----------|------------------------|--------|
| `reference/` | `benchmark/gold/` | Rename or alias; gold → reference in v1.1 |
| `testsuites/` | `benchmark/oracles/` | Merge oracle + path into testsuite schema |
| `schemas/` | `benchmark/oracles/schema.json` | Consolidate under `schemas/` |
| `scripts/evaluate_next.py` | `scripts/run_behavioral_evaluation.py` | Implement per §5 |

---

## 9. Version history

| Version | Date | Change |
|---------|------|--------|
| **1.0.0** | 2026-06-03 | Initial FSM-Bench-Next specification |

---

## Appendix A — Guard DSL grammar (EBNF sketch)

```ebnf
guard       := empty | bool_lit | predicate | compare | negation | conjunction ;
empty       := "" ;
bool_lit    := "true" | "false" ;
predicate   := IDENT ;
compare     := IDENT COMP_OP ( NUMBER | STRING ) ;
negation    := "not" IDENT ;
conjunction := guard "and" guard ;
IDENT       := [a-z][a-z0-9_]* ;
COMP_OP     := ">=" | "<=" | ">" | "<" | "==" | "!=" ;
```

## Appendix B — Simulator algorithm (deterministic)

```python
def simulate(fsm, trace, initial_context, step_contexts, guard_eval):
    state = fsm.initial_state
    context = dict(initial_context)
    for i, event in enumerate(trace):
        ctx = merge(context, step_contexts[i] if step_contexts else {})
        matches = [t for t in fsm.transitions
                   if t.source == state and t.event == event
                   and guard_eval(t.guard, ctx)]
        if len(matches) == 0:
            return Result(rejected=True, reason="no_transition")
        if len(matches) > 1:
            return Result(rejected=True, reason="nondeterministic")
        state = matches[0].target
        context = apply_actions(matches[0].action, context)
    return Result(rejected=False, final_state=state)
```

Tie-break policy: if multiple matches after guard eval → BF-06 (should not occur when G3′ pass).

## Appendix C — IST → FSM-Bench-Next metric mapping

| FSM-Bench-20 | FSM-Bench-Next |
|--------------|----------------|
| G1 | L0 `g1` |
| G2 | L0 `g2` |
| G3 nested | L1 `g3` |
| — | L1 `g3_prime` |
| requirement_coverage | L3 `rcov` |
| — | L2 `opr`, L3 `pcov` |
| — | L4 `teq`, `gba`, `gss` |
| — | L5 `fbns` |

---

*End of FSM-Bench-Next specification v1.0.0*
