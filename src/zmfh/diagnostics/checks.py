"""Doctor checks."""

from __future__ import annotations

import sys
from dataclasses import dataclass

from zmfh.runtime.state import get_state


@dataclass(frozen=True)
class Check:
    name: str
    ok: bool
    msg: str


def check_python() -> Check:
    return Check(name="python", ok=True, msg=f"{sys.version.split()[0]} ({sys.executable})")


def check_version() -> Check:
    try:
        import zmfh

        return Check(name="zmfh_version", ok=True, msg=str(getattr(zmfh, "__version__", "?")))
    except Exception as e:
        return Check(name="zmfh_version", ok=False, msg=f"error: {e!r}")


def check_disabled() -> Check:
    s = get_state()
    disabled = getattr(s, "disabled", False)
    return Check(name="disabled", ok=(not disabled), msg=f"disabled={disabled}")


def check_hook_installed() -> Check:
    s = get_state()
    ok = getattr(s, "hook_installed", False)
    return Check(name="hook_installed", ok=ok, msg=f"hook_installed={ok}")


def check_policy_loaded() -> Check:
    s = get_state()
    path = getattr(s, "policy_path", None)
    if not path:
        return Check(name="policy", ok=True, msg="policy_path=None")

    err = getattr(s, "last_error", None) or ""
    if err.startswith("policy_load_failed"):
        return Check(name="policy", ok=False, msg=str(err))

    pol = getattr(s, "_policy", None)
    if pol is None:
        return Check(name="policy", ok=False, msg=f"policy_path set but no policy loaded: {path}")

    return Check(name="policy", ok=True, msg=f"policy_path={path}")


def check_trace_file() -> Check:
    s = get_state()
    tf = getattr(s, "trace_file", None)
    if not tf:
        return Check(name="trace_file", ok=True, msg="trace_file=None")

    try:
        from pathlib import Path

        p = Path(str(tf)).expanduser()
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass
        with p.open("a", encoding="utf-8"):
            pass
        return Check(name="trace_file", ok=True, msg=str(p))
    except Exception as e:
        return Check(name="trace_file", ok=False, msg=f"{tf}: {e!r}")
