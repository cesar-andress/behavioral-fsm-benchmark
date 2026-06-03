# C1 negative and forbidden-behavior test audit

**Scope:** Approved gold corpus (`benchmark/test_suites/`, `benchmark/gold_fsms/`) and C1 pilot campaign outcomes  
**Audit date:** 2026-06-03  
**Method:** Read-only JSON/CSV analysis; benchmark assets and campaign run directory not modified.

---

## Terminology

| Term in audit | Benchmark representation |
|---------------|-------------------------|
| **Oracle test** | `kind: "oracle"` in `benchmark/test_suites/*.json` |
| **Path test** | `kind: "path"` |
| **Forbidden / negative test** | `kind: "negative"` (schema enum: `oracle`, `path`, `negative`, `invariant`) — **no suite uses `kind: "forbidden"`** |
| **Forbidden behaviours (metadata)** | `forbidden_behaviours[]` on gold FSM JSON (trace declarations; not automatically executable unless covered by a test) |

`rejected_event_agreement` is computed from tests where `kind == "negative"` **or** `expected_final_state is null` (see `framework/behavioral/metrics.py`).

---

## 1. Test counts per system (12 gold systems)

| System | Tier | Total | Oracle | Path | Negative | Rejection-scored† | Req count | FB metadata‡ |
|--------|------|------:|-------:|-----:|---------:|------------------:|----------:|-------------:|
| access_control | core | 18 | 8 | 6 | 4 | 6 | 8 | 2 |
| atm | pilot | 16 | 6 | 7 | 3 | 3 | 8 | 2 |
| bike_rental | core | 17 | 8 | 7 | 2 | 2 | 8 | 2 |
| elevator | core | 16 | 8 | 6 | 2 | 2 | 8 | 2 |
| hotel_booking | core | 16 | 8 | 6 | 2 | 2 | 8 | 2 |
| login_system | pilot | 6 | 2 | 1 | 3 | 3 | 6 | 1 |
| package_locker | core | 17 | 8 | 6 | 3 | 4 | 8 | 2 |
| parking_gate | core | 17 | 8 | 6 | 3 | 3 | 8 | 2 |
| smart_thermostat | core | 16 | 8 | 6 | 2 | 2 | 8 | 2 |
| train_ticket_booking | core | 16 | 8 | 6 | 2 | 2 | 8 | 2 |
| vending_machine | pilot | 6 | 2 | 1 | 3 | 3 | 6 | 1 |
| warehouse_inventory | core | 16 | 8 | 6 | 2 | 2 | 8 | 2 |
| **Totals** | | **177** | **82** | **64** | **31** | **34** | | **22** |

† Rejection-scored = negative tests plus path tests with `expected_final_state: null` (`access_control`: +2, `package_locker`: +1).  
‡ `forbidden_behaviours` entries in gold FSM (documentation / traceability; not extra executable tests).

**Corpus-wide shares:** oracle 46.3%, path 36.2%, negative 17.5%, rejection-scored 19.2% of all tests.

**FSM-Bench-20 note:** `benchmark/index.json` lists 20 systems; **12** have approved gold FSMs and test suites in v0.1.0. This audit covers those 12 only.

---

## 2. Forbidden and negative test density

### 2.1 Negative test density (negative / total tests)

| Density band | Systems |
|--------------|---------|
| **High (≥30%)** | `login_system` (50%), `vending_machine` (50%), `access_control` (33.3%) |
| **Medium (15–25%)** | `package_locker` (17.6%), `atm` (18.8%), `parking_gate` (17.6%) |
| **Low (<15%)** | `bike_rental`, `warehouse_inventory`, `smart_thermostat`, `elevator`, `hotel_booking`, `train_ticket_booking` (11.8–12.5%) |

**Mean negative density:** 17.5% (31/177).  
**Mean rejection-scored density:** 19.2% (34/177).

### 2.2 Forbidden-behaviour metadata density (gold entries / requirement count)

| System | FB entries | Requirements | FB / req |
|--------|----------:|-------------:|---------:|
| vending_machine | 1 | 6 | 0.17 |
| login_system | 1 | 6 | 0.17 |
| All other 10 systems | 2 | 8 | 0.25 |

Metadata density is uniform; **executable negative coverage is not** — core batch systems typically have only **2** negative tests vs **3–4** on pilot/security-heavy systems.

---

## 3. Systems with weak rejection coverage

| System | Issue |
|--------|--------|
| **bike_rental, warehouse_inventory, smart_thermostat, elevator, hotel_booking, train_ticket_booking** | Only **2** negative tests (12.5% of suite); lowest rejection-scored share in corpus |
| **atm, parking_gate** | 3 negative tests but **18%** density; C1 pilot systems with low positive-oracle pass rates |
| **Gold `forbidden_behaviours` vs tests** | Every system has ≥1 FB metadata entry but **no** standalone `forbidden` test kind; coverage relies entirely on authorship of `negative` tests |
| **access_control, package_locker** | Extra rejection-scored **path** tests without `expected_final_state` inflate denominator vs strict `negative` count |

