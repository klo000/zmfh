"""ZMFH: Python import governance layer.

The public API is intentionally tiny.
"""

from __future__ import annotations

from zmfh._version import __version__


def bootstrap() -> None:
    """Manually bootstrap ZMFH.

    Normally this is called automatically via `sitecustomize`.
    """
    from zmfh.runtime.bootstrap import bootstrap as _bootstrap

    _bootstrap()


def status() -> dict:
    """Return a shallow, JSON-friendly snapshot of ZMFH runtime state."""
    from zmfh.runtime.state import get_state

    return get_state().as_dict()


__all__ = ["__version__", "bootstrap", "status"]

# config helpers
from .config import load_config, discover_config_path, ZMFHConfigError
