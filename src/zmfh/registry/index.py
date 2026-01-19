"""In-memory registry index."""

from __future__ import annotations

from dataclasses import dataclass
from threading import RLock
from typing import Dict, Iterable, List, Optional

from zmfh._constants import DEFAULT_SCAN_TTL_SECONDS
from zmfh.registry.scan import Candidate, scan
from zmfh.util.time import mono, now_ns


@dataclass(frozen=True)
class Index:
    root: str
    mapping: Dict[str, List[Candidate]]
    built_at_ns: int
    built_at_mono: float
    generation: int

    def get_candidates(self, name: str) -> List[Candidate]:
        return list(self.mapping.get(name, []))


_LOCK = RLock()
_INDEX: Optional[Index] = None
_GEN = 0


def invalidate() -> None:
    global _INDEX
    with _LOCK:
        _INDEX = None


def _needs_refresh(idx: Index) -> bool:
    try:
        return (mono() - idx.built_at_mono) > DEFAULT_SCAN_TTL_SECONDS
    except Exception:
        return False


def get_index(root: str, *, exclude_dirs: Iterable[str], max_files: int, allow_ttl_refresh: bool = True) -> Index:
    global _INDEX, _GEN
    with _LOCK:
        if _INDEX is not None and _INDEX.root == root:
            if (not allow_ttl_refresh) or (not _needs_refresh(_INDEX)):
                return _INDEX

        _GEN += 1
        mapping = scan(root, exclude_dirs=exclude_dirs, max_files=max_files)
        _INDEX = Index(root=root, mapping=mapping, built_at_ns=now_ns(), built_at_mono=mono(), generation=_GEN)
        return _INDEX
