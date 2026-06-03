"""Tests for framework.evaluation."""

from __future__ import annotations

from framework.evaluation import evaluate_case, evaluation_to_export


def test_evaluate_case_full_pipeline(
    generated_fsm,
    requirement_spec,
    gold_fsm,
    test_suite,
) -> None:
    result = evaluate_case(
        generated_fsm,
        spec=requirement_spec,
        gold=gold_fsm,
        test_suite=test_suite,
        schema_valid=True,
    )
    assert result.structural.referential_valid
    assert result.determinism.strict_deterministic
    assert result.behavioral is not None
    assert result.equivalence is not None
    assert result.coverage is not None
    assert result.coverage.path_coverage == 2 / 3
    assert result.behavioral.behavioral_pass_rate == 2 / 3


def test_evaluate_case_schema_validation_runs(generated_fsm) -> None:
    result = evaluate_case(generated_fsm)
    assert result.structural.schema_valid


def test_evaluation_to_export_serializable(
    generated_fsm,
    requirement_spec,
    gold_fsm,
    test_suite,
) -> None:
    result = evaluate_case(
        generated_fsm,
        spec=requirement_spec,
        gold=gold_fsm,
        test_suite=test_suite,
        schema_valid=True,
    )
    exported = evaluation_to_export(result)
    assert exported["system_name"]
    assert "structural" in exported
    assert "determinism" in exported
