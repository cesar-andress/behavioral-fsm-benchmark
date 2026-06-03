"""FSM trace simulation."""

from __future__ import annotations

from framework.guards.guard_parser import eval_guard
from framework.types import FSM, SimulationResult, SimulationStep, Transition


def enabled_transitions(
    fsm: FSM,
    state: str,
    event: str,
    context: dict | None,
) -> list[Transition]:
    matches = [t for t in fsm.transitions if t.source == state and t.event == event]
    enabled: list[Transition] = []
    for transition in matches:
        result = eval_guard(transition.guard, context)
        if result is True:
            enabled.append(transition)
        elif result is None and not transition.guard.strip():
            enabled.append(transition)
    return enabled


def simulate(
    fsm: FSM,
    events: list[str],
    *,
    initial_state: str | None = None,
    guard_context: dict | None = None,
) -> SimulationResult:
    state = initial_state or fsm.initial_state
    if state not in fsm.state_set:
        return SimulationResult(False, error=f"invalid initial state '{state}'")

    trace: list[SimulationStep] = []
    state_trace = [state]
    ctx = dict(guard_context or {})

    for event in events:
        enabled = enabled_transitions(fsm, state, event, ctx)
        if not enabled:
            return SimulationResult(
                False,
                trace=trace,
                state_trace=state_trace,
                final_state=state,
                error=f"no enabled transition for event '{event}' in state '{state}'",
            )
        if len(enabled) > 1:
            targets = {t.target for t in enabled}
            if len(targets) > 1:
                return SimulationResult(
                    False,
                    trace=trace,
                    state_trace=state_trace,
                    final_state=state,
                    error=f"nondeterministic choice for event '{event}' in state '{state}'",
                )
        transition = enabled[0]
        trace.append(
            SimulationStep(
                event=event,
                source=transition.source,
                target=transition.target,
                guard=transition.guard,
            )
        )
        state = transition.target
        state_trace.append(state)

    return SimulationResult(True, trace=trace, state_trace=state_trace, final_state=state)
