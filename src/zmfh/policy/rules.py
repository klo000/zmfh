"""Rules helpers.

v0.1 rules are intentionally simple.

This module provides small, dependency-light helpers so the import hook can:
- decide whether an import is allowed/blocked (enforce/strict mode)
- keep safety guarantees (do not brick the interpreter)

Rule format (v0.1):
- strings like "requests" or "numpy" block the top-level module and all
  submodules ("requests.sessions", ...)
- glob patterns are allowed (fnmatch), e.g. "requests.*"

Notes:
- allow rules act as an override: if an allow matches, it wins over deny.
- ZMFH itself and critical import machinery modules are protected from
  policy blocks (fail-open safety).
"""

from __future__ import annotations

import fnmatch

from zmfh.policy.model import Policy


_PROTECTED_TOP_LEVEL: frozenset[str] = frozenset(
    {
        # Python import system
        "importlib",
        "encodings",
        "zipimport",
        # Core runtime
        "sys",
        "builtins",
        "types",
        # ZMFH itself
        "zmfh",
    }
)


def is_protected(fullname: str) -> bool:
    """Return True if this module should never be blocked by policy."""

    try:
        top = fullname.split(".", 1)[0]
    except Exception:
        return True
    return top in _PROTECTED_TOP_LEVEL


def _matches(fullname: str, rule: str) -> bool:
    r = (rule or "").strip()
    if not r:
        return False

    # Glob support
    if any(ch in r for ch in "*?[]"):
        try:
            return fnmatch.fnmatch(fullname, r)
        except Exception:
            return False

    # Prefix semantics: "requests" matches "requests" and "requests.something"
    return fullname == r or fullname.startswith(r + ".")


def allow_rule(fullname: str, policy: Policy) -> str | None:
    """Return the matching allow rule, if any."""

    try:
        for r in getattr(policy, "allow", []) or []:
            if _matches(fullname, r):
                return (r or "").strip()
    except Exception:
        return None
    return None


def deny_rule(fullname: str, policy: Policy) -> str | None:
    """Return the matching deny rule, if any.

    - allow overrides deny
    - protected modules are never blocked
    """

    if is_protected(fullname):
        return None

    # Allow overrides deny.
    if allow_rule(fullname, policy) is not None:
        return None

    try:
        for r in getattr(policy, "deny", []) or []:
            if _matches(fullname, r):
                return (r or "").strip()
    except Exception:
        return None

    return None