**No system has zero negative tests.** Weakest executable rejection coverage: **6 core systems with 2 negative tests each.**

---

## 4. Can `rejected_event_agreement` saturate at 1.0 too easily?

### 4.1 Verdict: **Yes — under current oracle semantics and C1 outcomes.**

| Evidence | Finding |
|----------|---------|
| C1 pilot (54 evaluable runs) | **54/54** runs have `rejected_event_agreement = 1.0` (100%) |
| Campaign mean (`rq_summary.md`) | Mean rejected-event agreement = **1.0** |
| Gold self-test (all 12 systems) | REA = **1.0** on approved gold FSMs (expected) |
| Low-BPR runs (14 runs with BPR ≤ 0.3125, mostly `atm`) | REA still **1.0**; `final_state_agreement` and `trace_agreement` near **0** |

### 4.2 Mechanism (evaluator logic)

From `framework/behavioral/oracle.py`:

- A test is **rejection-scored** when `kind == "negative"` or `expected_final_state is None`.
- If simulation **does not succeed** (missing transition, stuck, error), `rejection_matched = True` for rejection-scored tests — counted as **correct rejection**.
- If simulation **succeeds** on a rejection-scored test, `rejection_matched = False`.

**Consequence:** FSMs that fail positive paths by **omitting transitions** often **automatically pass all negative tests**, because forbidden event sequences fail to simulate. REA measures “did the simulator fail?” more than “did the FSM explicitly encode a rejection guard?”

**Controlled check:**

| Synthetic candidate | BPR | REA |
|---------------------|-----|-----|
| Empty transition set (`atm`) | 0.3125 | **1.0** |
| Gold + spurious accepting transition (`vending_machine`, coffee from Idle) | 0.833 | **0.667** |
| Gold + spurious accepting transition (`login_system`, logout from LoggedOut) | 0.833 | **0.667** |

REA **can** drop below 1.0 when candidates **accept** forbidden events, but C1 LLM outputs rarely exhibit that failure mode; they more often fail by **non-acceptance via missing transitions**, which inflates REA.

### 4.3 Saturation risk factors

1. **Small rejection denominators** (2–4 tests per system, 11–50% of suite).  
2. **Asymmetric oracle** — simulation failure ≡ pass on negative tests.  
3. **Decorrelation from BPR** — C1 shows REA = 1.0 while BPR ranges 0.3125–1.0 and trace agreement often ≈ 0.  
4. **Path tests in rejection denominator** — `path_invalid_scan`, `path_rejected_lock`, `path_invalid_code` use the same pass-on-failure rule.

---

## 5. C1 pilot alignment

Pilot systems in C1 (`vending_machine`, `login_system`, `atm`):

| System | Negative tests | Rejection-scored | C1 evaluable runs | REA = 1.0 |
|--------|---------------:|-----------------:|------------------:|----------:|
| vending_machine | 3 | 3 | 20 | 20/20 |
| login_system | 3 | 3 | 20 | 20/20 |
| atm | 3 | 3 | 14 | 14/14 |

Pilot suites have **higher negative density** than most core systems but still yield **no REA discrimination** in C1.

---

## 6. Implications for paper metrics

| Metric | C1 discriminatory power |
|--------|-------------------------|
| `behavioral_pass_rate` | **Yes** — spreads across models/systems |
| `final_state_agreement`, `trace_agreement` | **Yes** — often low when BPR low |
| `rejected_event_agreement` | **No in C1** — saturated at 1.0; weak construct validity as a quality differentiator |

**Recommendations (analysis only; not implemented here):**

1. Treat REA as **non-discriminative** in C1 post-hoc reporting; do not interpret REA = 1.0 as strong forbidden-behavior engineering.  
2. Strengthen negative coverage on core systems (≥3 targeted negatives per system; align with each `forbidden_behaviours` entry).  
3. Consider oracle refinements that distinguish **explicit rejection** from **accidental simulation failure** (future evaluator work).  
4. Report **negative test pass count** / **forbidden false-accept rate** per run alongside REA for transparency.

---

## 7. Artefacts and code references

| Path | Role |
|------|------|
| `benchmark/test_suites/*.json` | Executable test inventory |
| `benchmark/gold_fsms/*.json` | `forbidden_behaviours` metadata |
| `framework/behavioral/metrics.py` | REA = `rejection_matches / negative_total` |
| `framework/behavioral/oracle.py` | Rejection scoring on simulation failure |
| `experiments/runs/.../metrics.csv` | C1 exported REA (all 1.0 on evaluable stratum) |

No benchmark or campaign files were modified during this audit.
