"""JSON Schema validation."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import jsonschema
from jsonschema import RefResolver

from framework.io.load_json import load_json
from framework.io.paths import SCHEMA_DIR


@lru_cache(maxsize=1)
def _schema_store(schema_dir: str) -> dict[str, Any]:
    root = Path(schema_dir)
    store: dict[str, Any] = {}
    for schema_path in root.glob("*.json"):
        contents = load_json(schema_path)
        store[schema_path.name] = contents
        store[schema_path.stem] = contents
        schema_id = contents.get("$id")
        if isinstance(schema_id, str):
            store[schema_id] = contents
    return store


def validate_against_schema(
    payload: Any,
    schema_name: str,
    *,
    schema_dir: Path | None = None,
) -> tuple[bool, list[str]]:
    directory = schema_dir or SCHEMA_DIR
    path = directory / schema_name
    schema = load_json(path)
    store = _schema_store(str(directory.resolve()))
    base_uri = f"{directory.resolve().as_uri()}/"
    resolver = RefResolver(base_uri=base_uri, referrer=schema, store=store)
    validator = jsonschema.Draft7Validator(schema, resolver=resolver)
    errors = sorted(
        {
            f"{'.'.join(str(p) for p in err.path) or '$'}: {err.message}"
            for err in validator.iter_errors(payload)
        }
    )
    return len(errors) == 0, errors
