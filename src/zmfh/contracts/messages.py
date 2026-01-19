"""Canonical user-facing messages."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


def fmt_paths(paths: Iterable[str], *, limit: int = 4) -> list[str]:
    out: list[str] = []
    for p in paths:
        if p and p not in out:
            out.append(p)
        if len(out) >= limit:
            break
    return out


@dataclass(frozen=True)
class DeletionMessage:
    fullname: str
    root: str
    last_known_paths: list[str]

    def format(self) -> str:
        lines = [
            f"ZMFH: '{self.fullname}' looked resolvable under root '{self.root}', but the file vanished.",
            "This usually means the module/package was deleted or moved during runtime.",
        ]
        if self.last_known_paths:
            lines.append("Last known candidate path(s):")
            for p in self.last_known_paths:
                lines.append(f"  - {p}")
        lines.append("You can disable ZMFH with ZMFH_DISABLE=1 or ZMFH_MODE=off.")
        return "\n".join(lines)


@dataclass(frozen=True)
class PolicyBlockMessage:
    fullname: str
    rule: str
    mode: str

    def format(self) -> str:
        lines = [
            f"ZMFH: import '{self.fullname}' is blocked by policy (rule: {self.rule}).",
            f"Mode: {self.mode}",
            "If this is unexpected, update your policy or disable ZMFH with ZMFH_DISABLE=1 or ZMFH_MODE=off.",
        ]
        return "\n".join(lines)
