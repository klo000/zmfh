from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

@dataclass(frozen=True)
class ZMFH_LastOrigin:
    fullname: str
    path: str

_LAST: Dict[str, ZMFH_LastOrigin] = {}

def record(fullname: str, path: str) -> None:
    if not fullname or not path:
        return
    _LAST[fullname] = ZMFH_LastOrigin(fullname=fullname, path=str(path))

def get(fullname: str) -> Optional[ZMFH_LastOrigin]:
    return _LAST.get(fullname)

def vanished_under_roots(fullname: str, roots: list[str]) -> Optional[str]:
    o = get(fullname)
    if not o:
        return None
    p = Path(o.path)
    # only if previously under managed roots
    for r in roots or []:
        rp = Path(r)
        try:
            p.resolve().relative_to(rp.resolve())
            # was under root
            if not p.exists():
                return str(p)
        except Exception:
            continue
    return None
