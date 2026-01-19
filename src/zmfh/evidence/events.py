"""Event structures."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from zmfh.util.time import now_ns


@dataclass(frozen=True)
class Event:
    ts_ns: int
    kind: str
    outcome: str
    fullname: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)


def new_event(*, kind: str, outcome: str, fullname: Optional[str] = None, **data: Any) -> Event:
    return Event(ts_ns=now_ns(), kind=kind, outcome=outcome, fullname=fullname, data=dict(data))
