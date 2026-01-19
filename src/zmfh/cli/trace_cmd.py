"""CLI: zmfh trace.

In-memory trace is process-local, so in practice you usually want to set:

    ZMFH_TRACE_FILE=.../zmfh.trace.jsonl

and then `zmfh trace` will tail that file.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, List, Optional


def _safe_bootstrap() -> None:
    try:
        from zmfh.runtime.bootstrap import bootstrap

        bootstrap()
    except Exception:
        return


def _tail_lines(path: Path, n: int) -> List[str]:
    """Read last N lines from a text file (best-effort)."""

    if n <= 0:
        return []
    try:
        data = path.read_text(encoding="utf-8", errors="replace").splitlines()
        return data[-n:]
    except Exception:
        return []


def cmd_trace(*, tail: int = 50, pretty: bool = False) -> int:
    _safe_bootstrap()

    try:
        from zmfh.runtime.state import get_state

        st = get_state()
        tf = getattr(st, "trace_file", None)
        if tf:
            p = Path(str(tf)).expanduser()
            lines = _tail_lines(p, tail)
            for ln in lines:
                print(ln)
            return 0

        # Fall back to in-memory trace for this process.
        from dataclasses import asdict
        from zmfh.evidence.trace import TRACE

        items = TRACE.items()
        items = items[-tail:] if tail > 0 else items

        if pretty:
            out = [asdict(ev) for ev in items]
            print(json.dumps(out, indent=2, ensure_ascii=False))
        else:
            for ev in items:
                try:
                    print(json.dumps(asdict(ev), ensure_ascii=False))
                except Exception:
                    print(str(ev))
        return 0
    except Exception as e:
        try:
            print(json.dumps({"error": repr(e)}, ensure_ascii=False))
        except Exception:
            print(repr(e))
        return 1


def cmd_trace_clear() -> int:
    """Clear in-memory trace buffer and, if configured, truncate trace file."""

    _safe_bootstrap()

    try:
        # Always clear in-memory first.
        from zmfh.evidence.trace import TRACE

        # Reinitialize the deque by making a new TraceBuffer instance.
        # (TraceBuffer has no clear() in v0.1.)
        from zmfh.evidence.trace import TraceBuffer

        try:
            TRACE._d.clear()  # type: ignore[attr-defined]
        except Exception:
            pass

        # Clear file if configured.
        from zmfh.runtime.state import get_state

        st = get_state()
        tf = getattr(st, "trace_file", None)
        if tf:
            try:
                p = Path(str(tf)).expanduser()
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text("", encoding="utf-8")
            except Exception:
                pass

        return 0
    except Exception:
        return 1


# --- alias for cli/main.py ---

def cmd_trace(args):
    return main(args)

