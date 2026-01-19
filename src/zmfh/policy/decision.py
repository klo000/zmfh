"""Policy decisions."""

from __future__ import annotations

from zmfh.policy.model import Decision, Policy


def decide(fullname: str, policy: Policy) -> Decision:
    handle = bool(getattr(policy, "allow_loose_top_level", True)) and ("." not in fullname)

    managed = False
    try:
        for pref in getattr(policy, "managed_prefixes", []) or []:
            p = (pref or "").strip()
            if not p:
                continue
            if fullname == p or fullname.startswith(p + ".") or fullname.startswith(p):
                managed = True
                break
    except Exception:
        managed = False

    return Decision(handle=handle, managed=managed)
