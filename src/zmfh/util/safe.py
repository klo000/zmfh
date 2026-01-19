"""Fail-open helpers."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Callable, Iterator, Optional, TypeVar

T = TypeVar("T")


@contextmanager
def swallow(*, default: Any = None) -> Iterator[None]:
    """Context manager that swallows all exceptions."""
    try:
        yield
    except Exception:
        return


def safe_call(fn: Callable[..., T], *args: Any, default: Optional[T] = None, **kwargs: Any) -> Optional[T]:
    try:
        return fn(*args, **kwargs)
    except Exception:
        return default
