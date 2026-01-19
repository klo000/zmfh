"""Resolution orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from importlib.machinery import ModuleSpec
from pathlib import Path
from typing import Iterable, Sequence

from zmfh.policy.decision import decide
from zmfh.policy.model import Policy
from zmfh.registry.cache import (
    Cached,
    Observed,
    drop,
    get as cache_get,
    observed_drop,
    observed_get,
    observed_put,
    put,
)
from zmfh.registry.index import get_index, invalidate as invalidate_index
from zmfh.registry.scan import Candidate
from zmfh.resolver.fallback import UNHANDLED, python_find_spec
from zmfh.resolver.keyspace import is_supported_fullname
from zmfh.resolver.spec_factory import make_spec
from zmfh.resolver.verify import verify_candidate


@dataclass(frozen=True)
class Resolved:
    spec: ModuleSpec
    candidate: Candidate


@dataclass(frozen=True)
class Deleted:
    fullname: str
    last_known_paths: Sequence[str]


def _pick_unique(cands: Sequence[Candidate]) -> Candidate | None:
    if len(cands) == 1:
        return cands[0]
    return None


def _is_under_root(path: str, root: str) -> bool:
    """Best-effort check: is `path` inside `root`?"""

    try:
        rp = Path(root).expanduser().resolve()
        pp = Path(path).expanduser().resolve()
    except Exception:
        return False

    try:
        return rp == pp or rp in pp.parents
    except Exception:
        return False


def _candidate_from_python_spec(spec: ModuleSpec) -> Candidate | None:
    """Convert a Python-resolved ModuleSpec into a ZMFH Candidate, if possible."""

    origin = getattr(spec, "origin", None)
    if not origin:
        return None

    # Built-in/frozen modules don't have a file path.
    if origin in ("built-in", "frozen"):
        return None

    try:
        p = Path(origin)
        if not p.is_file():
            return None
    except Exception:
        return None

    # If it's a package, spec exposes search locations.
    pkg_locs = getattr(spec, "submodule_search_locations", None)
    if pkg_locs:
        pkg_dir = None
        try:
            pkg_dir = str(Path(list(pkg_locs)[0]))
        except Exception:
            pkg_dir = None
        return Candidate(kind="package", path=str(p), package_dir=pkg_dir)

    return Candidate(kind="module", path=str(p))


def _maybe_observe_python_resolution(fullname: str, spec: ModuleSpec, *, root: str, policy: Policy) -> None:
    """Record where Python resolved a module, so later deletions get a clear error."""

    # Only useful if we might raise helpful deletion diagnostics.
    if not getattr(policy, "raise_on_deleted", True):
        return
    if not getattr(policy, "cache_enabled", True):
        return

    cand = _candidate_from_python_spec(spec)
    if cand is None:
        return

    # Don't record every dependency in site-packages; keep scope to project root.
    if not _is_under_root(cand.path, root):
        return

    try:
        observed_put(fullname, Observed(candidate=cand))
    except Exception:
        return


def resolve(
    fullname: str,
    *,
    root: str,
    policy: Policy,
    exclude_dirs: Iterable[str],
    max_files: int,
    path=None,
):
    # v0.1: only top-level identifiers
    if not is_supported_fullname(fullname):
        return UNHANDLED

    d = decide(fullname, policy)
    if not d.handle:
        return UNHANDLED

    # Never override Python when Python can resolve.
    py_spec = python_find_spec(fullname, path)
    if py_spec is not None:
        _maybe_observe_python_resolution(fullname, py_spec, root=root, policy=policy)
        return UNHANDLED

    # If Python *used* to resolve this under the project root but now can't,
    # either fast-resolve from the observed path, or raise a deletion error.
    obs = observed_get(fullname)
    if obs is not None:
        ok_obs, fp_obs = verify_candidate(obs.candidate)
        if ok_obs:
            spec_obs = make_spec(fullname, obs.candidate)
            if spec_obs is not None:
                put(fullname, Cached(candidate=obs.candidate, fp=fp_obs))
                return Resolved(spec=spec_obs, candidate=obs.candidate)
        else:
            observed_drop(fullname)
            if getattr(policy, "raise_on_deleted", True):
                return Deleted(fullname=fullname, last_known_paths=[obs.candidate.path])

    # Cache fast-path (ZMFH-resolved modules)
    cached = cache_get(fullname)
    if cached is not None:
        ok, fp = verify_candidate(cached.candidate)
        if ok and cached.fp is not None and fp is not None and fp == cached.fp:
            spec = make_spec(fullname, cached.candidate)
            if spec is not None:
                return Resolved(spec=spec, candidate=cached.candidate)
        drop(fullname)

    # Build/refresh registry index
    idx = get_index(root, exclude_dirs=exclude_dirs, max_files=max_files)
    cands = idx.get_candidates(fullname)

    picked = _pick_unique(cands)
    if picked is None:
        # ambiguous or missing
        return UNHANDLED

    ok, fp = verify_candidate(picked)
    if not ok:
        # Might have moved: rescan once
        invalidate_index()
        idx2 = get_index(root, exclude_dirs=exclude_dirs, max_files=max_files, allow_ttl_refresh=False)
        cands2 = idx2.get_candidates(fullname)
        picked2 = _pick_unique(cands2)
        if picked2 is None:
            return UNHANDLED

        ok2, fp2 = verify_candidate(picked2)
        if not ok2:
            if getattr(policy, "raise_on_deleted", True):
                return Deleted(fullname=fullname, last_known_paths=[picked.path, picked2.path])
            return UNHANDLED

        spec2 = make_spec(fullname, picked2)
        if spec2 is None:
            return UNHANDLED
        put(fullname, Cached(candidate=picked2, fp=fp2))
        return Resolved(spec=spec2, candidate=picked2)

    spec = make_spec(fullname, picked)
    if spec is None:
        return UNHANDLED

    put(fullname, Cached(candidate=picked, fp=fp))
    return Resolved(spec=spec, candidate=picked)
