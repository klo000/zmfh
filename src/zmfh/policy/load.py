"""Policy loading.

ZMFH is fail-open, but silent policy failures are a debugging nightmare.

So, policy loading is *strict* here and the fail-open behavior lives in
bootstrap + the meta_path guard.

Rules:
- missing / unreadable / invalid policy => raise
- callers may catch and fall back to defaults
"""

from __future__ import annotations

from zmfh.policy.model import Policy
from zmfh.policy.validate import validate_policy_dict_ex
from zmfh.util.jsonx import load_json


def load_policy(path: str, *, fallback: Policy) -> Policy:
    """Load and validate a policy.

    `fallback` exists for backward compatibility, but this function does not
    silently fall back. Instead it raises and allows the caller to decide.
    """

    data = load_json(path)
    p, errors = validate_policy_dict_ex(data)
    if p is None:
        detail = "; ".join(errors) if errors else "invalid policy"
        raise ValueError(f"Invalid ZMFH policy ({detail}): {path}")
    return p
