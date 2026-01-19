"""In-memory trace buffer."""

from __future__ import annotations

from collections import deque
from typing import Deque, Iterable, List

from zmfh._constants import TRACE_RING_SIZE
from zmfh.evidence.events import Event


class TraceBuffer:
    def __init__(self, maxlen: int = TRACE_RING_SIZE):
        self._d: Deque[Event] = deque(maxlen=maxlen)

    def add(self, ev: Event) -> None:
        self._d.append(ev)

    def items(self) -> List[Event]:
        return list(self._d)


TRACE = TraceBuffer()
