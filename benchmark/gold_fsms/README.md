# Reference FSMs — behavioral-fsm-benchmark

Human-approved gold (reference) finite state machines for behavioral evaluation.

| Status | Meaning |
|--------|---------|
| `draft` | Under authoring |
| `review` | Pending reviewer sign-off |
| `approved` | Eligible for gold comparison and L4 scoring |
| `placeholder` | Bootstrap stub only |
| `deprecated` | Superseded |

**Schema:** `../schemas/reference_fsm.schema.json`  
**Spec:** `../../docs/benchmark_specification.md` §3

## Pilot systems (approved)

| System ID | File |
|-----------|------|
| `vending_machine` | `vending_machine.json` |
| `login_system` | `login_system.json` |
| `atm` | `atm.json` |

## Core systems (approved)

| System ID | File |
|-----------|------|
| `parking_gate` | `parking_gate.json` |
| `access_control` | `access_control.json` |
| `bike_rental` | `bike_rental.json` |
| `warehouse_inventory` | `warehouse_inventory.json` |
| `smart_thermostat` | `smart_thermostat.json` |
| `elevator` | `elevator.json` |
| `hotel_booking` | `hotel_booking.json` |
| `train_ticket_booking` | `train_ticket_booking.json` |
| `package_locker` | `package_locker.json` |

Each approved gold FSM MUST pass its paired test suite at 100% (reference self-test).
