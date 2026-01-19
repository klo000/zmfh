"""Emit events.

Quiet by default. When diagnostics are enabled, also prints to stderr.
"""

from __future__ import annotations

from typing import Any, Optional

from zmfh.evidence.events import new_event
from zmfh.evidence.sink import FileSink, MultiSink, NullSink, StderrSink
from zmfh.evidence.trace import TRACE
from zmfh.runtime.state import get_state


def _get_sink():
    st = get_state()
    trace_file = getattr(st, "trace_file", None)
    diag = bool(getattr(st, "diag", False))

    if trace_file and diag:
        return MultiSink([StderrSink(), FileSink(str(trace_file))])
    if trace_file:
        return FileSink(str(trace_file))
    if diag:
        return StderrSink()
    return NullSink()


def emit(kind: str, outcome: str, *, fullname: Optional[str] = None, **data: Any) -> None:
    try:
        ev = new_event(kind=kind, outcome=outcome, fullname=fullname, **data)
        TRACE.add(ev)
        _get_sink().write(ev)
    except Exception:
        return
