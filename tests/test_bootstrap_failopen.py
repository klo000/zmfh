import json
import os
import subprocess
import sys
from pathlib import Path


def test_bootstrap_never_raises_on_bad_policy_path(tmp_path: Path):
    env = dict(os.environ)
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src") + os.pathsep + env.get("PYTHONPATH", "")
    env["ZMFH_POLICY"] = str(tmp_path / "nope_does_not_exist.json")
    env.pop("ZMFH_DISABLE", None)
    env.pop("ZMFH_MODE", None)

    code = r"""
import json
import zmfh

zmfh.bootstrap()
print(json.dumps(zmfh.status(), ensure_ascii=False))
"""

    r = subprocess.run([sys.executable, "-c", code], env=env, capture_output=True, text=True)
    assert r.returncode == 0

    st = json.loads(r.stdout)
    assert st.get("last_error")
    assert "policy_load_failed" in st["last_error"]
