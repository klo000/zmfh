"""Doctor report types & formatting."""

from __future__ import annotations

from dataclasses import dataclass, field

from zmfh.diagnostics.checks import Check


@dataclass(frozen=True)
class DoctorReport:
    title: str
    checks: list[Check] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


def to_text(report: DoctorReport) -> str:
    lines = [report.title, "-" * len(report.title)]
    for c in report.checks:
        mark = "OK" if c.ok else "FAIL"
        lines.append(f"[{mark}] {c.name}: {c.msg}")
    if report.notes:
        lines.append("")
        lines.append("Notes:")
        lines.extend(f"- {n}" for n in report.notes)
    return "\n".join(lines) + "\n"
