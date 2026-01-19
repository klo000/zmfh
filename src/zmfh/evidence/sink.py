"""Event sinks."""

from __future__ import annotations

import sys
from pathlib import Path
from dataclasses import asdict
from typing import Protocol

from zmfh.evidence.events import Event
from zmfh.evidence.formats import to_json_line


class Sink(Protocol):
    def write(self, ev: Event) -> None: ...


class NullSink:
    def write(self, ev: Event) -> None:
        return


class StderrSink:
    def write(self, ev: Event) -> None:
        try:
            d = asdict(ev)
            kind = d.get("kind")
            outcome = d.get("outcome")
            name = d.get("fullname") or "-"
            print(f"[ZMFH][{kind}] {name} -> {outcome}", file=sys.stderr)
        except Exception:
            return


class FileSink:
    """Append JSONL events to a file.

    Fail-open: any error disables writing for that event.
    """

    def __init__(self, path: str):
        self.path = path

    def write(self, ev: Event) -> None:
        try:
            p = Path(self.path).expanduser()
            try:
                p.parent.mkdir(parents=True, exist_ok=True)
            except Exception:
                pass

            line = to_json_line(ev)
            with p.open("a", encoding="utf-8", newline="\n") as f:
                f.write(line)
                f.write("\n")
        except Exception:
            return


class MultiSink:
    """Fan out events to multiple sinks."""

    def __init__(self, sinks: list[Sink]):
        self.sinks = sinks

    def write(self, ev: Event) -> None:
        for s in list(self.sinks):
            try:
                s.write(ev)
            except Exception:
                continue
