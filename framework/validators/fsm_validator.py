"""Structural and determinism validation for FSMs."""

from __future__ import annotations

from collections import Counter, deque

from framework.guards.guard_overlap import find_guard_aware_conflicts
from framework.types import FSM, DeterminismValidation, StructuralValidation, Transition


def validate_referential(fsm: FSM) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if not fsm.states:
        errors.append("states must not be empty")
    if fsm.initial_state not in fsm.state_set:
        errors.append(f"initial_state '{fsm.initial_state}' is not in states")

    for idx, transition in enumerate(fsm.transitions):
        prefix = f"transitions[{idx}]"
        if transition.source not in fsm.state_set:
            errors.append(f"{prefix}.source '{transition.source}' is not a declared state")
        if transition.target not in fsm.state_set:
            errors.append(f"{prefix}.target '{transition.target}' is not a declared state")
        if transition.event and transition.event not in fsm.event_set:
            warnings.append(f"{prefix}.event '{transition.event}' is not listed in events")

    return len(errors) == 0, errors, warnings


def unreachable_states(fsm: FSM) -> list[str]:
    if not fsm.states or fsm.initial_state not in fsm.state_set:
        return list(fsm.states)

    graph: dict[str, set[str]] = {state: set() for state in fsm.states}
    for transition in fsm.transitions:
        if transition.source in graph and transition.target in graph:
            graph[transition.source].add(transition.target)

    seen = {fsm.initial_state}
    queue = deque([fsm.initial_state])
    while queue:
        current = queue.popleft()
        for nxt in graph[current]:
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    return [state for state in fsm.states if state not in seen]


def count_duplicate_pairs(transitions: list[Transition]) -> int:
    pairs = Counter((t.source, t.event) for t in transitions)
    return sum(1 for count in pairs.values() if count > 1)


def count_duplicate_triples(transitions: list[Transition]) -> int:
    triples = Counter((t.source, t.event, t.guard.strip()) for t in transitions)
    return sum(1 for count in triples.values() if count > 1)


def validate_determinism(fsm: FSM) -> DeterminismValidation:
    duplicate_pairs = count_duplicate_pairs(fsm.transitions)
    duplicate_triples = count_duplicate_triples(fsm.transitions)
    guard_conflicts = find_guard_aware_conflicts(fsm.transitions)
    unreachable = unreachable_states(fsm)

    return DeterminismValidation(
        strict_deterministic=duplicate_pairs == 0,
        guard_aware_deterministic=len(guard_conflicts) == 0,
        duplicate_source_event_pairs=duplicate_pairs,
        duplicate_source_event_guard_triples=duplicate_triples,
        guard_aware_conflicts=guard_conflicts,
        unreachable_states=unreachable,
    )


def validate_fsm(fsm: FSM, *, schema_valid: bool = True) -> StructuralValidation:
    referential_ok, errors, warnings = validate_referential(fsm)
    if not schema_valid:
        errors = ["schema validation failed"] + errors
    return StructuralValidation(
        schema_valid=schema_valid,
        referential_valid=referential_ok,
        errors=errors,
        warnings=warnings,
    )
