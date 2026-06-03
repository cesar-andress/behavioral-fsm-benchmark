"""Tests for framework.types."""

from __future__ import annotations

from framework.types import (
    FSM,
    Requirement,
    Transition,
    extract_requirement_refs,
    fsm_from_dict,
    parse_test_suite,
    requirement_spec_from_dict,
    transition_key,
)


def test_extract_requirement_refs() -> None:
    assert extract_requirement_refs("Implements R2 and R3") == {"R2", "R3"}
    assert extract_requirement_refs("") == set()


def test_requirement_spec_from_dict_mixed_items() -> None:
    spec = requirement_spec_from_dict(
        {
            "system_name": "demo",
            "domain": "test",
            "requirements": [
                "R1 idle behaviour",
                {"requirement_id": "R2", "text": "coin insert"},
            ],
        }
    )
    assert spec.system_name == "demo"
    assert spec.requirement_ids == {"R1", "R2"}


def test_fsm_from_dict_and_properties() -> None:
    fsm = fsm_from_dict(
        {
            "states": ["A", "B"],
            "initial_state": "A",
            "events": ["go"],
            "transitions": [
                {
                    "source": "A",
                    "event": "go",
                    "target": "B",
                    "guard": "",
                    "requirement": "R1",
                }
            ],
            "forbidden_behaviours": [{"trace": ["go"], "reason": "bad", "requirement": "R9"}],
        }
    )
    assert fsm.state_set == {"A", "B"}
    assert fsm.event_set == {"go"}
    assert len(fsm.forbidden_behaviours) == 1


def test_parse_test_suite() -> None:
    suite = parse_test_suite(
        {
            "system_name": "demo",
            "tests": [
                {
                    "test_id": "t1",
                    "kind": "oracle",
                    "events": ["e"],
                    "expected_final_state": "B",
                    "guard_context": {"x": 1},
                }
            ],
            "guard_contexts": {"default": {"x": 0}},
        }
    )
    assert suite.tests[0].test_id == "t1"
    assert suite.guard_contexts["default"]["x"] == 0


def test_transition_key_with_and_without_guard() -> None:
    transition = Transition("A", "e", "B", guard="balance >= 10")
    assert transition_key(transition, include_guard=True) == ("A", "e", "B", "balance >= 10")
    assert transition_key(transition, include_guard=False) == ("A", "e", "B")


def test_fsm_dataclass_defaults() -> None:
    fsm = FSM(
        states=["s0"],
        initial_state="s0",
        events=["e"],
        transitions=[Transition("s0", "e", "s0")],
    )
    assert fsm.metadata == {}
    assert fsm.forbidden_behaviours == []


def test_requirement_frozen() -> None:
    req = Requirement("R1", "text")
    assert req.requirement_id == "R1"
