# Research Scope and Extension Roadmap

**Document ID:** `research_scope_v1.0`  
**Repository:** `behavioral-fsm-benchmark`  
**Release:** `v0.1.0`  
**Status:** Public scientific scope statement  
**Companion:** `docs/implementation_roadmap.md`, `docs/evaluation_protocol.md`, `docs/benchmark_specification.md`, `REPRODUCIBILITY.md`  
**Date:** 2026-06-03

---

## Purpose

This document separates **what is implemented and released in v0.1.0** from **explicit non-goals** and **planned extension tracks**. It is intended for reviewers, replicators, and contributors who need a precise boundary on behavioural semantics without reading the full study design.

The private EMSE manuscript lives in a separate repository; this file describes **public research software scope only**.

---

## 1. Current implemented scope (v0.1.0)

The v0.1.0 release provides a **minimal reproducible foundation** for evaluating LLM-generated finite state machines from natural-language software requirements.

| Capability | Description | Primary artifacts |
|------------|-------------|-------------------|
| **Deterministic FSMs** | Single-step simulation with at most one enabled transition per `(state, event)` under strict G3; guard-aware resolution under G3a | `framework/validators/`, `framework/behavioral/simulator.py` |
| **Natural-language requirements** | Requirement specs per system (`R1`, `R2`, …) in `benchmark/datasets/systems/` | 12 pilot + core systems |
| **JSON / schema validation** | G1 (valid JSON), G2 (schema + referential closure) | `benchmark/schemas/`, `framework/validators/schema_validator.py` |
| **Strict determinism (G3)** | Guard-blind duplicate `(source, event)` detection | `framework/validators/fsm_validator.py` |
| **Guard-aware determinism (G3a)** | Decidable guard DSL; mutually exclusive guard checking | `benchmark/guards/`, `framework/guards/` |
| **Gold FSMs** | Human-approved reference models with metadata and requirement traceability | `benchmark/gold_fsms/` (12 systems) |
| **Behavioural test suites** | Executable oracles: positive, path, and negative (forbidden) tests | `benchmark/test_suites/` |
| **Trace / final-state / rejection agreement** | Synchronous stepwise simulation; verdict per test on accept, final state, and expected rejection | `framework/behavioral/test_runner.py`, `scripts/run_behavioral_tests.py` |
| **Requirement coverage** | RCov (requirement references on transitions), TCov, PCov | `framework/coverage/` |
| **Reproducible local evaluation** | Offline CLI, pytest suite, gold corpus evaluator, release audit; no cloud API required | `scripts/evaluate_gold_corpus.py`, `REPRODUCIBILITY.md` |

**Also in v0.1.0 (supporting, not behavioural semantics extensions):**

- Tiered benchmark catalog and index (`benchmark/catalog.json`, `benchmark/index.json`)
- Gold comparison metrics scaffold (GSS, transition overlap, BTA / oracle pass rate)
- Ollama pilot campaign runner and C1 config template (generation decoupled from evaluation)
- CI validation and public-release audit (`scripts/audit_public_release.py`)

**Corpus size at v0.1.0:** 3 pilot + 9 core systems (12 total), each with approved gold FSM, requirement spec, and behavioural test suite.

---

## 2. Explicit non-goals for v0.1.0

The following are **out of scope** for release v0.1.0. Their absence is intentional, not an oversight.

| Non-goal | Meaning for v0.1.0 |
|----------|-------------------|
| **Distributed testing** | No multi-tester architecture, no global/local verdict protocol, no ioco-style distributed conformance |
| **Multi-port FSMs** | No port-labelled events; one flat event alphabet per system |
| **Controllability analysis** | No controllable vs uncontrollable event partition; no supervisor synthesis |
| **Observability analysis** | No observability masks, projections, or ambiguous-state reporting |
| **Asynchronous FIFO / non-FIFO channels** | No message queues, reordering, or channel buffers in simulation |
| **Timed implementation relations** | No clocks, deadlines, timeouts, or tioco-style timed conformance |
| **Probabilistic schedulers** | No stochastic transitions or scheduler models |
| **EFSM slicing** | No variable stores, action languages, or slice-based reduction |
| **Semantic mutation testing** | No mutant seeding campaign or mutation score on FSM candidates |

