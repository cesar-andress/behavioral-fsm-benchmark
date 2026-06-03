# behavioral-fsm-benchmark — Benchmark Specification

**Document ID:** `benchmark_spec_v2.0`  
**Repository:** `behavioral-fsm-benchmark`  
**Status:** Authoritative benchmark design (pre-campaign)  
**Extends:** FSM-Bench-20 (IST 2026) — DOI [10.5281/zenodo.20516296](https://doi.org/10.5281/zenodo.20516296)  
**Target study:** EMSE 2026 — *Beyond Structural Validity*  
**Date:** 2026-06-03

---

## 1. Scope

### 1.1 Purpose

**behavioral-fsm-benchmark** is the evaluation layer that extends FSM-Bench-20 with:

- Human-approved **gold (reference) FSMs**
- Executable **behavioral test suites**
- **Guard DSL** semantics and **guard-aware determinism (G3a)**
- Transition, requirement, and path coverage
- Trace-based equivalence against gold
- Deterministic, schema-validated reporting

FSM-Bench-20 answers: *Is the output structurally valid?*  
This benchmark answers: *Does the FSM behave correctly, deterministically, and consistently with an approved reference under executable tests?*

### 1.2 In scope

| Item | Description |
|------|-------------|
| Requirement texts | 20 systems imported from FSM-Bench-20 (`benchmark/datasets/`) |
| Candidate FSMs | LLM outputs in `generated_fsm.schema.json` format |
| Gold FSMs | Reviewer-approved references in `benchmark/gold_fsms/` |
| Test suites | Oracle, path, and forbidden tests in `benchmark/test_suites/` |
| Evaluation | Layers L0–L5 via `framework/` (offline, deterministic) |
| Campaign exports | Manifest-driven runs under `experiments/` (gitignored until freeze) |

### 1.3 Out of scope

- Live LLM generation inside the evaluator
- Full bisimulation or model checking
- Manual per-run adjudication at scale
- Claiming EMSE empirical results before campaign freeze

### 1.4 Design constraints (single-researcher feasibility)

| Constraint | Response |
|------------|----------|
| Limited gold authoring time | Tiered rollout: 3 pilot → 12 core → 8 stretch |
| No manual oracle review at scale | Fully automated trace simulator + decidable guard DSL |
| No formal verification | Trace equivalence vs gold, not bisimulation |
| Compute budget | Evaluate cached candidates offline; generation is separate |
| Reviewer burden | One gold FSM + one test suite per system; checklist approval |
| Reproducibility | Pinned schemas (`benchmark/schemas/`), deterministic simulator, manifest hashes |

### 1.5 Relationship to FSM-Bench-20

```text
FSM-Bench-20                          behavioral-fsm-benchmark
─────────────────                     ───────────────────────────
dataset/systems/*.json        ───────► benchmark/datasets/systems/ (import)
FSMOutput / generated_fsm     ───────► candidate format (unchanged)
G1, G2, G3 gates              ───────► L0–L1 (inherited + G3a)
—                             ───────► benchmark/gold_fsms/
—                             ───────► benchmark/test_suites/
—                             ───────► L2–L5 evaluation layers
```

---

## 2. System tiers (20 systems)

All 20 requirement sets come from FSM-Bench-20. Gold FSMs and test suites are authored per tier.

| Tier | Count | Gold + test suite | Role in EMSE |
|------|------:|-------------------|--------------|
| **Pilot** | 3 | First authoring target; pipeline shake-down | Self-test and tooling validation only |
| **Core** | 12 | Required, `metadata.status = approved` | All primary inferential metrics (RQ1–RQ7) |
| **Stretch** | 8 | Phase 2; optional for inference | Full 20-system parity and descriptive extension |

### 2.1 Pilot systems (3)

`vending_machine`, `atm`, `login_system`

### 2.2 Core systems (12)

`vending_machine`, `atm`, `login_system`, `access_control`, `elevator`, `ticket_machine`, `ecommerce_checkout`, `medical_appointment_booking`, `hotel_booking`, `smart_thermostat`, `library_loan`, `parking_gate`

### 2.3 Stretch systems (8)

`bike_rental`, `car_rental`, `train_ticket_booking`, `restaurant_reservation`, `warehouse_inventory`, `gym_membership`, `package_locker`, `online_examination`

### 2.4 Tier rules

- **Core** systems MUST have approved gold and passing self-tests before C2 (behavioral campaign) freeze.
- **Stretch** systems MAY remain in `draft` during primary EMSE analysis; metrics are reported descriptively if present.
- **Pilot** systems MUST pass the gold acceptance checklist (§8) before core authoring scales.

---

## 3. Gold FSM requirements

Gold FSMs live in `benchmark/gold_fsms/<system_id>.json` and MUST validate against `benchmark/schemas/reference_fsm.schema.json`.

### 3.1 Authorship rules

| Rule | Requirement |
|------|-------------|
| Naming | PascalCase states; `snake_case` events |
| Guards | DSL-evaluable forms only in `approved` gold (§4) |
| Requirement mapping | Every requirement `R1…Rn` cited on ≥1 transition or `forbidden_behaviours` entry |
| Completeness | Document intentional `(state, event)` omissions in `metadata.completions[]` |
| Self-consistency | Gold MUST pass its own test suite at 100% before approval |
| Provenance | `metadata.source` points to imported requirement file |

### 3.2 Approval workflow

1. Author draft gold from imported requirements.
2. Author matching test suite (`benchmark/test_suites/<system_id>.json`).
3. Run reference self-test (§8.2).
4. Deferred review (≥48 h) using gold checklist (§8.1).
5. Set `metadata.status = "approved"`, record `approved_by`, `approved_at`.
6. Commit gold + test suite; update tier index in `benchmark/catalog.json` (when present).

### 3.3 Status values

| Status | L4 equivalence scoring | Use |
|--------|------------------------|-----|
| `placeholder` | Skipped | Bootstrap only; never in official EMSE tables |
| `draft` | Skipped | Work in progress |
| `review` | Skipped | Awaiting sign-off |
| `approved` | Enabled | Official scoring stratum |
| `deprecated` | Skipped | Superseded; retained for audit |

---

## 4. Guard DSL and determinism gates

### 4.1 Guard DSL (decidable subset)

Natural-language guards in candidate FSMs are parsed when possible; otherwise marked **non-decidable (ND)**.

| Form | Example | Semantics |
|------|---------|-----------|
| Empty | `""` | Always enabled |
| Boolean literal | `true`, `false` | Constant |
| Variable compare | `balance >= 10`, `attempts < 3` | Numeric/string literal compare |
| Negation | `not invalid_pin` | Boolean variable negation |
| Conjunction | `balance >= 10 and card_valid` | All conjuncts must hold |
| Named predicate | `pin_valid` | Resolved from test `guard_context` / `guard_predicates` |

Variables and predicates are declared in the test suite (`guard_predicates`, per-step `context`). **Approved gold guards MUST use DSL forms only.**

Grammar sketch: Appendix A.

### 4.2 G3 — strict determinism (inherited)

**G3 pass:** no duplicate `(source, event)` pairs among transitions, regardless of guards.

Retained for IST comparability (FSM-Bench-20 nested gate).

### 4.3 G3a — guard-aware determinism (primary)

For each `(source, event)` group, two transitions are **compatible** iff:

1. They share the same `target` and guards are **provably mutually exclusive**, or  
2. Guards are **identical** and targets are equal (duplicate row — hygiene violation, not ND).

**G3a pass:** no group contains two transitions with overlapping enabled guards reaching **different** targets.

G3a is the **primary** determinism gate for behavioral interpretation; G3 is reported alongside for structural replication.

### 4.4 Non-decidable guards

| Situation | Determinism check | Simulation |
|-----------|-------------------|------------|
| Unparseable guard (non-empty) | Group marked ND; conservative overlap assumed | Step marked `evaluable=false` |
| Empty guard | Always evaluable | Always evaluable |

Report `nd_guard_rate` = ND transitions / total transitions.

---

## 5. Behavioral test-suite requirements

Each system has one test suite JSON in `benchmark/test_suites/<system_id>.json`, validated against `benchmark/schemas/testsuite.schema.json`.

### 5.1 Components

| Component | Purpose |
|-----------|---------|
| **Oracle tests** | Single trace + expected outcome (positive, negative, invariant, binding) |
| **Path tests** | Multi-step scenarios with per-step `guard_context` |
| **Forbidden paths** | Negative traces that MUST be rejected |
| **Guard predicates** | Named variables used in guards |

### 5.2 Minimum counts (core tier)

| Component | Minimum | Category mix (oracles) |
|-----------|--------:|------------------------|
| Oracles | 8 | ≥3 positive, ≥2 negative, ≥2 invariant, ≥1 requirement binding |
| Paths | 6 | Each ≥2 steps; collectively cover ≥50% of gold transitions |
| Forbidden paths | 2 | Derived from "must not" requirements |

Stretch tier: ≥5 oracles (≥3 positive, ≥2 negative), ≥4 paths, ≥1 forbidden path acceptable during phase 2.

### 5.3 Test categories

| Category | Pass criterion |
|----------|----------------|
| `positive_trace` | Trace executes; final state matches expected |
| `negative_trace` | Trace rejected or remains in safe state per expected |
| `invariant_check` | Stated invariant holds after valid prefix |
| `requirement_binding` | Named requirement exercised by fired transitions |

### 5.4 Self-test requirement

Before gold approval, the reference self-test MUST achieve:

- G2 pass, G3a pass
- Behavioral test-suite agreement (oracle + path) = 1.0 on evaluable tests
- Forbidden-path rejection rate = 0 false accepts

---

## 6. JSON formats and schemas

**Authoritative schemas:** `benchmark/schemas/`

| Schema file | Artifact | Location |
|-------------|----------|----------|
| `requirement_spec.schema.json` | NL requirement sets | `benchmark/datasets/systems/` |
| `generated_fsm.schema.json` | Candidate / LLM FSM | `experiments/runs/` (cleaned exports) |
| `reference_fsm.schema.json` | Gold FSM | `benchmark/gold_fsms/` |
| `testsuite.schema.json` | Behavioral test suite | `benchmark/test_suites/` |
| `evaluation_report.schema.json` | Per-run evaluation export | `experiments/` / `analysis/` |
| `experiment_manifest.schema.json` | Campaign manifest | `experiments/manifests/` |
| `catalog.schema.json` | Tier lists and thresholds | `benchmark/catalog.json` |

Legacy aliases (`candidate_fsm.schema.json`) remain for migration; new artifacts MUST use the schemas above.

### 6.1 Candidate envelope (optional)

Evaluators accept bare FSM JSON or an envelope:

```json
{
  "candidate_metadata": {
    "model": "<ollama-tag>",
    "system_id": "<system_id>",
    "campaign_id": "C2_behavioral",
    "run_id": "<uuid>",
    "generated_at": "<ISO-8601>"
  },
  "fsm": { }
}
```

### 6.2 Evaluation report (summary fields)

Per-run reports include layer blocks `L0_structural` … `L4_equivalence`, composite scores, input hashes, and failure codes. Full field definitions: `benchmark/schemas/evaluation_report.schema.json`.

---

## 7. Traceability conventions

### 7.1 Requirement identifiers

- Requirements in imported specs use IDs `R1`, `R2`, …, `Rn` (FSM-Bench-20 convention).
- Transitions MAY cite one requirement in `requirement` (string).
- Test cases MAY cite multiple requirements in `requirement_refs[]`.

### 7.2 Transition tuple keys

Normalized transition tuple for matching and coverage:

```text
τ = (normalize(source), normalize(event), normalize(target), guard_key)
```

`guard_key` = canonical DSL string, or `"_"` if empty.

Human-readable key: `source:event:target` (guard omitted in relaxed matching).

### 7.3 Test identifiers

| Kind | Pattern | Example |
|------|---------|---------|
| Oracle | `O[0-9]+` | `O1` |
| Path | `P[0-9]+` | `P3` |
| Forbidden | `F[0-9]+` | `F1` |

### 7.4 Provenance chain

```text
requirement_spec  →  gold_fsm  →  testsuite  →  candidate  →  evaluation_report
     (R*)              ( cites R*)   (refs R*)      ( cites R*)     (metrics + hashes)
```

Each evaluation report MUST record SHA-256 hashes of: candidate JSON, gold FSM, test suite, and manifest row.

### 7.5 Campaign traceability

| ID | Format | Example |
|----|--------|---------|
| Campaign | `C[0-9]_<slug>` | `C2_behavioral` |
| Run | UUID v4 | `a1b2c3d4-…` |
| Manifest | `experiments/manifests/<campaign>_v<semver>.json` | Frozen at `frozen_at` |

---

## 8. Acceptance criteria

### 8.1 Gold approval checklist

- [ ] Validates against `reference_fsm.schema.json`
- [ ] All guards parse as DSL v1.0
- [ ] Every requirement mapped (transition or forbidden)
- [ ] Test suite validates against `testsuite.schema.json`
- [ ] Self-test: G2, G3a, full behavioral agreement on gold
- [ ] Reviewer sign-off recorded in metadata
- [ ] Committed to `benchmark/gold_fsms/` and `benchmark/test_suites/`

### 8.2 Reference self-test command

```bash
python3.12 scripts/evaluate_case.py \
  --candidate benchmark/gold_fsms/vending_machine.json \
  --system vending_machine \
  --self-test
```

(Pilot systems run first; exact CLI flags follow `scripts/` implementation.)

### 8.3 Campaign freeze gate

No EMSE Results population until:

- [ ] All **core** gold FSMs approved and self-tested
- [ ] C2 manifest frozen (`frozen_at` set)
- [ ] Evaluator version pinned in manifest
- [ ] Schema versions match `benchmark/schemas/`

---

## 9. Quality gates and evaluation layers (L0–L5)

Evaluation proceeds in **six ordered layers**. Failure at layer *L* does not abort the pipeline; downstream layers may record `skipped` with reason (e.g., L2–L4 when G2 fails).

| Layer | ID | Name | Input | Primary outputs |
|-------|-----|------|-------|-----------------|
| **L0** | Structural | JSON + schema + referential closure | Candidate FSM | G1, G2 |
| **L1** | Deterministic | Strict and guard-aware determinism | G2 passers | G3, G3a, `nd_guard_rate` |
| **L2** | Behavioral | Test-suite execution | G2 passers | Oracle/path/forbidden results, failure codes |
| **L3** | Coverage | Requirement, transition, path coverage | G2 passers | RCov, TCov, PCov, RRef |
| **L4** | Equivalence | Gold comparison | G2 passers + approved gold | GSS, GBA, GFV, TEQ |
| **L5** | Composite | Weighted index | All layer outputs | Sub-scores, FBNS |

### 9.1 Gate summary

| Gate | Rule | Layer |
|------|------|-------|
| G1 | Valid JSON | L0 |
| G2 | Schema valid + referential closure + no wildcard sources | L0 |
| G3 | Unique `(source, event)` (strict) | L1 |
| G3a | No overlapping enabled guards to different targets | L1 |
| DET_pass | G3a pass (primary determinism endpoint) | L1 |

### 9.2 L2 behavioral failure codes

| Code | Label |
|------|-------|
| BF-01 | Wrong terminal state |
| BF-02 | Forbidden trace accepted |
| BF-03 | Invariant violated |
| BF-04 | Requirement not exercised |
| BF-05 | Trace stuck (no transition) |
| BF-06 | Non-deterministic resolution at runtime |
| BF-07 | Not evaluable (guard ND) |
| SF-01 | Invalid JSON |
| SF-02 | Schema invalid |
| SF-03 | Strict non-determinism (G3) |
| SF-04 | Guard-aware non-determinism (G3a) |

### 9.3 Coverage definitions (L3)

**Requirement coverage (RCov):**

```text
RCov = |{ Rn cited in any transition.requirement }| / |{ R1…Rn in requirements }|
```

**Reference-aligned requirement recall (RRef):**

```text
RRef = |{ Rn in candidate ∩ Rn in gold }| / |{ Rn cited in gold }|
```

**Transition coverage (TCov):** exact and relaxed (guard ignored) overlap vs gold transition set.

**Path coverage (PCov):**

```text
PCov = |{ p : pass(p) ∧ evaluable(p) }| / |{ p : evaluable(p) }|
```

### 9.4 Equivalence (L4)

Full bisimulation is out of scope. Trace-oriented equivalence vs approved gold:

| Metric | Symbol | Definition |
|--------|--------|------------|
| Gold structural similarity | GSS | Relaxed transition overlap vs gold |
| Gold behavioral alignment | GBA | Fraction of gold-positive path tests passing on candidate |
| Gold forbidden violation | GFV | Fraction of forbidden paths incorrectly accepted |
| Trace equivalence score | TEQ | Weighted composite of GBA, GFV, GSS (weights in catalog) |

L4 is **skipped** when gold `metadata.status ≠ approved`.

### 9.5 Composite score (L5)

FBNS is a weighted summary index for benchmark consumers. EMSE inferential analysis uses **layer-specific metrics** (see `docs/evaluation_protocol.md`); FBNS is not a primary hypothesis endpoint.

---

## 10. Repository layout

```text
behavioral-fsm-benchmark/
├── benchmark/
│   ├── datasets/           # FSM-Bench-20 import (requirements)
│   ├── gold_fsms/          # Approved reference FSMs
│   ├── test_suites/        # Behavioral test suites
│   ├── guards/             # Guard DSL fixtures / perturbation variants
│   └── schemas/            # JSON Schema (authoritative)
├── framework/              # Python evaluation engine
├── experiments/            # configs, manifests, runs (runs gitignored)
├── analysis/               # post-freeze aggregation
├── docs/                   # this specification, protocols, policies
├── paper/                  # EMSE manuscript sources
└── scripts/                # CLI entry points
```

---

## 11. Version history

| Version | Date | Change |
|---------|------|--------|
| 1.0.0 | 2026-06-03 | Initial FSM-Bench-Next specification |
| **2.0.0** | 2026-06-03 | Renamed to `behavioral-fsm-benchmark`; G3a naming; schema paths; tier lists; traceability §7 |

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

## Appendix B — Deterministic simulator (tie-break)

When G3a passes, at most one transition is enabled per step. If multiple matches occur after guard evaluation, return BF-06. Tie-break policy when implementing: first matching transition in list order (documented in manifest).

## Appendix C — IST → behavioral-fsm-benchmark mapping

| FSM-Bench-20 | This benchmark |
|--------------|----------------|
| G1 | L0 |
| G2 | L0 |
| G3 (strict) | L1 `g3` |
| — | L1 `g3a` |
| requirement_coverage | L3 RCov |
| — | L2 behavioral agreement, L3 PCov |
| — | L4 TEQ, GSS, GBA |
| — | L5 FBNS |

---

*End of benchmark specification v2.0*
