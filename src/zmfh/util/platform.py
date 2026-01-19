"""Platform info."""

from __future__ import annotations

import platform
import sys


def python_version() -> str:
    return sys.version.split()[0]


def platform_summary() -> str:
    try:
        return platform.platform()
    except Exception:
        return "unknown"
