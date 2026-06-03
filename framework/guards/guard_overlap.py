"""Guard overlap analysis for guard-aware determinism."""

from __future__ import annotations

from framework.guards.guard_parser import parse_guard
from framework.types import Transition


def guards_mutually_exclusive(g1: str, g2: str) -> bool | None:
    a = parse_guard(g1)
    b = parse_guard(g2)

    if a.kind == "false" or b.kind == "false":
        return True
    if a.text.strip() == b.text.strip():
        return False
    if a.kind == "true" and b.kind == "true":
        return False

    from framework.guards.guard_parser import COMPARE_RE

    ma = COMPARE_RE.match(a.text) if a.kind == "compare" else None
    mb = COMPARE_RE.match(b.text) if b.kind == "compare" else None
    if ma and mb and ma.group(1) == mb.group(1):
        op_a, lit_a = ma.group(2), ma.group(3)
        op_b, lit_b = mb.group(2), mb.group(3)
        try:
            va = float(lit_a) if "." in lit_a else int(lit_a)
            vb = float(lit_b) if "." in lit_b else int(lit_b)
        except ValueError:
            return None
        if op_a == ">=" and op_b == "<" and va >= vb:
            return True
        if op_a == ">" and op_b == "<=" and va >= vb:
            return True
        if op_a == "<=" and op_b == ">=" and va <= vb:
            return True
        if op_a == "<" and op_b == ">=" and va <= vb:
            return True

    return None


def find_guard_aware_conflicts(transitions: list[Transition]) -> list[str]:
    groups: dict[tuple[str, str], list[Transition]] = {}
    for transition in transitions:
        key = (transition.source, transition.event)
        groups.setdefault(key, []).append(transition)

    conflicts: list[str] = []
    for (source, event), group in sorted(groups.items()):
        if len(group) < 2:
            continue
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                t1, t2 = group[i], group[j]
                if t1.target == t2.target:
                    continue
                exclusive = guards_mutually_exclusive(t1.guard, t2.guard)
                if exclusive is False or exclusive is None:
                    conflicts.append(
                        f"{source}/{event}: guards '{t1.guard}' -> {t1.target} "
                        f"and '{t2.guard}' -> {t2.target} may overlap"
                    )
    return conflicts
