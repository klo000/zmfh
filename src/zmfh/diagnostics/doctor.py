"""Doctor runner."""

from __future__ import annotations

from zmfh.diagnostics.checks import (
    check_disabled,
    check_hook_installed,
    check_policy_loaded,
    check_python,
    check_trace_file,
    check_version,
)
from zmfh.diagnostics.report import DoctorReport
from zmfh.runtime.state import get_state


def run_doctor() -> DoctorReport:
    s = get_state()
    checks = [
        check_python(),
        check_version(),
        check_disabled(),
        check_policy_loaded(),
        check_trace_file(),
        check_hook_installed(),
    ]

    notes: list[str] = []
    if getattr(s, "last_error", None):
        notes.append(f"last_error: {s.last_error}")

    if not getattr(s, "hook_installed", False):
        notes.append("Hook not installed. If you expected auto-activation, confirm sitecustomize is installed.")

    return DoctorReport(title="ZMFH Doctor", checks=checks, notes=notes)
