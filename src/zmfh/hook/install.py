"""Hook installation."""

from __future__ import annotations

import sys
from typing import Optional


def install_meta_path_hook() -> Optional[object]:
    """Install the ZMFH MetaPathFinder if missing.

    Returns the finder instance on success, or None on failure.
    """
    try:
        from zmfh.hook.meta_path import ZMFHMetaPathFinder

        for f in sys.meta_path:
            if isinstance(f, ZMFHMetaPathFinder):
                return f

        finder = ZMFHMetaPathFinder()
        sys.meta_path.insert(0, finder)
        return finder
    except Exception:
        return None
