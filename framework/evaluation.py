"""End-to-end evaluation for a single system case."""

from __future__ import annotations

from typing import Any

from framework.behavioral.test_runner import run_test_suite
from framework.coverage.path_coverage import compute_path_coverage
from framework.coverage.requirement_coverage import compute_requirement_coverage
from framework.coverage.transition_coverage import compute_transition_coverage
from framework.equivalence.behavioral_equivalence import compare_fsms
from framework.types import (
    FSM,
    CoverageResults,
    EvaluationResult,
    RequirementSpec,
    TestSuite,
)
from framework.validators.fsm_validator import validate_determinism, validate_fsm
from framework.validators.schema_validator import validate_against_schema
from framework.validators.traceability_validator import validate_traceability


def evaluate_case(
    candidate: FSM,
    *,
    candidate_label: str = "candidate",
    spec: RequirementSpec | None = None,
    gold: FSM | None = None,
    test_suite: TestSuite | None = None,
    schema_valid: bool | None = None,
) -> EvaluationResult:
    if schema_valid is None:

        payload = {
            "states": candidate.states,
            "initial_state": candidate.initial_state,
            "events": candidate.events,
            "transitions": [
                {
                    "source": t.source,
                    "event": t.event,
                    "target": t.target,
                    "guard": t.guard,
                    "action": t.action,
                    "requirement": t.requirement,
                }
                for t in candidate.transitions
            ],
            "forbidden_behaviours": [
                {"trace": fb.trace, "reason": fb.reason, "requirement": fb.requirement}
                for fb in candidate.forbidden_behaviours
            ],
        }
        schema_valid, _ = validate_against_schema(payload, "generated_fsm.schema.json")

    structural = validate_fsm(candidate, schema_valid=schema_valid)
    determinism = validate_determinism(candidate)

    traceability = (
        validate_traceability(candidate, spec)
        if spec is not None
        else validate_traceability(candidate, RequirementSpec("", "", []))
    )

    behavioral = run_test_suite(candidate, test_suite) if test_suite is not None else None
    equivalence = compare_fsms(gold, candidate, spec=spec, test_suite=test_suite) if gold else None

    coverage: CoverageResults | None = None
    if spec is not None or gold is not None:
        req = compute_requirement_coverage(candidate, spec) if spec else None
        trans = compute_transition_coverage(candidate, gold) if gold else None
        path = compute_path_coverage(candidate, test_suite) if test_suite else 0.0
        coverage = CoverageResults(
            requirement_coverage=req.coverage if req else 0.0,
            transition_coverage_exact=trans.exact if trans else 0.0,
            transition_coverage_relaxed=trans.relaxed if trans else 0.0,
            path_coverage=path,
            covered_requirements=req.covered if req else [],
            missing_requirements=req.missing if req else [],
        )

    return EvaluationResult(
        system_name=candidate.system_name or (spec.system_name if spec else candidate_label),
        candidate_label=candidate_label,
        structural=structural,
        determinism=determinism,
        traceability=traceability,
        behavioral=behavioral,
        equivalence=equivalence,
        coverage=coverage,
    )


def evaluation_to_export(result: EvaluationResult) -> dict[str, Any]:
    return result.to_dict()
