"""Formatting helpers."""

from __future__ import annotations

import json
from dataclasses import asdict

from zmfh.evidence.events import Event


def to_json_line(ev: Event) -> str:
    try:
        return json.dumps(asdict(ev), ensure_ascii=False)
    except Exception:
        return "{}"
