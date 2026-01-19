"""ZMFH automatic bootstrap entrypoint.

Python's `site` module imports `sitecustomize` at interpreter startup if it is
present on `sys.path` (typically in site-packages).

ZMFH uses this to auto-install a conservative import hook.

Hard rules:
- Never raise (fail-open)
- No printing by default (no console pollution)
"""


def _zmfh_bootstrap_fail_open() -> None:
    try:
        from zmfh.runtime.bootstrap import bootstrap

        bootstrap()
    except Exception:
        return


_zmfh_bootstrap_fail_open()
