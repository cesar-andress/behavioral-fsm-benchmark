"""Oracle test evaluation helpers."""

from __future__ import annotations

from dataclasses import dataclass

from framework.behavioral.simulator import simulate
from framework.types import FSM, SimulationResult, TestCase


@dataclass(frozen=True)
class OracleOutcome:
    passed: bool
    evaluable: bool
    message: str
    simulation: SimulationResult
    final_state_matched: bool | None = None
    trace_matched: bool | None = None
    rejection_matched: bool | None = None


def evaluate_oracle(fsm: FSM, test: TestCase) -> OracleOutcome:
    simulation = simulate(fsm, test.events, guard_context=test.guard_context)
    is_negative = test.kind == "negative" or test.expected_final_state is None

    if simulation.error and "nondeterministic" in simulation.error:
        return OracleOutcome(
            passed=False,
            evaluable=True,
            message=simulation.error,
            simulation=simulation,
            rejection_matched=False if is_negative else None,
        )

    if not simulation.success:
        rejection_ok = is_negative
        passed = rejection_ok
        message = (
            "expected rejection occurred"
            if rejection_ok
            else (simulation.error or "simulation failed")
        )
        return OracleOutcome(
            passed=passed,
            evaluable=True,
            message=message,
            simulation=simulation,
            rejection_matched=rejection_ok if is_negative else None,
            final_state_matched=False if test.expected_final_state is not None else None,
        )

    if is_negative:
        return OracleOutcome(
            passed=False,
            evaluable=True,
            message="expected rejection but simulation succeeded",
            simulation=simulation,
            rejection_matched=False,
        )

    final_state_matched: bool | None = None
    if test.expected_final_state is not None:
        final_state_matched = simulation.final_state == test.expected_final_state
        if not final_state_matched:
            return OracleOutcome(
                passed=False,
                evaluable=True,
                message=(
                    f"expected final state '{test.expected_final_state}', "
                    f"got '{simulation.final_state}'"
                ),
                simulation=simulation,
                final_state_matched=False,
            )

    trace_matched: bool | None = None
    if test.expected_trace is not None:
        actual = [step.target for step in simulation.trace]
        trace_matched = actual == test.expected_trace
        if not trace_matched:
            return OracleOutcome(
                passed=False,
                evaluable=True,
                message=f"expected trace {test.expected_trace}, got {actual}",
                simulation=simulation,
                final_state_matched=final_state_matched,
                trace_matched=False,
            )

    return OracleOutcome(
        passed=True,
        evaluable=True,
        message="passed",
        simulation=simulation,
        final_state_matched=final_state_matched if test.expected_final_state is not None else None,
        trace_matched=trace_matched if test.expected_trace is not None else None,
        rejection_matched=None,
    )


def evaluate_oracle_legacy(fsm: FSM, test: TestCase) -> tuple[bool, bool, str, SimulationResult]:
    outcome = evaluate_oracle(fsm, test)
    return outcome.passed, outcome.evaluable, outcome.message, outcome.simulation
