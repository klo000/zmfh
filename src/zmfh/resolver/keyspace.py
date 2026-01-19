"""Keyspace rules.

ZMFH handles a very small set of names in v0.1:
- only top-level imports (no dots)
- only identifiers
- never builtins
"""

from __future__ import annotations

import sys


def is_supported_fullname(fullname: str) -> bool:
    if not isinstance(fullname, str):
        return False
    if "." in fullname:
        return False
    if not fullname.isidentifier():
        return False
    try:
        if fullname in sys.builtin_module_names:
            return False
    except Exception:
        pass
    return True
