#!/usr/bin/env python3
"""Compare generated FSM against gold reference FSM."""

from __future__ import annotations

import argparse
import sys

from framework.coverage.requirement_coverage import compute_requirement_coverage
from framework.coverage.transition_coverage import compute_transition_coverage
from framework.equivalence.behavioral_equivalence import compare_fsms
from framework.io.load_json import load_json
from framework.io.write_json import write_json
from framework.types import fsm_from_dict, parse_test_suite, requirement_spec_from_dict


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare candidate FSM to gold reference FSM.")
    parser.add_argument("gold_path", help="Path to gold/reference FSM JSON")
    parser.add_argument("candidate_path", help="Path to generated FSM JSON")
    parser.add_argument("--requirements", help="Optional requirement spec JSON")
    parser.add_argument("--test-suite", help="Optional behavioral test suite JSON")
    parser.add_argument("--json-out", help="Optional JSON report path")
    args = parser.parse_args()

    gold = fsm_from_dict(load_json(args.gold_path))
    candidate = fsm_from_dict(load_json(args.candidate_path))
    spec = requirement_spec_from_dict(load_json(args.requirements)) if args.requirements else None
    suite = parse_test_suite(load_json(args.test_suite)) if args.test_suite else None

    equivalence = compare_fsms(gold, candidate, spec=spec, test_suite=suite)
    report: dict = {
        "exact_transition_match_rate": equivalence.exact_transition_match_rate,
        "state_overlap_rate": equivalence.state_overlap_rate,
        "event_overlap_rate": equivalence.event_overlap_rate,
        "behavioral_agreement_rate": equivalence.behavioral_agreement_rate,
        "missing_transitions": equivalence.missing_transitions,
        "extra_transitions": equivalence.extra_transitions,
        "unsupported_transitions": equivalence.unsupported_transitions,
    }

    if spec is not None:
        req = compute_requirement_coverage(candidate, spec)
        report["requirement_coverage"] = req.coverage
        report["missing_requirements"] = req.missing
    trans = compute_transition_coverage(candidate, gold)
    report["transition_coverage_exact"] = trans.exact
    report["transition_coverage_relaxed"] = trans.relaxed

    print(f"exact_transition_match_rate={equivalence.exact_transition_match_rate:.3f}")
    print(f"state_overlap_rate={equivalence.state_overlap_rate:.3f}")
    print(f"behavioral_agreement_rate={equivalence.behavioral_agreement_rate:.3f}")
    print(f"missing_transitions={len(equivalence.missing_transitions)}")
    print(f"extra_transitions={len(equivalence.extra_transitions)}")

    if args.json_out:
        write_json(args.json_out, report)

    return 0


if __name__ == "__main__":
    sys.exit(main())
