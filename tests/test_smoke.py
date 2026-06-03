"""Smoke tests for package import."""

import framework
from framework.types import FSM, Transition


def test_package_version() -> None:
    assert framework.__version__


def test_fsm_dataclass() -> None:
    fsm = FSM(
        states=["s0", "s1"],
        initial_state="s0",
        events=["e"],
        transitions=[Transition("s0", "e", "s1")],
    )
    assert fsm.initial_state == "s0"
