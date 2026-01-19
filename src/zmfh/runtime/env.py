"""Environment configuration.

ZMFH is configured primarily via environment variables so it can be:
- safe by default
- trivially disabled

This module must be import-safe and must never raise.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from zmfh._constants import (
    DEFAULT_EXCLUDE_DIRS,
    DEFAULT_MAX_SCAN_FILES,
    DEFAULT_MODE,
    ENV_DIAG,
    ENV_DISABLE,
    ENV_MODE,
    ENV_POLICY,
    ENV_ROOT,
    ENV_TRACE_FILE,
)
from zmfh.runtime.modes import Mode, normalize_mode


ROOT_MARKERS = (
    "pyproject.toml",
    "setup.cfg",
    "setup.py",
    "requirements.txt",
    ".git",
)


@dataclass(frozen=True)
class EnvConfig:
    disabled: bool
    diag: bool
    mode: Mode
    policy_path: Optional[str]

    # Optional file path where ZMFH appends JSONL trace/evidence.
    trace_file: Optional[str]

    root: str
    roots: list[str]

    exclude_dirs: frozenset[str]
    max_scan_files: int


def _coerce_bool(raw: Optional[str]) -> bool:
    if raw is None:
        return False
    return raw.strip().lower() in ("1", "true", "yes", "on")


def _find_root_from(start: Path) -> Path:
    cur = start
    try:
        cur = cur.resolve()
    except Exception:
        pass

    for _ in range(64):
        try:
            for m in ROOT_MARKERS:
                if (cur / m).exists():
                    return cur
        except Exception:
            pass

        parent = cur.parent
        if parent == cur:
            break
        cur = parent

    return start


def _parse_roots_env(value: str) -> list[str]:
    roots: list[str] = []
    for part in value.split(os.pathsep):
        p = (part or "").strip()
        if not p:
            continue
        try:
            roots.append(str(Path(p).expanduser().resolve()))
        except Exception:
            roots.append(p)

    out: list[str] = []
    for r in roots:
        if r not in out:
            out.append(r)
    return out


def detect_roots() -> list[str]:
    try:
        v = os.environ.get(ENV_ROOT)
        if v:
            roots = _parse_roots_env(v)
            if roots:
                return roots
    except Exception:
        pass

    try:
        cwd = Path.cwd()
        root = _find_root_from(cwd)
        return [str(root)]
    except Exception:
        try:
            return [os.getcwd()]
        except Exception:
            return ["."]


def read_env() -> EnvConfig:
    try:
        disabled = _coerce_bool(os.environ.get(ENV_DISABLE))
        diag = _coerce_bool(os.environ.get(ENV_DIAG))

        raw_mode = (os.environ.get(ENV_MODE) or DEFAULT_MODE).strip().lower()
        if raw_mode == "diag":
            diag = True
        mode = normalize_mode(raw_mode)

        policy_path = os.environ.get(ENV_POLICY)
        policy_path = policy_path.strip() if policy_path else None

        trace_file = os.environ.get(ENV_TRACE_FILE)
        trace_file = trace_file.strip() if trace_file else None

        roots = detect_roots()
        root = roots[0] if roots else "."

        return EnvConfig(
            disabled=disabled,
            diag=diag,
            mode=mode,
            policy_path=policy_path,
            trace_file=trace_file,
            root=root,
            roots=roots,
            exclude_dirs=frozenset(DEFAULT_EXCLUDE_DIRS),
            max_scan_files=DEFAULT_MAX_SCAN_FILES,
        )
    except Exception:
        return EnvConfig(
            disabled=False,
            diag=False,
            mode=Mode.PASSIVE,
            policy_path=None,
            trace_file=None,
            root=".",
            roots=["."],
            exclude_dirs=frozenset(DEFAULT_EXCLUDE_DIRS),
            max_scan_files=DEFAULT_MAX_SCAN_FILES,
        )
