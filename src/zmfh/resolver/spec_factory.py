"""ModuleSpec creation for a candidate."""

from __future__ import annotations

import importlib.util
from importlib.machinery import ModuleSpec
from typing import Optional

from zmfh.registry.scan import Candidate


def make_spec(fullname: str, cand: Candidate) -> Optional[ModuleSpec]:
    try:
        if cand.kind == "package":
            return importlib.util.spec_from_file_location(
                fullname,
                cand.path,
                submodule_search_locations=[cand.package_dir] if cand.package_dir else None,
            )
        return importlib.util.spec_from_file_location(fullname, cand.path)
    except Exception:
        return None
