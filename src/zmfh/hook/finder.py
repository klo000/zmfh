"""Finder logic."""

from __future__ import annotations

from zmfh.contracts.messages import DeletionMessage, PolicyBlockMessage, fmt_paths
from zmfh.evidence.log import emit
from zmfh.policy.defaults import default_policy
from zmfh.policy.rules import deny_rule
from zmfh.resolver.fallback import UNHANDLED
from zmfh.resolver.resolve import Deleted, Resolved, resolve
from zmfh.runtime.env import read_env
from zmfh.runtime.state import get_state


def _active_policy():
    st = get_state()
    pol = getattr(st, "_policy", None)
    return pol if pol is not None else default_policy()


def find_spec(fullname: str, path=None, target=None):
    st = get_state()
    if st.disabled or getattr(st.mode, "value", str(st.mode)) == "off":
        return None

    pol = _active_policy()

    # Enforce-mode policy blocks.
    #
    # In enforce/strict mode we intentionally *do* override Python when a module is denied.
    # This is the "governance" part of ZMFH.
    mode_text = getattr(st.mode, "value", str(st.mode))
    if mode_text == "enforce":
        try:
            rule = deny_rule(fullname, pol)
            if rule:
                emit("policy", "blocked", fullname=fullname, rule=rule)
                msg = PolicyBlockMessage(fullname=fullname, rule=rule, mode=mode_text).format()
                raise ModuleNotFoundError(msg)
        except ModuleNotFoundError:
            raise
        except Exception:
            # Fail-open: policy evaluation errors should never break Python.
            pass

    cfg = read_env()
    root = st.root or cfg.root

    exclude_dirs = pol.exclude_dirs if getattr(pol, "exclude_dirs", None) else list(cfg.exclude_dirs)
    max_files = int(getattr(pol, "max_scan_files", cfg.max_scan_files) or cfg.max_scan_files)

    r = resolve(
        fullname,
        root=root,
        policy=pol,
        exclude_dirs=exclude_dirs,
        max_files=max_files,
        path=path,
    )

    if r is UNHANDLED:
        return None

    if isinstance(r, Resolved):
        emit("resolve", "resolved", fullname=fullname, path=r.candidate.path, candidate_kind=r.candidate.kind)
        return r.spec

    if isinstance(r, Deleted):
        emit("resolve", "deleted", fullname=fullname, paths=list(r.last_known_paths))
        msg = DeletionMessage(fullname=fullname, root=root, last_known_paths=fmt_paths(r.last_known_paths)).format()
        raise ModuleNotFoundError(msg)

    return None
