"""JSON Schema validation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import jsonschema

from framework.io.load_json import load_json
from framework.io.paths import SCHEMA_DIR


def validate_against_schema(
    payload: Any,
    schema_name: str,
    *,
    schema_dir: Path | None = None,
) -> tuple[bool, list[str]]:
    path = (schema_dir or SCHEMA_DIR) / schema_name
    schema = load_json(path)
    validator = jsonschema.Draft7Validator(schema)
    errors = sorted(
        {
            f"{'.'.join(str(p) for p in err.path) or '$'}: {err.message}"
            for err in validator.iter_errors(payload)
        }
    )
    return len(errors) == 0, errors
