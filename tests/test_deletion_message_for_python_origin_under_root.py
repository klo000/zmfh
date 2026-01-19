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


def test_deleted_file_origin_yields_clear_message(tmp_path: Path):
    # Create a temporary root with a simple module.
    root = tmp_path / "root"
    root.mkdir(parents=True)

    env = dict(os.environ)
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src") + os.pathsep + env.get("PYTHONPATH", "")
    env["ZMFH_ROOT"] = str(root)
    env.pop("ZMFH_POLICY", None)
    env.pop("ZMFH_MODE", None)

    code = r"""
import importlib
import os
import sys
from pathlib import Path

root = Path(os.environ['ZMFH_ROOT'])
mod = root / 'ghostmod.py'
mod.write_text('X=1\n', encoding='utf-8')

# Ensure module is importable via Python.
sys.path.insert(0, str(root))

import zmfh
zmfh.bootstrap()

importlib.import_module('ghostmod')
mod.unlink()

sys.modules.pop('ghostmod', None)
importlib.invalidate_caches()

try:
    importlib.import_module('ghostmod')
    print('IMPORTED_AGAIN')
except ModuleNotFoundError as e:
    print('ERROR')
    print(str(e))
"""

    r = _run(code, env=env)
    assert r.returncode == 0
    assert "ERROR" in r.stdout
    # The message should be upgraded to the ZMFH deletion message.
    assert "ZMFH:" in r.stdout
    assert "file vanished" in r.stdout
