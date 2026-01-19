"""JSON helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json(path: str | Path) -> Any:
    p = Path(path)
    # PowerShell 5.x commonly writes UTF-8 *with* BOM by default.
    # `utf-8-sig` transparently strips BOM while still accepting plain UTF-8.
    with p.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


def loads_json(text: str) -> Any:
    return json.loads(text)


def dump_json(obj: Any, path: str | Path, *, indent: int = 2) -> None:
    p = Path(path)
    with p.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=indent)
        f.write("\n")


def dumps_json(obj: Any, *, indent: int = 2) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=indent)
