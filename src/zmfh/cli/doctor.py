"""CLI: zmfh doctor."""

from __future__ import annotations

from zmfh.diagnostics.doctor import run_doctor


def cmd_doctor() -> int:
    # Ensure ZMFH is bootstrapped even if `sitecustomize` / `.pth` auto-apply
    # isn't active in this environment (e.g. running from source).
    try:
        from zmfh.runtime.bootstrap import bootstrap

        bootstrap()
    except Exception:
        pass

    rep = run_doctor()

    print(rep.title)
    for c in rep.checks:
        mark = "OK" if c.ok else "FAIL"
        print(f"- {mark} {c.name}: {c.msg}")

    if rep.notes:
        print()
        print("Notes:")
        for n in rep.notes:
            print(f"- {n}")

    return 0 if all(c.ok for c in rep.checks) else 1
