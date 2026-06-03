# Behavioral FSM generation prompt

Generate **exactly one** finite state machine (FSM) for the system below.

## Output contract

- Return **JSON only**. No markdown fences, no explanations, no comments.
- The JSON MUST validate against the project FSM schema: `{{SCHEMA_REFERENCE}}`.
- Include these top-level fields: `system_name`, `domain`, `states`, `initial_state`, `events`, `transitions`.
- Optionally include `forbidden_behaviours` when requirements describe rejected traces.

## System identifier

`{{SYSTEM_ID}}`

## System name

{{SYSTEM_NAME}}

## Domain

{{DOMAIN}}

## Requirements

{{REQUIREMENTS}}

## Transition object schema

Every object in the `transitions` array MUST include **exactly** these required fields:

- `source` — source state name (must appear in `states`)
- `event` — event name (must appear in `events`)
- `target` — destination state name (must appear in `states`); **always required**
- `requirement` — requirement ID string citing traceability (for example `"R1"`, `"R2"`)

Optional transition fields (include only when needed; use an empty string when unused):

- `guard` — guard expression string
- `action` — action string

Do **not** add other transition properties. The schema does not define `output`, `description`, or other extra keys on transitions.

### Valid transition example

{
  "source": "Idle",
  "event": "coin_inserted",
  "target": "HasCredit",
  "requirement": "R1"
}

### Invalid field names — do not use

Do not use alternative field names such as `to`, `destination`, `next_state`, `next`, `state`, or `target_state`. Use **`target`** only for the destination state.

Do not rename `requirement` to `requirement_ids`, `requirements`, `req`, or similar. Use the field name **`requirement`** with a single requirement ID string per transition.

## Modeling rules

1. Generate **exactly one** FSM that implements the requirements above.
2. Use **only** state names listed in `states` and event names listed in `events`.
3. Every transition MUST have `source`, `event`, `target`, and `requirement`. Missing `target` is invalid.
4. Do **not** create duplicate `(source, event)` transitions unless guards are mutually exclusive.
5. Include guards **only** when required for behavioral branching; otherwise use an empty guard string.
6. Do **not** invent behavior not supported by the requirements.
7. Ensure `initial_state` is one of the declared states.
8. Every transition `source` and `target` MUST be declared in `states`.

## Final checklist (verify before output)

- [ ] All states referenced by transitions are declared in `states`
- [ ] Every transition has `source`, `event`, `target`, and `requirement`
- [ ] Each `requirement` value refers to an existing requirement ID from the requirements section
- [ ] Output is JSON only
- [ ] No Markdown, prose, or code fences

Return the FSM JSON object now.
