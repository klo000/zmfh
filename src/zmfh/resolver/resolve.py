"""ZMFH resolver.

Goal: make imports "just work" in messy project trees *without* turning the
import system into a roulette wheel.

Rules:

1) CPython first (fail-open):
   If the standard import machinery can resolve a module, we don't interfere.

2) Loose top-level rescue:
   If CPython can't resolve a *top-level* module name, we scan the project root
   and treat any <name>.py or <name>/__init__.py anywhere under the root as a
   candidate for importing <name>.

3) Clear deletion diagnostics:
   If a module was previously observed under the project root(s) and later
   disappears, we can surface a clearer error (raise_on_deleted).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence

import os

from zmfh.policy.decision import decide
from zmfh.policy.model import Policy
from zmfh.registry.cache import (
    Cached as CacheEntry,
    Observed,
    drop as cache_drop,
    get as cache_get,
    put as cache_put,
    observed_get,
    observed_put,
)
from zmfh.registry.index import get_index, invalidate as invalidate_index
from zmfh.registry.scan import Candidate
from zmfh.resolver.fallback import UNHANDLED, python_find_spec
from zmfh.resolver.keyspace import is_supported_fullname
from zmfh.resolver.spec_factory import make_spec
from zmfh.resolver.verify import verify_candidate


@dataclass(frozen=True)
class Resolved:
    fullname: str
    candidate: Candidate
    spec: object
    managed: bool


@dataclass(frozen=True)
class Deleted:
    fullname: str
    last_known_paths: Sequence[str]
    managed: bool


def _norm_abs(p: str) -> str:
    return os.path.abspath(p)


def _roots(policy: Policy, root: str) -> tuple[list[str], list[str]]:
    roots = list(policy.roots) if policy.roots else [root]
    abs_roots: list[str] = []
    cmp_roots: list[str] = []
    for r in roots:
        if not r:
            continue
        a = _norm_abs(r)
        abs_roots.append(a)
        cmp_roots.append(os.path.normcase(a))
    return abs_roots, cmp_roots


def _is_under_any(path_abs: str, roots_cmp: Sequence[str]) -> bool:
    p = os.path.normcase(path_abs)
    for r in roots_cmp:
        if p == r:
            return True
        r_sep = r + os.sep
        if p.startswith(r_sep):
            return True
    return False


def _observe_candidate(fullname: str, cand: Candidate, roots_cmp: Sequence[str]) -> None:
    """Remember that `fullname` previously resolved to `cand` under roots."""
    try:
        p = _norm_abs(cand.path)
        if not _is_under_any(p, roots_cmp):
            return
        observed_put(fullname, Observed(candidate=cand))
    except Exception:
        return


def _observe_python_spec(fullname: str, spec: object, roots_cmp: Sequence[str]) -> None:
    """If CPython resolved a module under the root, remember its origin."""
    origin = getattr(spec, "origin", None)
    if not isinstance(origin, str) or not origin:
        return
    if origin in {"built-in", "frozen"}:
        return

    origin_abs = _norm_abs(origin)
    if not _is_under_any(origin_abs, roots_cmp):
        return

    if origin_abs.endswith(os.sep + "__init__.py"):
        cand = Candidate(kind="package", path=origin_abs, package_dir=os.path.dirname(origin_abs))
    else:
        cand = Candidate(kind="module", path=origin_abs)

    observed_put(fullname, Observed(candidate=cand))


def _deleted_paths(
    fullname: str,
    roots_cmp: Sequence[str],
    missing_hints: Sequence[str],
) -> list[str]:
    """Return last-known paths under roots that are now missing."""
    vanished: set[str] = set()

    # Hints (usually from a stale cache entry)
    for p in missing_hints:
        try:
            ap = _norm_abs(p)
            if _is_under_any(ap, roots_cmp) and not os.path.exists(ap):
                vanished.add(ap)
        except Exception:
            continue

    # Observed origins (CPython or ZMFH) under roots
    try:
        obs = observed_get(fullname)
        if obs is not None:
            ap = _norm_abs(obs.candidate.path)
            if _is_under_any(ap, roots_cmp) and not os.path.exists(ap):
                vanished.add(ap)
    except Exception:
        pass

    return sorted(vanished)


def resolve(
    fullname: str,
    root: str,
    policy: Policy,
    exclude_dirs: set[str],
    max_files: int,
    path: Optional[Sequence[str]] = None,
):
    if not is_supported_fullname(fullname):
        return UNHANDLED

    d = decide(fullname, policy)
    if not d.handle:
        return UNHANDLED
    managed = d.managed

    _abs_roots, roots_cmp = _roots(policy, root)

    # 1) Fail-open: let CPython handle if it can.
    py_spec = python_find_spec(fullname, path)
    if py_spec is not None:
        _observe_python_spec(fullname, py_spec, roots_cmp)
        return UNHANDLED

    # We'll collect candidate paths that *used* to exist but now don't.
    missing_hints: list[str] = []

    # 2) Cache
    if policy.cache_enabled:
        cached = cache_get(fullname)
    else:
        cached = None

    if cached is not None:
        ok, fp = verify_candidate(cached.candidate)
        if ok and fp is not None and cached.fp == fp:
            spec = make_spec(fullname, cached.candidate)
            if spec is not None:
                _observe_candidate(fullname, cached.candidate, roots_cmp)
                return Resolved(fullname=fullname, candidate=cached.candidate, spec=spec, managed=managed)

        # stale cache entry
        try:
            if not os.path.exists(cached.candidate.path):
                missing_hints.append(cached.candidate.path)
        except Exception:
            pass
        cache_drop(fullname)

    # 3) Root scan
    idx = get_index(root, exclude_dirs=exclude_dirs, max_files=max_files)
    cands = idx.get_candidates(fullname) or []

    # Missing
    if not cands:
        if policy.raise_on_deleted:
            vanished = _deleted_paths(fullname, roots_cmp, missing_hints)
            if vanished:
                return Deleted(fullname=fullname, last_known_paths=vanished, managed=managed)
        return UNHANDLED

    # Ambiguous
    if len(cands) != 1:
        return UNHANDLED

    picked = cands[0]
    ok, fp = verify_candidate(picked)

    # If the file disappeared between scan and import, invalidate and retry once.
    if not ok:
        invalidate_index()
        idx = get_index(root, exclude_dirs=exclude_dirs, max_files=max_files)
        cands2 = idx.get_candidates(fullname) or []
        if len(cands2) != 1:
            if not cands2 and policy.raise_on_deleted:
                vanished = _deleted_paths(fullname, roots_cmp, missing_hints)
                if vanished:
                    return Deleted(fullname=fullname, last_known_paths=vanished, managed=managed)
            return UNHANDLED
        picked = cands2[0]
        ok, fp = verify_candidate(picked)
        if not ok:
            if policy.raise_on_deleted:
                vanished = _deleted_paths(fullname, roots_cmp, missing_hints + [picked.path])
                if vanished:
                    return Deleted(fullname=fullname, last_known_paths=vanished, managed=managed)
            return UNHANDLED

    spec = make_spec(fullname, picked)
    if spec is None:
        return UNHANDLED

    if policy.cache_enabled:
        cache_put(fullname, CacheEntry(candidate=picked, fp=fp))

    _observe_candidate(fullname, picked, roots_cmp)
    return Resolved(fullname=fullname, candidate=picked, spec=spec, managed=managed)
