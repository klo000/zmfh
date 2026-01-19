"""Runtime modes.

- off: ZMFH does nothing
- passive: ZMFH may assist imports but never blocks
- enforce: reserved for future stricter behavior

v0.1 treats "diag" as PASSIVE + diagnostics.
"""

from __future__ import annotations

from enum import Enum


class Mode(str, Enum):
    OFF = "off"
    PASSIVE = "passive"
    ENFORCE = "enforce"

    @classmethod
    def from_text(cls, raw) -> "Mode":
        try:
            s = str(raw).strip().lower()
        except Exception:
            return cls.PASSIVE

        if s == "off":
            return cls.OFF
        if s in ("enforce", "strict"):
            return cls.ENFORCE
        # "diag" is handled by env flag.
        return cls.PASSIVE


def normalize_mode(raw: str | None) -> Mode:
    return Mode.from_text(raw)
