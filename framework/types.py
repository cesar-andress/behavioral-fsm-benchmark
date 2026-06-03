"""Shared typed structures for FSM artifacts."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any

REQUIREMENT_REF = re.compile(r"R\d+")


@dataclass(frozen=True)
class Requirement:
    requirement_id: str
    text: str


@dataclass(frozen=True)
class RequirementSpec:
    system_name: str
    domain: str
    requirements: list[Requirement]

    @property
    def requirement_ids(self) -> set[str]:
        return {r.requirement_id for r in self.requirements}


@dataclass(frozen=True)
class Transition:
    source: str
    event: str
    target: str
    guard: str = ""
    action: str = ""
    requirement: str = ""


@dataclass(frozen=True)
class ForbiddenBehaviour:
    trace: list[str] = field(default_factory=list)
    reason: str = ""
    requirement: str = ""


@dataclass
class FSM:
    states: list[str]
    initial_state: str
    events: list[str]
    transitions: list[Transition]
    forbidden_behaviours: list[ForbiddenBehaviour] = field(default_factory=list)
    system_name: str = ""
    domain: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def state_set(self) -> set[str]:
        return set(self.states)

    @property
    def event_set(self) -> set[str]:
        return set(self.events)


@dataclass(frozen=True)
class TestCase:
    test_id: str
    kind: str
    events: list[str]
    expected_final_state: str | None = None
    expected_trace: list[str] | None = None
    guard_context: dict[str, Any] = field(default_factory=dict)
    description: str = ""


@dataclass
class TestSuite:
    system_name: str
    tests: list[TestCase]
    guard_contexts: dict[str, dict[str, Any]] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class StructuralValidation:
    schema_valid: bool
    referential_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class DeterminismValidation:
    strict_deterministic: bool
    guard_aware_deterministic: bool
    duplicate_source_event_pairs: int = 0
    duplicate_source_event_guard_triples: int = 0
    guard_aware_conflicts: list[str] = field(default_factory=list)
    unreachable_states: list[str] = field(default_factory=list)


@dataclass
class SimulationStep:
    event: str
    source: str
    target: str
    guard: str


@dataclass
class SimulationResult:
    success: bool
    trace: list[SimulationStep] = field(default_factory=list)
    state_trace: list[str] = field(default_factory=list)
    final_state: str = ""
    error: str | None = None


@dataclass
class TestCaseResult:
    test_id: str
    passed: bool
    evaluable: bool
    message: str = ""
    simulation: SimulationResult | None = None
    kind: str = ""
    final_state_matched: bool | None = None
    trace_matched: bool | None = None
    rejection_matched: bool | None = None


@dataclass
class BehavioralResults:
    oracle_pass_rate: float
    tests_passed: int
    tests_total: int
    test_results: list[TestCaseResult] = field(default_factory=list)
    behavioral_pass_rate: float = 0.0
    final_state_agreement_rate: float = 0.0
    trace_agreement_rate: float = 0.0
    rejected_event_agreement_rate: float = 0.0
    final_state_tests: int = 0
    final_state_matches: int = 0
    trace_tests: int = 0
    trace_matches: int = 0
    negative_tests: int = 0
    rejection_matches: int = 0


@dataclass
class EquivalenceResults:
    exact_transition_match_rate: float
    state_overlap_rate: float
    event_overlap_rate: float
    missing_transitions: list[str] = field(default_factory=list)
    extra_transitions: list[str] = field(default_factory=list)
    unsupported_transitions: int = 0
    behavioral_agreement_rate: float = 0.0


@dataclass
class CoverageResults:
    requirement_coverage: float
    transition_coverage_exact: float
    transition_coverage_relaxed: float
    path_coverage: float
    covered_requirements: list[str] = field(default_factory=list)
    missing_requirements: list[str] = field(default_factory=list)


@dataclass
class TraceabilityResults:
    covered_requirements: list[str] = field(default_factory=list)
    missing_requirements: list[str] = field(default_factory=list)
    unsupported_transitions: int = 0
    empty_requirement_transitions: int = 0


@dataclass
class EvaluationResult:
    system_name: str
    candidate_label: str
    structural: StructuralValidation
    determinism: DeterminismValidation
    traceability: TraceabilityResults
    behavioral: BehavioralResults | None = None
    equivalence: EquivalenceResults | None = None
    coverage: CoverageResults | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def extract_requirement_refs(text: str) -> set[str]:
    return set(REQUIREMENT_REF.findall(text or ""))


def requirement_spec_from_dict(data: dict[str, Any]) -> RequirementSpec:
    reqs: list[Requirement] = []
    for idx, item in enumerate(data.get("requirements", []), start=1):
        if isinstance(item, str):
            match = REQUIREMENT_REF.match(item.strip())
            req_id = match.group(0) if match else f"R{idx}"
            reqs.append(Requirement(req_id, item))
        elif isinstance(item, dict):
            reqs.append(
                Requirement(
                    str(item.get("requirement_id", item.get("id", f"R{idx}"))),
                    str(item.get("text", "")),
                )
            )
    return RequirementSpec(
        system_name=str(data.get("system_name", "")),
        domain=str(data.get("domain", "")),
        requirements=reqs,
    )


def fsm_from_dict(data: dict[str, Any]) -> FSM:
    transitions = [
        Transition(
            source=str(t["source"]),
            event=str(t["event"]),
            target=str(t["target"]),
            guard=str(t.get("guard", "")),
            action=str(t.get("action", "")),
            requirement=str(t.get("requirement", "")),
        )
        for t in data.get("transitions", [])
    ]
    forbidden = [
        ForbiddenBehaviour(
            trace=list(fb.get("trace", [])),
            reason=str(fb.get("reason", "")),
            requirement=str(fb.get("requirement", "")),
        )
        for fb in data.get("forbidden_behaviours", [])
    ]
    return FSM(
        states=[str(s) for s in data.get("states", [])],
        initial_state=str(data.get("initial_state", "")),
        events=[str(e) for e in data.get("events", [])],
        transitions=transitions,
        forbidden_behaviours=forbidden,
        system_name=str(data.get("system_name", "")),
        domain=str(data.get("domain", "")),
        metadata=dict(data.get("metadata", {})),
    )


def parse_test_suite(data: dict[str, Any]) -> TestSuite:
    tests = [
        TestCase(
            test_id=str(t["test_id"]),
            kind=str(t.get("kind", "oracle")),
            events=[str(e) for e in t.get("events", [])],
            expected_final_state=t.get("expected_final_state"),
            expected_trace=t.get("expected_trace"),
            guard_context=dict(t.get("guard_context", {})),
            description=str(t.get("description", "")),
        )
        for t in data.get("tests", [])
    ]
    return TestSuite(
        system_name=str(data.get("system_name", "")),
        tests=tests,
        guard_contexts={k: dict(v) for k, v in data.get("guard_contexts", {}).items()},
        metadata=dict(data.get("metadata", {})),
    )


def transition_key(
    transition: Transition,
    *,
    include_guard: bool = True,
) -> tuple[str, ...]:
    base = (transition.source.strip(), transition.event.strip(), transition.target.strip())
    if include_guard:
        guard = transition.guard.strip() or "_"
        return (*base, guard)
    return base
