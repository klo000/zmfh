"""Process-local runtime state."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from zmfh.runtime.modes import Mode


@dataclass
class ZMFHState:
    bootstrapped: bool = False
    disabled: bool = False
    diag: bool = False
    mode: Mode = Mode.PASSIVE

    root: Optional[str] = None
    roots: list[str] = field(default_factory=list)
    policy_path: Optional[str] = None

    # Optional JSONL evidence/trace file path.
    trace_file: Optional[str] = None

    hook_installed: bool = False
    last_error: Optional[str] = None

    def as_dict(self) -> dict:
        pol = getattr(self, "_policy", None)
        policy_summary = None
        try:
            if pol is not None:
                policy_summary = {
                    "mode": getattr(getattr(pol, "mode", None), "value", getattr(pol, "mode", None)),
                    "deny": list(getattr(pol, "deny", []) or []),
                    "allow": list(getattr(pol, "allow", []) or []),
                    "managed_prefixes": list(getattr(pol, "managed_prefixes", []) or []),
                    "allow_loose_top_level": bool(getattr(pol, "allow_loose_top_level", True)),
                    "raise_on_deleted": bool(getattr(pol, "raise_on_deleted", True)),
                    "roots": list(getattr(pol, "roots", []) or []),
                }
        except Exception:
            policy_summary = None

        return {
            "bootstrapped": self.bootstrapped,
            "disabled": self.disabled,
            "diag": self.diag,
            "mode": getattr(self.mode, "value", str(self.mode)),
            "root": self.root,
            "roots": list(self.roots) if self.roots else None,
            "policy_path": self.policy_path,
            "trace_file": self.trace_file,
            "policy": policy_summary,
            "hook_installed": self.hook_installed,
            "last_error": self.last_error,
        }


_STATE = ZMFHState()


def get_state() -> ZMFHState:
    return _STATE
