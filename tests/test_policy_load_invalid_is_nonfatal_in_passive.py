import json
import os
import subprocess
import sys
from pathlib import Path


def _run(code: str, *, env: dict) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-c", code],
        env=env,
        capture_output=True,
        text=True,
    )


def test_policy_unknown_keys_fail_open(tmp_path: Path):
    # If the user writes a policy with a typo key, ZMFH must:
    # - not crash Python
    # - ignore the invalid policy (fail-open)
    # - surface a clear error for debugging
    root = tmp_path / "root"
    root.mkdir(parents=True)

    policy_path = tmp_path / "zmfh.policy.json"
    policy_path.write_text(
        json.dumps(
            {
                "mode": "passive",
                "deny": ["requests"],
                "typo_key": 123,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    env = dict(os.environ)
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src") + os.pathsep + env.get("PYTHONPATH", "")
    env["ZMFH_ROOT"] = str(root)
    env["ZMFH_POLICY"] = str(policy_path)
    env.pop("ZMFH_MODE", None)

    code = r"""
import json
import zmfh

zmfh.bootstrap()
print(json.dumps(zmfh.status(), ensure_ascii=False))
"""

    r = _run(code, env=env)
    assert r.returncode == 0

    st = json.loads(r.stdout)
    assert st.get("policy_path") == str(policy_path)
    # Policy should be treated as invalid, but not fatal.
    assert st.get("last_error")
    assert "unknown key" in st["last_error"]
