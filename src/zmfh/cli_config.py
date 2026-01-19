from __future__ import annotations
import json, os
from pathlib import Path
from typing import Optional
from .config import discover_config_path, load_config, ZMFHConfigError

_TEMPLATE_CONFIG = {
  "version": 1,
  "root": None,
  "policy_path": None,
  "mode": "passive",
  "diag": False,
  "trace": {"enabled": True, "path": "zmfh.trace.jsonl", "max_mb": 50},
  "autoboot": {"enabled": True},
  "resolver": {"observe_origins": True, "deleted_message": True}
}
_TEMPLATE_POLICY = {"mode":"passive","deny":[]}

def cmd_config_find() -> int:
    p = discover_config_path()
    print("none" if p is None else str(p))
    return 0

def cmd_config_show() -> int:
    cfg, path = load_config()
    out = dict(cfg)
    out["_loaded_from"] = path
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0

def cmd_config_validate(path: Optional[str]) -> int:
    try:
        if path:
            os.environ["ZMFH_CONFIG"] = path
        load_config()
        print("OK")
        return 0
    except ZMFHConfigError as e:
        print(str(e))
        return 2

def cmd_init() -> int:
    root = Path.cwd()
    d = root / ".zmfh"
    d.mkdir(exist_ok=True)
    cpath = d / "zmfh.config.json"
    ppath = d / "zmfh.policy.json"
    if not cpath.exists():
        cpath.write_text(json.dumps(_TEMPLATE_CONFIG, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not ppath.exists():
        ppath.write_text(json.dumps(_TEMPLATE_POLICY, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(str(cpath))
    print(str(ppath))
    return 0
