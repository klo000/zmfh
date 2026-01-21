"""CLI: zmfh status."""

from __future__ import annotations

import json


def cmd_status(*, pretty: bool = True) -> int:
    """Print ZMFH runtime status as JSON."""

    try:
        from zmfh.runtime.bootstrap import bootstrap

        bootstrap()
    except Exception:
        # Fail-open.
        pass

    try:
        import zmfh

        data = zmfh.status()
    except Exception as e:
        data = {"error": repr(e)}

    try:
        if pretty:
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(json.dumps(data, ensure_ascii=False))
    except Exception:
        try:
            print(str(data))
        except Exception:
            return 1

    return 0


__all__ = ["cmd_status"]

