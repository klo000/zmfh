"""Filesystem scanning.

v0.1 scanning builds a *loose* mapping:

    module_name -> [candidates]

Where `module_name` is the filename/directory name only (top-level import), and
candidates are discovered anywhere under the detected project root.

Ambiguity is expected in large repos; ZMFH will fail-open in that case.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional


@dataclass(frozen=True)
class Candidate:
    kind: str  # "module" | "package"
    path: str  # module file path OR package __init__.py path
    package_dir: Optional[str] = None


def _is_identifier(name: str) -> bool:
    try:
        return name.isidentifier()
    except Exception:
        return False


def scan(root: str, *, exclude_dirs: Iterable[str], max_files: int) -> Dict[str, List[Candidate]]:
    mapping: Dict[str, List[Candidate]] = {}
    root_path = Path(root)

    excl = set(exclude_dirs)

    count = 0
    try:
        for dirpath, dirnames, filenames in os.walk(root_path, topdown=True, followlinks=False):
            # prune dirs
            pruned = []
            for d in dirnames:
                if d in excl:
                    continue
                if d.startswith('.'):
                    continue
                pruned.append(d)
            dirnames[:] = pruned

            # packages (dir/__init__.py)
            for d in list(dirnames):
                if not _is_identifier(d):
                    continue
                init_py = Path(dirpath) / d / "__init__.py"
                if init_py.is_file():
                    mapping.setdefault(d, []).append(
                        Candidate(kind="package", path=str(init_py), package_dir=str((Path(dirpath) / d)))
                    )

            # modules
            for fn in filenames:
                if not fn.endswith('.py'):
                    continue
                if fn == '__init__.py':
                    continue
                stem = fn[:-3]
                if not _is_identifier(stem):
                    continue

                path = str(Path(dirpath) / fn)
                mapping.setdefault(stem, []).append(Candidate(kind="module", path=path))

                count += 1
                if count >= max_files:
                    return mapping
    except Exception:
        return mapping

    return mapping
