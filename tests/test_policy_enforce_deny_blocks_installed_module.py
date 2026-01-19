import os
import subprocess
import sys
import tempfile
from pathlib import Path


def _run(code: str, *, env: dict) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-c", code],
        env=env,
        capture_output=True,
        text=True,
    )


def test_enforce_deny_blocks_installed_module_requests(tmp_path: Path):
    # Write a UTF-8 BOM policy file like PowerShell 5.x Set-Content -Encoding UTF8.
    policy = {
        "mode": "strict",
        "deny": ["requests"],
    }
    policy_path = tmp_path / "zmfh.policy.json"
    # json text with BOM
    policy_path.write_bytes(("\ufeff" + __import__("json").dumps(policy)).encode("utf-8"))

    env = dict(os.environ)
    # Force this repo's src first.
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src") + os.pathsep + env.get("PYTHONPATH", "")
    env.pop("ZMFH_MODE", None)
    env["ZMFH_POLICY"] = str(policy_path)

    code = """
import zmfh
zmfh.bootstrap()
import importlib
try:
    importlib.import_module('requests')
    print('IMPORTED')
except ModuleNotFoundError as e:
    print('BLOCKED')
    print(str(e).splitlines()[0])
"""
    r = _run(code, env=env)
    assert r.returncode == 0
    assert "BLOCKED" in r.stdout
    assert "blocked by policy" in r.stdout.lower() or "blocked" in r.stdout.lower()
