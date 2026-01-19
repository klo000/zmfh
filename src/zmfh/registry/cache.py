"""In-memory resolution cache.

This module is intentionally process-local and fail-open.

There are two caches:

1) _CACHE
   - Candidates that ZMFH resolved (i.e., Python could *not* resolve).

2) _OBSERVED
   - Candidates that Python resolved successfully while ZMFH was installed.
   - Used only for better diagnostics (e.g., "this existed under root but
     vanished") when a later import fails.

The caches are deliberately small/simple in v0.1.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from zmfh.registry.fingerprint import Fingerprint
from zmfh.registry.scan import Candidate


@dataclass(frozen=True)
class Cached:
    candidate: Candidate
    fp: Optional[Fingerprint]


@dataclass(frozen=True)
class Observed:
    """A candidate that was observed via Python's own import resolution."""

    candidate: Candidate


_CACHE: Dict[str, Cached] = {}
_OBSERVED: Dict[str, Observed] = {}


def get(fullname: str) -> Optional[Cached]:
    return _CACHE.get(fullname)


def put(fullname: str, entry: Cached) -> None:
    _CACHE[fullname] = entry


def drop(fullname: str) -> None:
    _CACHE.pop(fullname, None)


def clear() -> None:
    _CACHE.clear()
    _OBSERVED.clear()


def observed_get(fullname: str) -> Optional[Observed]:
    return _OBSERVED.get(fullname)


def observed_put(fullname: str, entry: Observed) -> None:
    _OBSERVED[fullname] = entry


def observed_drop(fullname: str) -> None:
    _OBSERVED.pop(fullname, None)


def observed_clear() -> None:
    _OBSERVED.clear()
