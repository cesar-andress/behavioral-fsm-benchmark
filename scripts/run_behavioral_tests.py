#!/usr/bin/env python3
"""Run behavioral test suite against an FSM."""

from __future__ import annotations

import argparse
import sys

from framework.behavioral.test_runner import run_test_suite
from framework.io.load_json import load_json
from framework.io.write_json import write_json
from framework.types import fsm_from_dict, parse_test_suite
from framework.validators.schema_validator import validate_against_schema


def main() -> int:
    parser = argparse.ArgumentParser(description="Execute behavioral test suite on an FSM.")
    parser.add_argument("fsm_path", help="Path to candidate FSM JSON")
    parser.add_argument("suite_path", help="Path to behavioral test suite JSON")
    parser.add_argument("--json-out", help="Optional JSON report path")
    args = parser.parse_args()

    fsm_payload = load_json(args.fsm_path)
    suite_payload = load_json(args.suite_path)
    ok_fsm, fsm_errors = validate_against_schema(fsm_payload, "generated_fsm.schema.json")
    ok_suite, suite_errors = validate_against_schema(suite_payload, "testsuite.schema.json")
    if not ok_fsm or not ok_suite:
        for err in fsm_errors + suite_errors:
            print(f"ERROR: {err}")
        return 1

    fsm = fsm_from_dict(fsm_payload)
    suite = parse_test_suite(suite_payload)
    results = run_test_suite(fsm, suite)

    print(f"behavioral_pass_rate={results.behavioral_pass_rate:.3f}")
    print(f"final_state_agreement={results.final_state_agreement_rate:.3f}")
    print(f"trace_agreement={results.trace_agreement_rate:.3f}")
    print(f"rejected_event_agreement={results.rejected_event_agreement_rate:.3f}")
    print(f"tests_passed={results.tests_passed}/{results.tests_total}")
    for item in results.test_results:
        status = "PASS" if item.passed else "FAIL"
        print(f"{status} {item.test_id}: {item.message}")

    if args.json_out:
        write_json(
            args.json_out,
            {
                "behavioral_pass_rate": results.behavioral_pass_rate,
                "oracle_pass_rate": results.oracle_pass_rate,
                "final_state_agreement_rate": results.final_state_agreement_rate,
                "trace_agreement_rate": results.trace_agreement_rate,
                "rejected_event_agreement_rate": results.rejected_event_agreement_rate,
                "tests_passed": results.tests_passed,
                "tests_total": results.tests_total,
                "test_results": [
                    {
                        "test_id": t.test_id,
                        "passed": t.passed,
                        "evaluable": t.evaluable,
                        "message": t.message,
                    }
                    for t in results.test_results
                ],
            },
        )

    return 0 if results.tests_passed == results.tests_total else 1


if __name__ == "__main__":
    sys.exit(main())
