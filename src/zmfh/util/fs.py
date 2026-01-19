"""Filesystem helpers (import-safe)."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable, Iterator


def normpath(p: str | os.PathLike[str]) -> str:
    """Best-effort normalized absolute path (never raises)."""
    try:
        return str(Path(p).expanduser().resolve())
    except Exception:
        try:
            return os.fspath(p)
        except Exception:
            return str(p)


def read_text(path: str | Path, *, encoding: str = "utf-8") -> str:
    return Path(path).read_text(encoding=encoding)


def write_text(path: str | Path, text: str, *, encoding: str = "utf-8") -> None:
    Path(path).write_text(text, encoding=encoding)


def iter_parents(p: Path, *, max_depth: int = 64) -> Iterator[Path]:
    cur = p
    for _ in range(max_depth):
        yield cur
        parent = cur.parent
        if parent == cur:
            break
        cur = parent


def is_probably_project_root(path: Path) -> bool:
    markers = ("pyproject.toml", "setup.cfg", "setup.py", "requirements.txt", ".git")
    try:
        return any((path / m).exists() for m in markers)
    except Exception:
        return False
