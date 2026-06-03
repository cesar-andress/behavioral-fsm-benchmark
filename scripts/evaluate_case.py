#!/usr/bin/env python3
"""Evaluate a full system case (validation, behavioral, equivalence, coverage)."""

from __future__ import annotations

import argparse
import sys

from framework.evaluation import evaluate_case, evaluation_to_export
from framework.io.load_json import load_json
from framework.io.write_json import write_json
from framework.types import fsm_from_dict, parse_test_suite, requirement_spec_from_dict
from framework.validators.schema_validator import validate_against_schema


def main() -> int:
    parser = argparse.ArgumentParser(description="Run full evaluation for one FSM case.")
    parser.add_argument("candidate_path", help="Path to candidate FSM JSON")
    parser.add_argument("--label", default="candidate", help="Candidate label for reports")
    parser.add_argument("--requirements", help="Requirement spec JSON")
    parser.add_argument("--gold", help="Gold/reference FSM JSON")
    parser.add_argument("--test-suite", help="Behavioral test suite JSON")
    parser.add_argument("--json-out", help="Structured evaluation result JSON")
    args = parser.parse_args()

    candidate_payload = load_json(args.candidate_path)
    schema_ok, schema_errors = validate_against_schema(
        candidate_payload, "generated_fsm.schema.json"
    )
    if not schema_ok:
        for err in schema_errors:
            print(f"ERROR: {err}")
        return 1

    candidate = fsm_from_dict(candidate_payload)
    spec = requirement_spec_from_dict(load_json(args.requirements)) if args.requirements else None
    gold = fsm_from_dict(load_json(args.gold)) if args.gold else None
    suite = parse_test_suite(load_json(args.test_suite)) if args.test_suite else None

    result = evaluate_case(
        candidate,
        candidate_label=args.label,
        spec=spec,
        gold=gold,
        test_suite=suite,
        schema_valid=True,
    )
    export = evaluation_to_export(result)

    print(f"system={result.system_name}")
    print(f"schema_valid={result.structural.schema_valid}")
    print(f"strict_deterministic={result.determinism.strict_deterministic}")
    print(f"guard_aware_deterministic={result.determinism.guard_aware_deterministic}")
    if result.behavioral:
        print(f"oracle_pass_rate={result.behavioral.oracle_pass_rate:.3f}")
    if result.equivalence:
        print(f"exact_transition_match_rate={result.equivalence.exact_transition_match_rate:.3f}")
    if result.coverage:
        print(f"requirement_coverage={result.coverage.requirement_coverage:.3f}")

    if args.json_out:
        ok, export_errors = validate_against_schema(export, "evaluation_result.schema.json")
        if not ok:
            print("WARN: export does not fully match evaluation_result schema")
            for err in export_errors:
                print(f"  {err}")
        write_json(args.json_out, export)

    ok = result.structural.referential_valid and result.determinism.strict_deterministic
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
