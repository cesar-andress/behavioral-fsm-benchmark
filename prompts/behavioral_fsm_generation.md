# Behavioral FSM generation prompt

Generate **exactly one** finite state machine (FSM) for the system below.

## Output contract

- Return **JSON only**. No markdown fences, no explanations, no comments.
- The JSON MUST validate against the project FSM schema: `{{SCHEMA_REFERENCE}}`.
- Include these top-level fields: `system_name`, `domain`, `states`, `initial_state`, `events`, `transitions`.
- Optionally include `forbidden_behaviours` when requirements describe rejected traces.
- Use an empty string for unused `guard`, `action`, or optional fields.

## System identifier

`{{SYSTEM_ID}}`

## System name

{{SYSTEM_NAME}}

## Domain

{{DOMAIN}}

## Requirements

{{REQUIREMENTS}}

## Modeling rules

1. Generate **exactly one** FSM that implements the requirements above.
2. Use **only** state names listed in `states` and event names listed in `events`.
3. Cite requirement IDs (for example `R2`, `R3`) in each transition `requirement` field.
4. Do **not** create duplicate `(source, event)` transitions unless guards are mutually exclusive.
5. Include guards **only** when required for behavioral branching; otherwise use an empty guard string.
6. Do **not** invent behavior not supported by the requirements.
7. Ensure `initial_state` is one of the declared states.
8. Every transition `source` and `target` MUST be declared in `states`.

Return the FSM JSON object now.
