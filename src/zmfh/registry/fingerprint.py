"""File fingerprints."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class Fingerprint:
    mtime_ns: int
    size: int


def fingerprint(path: str | Path) -> Optional[Fingerprint]:
    try:
        st = Path(path).stat()
        return Fingerprint(mtime_ns=int(getattr(st, "st_mtime_ns", int(st.st_mtime * 1_000_000_000))), size=int(st.st_size))
    except Exception:
        return None