**Related but in-scope differently:** Requirement **perturbation** (NL paraphrase / omission / polarity) is planned for a later campaign milestone (`docs/implementation_roadmap.md`, M5)—that is **text robustness**, not semantic FSM mutation.

---

## 3. Planned extension tracks

Future work is organised as **extension tracks** that build on v0.1.0 without redefining its core metrics. Tracks may ship as minor releases (`v0.2.x`) or major releases (`v1.x`) depending on schema impact.

| Track | Objective | Builds on v0.1.0 |
|-------|-----------|------------------|
| **Distinguishability-aware evaluation** | Compute or ingest W-sets, UIO sequences, or ADS diagnostics; relate structural LLM FSM quality to state-identification difficulty | Deterministic simulator + gold FSM graph |
| **Oracle-generation evaluation** | Measure LLM- or tool-generated test suites against gold oracles (precision/recall of tests, not just FSM pass rate) | Existing test-suite schema and runner |
| **Mutation-based robustness evaluation** | Seed semantic mutants (wrong target, missing rejection, spurious transition); report fault detection of oracle battery | Behavioural test suites + gold FSMs |
| **Asynchronous trace evaluation** | Extend simulator with quiescence, timeouts, and reordering; async trace oracles | Single-port event alphabet (interim) → multi-port |
| **Distributed FSM evaluation** | Port-labelled models; controllable/uncontrollable partitions; distributed conformance checks | Multi-port schema + evaluation protocol extension |
| **Timed behavioural evaluation** | Clocks, deadlines, tock-style traces; timed pass/fail oracles | Guard DSL + synchronous core |

**Milestone alignment:** See `docs/implementation_roadmap.md` (M1–M9). Extension tracks above map primarily to post-M9 or parallel research branches unless explicitly promoted into a release milestone.

---

## 4. Rationale

v0.1.0 **intentionally** limits semantics to **single-port, deterministic, synchronous** behavioural agreement because:

1. **Reproducibility.** Local replicators can obtain identical simulation verdicts on fixed JSON artefacts without modelling schedulers, network delay, or probabilistic choice.

2. **Construct validity before complexity.** The EMSE study targets a documented phenomenon: LLM outputs often pass **structural** gates yet fail **behavioural** oracles. Measuring that gap requires a trusted gold corpus and executable tests—not full distributed or timed conformance theory.

3. **Incremental schema stability.** Multi-port, timed, and asynchronous semantics require new JSON schemas, simulator semantics, and oracle languages. Shipping them prematurely would blur v0.1.0 baselines and complicate comparison with [FSM-Bench-20](https://doi.org/10.5281/zenodo.20516296).

4. **Clear reviewer boundaries.** Non-goals in §2 prevent over-claiming conformance with mature branches of model-based testing (distributed, timed, mutation-based). v0.1.0 **uses** classical MBT ideas (gold models, finite test suites, trace agreement) as an **evaluation foundation**, not as new testing theory.

5. **Extension ordering.** Distinguishability and oracle-generation tracks extend **diagnostics** on the existing corpus. Mutation and async/distributed/timed tracks extend **semantics**; they depend on a frozen v0.1.0 baseline for before/after comparison.

**Summary:** v0.1.0 is the **minimal reproducible layer** for behavioural correctness of LLM-generated software FSMs. Extension tracks in §3 add theory-aligned capabilities without retroactively changing what v0.1.0 claims.

---

## Document control

| Version | Date | Change |
|---------|------|--------|
| v1.0 | 2026-06-03 | Initial public research scope and extension roadmap |

---

*End of research_scope_v1.0*
