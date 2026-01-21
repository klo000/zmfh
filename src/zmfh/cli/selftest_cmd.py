"""CLI: zmfh selftest.

This runs a small set of end-to-end checks in a subprocess so it validates the
real import behavior (including meta_path hook ordering).

The tests are designed to be:
- dependency-free
- platform-neutral (Windows/PowerShell included)
- deterministic
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path


def _run_py(code: str, *, env: dict[str, str]) -> tuple[int, str, str]:
    p = subprocess.run(
        [sys.executable, "-c", code],
        env=env,
        capture_output=True,
        text=True,
    )
    return p.returncode, p.stdout, p.stderr


def cmd_selftest() -> int:
    """Run a quick self-test suite.

    Exit codes:
    - 0: all checks passed
    - 1: at least one check failed
    """

    root = Path(tempfile.mkdtemp(prefix="zmfh_selftest_"))
    pol_path = root / "zmfh.policy.json"
    trace_path = root / "zmfh.trace.jsonl"

    # A module we create ourselves so the test doesn't depend on external packages.
    (root / "denyme.py").write_text("X=1\n", encoding="utf-8")

    pol_path.write_text(
        json.dumps({"mode": "enforce", "deny": ["denyme"], "roots": [str(root)]}, ensure_ascii=False),
        encoding="utf-8",
    )

    base_env = os.environ.copy()
    base_env.update(
        {
            "ZMFH_POLICY": str(pol_path),
            "ZMFH_ROOT": str(root),
            "ZMFH_TRACE_FILE": str(trace_path),
            # Don't force diag (we want to validate trace file output quietly).
        }
    )

    checks: list[tuple[str, bool, str]] = []

    # 1) Deny enforce blocks a module that Python could otherwise import.
    root_repr = repr(str(root))
    ghost_repr = repr(str(root / "ghostmod.py"))

    code_deny = textwrap.dedent(
        f"""
        import importlib
        import sys

        import zmfh

        sys.path.insert(0, {root_repr})
        zmfh.bootstrap()

        try:
            importlib.import_module("denyme")
            print("IMPORTED")
        except Exception as e:
            print(type(e).__name__)
            print(str(e).splitlines()[0][:200])
        """
    )
    rc, out, err = _run_py(code_deny, env=base_env)
    ok = ("ModuleNotFoundError" in out) and ("ZMFH" in out)
    checks.append(("deny_enforce_blocks", ok, out.strip() or err.strip()))

    # 2) Deletion message for a module under root that used to resolve.
    (root / "ghostmod.py").write_text("X=1\n", encoding="utf-8")
    code_del = textwrap.dedent(
        f"""
        import importlib
        import os
        import sys

        import zmfh

        sys.path.insert(0, {root_repr})
        zmfh.bootstrap()

        importlib.import_module("ghostmod")
        os.remove({ghost_repr})
        sys.modules.pop("ghostmod", None)
        importlib.invalidate_caches()

        try:
            importlib.import_module("ghostmod")
            print("IMPORTED")
        except Exception as e:
            print(type(e).__name__)
            print(str(e).splitlines()[0][:200])
        """
    )
    rc2, out2, err2 = _run_py(code_del, env=base_env)
    ok2 = ("ModuleNotFoundError" in out2) and ("ZMFH" in out2)
    checks.append(("deleted_module_message", ok2, out2.strip() or err2.strip()))

    # Summarize.
    all_ok = all(ok for _, ok, _ in checks)
    print("ZMFH Selftest")
    for name, ok, detail in checks:
        mark = "OK" if ok else "FAIL"
        print(f"- {mark} {name}: {detail}")

    return 0 if all_ok else 1


__all__ = ["cmd_selftest"]

