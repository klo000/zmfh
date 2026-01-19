"""Policy model.

Policy is intentionally simple in v0.1.
If the policy file is missing/invalid, ZMFH falls back to safe defaults.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from zmfh._constants import DEFAULT_EXCLUDE_DIRS, DEFAULT_MAX_SCAN_FILES
from zmfh.runtime.modes import Mode


@dataclass(frozen=True)
class Policy:
    mode: Mode = Mode.PASSIVE

    # Top-level import governance (v0.1.1+)
    # - deny: block these top-level modules in enforce/strict mode
    # - allow: reserved for future allowlist semantics
    deny: list[str] = field(default_factory=list)
    allow: list[str] = field(default_factory=list)

    managed_prefixes: list[str] = field(default_factory=list)

    allow_loose_top_level: bool = True
    raise_on_ambiguous: bool = False
    raise_on_deleted: bool = True

    exclude_dirs: list[str] = field(default_factory=lambda: list(DEFAULT_EXCLUDE_DIRS))
    max_scan_files: int = DEFAULT_MAX_SCAN_FILES

    roots: list[str] = field(default_factory=list)
    cache_enabled: bool = True


@dataclass(frozen=True)
class Decision:
    handle: bool
    managed: bool
