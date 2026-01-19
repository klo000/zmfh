import os
import subprocess
import sys
from pathlib import Path


def test_cli_doctor_exit_code_is_zero_when_bootstrap_succeeds(tmp_path: Path):
    env = dict(os.environ)

    # Run from source tree.
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src") + os.pathsep + env.get("PYTHONPATH", "")

    # Ensure nothing explicitly disables ZMFH.
    env.pop("ZMFH_DISABLE", None)
    env.pop("ZMFH_MODE", None)
    env.pop("ZMFH_POLICY", None)

    r = subprocess.run(
        [sys.executable, "-m", "zmfh", "doctor"],
        env=env,
        capture_output=True,
        text=True,
    )

    assert r.returncode == 0
    assert "ZMFH Doctor" in r.stdout
