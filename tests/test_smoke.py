"""Smoke tests for repository bootstrap."""

import framework
from framework.types import CandidateFSM, Transition


def test_package_version() -> None:
    assert framework.__version__


def test_candidate_fsm_placeholder() -> None:
    fsm = CandidateFSM(
        system_name="example",
        states=["s0", "s1"],
        initial_state="s0",
        transitions=[Transition("s0", "e", "s1")],
    )
    assert fsm.initial_state == "s0"
    assert len(fsm.transitions) == 1
