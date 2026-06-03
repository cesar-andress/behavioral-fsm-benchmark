"""Transition tuple matching."""

from __future__ import annotations

from framework.types import FSM, transition_key


def transition_set(fsm: FSM, *, include_guard: bool = True) -> set[tuple[str, ...]]:
    return {transition_key(t, include_guard=include_guard) for t in fsm.transitions}


def format_transition_key(key: tuple[str, ...]) -> str:
    return " -> ".join(key)
