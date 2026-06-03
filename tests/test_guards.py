"""Tests for framework.guards."""

from __future__ import annotations

from framework.guards.guard_overlap import find_guard_aware_conflicts, guards_mutually_exclusive
from framework.guards.guard_parser import eval_guard, parse_guard


def test_parse_guard_kinds() -> None:
    assert parse_guard("").kind == "true"
    assert parse_guard("false").kind == "false"
    assert parse_guard("balance >= 10").kind == "compare"
    assert parse_guard("ready and balance >= 10").kind == "and"
    assert parse_guard("not ready").kind == "not"
    assert parse_guard("ready").kind == "var"
    assert parse_guard("weird expr").kind == "unknown"


def test_eval_guard_numeric_and_boolean() -> None:
    assert eval_guard("balance >= 10", {"balance": 15}) is True
    assert eval_guard("balance >= 10", {"balance": 5}) is False
    assert eval_guard("ready", {"ready": True}) is True
    assert eval_guard("ready", {}) is None


def test_eval_guard_and_not() -> None:
    ctx = {"ready": True, "balance": 20}
    assert eval_guard("ready and balance >= 10", ctx) is True
    assert eval_guard("not ready", {"ready": False}) is True


def test_guard_mutually_exclusive_numeric() -> None:
    assert guards_mutually_exclusive("balance >= 10", "balance < 5") is True
    assert guards_mutually_exclusive("", "") is False
    assert guards_mutually_exclusive("balance >= 10", "balance >= 10") is False


def test_guard_aware_conflicts_detected(nondeterministic_fsm) -> None:
    conflicts = find_guard_aware_conflicts(nondeterministic_fsm.transitions)
    assert conflicts


def test_guard_aware_no_conflicts_for_resolved_fsm(guard_resolved_fsm) -> None:
    conflicts = find_guard_aware_conflicts(guard_resolved_fsm.transitions)
    assert not conflicts
