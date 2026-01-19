"""MetaPathFinder implementation."""

from __future__ import annotations

from zmfh.hook.finder import find_spec as _find_spec
from zmfh.hook.guards import guard


class ZMFHMetaPathFinder:
    """Fail-open MetaPathFinder."""

    def find_spec(self, fullname: str, path=None, target=None):
        return guard(lambda: _find_spec(fullname, path=path, target=target), default=None)
