"""Guard helpers for import hooks."""

from __future__ import annotations

from typing import Callable, Optional, TypeVar

T = TypeVar("T")


def guard(fn: Callable[[], T], *, default: Optional[T] = None) -> Optional[T]:
    try:
        return fn()
    except ModuleNotFoundError:
        raise
    except Exception:
        return default
