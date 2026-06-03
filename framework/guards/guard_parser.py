"""Guard expression parsing and evaluation."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

COMPARE_RE = re.compile(
    r"^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*(>=|<=|==|!=|>|<)\s*(-?\d+(?:\.\d+)?|'[^']*'|\"[^\"]*\"|[a-zA-Z_][a-zA-Z0-9_]*)\s*$"
)


@dataclass(frozen=True)
class GuardAtom:
    kind: str
    text: str


def parse_guard(guard: str) -> GuardAtom:
    text = (guard or "").strip()
    if not text:
        return GuardAtom("true", "")
    lowered = text.lower()
    if lowered == "true":
        return GuardAtom("true", text)
    if lowered == "false":
        return GuardAtom("false", text)
    if lowered.startswith("not "):
        return GuardAtom("not", text[4:].strip())
    if " and " in lowered:
        parts = [part.strip() for part in text.split(" and ") if part.strip()]
        return GuardAtom("and", " and ".join(parts))
    if COMPARE_RE.match(text):
        return GuardAtom("compare", text)
    if re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", text):
        return GuardAtom("var", text)
    return GuardAtom("unknown", text)


def _coerce_literal(raw: str, context: dict[str, Any]) -> Any:
    token = raw.strip()
    quoted = (
        (token.startswith("'") and token.endswith("'"))
        or (token.startswith('"') and token.endswith('"'))
    )
    if quoted:
        return token[1:-1]
    if re.match(r"^-?\d+(?:\.\d+)?$", token):
        return float(token) if "." in token else int(token)
    if token.lower() in {"true", "false"}:
        return token.lower() == "true"
    return context.get(token, token)


def eval_guard(guard: str, context: dict[str, Any] | None = None) -> bool | None:
    ctx = context or {}
    atom = parse_guard(guard)

    if atom.kind == "true":
        return True
    if atom.kind == "false":
        return False
    if atom.kind == "unknown":
        return None
    if atom.kind == "var":
        value = ctx.get(atom.text)
        if value is None:
            return None
        return bool(value)
    if atom.kind == "not":
        inner = eval_guard(atom.text, ctx)
        return None if inner is None else not inner
    if atom.kind == "and":
        parts = atom.text.split(" and ")
        results = [eval_guard(part, ctx) for part in parts]
        if any(r is None for r in results):
            return None
        return all(results)
    if atom.kind == "compare":
        match = COMPARE_RE.match(atom.text)
        if not match:
            return None
        var, op, literal = match.groups()
        if var not in ctx:
            return None
        left = ctx[var]
        right = _coerce_literal(literal, ctx)
        try:
            if op == ">=":
                return left >= right
            if op == "<=":
                return left <= right
            if op == ">":
                return left > right
            if op == "<":
                return left < right
            if op == "==":
                return left == right
            if op == "!=":
                return left != right
        except TypeError:
            return None
    return None
