"""Autoboot entry.

This module is imported by a `.pth` file placed in site-packages.

Why `.pth`?
- Some environments already ship a `sitecustomize.py`.
- Python imports at most one module named `sitecustomize`.

Using a `.pth` file avoids conflicts and provides a robust auto-apply mechanism.

Hard rule: never raise.
"""

from __future__ import annotations


def _safe_boot() -> None:
    try:
        from zmfh.runtime.bootstrap import bootstrap

        bootstrap()
    except Exception:
        # Never break interpreter startup.
        return


_safe_boot()
