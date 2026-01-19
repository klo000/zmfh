"""Fallback helpers."""

from __future__ import annotations

from importlib.machinery import ModuleSpec, PathFinder
from typing import Optional


# Sentinel used by resolver to indicate "do not handle".
UNHANDLED = object()


def python_find_spec(fullname: str, path=None) -> Optional[ModuleSpec]:
    """Ask the standard PathFinder to resolve without invoking meta_path recursion."""
    try:
        return PathFinder.find_spec(fullname, path)
    except Exception:
        return None
