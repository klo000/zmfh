from __future__ import annotations
import json, os
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

class ZMFHConfigError(RuntimeError):
    pass

_ALLOWED_TOP_KEYS = {"version","root","policy_path","mode","diag","trace","autoboot","resolver"}
_ALLOWED_TRACE_KEYS = {"enabled","path","max_mb"}
_ALLOWED_AUTOBOOT_KEYS = {"enabled"}
_ALLOWED_RESOLVER_KEYS = {"observe_origins","deleted_message"}

def _err(msg: str) -> None:
    raise ZMFHConfigError("ZMFH: " + msg)

def _validate(doc: Dict[str, Any]) -> None:
    for k in doc:
        if k not in _ALLOWED_TOP_KEYS:
            _err(f"unknown config key: {k!r}")
    ver = doc.get("version", 1)
    if ver != 1:
        _err(f"unsupported config version: {ver!r}")
    if "mode" in doc and doc["mode"] is not None:
        if not isinstance(doc["mode"], str):
            _err("config type error: mode must be str")
        m = doc["mode"].strip().lower()
        if m == "strict":
            m = "enforce"
        if m not in ("passive","enforce"):
            _err(f"unsupported mode: {doc['mode']!r}")
    if "diag" in doc and doc["diag"] is not None and not isinstance(doc["diag"], bool):
        _err("config type error: diag must be bool")
    if "trace" in doc:
        t = doc["trace"]
        if not isinstance(t, dict):
            _err("config type error: trace must be object")
        for k in t:
            if k not in _ALLOWED_TRACE_KEYS:
                _err(f"unknown trace key: {k!r}")
        if "enabled" in t and not isinstance(t["enabled"], bool):
            _err("trace.enabled must be bool")
        if "path" in t and t["path"] is not None and not isinstance(t["path"], str):
            _err("trace.path must be str")
        if "max_mb" in t and not (isinstance(t["max_mb"], int) and t["max_mb"] >= 0):
            _err("trace.max_mb must be non-negative int")
    if "autoboot" in doc:
        a = doc["autoboot"]
        if not isinstance(a, dict):
            _err("config type error: autoboot must be object")
        for k in a:
            if k not in _ALLOWED_AUTOBOOT_KEYS:
                _err(f"unknown autoboot key: {k!r}")
        if "enabled" in a and not isinstance(a["enabled"], bool):
            _err("autoboot.enabled must be bool")
    if "resolver" in doc:
        r = doc["resolver"]
        if not isinstance(r, dict):
            _err("config type error: resolver must be object")
        for k in r:
            if k not in _ALLOWED_RESOLVER_KEYS:
                _err(f"unknown resolver key: {k!r}")
        for kk in ("observe_origins","deleted_message"):
            if kk in r and not isinstance(r[kk], bool):
                _err(f"resolver.{kk} must be bool")

def default_config() -> Dict[str, Any]:
    return {
        "version": 1,
        "root": None,
        "policy_path": None,
        "mode": None,
        "diag": False,
        "trace": {"enabled": False, "path": None, "max_mb": 50},
        "autoboot": {"enabled": True},
        "resolver": {"observe_origins": True, "deleted_message": True},
    }

def discover_config_path() -> Optional[Path]:
    env = os.environ.get("ZMFH_CONFIG")
    if env and env.strip():
        return Path(env).expanduser()
    cwd = Path.cwd()
    p1 = cwd / "zmfh.config.json"
    if p1.exists():
        return p1
    root_env = os.environ.get("ZMFH_ROOT")
    if root_env and root_env.strip():
        p2 = Path(root_env) / ".zmfh" / "zmfh.config.json"
        if p2.exists():
            return p2
    p3 = Path.home() / ".zmfh" / "zmfh.config.json"
    if p3.exists():
        return p3
    return None

def load_config() -> Tuple[Dict[str, Any], Optional[str]]:
    cfg = default_config()
    p = discover_config_path()
    if not p:
        return cfg, None
    try:
        raw = p.read_text(encoding="utf-8-sig")
        doc = json.loads(raw)
    except Exception as e:
        _err(f"invalid config json: {p}: {e.__class__.__name__}: {e}")
    if not isinstance(doc, dict):
        _err(f"invalid config root type (expected object): {p}")
    _validate(doc)
    # shallow merge + known nested dicts
    for k,v in doc.items():
        if k not in ("trace","autoboot","resolver"):
            cfg[k] = v
    for nk in ("trace","autoboot","resolver"):
        if nk in doc:
            merged = dict(cfg.get(nk) or {})
            merged.update(doc[nk])
            cfg[nk] = merged
    return cfg, str(p)
