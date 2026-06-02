"""Shared typed structures for FSM artifacts (skeleton)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Transition:
    """Single FSM transition (minimal placeholder)."""

    source: str
    event: str
    target: str
    guard: str | None = None
    action: str | None = None


@dataclass
class CandidateFSM:
    """LLM-generated FSM candidate (FSMOutput-compatible placeholder)."""

    system_name: str
    states: list[str] = field(default_factory=list)
    initial_state: str = ""
    events: list[str] = field(default_factory=list)
    transitions: list[Transition] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
