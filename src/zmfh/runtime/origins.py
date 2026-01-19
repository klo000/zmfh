"""Observed Python origins.

ZMFH's v0.1 resolver is conservative: it normally does not override Python when
Python can already import a module.

However, for *deletion* detection we want high-signal evidence:
- If a module was previously importable via Python's PathFinder, and
- its origin was under the project root, and
- later the origin disappears,

...then we can emit a clearer error message than the default
"No module named ...".

This module stores those observed origins in-process.

Hard rules:
- must never raise
- must never perform heavy I/O
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional


@dataclass(frozen=True)
class OriginRecord:
    fullname: str
    origin: str


# Process-local in-memory cache.
_ORIGINS: Dict[str, OriginRecord] = {}


def _safe_resolve(p: str) -> Optional[Path]:
    try:
        return Path(p).expanduser().resolve()
    except Exception:
        try:
            return Path(p)
        except Exception:
            return None


def _is_under_root(origin: Path, root: Path) -> bool:
    try:
        return origin.is_relative_to(root)
    except Exception:
        try:
            o = str(origin)
            r = str(root)
            if not r.endswith("/") and not r.endswith("\\"):
                r = r + ("\\" if "\\" in o else "/")
            return o.startswith(r)
        except Exception:
            return False


def remember(fullname: str, origin: str) -> None:
    """Remember an origin path for a top-level module."""
    try:
        if not fullname or "." in fullname:
            return
        if not origin:
            return
        _ORIGINS[fullname] = OriginRecord(fullname=fullname, origin=origin)

        # Keep the cache bounded.
        if len(_ORIGINS) > 2048:
            # Drop an arbitrary half. Deterministic order isn't required.
            for k in list(_ORIGINS.keys())[:1024]:
                _ORIGINS.pop(k, None)
    except Exception:
        return


def remember_if_under_root(fullname: str, origin: str, *, root: str) -> None:
    """Remember origin only if it is located under the given root."""
    try:
        if not origin:
            return
        # Exclude pseudo-origins.
        if origin in ("built-in", "frozen"):
            return
        op = _safe_resolve(origin)
        rp = _safe_resolve(root)
        if op is None or rp is None:
            return
        if _is_under_root(op, rp):
            remember(fullname, str(op))
    except Exception:
        return


def get(fullname: str) -> Optional[OriginRecord]:
    try:
        return _ORIGINS.get(fullname)
    except Exception:
        return None


def drop(fullname: str) -> None:
    try:
        _ORIGINS.pop(fullname, None)
    except Exception:
        return


def clear() -> None:
    try:
        _ORIGINS.clear()
    except Exception:
        return
