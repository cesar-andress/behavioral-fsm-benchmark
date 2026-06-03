#!/usr/bin/env python3
"""Validate an FSM JSON file against schema and structural rules."""

from __future__ import annotations

import argparse
import sys

from framework.io.load_json import load_json
from framework.io.write_json import write_json
from framework.types import fsm_from_dict
from framework.validators.fsm_validator import validate_determinism, validate_fsm
from framework.validators.schema_validator import validate_against_schema


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate FSM JSON (schema + structural + determinism).",
    )
    parser.add_argument("fsm_path", help="Path to FSM JSON file")
    parser.add_argument("--schema", default="generated_fsm.schema.json", help="Schema file name")
    parser.add_argument("--json-out", help="Optional path for structured validation report")
    args = parser.parse_args()

    payload = load_json(args.fsm_path)
    schema_ok, schema_errors = validate_against_schema(payload, args.schema)
    fsm = fsm_from_dict(payload)
    structural = validate_fsm(fsm, schema_valid=schema_ok)
    if not schema_ok:
        structural.errors = schema_errors + structural.errors
    determinism = validate_determinism(fsm)

    report = {
        "schema_valid": schema_ok,
        "schema_errors": schema_errors,
        "structural": {
            "schema_valid": structural.schema_valid,
            "referential_valid": structural.referential_valid,
            "errors": structural.errors,
            "warnings": structural.warnings,
        },
        "determinism": {
            "strict_deterministic": determinism.strict_deterministic,
            "guard_aware_deterministic": determinism.guard_aware_deterministic,
            "duplicate_source_event_pairs": determinism.duplicate_source_event_pairs,
            "duplicate_source_event_guard_triples": (
                determinism.duplicate_source_event_guard_triples
            ),
            "guard_aware_conflicts": determinism.guard_aware_conflicts,
            "unreachable_states": determinism.unreachable_states,
        },
    }

    ok = schema_ok and structural.referential_valid
    print(f"schema_valid={schema_ok}")
    print(f"referential_valid={structural.referential_valid}")
    print(f"strict_deterministic={determinism.strict_deterministic}")
    print(f"guard_aware_deterministic={determinism.guard_aware_deterministic}")
    for err in schema_errors + structural.errors:
        print(f"ERROR: {err}")
    for warn in structural.warnings:
        print(f"WARN: {warn}")

    if args.json_out:
        write_json(args.json_out, report)

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
