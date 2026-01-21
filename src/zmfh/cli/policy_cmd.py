"""CLI: zmfh policy ...

Policy commands are designed to answer one question quickly:
"Is the rule I think is active actually active?"

This module must be safe to run even when policy loading is broken.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any, Optional


def _safe_bootstrap() -> None:
    try:
        from zmfh.runtime.bootstrap import bootstrap

        bootstrap()
    except Exception:
        return


def _active_policy_any() -> Any:
    """Return the active policy object (may be default policy)."""

    try:
        from zmfh.runtime.state import get_state

        st = get_state()
        pol = getattr(st, "_policy", None)
        if pol is not None:
            return pol
    except Exception:
        pass

    try:
        from zmfh.policy.defaults import default_policy

        return default_policy()
    except Exception:
        return None


def _json_print(obj: Any, *, pretty: bool = True) -> None:
    try:
        if pretty:
            print(json.dumps(obj, indent=2, ensure_ascii=False))
        else:
            print(json.dumps(obj, ensure_ascii=False))
    except Exception:
        print(str(obj))


def cmd_policy_show(*, pretty: bool = True) -> int:
    """Show the loaded policy (effective)."""

    _safe_bootstrap()

    try:
        from zmfh.runtime.state import get_state

        st = get_state()
        pol = _active_policy_any()

        out = {
            "policy_path": getattr(st, "policy_path", None),
            "mode": getattr(getattr(st, "mode", None), "value", str(getattr(st, "mode", None))),
            "roots": list(getattr(st, "roots", []) or []),
            "effective": None,
        }

        if pol is not None:
            try:
                out["effective"] = asdict(pol)  # dataclass
            except Exception:
                # Fall back to attributes.
                out["effective"] = {
                    "mode": getattr(getattr(pol, "mode", None), "value", getattr(pol, "mode", None)),
                    "deny": list(getattr(pol, "deny", []) or []),
                    "allow": list(getattr(pol, "allow", []) or []),
                    "managed_prefixes": list(getattr(pol, "managed_prefixes", []) or []),
                    "raise_on_deleted": bool(getattr(pol, "raise_on_deleted", True)),
                    "roots": list(getattr(pol, "roots", []) or []),
                }

        _json_print(out, pretty=pretty)
        return 0
    except Exception as e:
        _json_print({"error": repr(e)}, pretty=pretty)
        return 1


def cmd_policy_validate(path: str, *, pretty: bool = True) -> int:
    """Validate a policy JSON file without applying it."""

    try:
        from zmfh.util.jsonx import load_json
        from zmfh.policy.validate import validate_policy_dict_ex

        data = load_json(path)
        pol, errors = validate_policy_dict_ex(data)
        if pol is None:
            _json_print({"valid": False, "errors": errors, "path": path}, pretty=pretty)
            return 2
        _json_print({"valid": True, "path": path}, pretty=pretty)
        return 0
    except Exception as e:
        _json_print({"valid": False, "errors": [repr(e)], "path": path}, pretty=pretty)
        return 2


def cmd_policy_check(fullname: str, *, pretty: bool = True) -> int:
    """Explain how policy would treat an import."""

    _safe_bootstrap()

    try:
        from zmfh.runtime.state import get_state
        from zmfh.policy.rules import allow_rule, deny_rule, is_protected

        st = get_state()
        pol = _active_policy_any()

        mode = getattr(getattr(st, "mode", None), "value", str(getattr(st, "mode", None)))
        protected = bool(is_protected(fullname))
        allow = allow_rule(fullname, pol) if pol is not None else None
        deny = deny_rule(fullname, pol) if pol is not None else None

        decision: str
        if mode == "enforce" and deny:
            decision = "blocked"
        else:
            decision = "allowed"

        out = {
            "fullname": fullname,
            "mode": mode,
            "protected": protected,
            "allow_match": allow,
            "deny_match": deny,
            "decision": decision,
            "policy_path": getattr(st, "policy_path", None),
        }

        _json_print(out, pretty=pretty)
        return 0 if decision != "blocked" else 3
    except Exception as e:
        _json_print({"error": repr(e), "fullname": fullname}, pretty=pretty)
        return 1


def cmd_policy(args) -> int:
    """Dispatcher for `zmfh policy ...`.

    `cli/main.py` routes all `policy` invocations here.
    """

    action = getattr(args, "action", None)
    if action in (None, "show"):
        return cmd_policy_show(pretty=True)

    if action == "validate":
        path = getattr(args, "path", None)
        if not path:
            # argparse makes this optional; treat missing as usage error.
            _json_print({"valid": False, "errors": ["missing path"], "path": None}, pretty=True)
            return 2
        return cmd_policy_validate(path, pretty=True)

    if action == "check":
        fullname = getattr(args, "module", None)
        if not fullname:
            _json_print({"error": "missing module"}, pretty=True)
            return 2
        return cmd_policy_check(fullname, pretty=True)

    _json_print({"error": f"unknown policy action: {action}"}, pretty=True)
    return 2


__all__ = [
    "cmd_policy",
    "cmd_policy_show",
    "cmd_policy_validate",
    "cmd_policy_check",
]

