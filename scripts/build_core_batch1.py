#!/usr/bin/env python3
"""Build and validate core benchmark batch 1 artifacts (offline helper)."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from framework.benchmark.validate import run_gold_self_test, validate_gold_fsm, validate_test_suite  # noqa: E402
from framework.coverage.requirement_coverage import compute_requirement_coverage  # noqa: E402
from framework.io.write_json import write_json  # noqa: E402
from framework.types import fsm_from_dict, parse_test_suite, requirement_spec_from_dict  # noqa: E402
from framework.validators.fsm_validator import validate_determinism  # noqa: E402
from framework.validators.traceability_validator import validate_traceability  # noqa: E402

CORE_SYSTEMS = [
    "parking_gate",
    "access_control",
    "bike_rental",
    "warehouse_inventory",
    "smart_thermostat",
    "elevator",
    "hotel_booking",
    "train_ticket_booking",
    "package_locker",
]


def _spec(system_id: str, domain: str, requirements: list[str]) -> dict:
    return {
        "system_name": system_id.replace("_", " ").title(),
        "domain": domain,
        "requirements": requirements,
    }


def _gold(
    system_id: str,
    domain: str,
    states: list[str],
    initial: str,
    events: list[str],
    transitions: list[dict],
    forbidden: list[dict] | None = None,
) -> dict:
    normalized = []
    for tr in transitions:
        item = dict(tr)
        item.setdefault("guard", "")
        normalized.append(item)
    return {
        "system_name": system_id.replace("_", " ").title(),
        "domain": domain,
        "metadata": {
            "status": "approved",
            "approved_by": "benchmark-author",
            "approved_at": "2026-06-03",
            "source": f"benchmark/datasets/systems/{system_id}.json",
            "notes": f"Core gold FSM for {system_id}",
        },
        "states": states,
        "initial_state": initial,
        "events": events,
        "transitions": normalized,
        "forbidden_behaviours": forbidden or [],
    }


def _suite(system_id: str, tests: list[dict]) -> dict:
    return {
        "system_name": system_id.replace("_", " ").title(),
        "metadata": {"status": "approved", "tier": "core", "version": "1.0"},
        "tests": tests,
    }


def _t(
    test_id: str,
    kind: str,
    events: list[str],
    *,
    expected_final_state: str | None = None,
    expected_trace: list[str] | None = None,
    guard_context: dict | None = None,
    description: str = "",
) -> dict:
    item: dict = {
        "test_id": test_id,
        "kind": kind,
        "events": events,
        "description": description,
    }
    if expected_final_state is not None or kind == "negative":
        item["expected_final_state"] = expected_final_state
    if expected_trace is not None:
        item["expected_trace"] = expected_trace
    if guard_context is not None:
        item["guard_context"] = guard_context
    return item


SYSTEMS: dict[str, dict] = {}


def register(system_id: str, spec: dict, gold: dict, suite: dict) -> None:
    SYSTEMS[system_id] = {"spec": spec, "gold": gold, "suite": suite}


register(
    "parking_gate",
    _spec(
        "parking_gate",
        "parking automation",
        [
            "R1: The gate starts in Closed.",
            "R2: Vehicle detection in Closed opens the gate (Opening).",
            "R3: Completion signal in Opening moves to Open.",
            "R4: Close command in Open starts closing (Closing).",
            "R5: Gate closed signal in Closing returns to Closed.",
            "R6: Vehicle detection is ignored while Open.",
            "R7: Close command is rejected in Closed.",
            "R8: A full open-close cycle ends in Closed.",
        ],
    ),
    _gold(
        "parking_gate",
        "parking automation",
        ["Closed", "Opening", "Open", "Closing"],
        "Closed",
        ["detect_vehicle", "gate_opened", "close_command", "gate_closed"],
        [
            {"source": "Closed", "event": "detect_vehicle", "target": "Opening", "requirement": "R1, R2"},
            {"source": "Opening", "event": "gate_opened", "target": "Open", "requirement": "R3"},
            {"source": "Open", "event": "close_command", "target": "Closing", "requirement": "R4, R6"},
            {"source": "Closing", "event": "gate_closed", "target": "Closed", "requirement": "R5, R7, R8"},
        ],
        [
            {
                "trace": ["detect_vehicle", "gate_opened", "detect_vehicle"],
                "reason": "Detection ignored in Open per R6",
                "requirement": "R6",
            },
            {
                "trace": ["close_command"],
                "reason": "Close rejected in Closed per R7",
                "requirement": "R7",
            },
        ],
    ),
    _suite(
        "parking_gate",
        [
            _t("full_open_close_cycle", "oracle", ["detect_vehicle", "gate_opened", "close_command", "gate_closed"], expected_final_state="Closed", expected_trace=["Opening", "Open", "Closing", "Closed"], description="R8 full cycle"),
            _t("detect_to_opening", "oracle", ["detect_vehicle"], expected_final_state="Opening", description="R2 vehicle detection"),
            _t("opening_to_open", "oracle", ["detect_vehicle", "gate_opened"], expected_final_state="Open", expected_trace=["Opening", "Open"], description="R3 gate opened"),
            _t("open_to_closing", "oracle", ["detect_vehicle", "gate_opened", "close_command"], expected_final_state="Closing", expected_trace=["Opening", "Open", "Closing"], description="R4 close command"),
            _t("closing_to_closed", "oracle", ["detect_vehicle", "gate_opened", "close_command", "gate_closed"], expected_final_state="Closed", description="R5 gate closed"),
            _t("remain_closed_initial", "oracle", [], expected_final_state="Closed", description="R1 initial Closed"),
            _t("open_before_close", "oracle", ["detect_vehicle", "gate_opened"], expected_final_state="Open", description="Open reachable before close"),
            _t("cycle_returns_closed", "oracle", ["detect_vehicle", "gate_opened", "close_command", "gate_closed"], expected_final_state="Closed", description="R8 cycle ends Closed"),
            _t("reject_second_detect_in_opening", "negative", ["detect_vehicle", "detect_vehicle"], expected_final_state=None, description="Second detect rejected in Opening"),
            _t("reject_detect_while_open", "negative", ["detect_vehicle", "gate_opened", "detect_vehicle"], expected_final_state=None, description="R6 forbidden detect in Open"),
            _t("reject_close_while_closed", "negative", ["close_command"], expected_final_state=None, description="R7 forbidden close in Closed"),
            _t("path_two_step_open", "path", ["detect_vehicle", "gate_opened"], expected_final_state="Open", expected_trace=["Opening", "Open"], description="Path to Open"),
            _t("path_three_step_closing", "path", ["detect_vehicle", "gate_opened", "close_command"], expected_final_state="Closing", description="Path to Closing"),
            _t("path_four_step_closed", "path", ["detect_vehicle", "gate_opened", "close_command", "gate_closed"], expected_final_state="Closed", description="Path full cycle"),
            _t("path_single_detect", "path", ["detect_vehicle"], expected_final_state="Opening", description="Path detect only"),
            _t("path_open_then_close", "path", ["detect_vehicle", "gate_opened", "close_command"], expected_final_state="Closing", expected_trace=["Opening", "Open", "Closing"], description="Path through Open to Closing"),
            _t("path_idle_no_events", "path", [], expected_final_state="Closed", description="Path initial state"),
        ],
    ),
)

register(
    "access_control",
    _spec(
        "access_control",
        "physical access control",
        [
            "R1: Door starts Locked.",
            "R2: Valid badge scan unlocks the door.",
            "R3: Lock command from Unlocked returns to Locked.",
            "R4: Invalid badge scan is rejected in Locked.",
            "R5: Lock command is rejected while already Locked.",
            "R6: Badge scan is rejected while Unlocked.",
            "R7: Unlock then lock restores Locked.",
            "R8: Only Unlocked state permits entry.",
        ],
    ),
    _gold(
        "access_control",
        "physical access control",
        ["Locked", "Unlocked"],
        "Locked",
        ["badge_scan", "lock_command"],
        [
            {"source": "Locked", "event": "badge_scan", "guard": "badge_valid", "target": "Unlocked", "requirement": "R1, R2, R4, R8"},
            {"source": "Unlocked", "event": "lock_command", "target": "Locked", "requirement": "R3, R5, R6, R7"},
        ],
        [
            {"trace": ["badge_scan"], "reason": "Invalid badge rejected per R4", "requirement": "R4"},
            {"trace": ["lock_command"], "reason": "Lock rejected when Locked per R5", "requirement": "R5"},
        ],
    ),
    _suite(
        "access_control",
        [
            _t("unlock_with_valid_badge", "oracle", ["badge_scan"], expected_final_state="Unlocked", guard_context={"badge_valid": True}, description="R2 valid badge"),
            _t("lock_from_unlocked", "oracle", ["badge_scan", "lock_command"], expected_final_state="Locked", guard_context={"badge_valid": True}, expected_trace=["Unlocked", "Locked"], description="R3 lock command"),
            _t("unlock_lock_cycle", "oracle", ["badge_scan", "lock_command"], expected_final_state="Locked", guard_context={"badge_valid": True}, description="R7 cycle"),
            _t("initial_locked", "oracle", [], expected_final_state="Locked", description="R1 initial Locked"),
            _t("unlocked_entry_state", "oracle", ["badge_scan"], expected_final_state="Unlocked", guard_context={"badge_valid": True}, description="R8 unlocked entry state"),
            _t("lock_restores_secure", "oracle", ["badge_scan", "lock_command"], expected_final_state="Locked", guard_context={"badge_valid": True}, description="R7 lock restores Locked"),
            _t("valid_badge_from_locked", "oracle", ["badge_scan"], expected_final_state="Unlocked", guard_context={"badge_valid": True}, expected_trace=["Unlocked"], description="R2 unlock transition"),
            _t("reject_invalid_badge", "negative", ["badge_scan"], expected_final_state=None, guard_context={"badge_valid": False}, description="R4 invalid badge fails"),
            _t("lock_without_unlock", "oracle", [], expected_final_state="Locked", description="Locked without events"),
            _t("second_badge_while_unlocked", "negative", ["badge_scan", "badge_scan"], expected_final_state=None, guard_context={"badge_valid": True}, description="R6 badge rejected when Unlocked"),
            _t("reject_lock_when_locked", "negative", ["lock_command"], expected_final_state=None, description="R5 forbidden lock"),
            _t("reject_badge_when_unlocked", "negative", ["badge_scan", "badge_scan"], expected_final_state=None, guard_context={"badge_valid": True}, description="R6 duplicate badge scan rejected"),
            _t("path_unlock", "path", ["badge_scan"], expected_final_state="Unlocked", guard_context={"badge_valid": True}, description="Path unlock"),
            _t("path_lock_after_unlock", "path", ["badge_scan", "lock_command"], expected_final_state="Locked", guard_context={"badge_valid": True}, expected_trace=["Unlocked", "Locked"], description="Path lock"),
            _t("path_initial", "path", [], expected_final_state="Locked", description="Path initial"),
            _t("path_invalid_scan", "path", ["badge_scan"], expected_final_state=None, guard_context={"badge_valid": False}, description="Path invalid scan rejection"),
            _t("path_rejected_lock", "path", ["lock_command"], expected_final_state=None, description="Path rejected lock"),
            _t("path_full_cycle", "path", ["badge_scan", "lock_command"], expected_final_state="Locked", guard_context={"badge_valid": True}, description="Path full cycle"),
        ],
    ),
)

register(
    "bike_rental",
    _spec(
        "bike_rental",
        "micromobility rental",
        [
            "R1: Dock starts Available.",
            "R2: Reserve from Available moves to Reserved.",
            "R3: Confirm pickup from Reserved moves to Rented.",
            "R4: Return from Rented restores Available.",
            "R5: Report fault from Rented moves to Maintenance.",
            "R6: Repair complete from Maintenance restores Available.",
            "R7: Reserve is rejected while Rented.",
            "R8: Return is rejected while Available.",
        ],
    ),
    _gold(
        "bike_rental",
        "micromobility rental",
        ["Available", "Reserved", "Rented", "Maintenance"],
        "Available",
        ["reserve", "confirm_pickup", "return_bike", "report_fault", "repair_complete"],
        [
            {"source": "Available", "event": "reserve", "target": "Reserved", "requirement": "R1, R2, R8"},
            {"source": "Reserved", "event": "confirm_pickup", "target": "Rented", "requirement": "R3, R7"},
            {"source": "Rented", "event": "return_bike", "target": "Available", "requirement": "R4"},
            {"source": "Rented", "event": "report_fault", "target": "Maintenance", "requirement": "R5"},
            {"source": "Maintenance", "event": "repair_complete", "target": "Available", "requirement": "R6"},
        ],
        [
            {"trace": ["reserve", "confirm_pickup", "reserve"], "reason": "Reserve rejected while Rented per R7", "requirement": "R7"},
            {"trace": ["return_bike"], "reason": "Return rejected while Available per R8", "requirement": "R8"},
        ],
    ),
    _suite(
        "bike_rental",
        [
            _t("happy_rental_cycle", "oracle", ["reserve", "confirm_pickup", "return_bike"], expected_final_state="Available", expected_trace=["Reserved", "Rented", "Available"], description="Full rental cycle"),
            _t("reserve_only", "oracle", ["reserve"], expected_final_state="Reserved", description="R2 reserve"),
            _t("pickup_from_reserved", "oracle", ["reserve", "confirm_pickup"], expected_final_state="Rented", expected_trace=["Reserved", "Rented"], description="R3 pickup"),
            _t("initial_available", "oracle", [], expected_final_state="Available", description="R1 initial Available"),
            _t("maintenance_cycle", "oracle", ["reserve", "confirm_pickup", "report_fault", "repair_complete"], expected_final_state="Available", description="R5/R6 maintenance path"),
            _t("to_maintenance", "oracle", ["reserve", "confirm_pickup", "report_fault"], expected_final_state="Maintenance", description="R5 report fault"),
            _t("repair_restores", "oracle", ["reserve", "confirm_pickup", "report_fault", "repair_complete"], expected_final_state="Available", description="R6 repair complete"),
            _t("return_from_rented", "oracle", ["reserve", "confirm_pickup", "return_bike"], expected_final_state="Available", description="R4 return bike"),
            _t("reject_return_available", "negative", ["return_bike"], expected_final_state=None, description="R8 return rejected"),
            _t("reject_reserve_rented", "negative", ["reserve", "confirm_pickup", "reserve"], expected_final_state=None, description="R7 reserve rejected"),
            _t("path_to_reserved", "path", ["reserve"], expected_final_state="Reserved", description="Path reserve"),
            _t("path_to_rented", "path", ["reserve", "confirm_pickup"], expected_final_state="Rented", expected_trace=["Reserved", "Rented"], description="Path rented"),
            _t("path_return", "path", ["reserve", "confirm_pickup", "return_bike"], expected_final_state="Available", description="Path return"),
            _t("path_maintenance", "path", ["reserve", "confirm_pickup", "report_fault"], expected_final_state="Maintenance", description="Path maintenance"),
            _t("path_repair", "path", ["reserve", "confirm_pickup", "report_fault", "repair_complete"], expected_final_state="Available", description="Path repair"),
            _t("path_initial", "path", [], expected_final_state="Available", description="Path initial"),
            _t("path_reserve_pickup_return", "path", ["reserve", "confirm_pickup", "return_bike"], expected_final_state="Available", expected_trace=["Reserved", "Rented", "Available"], description="Path full rental"),
        ],
    ),
)

register(
    "warehouse_inventory",
    _spec(
        "warehouse_inventory",
        "warehouse logistics",
        [
            "R1: Inventory starts Idle.",
            "R2: Receive stock from Idle moves to Stocked.",
            "R3: Allocate from Stocked moves to Allocated.",
            "R4: Dispatch from Allocated moves to Dispatched.",
            "R5: Cancel allocation from Allocated returns to Stocked.",
            "R6: Restock from Dispatched returns to Stocked.",
            "R7: Allocate is rejected from Idle.",
            "R8: Dispatch is rejected from Stocked.",
        ],
    ),
    _gold(
        "warehouse_inventory",
        "warehouse logistics",
        ["Idle", "Stocked", "Allocated", "Dispatched"],
        "Idle",
        ["receive_stock", "allocate", "dispatch", "cancel_allocation", "restock"],
        [
            {"source": "Idle", "event": "receive_stock", "target": "Stocked", "requirement": "R1, R2"},
            {"source": "Stocked", "event": "allocate", "target": "Allocated", "requirement": "R3, R7"},
            {"source": "Allocated", "event": "dispatch", "target": "Dispatched", "requirement": "R4, R8"},
            {"source": "Allocated", "event": "cancel_allocation", "target": "Stocked", "requirement": "R5"},
            {"source": "Dispatched", "event": "restock", "target": "Stocked", "requirement": "R6"},
        ],
        [
            {"trace": ["allocate"], "reason": "Allocate rejected from Idle per R7", "requirement": "R7"},
            {"trace": ["receive_stock", "dispatch"], "reason": "Dispatch rejected from Stocked per R8", "requirement": "R8"},
        ],
    ),
    _suite(
        "warehouse_inventory",
        [
            _t("fulfillment_cycle", "oracle", ["receive_stock", "allocate", "dispatch", "restock"], expected_final_state="Stocked", expected_trace=["Stocked", "Allocated", "Dispatched", "Stocked"], description="Full fulfillment cycle"),
            _t("receive_stock", "oracle", ["receive_stock"], expected_final_state="Stocked", description="R2 receive stock"),
            _t("allocate_item", "oracle", ["receive_stock", "allocate"], expected_final_state="Allocated", expected_trace=["Stocked", "Allocated"], description="R3 allocate"),
            _t("initial_idle", "oracle", [], expected_final_state="Idle", description="R1 initial Idle"),
            _t("cancel_allocation", "oracle", ["receive_stock", "allocate", "cancel_allocation"], expected_final_state="Stocked", description="R5 cancel allocation"),
            _t("dispatch_order", "oracle", ["receive_stock", "allocate", "dispatch"], expected_final_state="Dispatched", description="R4 dispatch"),
            _t("restock_after_dispatch", "oracle", ["receive_stock", "allocate", "dispatch", "restock"], expected_final_state="Stocked", description="R6 restock"),
            _t("stocked_after_receive", "oracle", ["receive_stock"], expected_final_state="Stocked", description="Stocked state after receive"),
            _t("reject_allocate_idle", "negative", ["allocate"], expected_final_state=None, description="R7 allocate rejected"),
            _t("reject_dispatch_stocked", "negative", ["receive_stock", "dispatch"], expected_final_state=None, description="R8 dispatch rejected"),
            _t("path_to_stocked", "path", ["receive_stock"], expected_final_state="Stocked", description="Path stocked"),
            _t("path_to_allocated", "path", ["receive_stock", "allocate"], expected_final_state="Allocated", description="Path allocated"),
            _t("path_to_dispatched", "path", ["receive_stock", "allocate", "dispatch"], expected_final_state="Dispatched", description="Path dispatched"),
            _t("path_cancel", "path", ["receive_stock", "allocate", "cancel_allocation"], expected_final_state="Stocked", description="Path cancel"),
            _t("path_initial", "path", [], expected_final_state="Idle", description="Path initial"),
            _t("path_restock", "path", ["receive_stock", "allocate", "dispatch", "restock"], expected_final_state="Stocked", description="Path restock"),
        ],
    ),
)

register(
    "smart_thermostat",
    _spec(
        "smart_thermostat",
        "building climate control",
        [
            "R1: Thermostat starts Off.",
            "R2: Power on heat from Off moves to Heating.",
            "R3: Power on cool from Off moves to Cooling.",
            "R4: Power off from Heating returns to Off.",
            "R5: Power off from Cooling returns to Off.",
            "R6: Target reached from Heating returns to Off.",
            "R7: Target reached from Cooling returns to Off.",
            "R8: Heat command is rejected while Heating.",
        ],
    ),
    _gold(
        "smart_thermostat",
        "building climate control",
        ["Off", "Heating", "Cooling"],
        "Off",
        ["power_on_heat", "power_on_cool", "power_off", "target_reached"],
        [
            {"source": "Off", "event": "power_on_heat", "target": "Heating", "requirement": "R1, R2"},
            {"source": "Off", "event": "power_on_cool", "target": "Cooling", "requirement": "R3"},
            {"source": "Heating", "event": "power_off", "target": "Off", "requirement": "R4, R8"},
            {"source": "Heating", "event": "target_reached", "target": "Off", "requirement": "R6"},
            {"source": "Cooling", "event": "power_off", "target": "Off", "requirement": "R5"},
            {"source": "Cooling", "event": "target_reached", "target": "Off", "requirement": "R7"},
        ],
        [
            {"trace": ["power_on_heat", "power_on_heat"], "reason": "Heat rejected while Heating per R8", "requirement": "R8"},
            {"trace": ["power_on_cool", "power_off", "power_on_cool"], "reason": "Cool rejected while Cooling", "requirement": "R8"},
        ],
    ),
    _suite(
        "smart_thermostat",
        [
            _t("heat_cycle_off", "oracle", ["power_on_heat", "power_off"], expected_final_state="Off", expected_trace=["Heating", "Off"], description="R2/R4 heat cycle"),
            _t("cool_cycle_off", "oracle", ["power_on_cool", "power_off"], expected_final_state="Off", expected_trace=["Cooling", "Off"], description="R3/R5 cool cycle"),
            _t("heat_target_reached", "oracle", ["power_on_heat", "target_reached"], expected_final_state="Off", expected_trace=["Heating", "Off"], description="R6 target reached heating"),
            _t("cool_target_reached", "oracle", ["power_on_cool", "target_reached"], expected_final_state="Off", expected_trace=["Cooling", "Off"], description="R7 target reached cooling"),
            _t("initial_off", "oracle", [], expected_final_state="Off", description="R1 initial Off"),
            _t("start_heating", "oracle", ["power_on_heat"], expected_final_state="Heating", description="R2 start heating"),
            _t("start_cooling", "oracle", ["power_on_cool"], expected_final_state="Cooling", description="R3 start cooling"),
            _t("off_after_cool_off", "oracle", ["power_on_cool", "power_off"], expected_final_state="Off", description="Cooling stops on power off"),
            _t("reject_heat_while_heating", "negative", ["power_on_heat", "power_on_heat"], expected_final_state=None, description="R8 heat rejected"),
            _t("reject_cool_while_cooling", "negative", ["power_on_cool", "power_on_cool"], expected_final_state=None, description="Cool command rejected while Cooling"),
            _t("path_heat", "path", ["power_on_heat"], expected_final_state="Heating", description="Path heating"),
            _t("path_cool", "path", ["power_on_cool"], expected_final_state="Cooling", description="Path cooling"),
            _t("path_heat_off", "path", ["power_on_heat", "power_off"], expected_final_state="Off", description="Path heat off"),
            _t("path_cool_off", "path", ["power_on_cool", "power_off"], expected_final_state="Off", description="Path cool off"),
            _t("path_heat_target", "path", ["power_on_heat", "target_reached"], expected_final_state="Off", description="Path heat target"),
            _t("path_initial", "path", [], expected_final_state="Off", description="Path initial"),
        ],
    ),
)

register(
    "elevator",
    _spec(
        "elevator",
        "vertical transport",
        [
            "R1: Elevator starts Idle.",
            "R2: Call from Idle moves to Moving.",
            "R3: Arrival from Moving opens doors (DoorOpen).",
            "R4: Close door command from DoorOpen moves to Closing.",
            "R5: Door sealed signal from Closing returns to Idle.",
            "R6: Call is rejected while Moving.",
            "R7: Close door is rejected while Idle.",
            "R8: A complete ride cycle ends in Idle.",
        ],
    ),
    _gold(
        "elevator",
        "vertical transport",
        ["Idle", "Moving", "DoorOpen", "Closing"],
        "Idle",
        ["call_elevator", "arrived", "close_door", "door_sealed"],
        [
            {"source": "Idle", "event": "call_elevator", "target": "Moving", "requirement": "R1, R2"},
            {"source": "Moving", "event": "arrived", "target": "DoorOpen", "requirement": "R3, R6"},
            {"source": "DoorOpen", "event": "close_door", "target": "Closing", "requirement": "R4"},
            {"source": "Closing", "event": "door_sealed", "target": "Idle", "requirement": "R5, R7, R8"},
        ],
        [
            {"trace": ["call_elevator", "call_elevator"], "reason": "Call rejected while Moving per R6", "requirement": "R6"},
            {"trace": ["close_door"], "reason": "Close rejected while Idle per R7", "requirement": "R7"},
        ],
    ),
    _suite(
        "elevator",
        [
            _t("full_ride_cycle", "oracle", ["call_elevator", "arrived", "close_door", "door_sealed"], expected_final_state="Idle", expected_trace=["Moving", "DoorOpen", "Closing", "Idle"], description="R8 full cycle"),
            _t("call_to_moving", "oracle", ["call_elevator"], expected_final_state="Moving", description="R2 call"),
            _t("arrive_open_doors", "oracle", ["call_elevator", "arrived"], expected_final_state="DoorOpen", expected_trace=["Moving", "DoorOpen"], description="R3 arrived"),
            _t("initial_idle", "oracle", [], expected_final_state="Idle", description="R1 initial Idle"),
            _t("close_from_open", "oracle", ["call_elevator", "arrived", "close_door"], expected_final_state="Closing", expected_trace=["Moving", "DoorOpen", "Closing"], description="R4 close door"),
            _t("sealed_to_idle", "oracle", ["call_elevator", "arrived", "close_door", "door_sealed"], expected_final_state="Idle", description="R5 door sealed"),
            _t("door_open_reached", "oracle", ["call_elevator", "arrived"], expected_final_state="DoorOpen", description="DoorOpen reachable"),
            _t("moving_after_call", "oracle", ["call_elevator"], expected_final_state="Moving", description="Moving after elevator call"),
            _t("reject_call_moving", "negative", ["call_elevator", "call_elevator"], expected_final_state=None, description="R6 call rejected"),
            _t("reject_close_idle", "negative", ["close_door"], expected_final_state=None, description="R7 close rejected"),
            _t("path_moving", "path", ["call_elevator"], expected_final_state="Moving", description="Path moving"),
            _t("path_door_open", "path", ["call_elevator", "arrived"], expected_final_state="DoorOpen", description="Path door open"),
            _t("path_closing", "path", ["call_elevator", "arrived", "close_door"], expected_final_state="Closing", description="Path closing"),
            _t("path_full_cycle", "path", ["call_elevator", "arrived", "close_door", "door_sealed"], expected_final_state="Idle", description="Path full cycle"),
            _t("path_initial", "path", [], expected_final_state="Idle", description="Path initial"),
            _t("path_arrive_only", "path", ["call_elevator", "arrived"], expected_final_state="DoorOpen", expected_trace=["Moving", "DoorOpen"], description="Path arrive"),
        ],
    ),
)

register(
    "hotel_booking",
    _spec(
        "hotel_booking",
        "hospitality reservation",
        [
            "R1: Session starts with NoBooking.",
            "R2: Search from NoBooking shows SearchResults.",
            "R3: Select room from SearchResults holds a booking.",
            "R4: Confirm payment from BookingHeld confirms reservation.",
            "R5: Cancel from BookingHeld returns to NoBooking.",
            "R6: Cancel from Confirmed returns to NoBooking.",
            "R7: Confirm payment is rejected from SearchResults.",
            "R8: Select room is rejected from NoBooking without search.",
        ],
    ),
    _gold(
        "hotel_booking",
        "hospitality reservation",
        ["NoBooking", "SearchResults", "BookingHeld", "Confirmed"],
        "NoBooking",
        ["search", "select_room", "confirm_payment", "cancel"],
        [
            {"source": "NoBooking", "event": "search", "target": "SearchResults", "requirement": "R1, R2, R8"},
            {"source": "SearchResults", "event": "select_room", "target": "BookingHeld", "requirement": "R3, R7"},
            {"source": "BookingHeld", "event": "confirm_payment", "target": "Confirmed", "requirement": "R4"},
            {"source": "BookingHeld", "event": "cancel", "target": "NoBooking", "requirement": "R5"},
            {"source": "Confirmed", "event": "cancel", "target": "NoBooking", "requirement": "R6"},
        ],
        [
            {"trace": ["search", "confirm_payment"], "reason": "Confirm rejected from SearchResults per R7", "requirement": "R7"},
            {"trace": ["select_room"], "reason": "Select rejected without search per R8", "requirement": "R8"},
        ],
    ),
    _suite(
        "hotel_booking",
        [
            _t("confirmed_booking", "oracle", ["search", "select_room", "confirm_payment"], expected_final_state="Confirmed", expected_trace=["SearchResults", "BookingHeld", "Confirmed"], description="Full booking"),
            _t("search_only", "oracle", ["search"], expected_final_state="SearchResults", description="R2 search"),
            _t("hold_booking", "oracle", ["search", "select_room"], expected_final_state="BookingHeld", expected_trace=["SearchResults", "BookingHeld"], description="R3 select room"),
            _t("initial_no_booking", "oracle", [], expected_final_state="NoBooking", description="R1 initial"),
            _t("cancel_from_held", "oracle", ["search", "select_room", "cancel"], expected_final_state="NoBooking", description="R5 cancel held"),
            _t("cancel_from_confirmed", "oracle", ["search", "select_room", "confirm_payment", "cancel"], expected_final_state="NoBooking", description="R6 cancel confirmed"),
            _t("confirm_payment_step", "oracle", ["search", "select_room", "confirm_payment"], expected_final_state="Confirmed", description="R4 confirm payment"),
            _t("search_results_state", "oracle", ["search"], expected_final_state="SearchResults", description="SearchResults reachable"),
            _t("reject_confirm_search", "negative", ["search", "confirm_payment"], expected_final_state=None, description="R7 confirm rejected"),
            _t("reject_select_no_search", "negative", ["select_room"], expected_final_state=None, description="R8 select rejected"),
            _t("path_search", "path", ["search"], expected_final_state="SearchResults", description="Path search"),
            _t("path_held", "path", ["search", "select_room"], expected_final_state="BookingHeld", description="Path held"),
            _t("path_confirmed", "path", ["search", "select_room", "confirm_payment"], expected_final_state="Confirmed", description="Path confirmed"),
            _t("path_cancel_held", "path", ["search", "select_room", "cancel"], expected_final_state="NoBooking", description="Path cancel held"),
            _t("path_initial", "path", [], expected_final_state="NoBooking", description="Path initial"),
            _t("path_cancel_confirmed", "path", ["search", "select_room", "confirm_payment", "cancel"], expected_final_state="NoBooking", description="Path cancel confirmed"),
        ],
    ),
)

register(
    "train_ticket_booking",
    _spec(
        "train_ticket_booking",
        "rail ticketing",
        [
            "R1: Flow starts at Start.",
            "R2: Select route from Start moves to RouteSelected.",
            "R3: Choose seat from RouteSelected moves to SeatHeld.",
            "R4: Pay from SeatHeld issues ticket.",
            "R5: Cancel from SeatHeld returns to Start.",
            "R6: Cancel from TicketIssued returns to Start.",
            "R7: Pay is rejected from RouteSelected.",
            "R8: Choose seat is rejected from Start.",
        ],
    ),
    _gold(
        "train_ticket_booking",
        "rail ticketing",
        ["Start", "RouteSelected", "SeatHeld", "TicketIssued"],
        "Start",
        ["select_route", "choose_seat", "pay", "cancel"],
        [
            {"source": "Start", "event": "select_route", "target": "RouteSelected", "requirement": "R1, R2, R8"},
            {"source": "RouteSelected", "event": "choose_seat", "target": "SeatHeld", "requirement": "R3, R7"},
            {"source": "SeatHeld", "event": "pay", "target": "TicketIssued", "requirement": "R4"},
            {"source": "SeatHeld", "event": "cancel", "target": "Start", "requirement": "R5"},
            {"source": "TicketIssued", "event": "cancel", "target": "Start", "requirement": "R6"},
        ],
        [
            {"trace": ["select_route", "pay"], "reason": "Pay rejected from RouteSelected per R7", "requirement": "R7"},
            {"trace": ["choose_seat"], "reason": "Choose seat rejected from Start per R8", "requirement": "R8"},
        ],
    ),
    _suite(
        "train_ticket_booking",
        [
            _t("ticket_issued", "oracle", ["select_route", "choose_seat", "pay"], expected_final_state="TicketIssued", expected_trace=["RouteSelected", "SeatHeld", "TicketIssued"], description="Full ticket flow"),
            _t("route_selected", "oracle", ["select_route"], expected_final_state="RouteSelected", description="R2 select route"),
            _t("seat_held", "oracle", ["select_route", "choose_seat"], expected_final_state="SeatHeld", expected_trace=["RouteSelected", "SeatHeld"], description="R3 choose seat"),
            _t("initial_start", "oracle", [], expected_final_state="Start", description="R1 initial"),
            _t("cancel_seat_held", "oracle", ["select_route", "choose_seat", "cancel"], expected_final_state="Start", description="R5 cancel held"),
            _t("cancel_issued", "oracle", ["select_route", "choose_seat", "pay", "cancel"], expected_final_state="Start", description="R6 cancel issued"),
            _t("pay_step", "oracle", ["select_route", "choose_seat", "pay"], expected_final_state="TicketIssued", description="R4 pay"),
            _t("route_state_reachable", "oracle", ["select_route"], expected_final_state="RouteSelected", description="RouteSelected reachable"),
            _t("reject_pay_route", "negative", ["select_route", "pay"], expected_final_state=None, description="R7 pay rejected"),
            _t("reject_seat_start", "negative", ["choose_seat"], expected_final_state=None, description="R8 seat rejected"),
            _t("path_route", "path", ["select_route"], expected_final_state="RouteSelected", description="Path route"),
            _t("path_seat", "path", ["select_route", "choose_seat"], expected_final_state="SeatHeld", description="Path seat"),
            _t("path_ticket", "path", ["select_route", "choose_seat", "pay"], expected_final_state="TicketIssued", description="Path ticket"),
            _t("path_cancel_held", "path", ["select_route", "choose_seat", "cancel"], expected_final_state="Start", description="Path cancel held"),
            _t("path_initial", "path", [], expected_final_state="Start", description="Path initial"),
            _t("path_cancel_issued", "path", ["select_route", "choose_seat", "pay", "cancel"], expected_final_state="Start", description="Path cancel issued"),
        ],
    ),
)

register(
    "package_locker",
    _spec(
        "package_locker",
        "parcel pickup locker",
        [
            "R1: Locker starts Empty.",
            "R2: Load package from Empty moves to Loaded.",
            "R3: Send notification from Loaded moves to ReadyForPickup.",
            "R4: Enter valid code from ReadyForPickup completes pickup.",
            "R5: Collect package from Completed returns locker to Empty.",
            "R6: Load is rejected while Loaded.",
            "R7: Notification is rejected from Empty.",
            "R8: Invalid code is rejected in ReadyForPickup.",
        ],
    ),
    _gold(
        "package_locker",
        "parcel pickup locker",
        ["Empty", "Loaded", "ReadyForPickup", "Completed"],
        "Empty",
        ["load_package", "send_notification", "enter_code", "collect_package"],
        [
            {"source": "Empty", "event": "load_package", "target": "Loaded", "requirement": "R1, R2, R7"},
            {"source": "Loaded", "event": "send_notification", "target": "ReadyForPickup", "requirement": "R3, R6"},
            {"source": "ReadyForPickup", "event": "enter_code", "guard": "code_valid", "target": "Completed", "requirement": "R4, R8"},
            {"source": "Completed", "event": "collect_package", "target": "Empty", "requirement": "R5"},
        ],
        [
            {"trace": ["load_package", "load_package"], "reason": "Load rejected while Loaded per R6", "requirement": "R6"},
            {"trace": ["send_notification"], "reason": "Notification rejected from Empty per R7", "requirement": "R7"},
        ],
    ),
    _suite(
        "package_locker",
        [
            _t("full_pickup_cycle", "oracle", ["load_package", "send_notification", "enter_code", "collect_package"], expected_final_state="Empty", expected_trace=["Loaded", "ReadyForPickup", "Completed", "Empty"], guard_context={"code_valid": True}, description="Full locker cycle"),
            _t("load_package", "oracle", ["load_package"], expected_final_state="Loaded", description="R2 load"),
            _t("notify_recipient", "oracle", ["load_package", "send_notification"], expected_final_state="ReadyForPickup", expected_trace=["Loaded", "ReadyForPickup"], description="R3 notify"),
            _t("initial_empty", "oracle", [], expected_final_state="Empty", description="R1 initial"),
            _t("enter_valid_code", "oracle", ["load_package", "send_notification", "enter_code"], expected_final_state="Completed", guard_context={"code_valid": True}, description="R4 valid code"),
            _t("collect_clears", "oracle", ["load_package", "send_notification", "enter_code", "collect_package"], expected_final_state="Empty", guard_context={"code_valid": True}, description="R5 collect"),
            _t("ready_state", "oracle", ["load_package", "send_notification"], expected_final_state="ReadyForPickup", description="ReadyForPickup reachable"),
            _t("loaded_after_package", "oracle", ["load_package"], expected_final_state="Loaded", description="Loaded state after deposit"),
            _t("reject_load_loaded", "negative", ["load_package", "load_package"], expected_final_state=None, description="R6 load rejected"),
            _t("reject_notify_empty", "negative", ["send_notification"], expected_final_state=None, description="R7 notify rejected"),
            _t("reject_invalid_code", "negative", ["load_package", "send_notification", "enter_code"], expected_final_state=None, guard_context={"code_valid": False}, description="R8 invalid code"),
            _t("path_loaded", "path", ["load_package"], expected_final_state="Loaded", description="Path loaded"),
            _t("path_ready", "path", ["load_package", "send_notification"], expected_final_state="ReadyForPickup", description="Path ready"),
            _t("path_completed", "path", ["load_package", "send_notification", "enter_code"], expected_final_state="Completed", guard_context={"code_valid": True}, description="Path completed"),
            _t("path_empty_again", "path", ["load_package", "send_notification", "enter_code", "collect_package"], expected_final_state="Empty", guard_context={"code_valid": True}, description="Path reset"),
            _t("path_initial", "path", [], expected_final_state="Empty", description="Path initial"),
            _t("path_invalid_code", "path", ["load_package", "send_notification", "enter_code"], expected_final_state=None, guard_context={"code_valid": False}, description="Path invalid code rejection"),
        ],
    ),
)


def validate_system(system_id: str) -> list[str]:
    errors: list[str] = []
    bundle = SYSTEMS[system_id]
    ok, schema_errors = validate_gold_fsm(bundle["gold"])
    if not ok:
        errors.extend([f"{system_id} gold schema: {e}" for e in schema_errors])

    ok, suite_errors = validate_test_suite(bundle["suite"])
    if not ok:
        errors.extend([f"{system_id} suite schema: {e}" for e in suite_errors])

    gold = fsm_from_dict(bundle["gold"])
    spec = requirement_spec_from_dict(bundle["spec"])
    det = validate_determinism(gold)
    if not det.strict_deterministic:
        errors.append(f"{system_id}: G3 strict failed ({det.duplicate_source_event_pairs} duplicate pairs)")
    if not det.guard_aware_deterministic:
        errors.append(f"{system_id}: G3a failed: {det.guard_aware_conflicts}")

    trace = validate_traceability(gold, spec)
    if trace.missing_requirements:
        errors.append(f"{system_id}: missing requirement refs on transitions: {trace.missing_requirements}")

    cov = compute_requirement_coverage(gold, spec)
    if cov.missing:
        errors.append(f"{system_id}: requirement coverage missing: {cov.missing}")

    suite = parse_test_suite(bundle["suite"])
    ok, results = run_gold_self_test(gold, suite)
    if not ok:
        for item in results.test_results:
            if not item.passed:
                errors.append(f"{system_id} self-test FAIL {item.test_id}: {item.message}")

    kinds = {t.kind for t in suite.tests}
    counts = {k: sum(1 for t in suite.tests if t.kind == k) for k in kinds}
    if counts.get("oracle", 0) < 8:
        errors.append(f"{system_id}: need >=8 oracle tests, got {counts.get('oracle', 0)}")
    if counts.get("negative", 0) < 2:
        errors.append(f"{system_id}: need >=2 negative tests, got {counts.get('negative', 0)}")
    if counts.get("path", 0) < 6:
        errors.append(f"{system_id}: need >=6 path tests, got {counts.get('path', 0)}")

    return errors


def write_artifacts() -> None:
    for system_id in CORE_SYSTEMS:
        bundle = SYSTEMS[system_id]
        write_json(REPO / f"benchmark/datasets/systems/{system_id}.json", bundle["spec"])
        write_json(REPO / f"benchmark/gold_fsms/{system_id}.json", bundle["gold"])
        write_json(REPO / f"benchmark/test_suites/{system_id}.json", bundle["suite"])


def main() -> int:
    all_errors: list[str] = []
    for system_id in CORE_SYSTEMS:
        all_errors.extend(validate_system(system_id))

    if all_errors:
        print("VALIDATION FAILED:")
        for err in all_errors:
            print(f"  - {err}")
        return 1

    if "--write" in sys.argv:
        write_artifacts()
        print(f"Wrote artifacts for {len(CORE_SYSTEMS)} core systems.")
    else:
        print(f"All {len(CORE_SYSTEMS)} core systems validated OK (dry run). Use --write to emit JSON.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
