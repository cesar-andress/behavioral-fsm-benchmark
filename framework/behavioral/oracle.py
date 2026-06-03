"""Oracle test evaluation helpers."""

from __future__ import annotations

from framework.behavioral.simulator import simulate
from framework.types import FSM, SimulationResult, TestCase


def evaluate_oracle(fsm: FSM, test: TestCase) -> tuple[bool, bool, str, SimulationResult]:
    simulation = simulate(fsm, test.events, guard_context=test.guard_context)
    if simulation.error and "nondeterministic" in simulation.error:
        return False, True, simulation.error, simulation

    if not simulation.success:
        if test.expected_final_state is None:
            return True, True, "expected rejection occurred", simulation
        return False, True, simulation.error or "simulation failed", simulation

    expected = test.expected_final_state
    if expected is not None and simulation.final_state != expected:
        return (
            False,
            True,
            f"expected final state '{test.expected_final_state}', got '{simulation.final_state}'",
            simulation,
        )

    if test.expected_trace is not None:
        actual = [step.target for step in simulation.trace]
        if actual != test.expected_trace:
            return False, True, f"expected trace {test.expected_trace}, got {actual}", simulation

    return True, True, "passed", simulation
