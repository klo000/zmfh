"""Verification of candidate paths."""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple

from zmfh.registry.fingerprint import Fingerprint, fingerprint
from zmfh.registry.scan import Candidate


def verify_candidate(cand: Candidate) -> Tuple[bool, Optional[Fingerprint]]:
    """Return (exists, fingerprint)."""
    try:
        p = Path(cand.path)
        if not p.is_file():
            return False, None
        return True, fingerprint(p)
    except Exception:
        return False, None
