"""JSON loading utilities."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json(path: str | Path) -> Any:
    file_path = Path(path)
    with file_path.open(encoding="utf-8") as handle:
        return json.load(handle)
