"""Time helpers."""

from __future__ import annotations

import time


def now_ns() -> int:
    try:
        return time.time_ns()
    except Exception:
        # time.time_ns() exists in Python 3.7+, but keep a fallback.
        return int(time.time() * 1_000_000_000)


def mono() -> float:
    """Monotonic seconds."""
    try:
        return time.monotonic()
    except Exception:
        return time.time()
