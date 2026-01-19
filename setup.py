"""Setup shim.

ZMFH primarily uses `pyproject.toml` + setuptools.

We keep a minimal `setup.py` to customize wheel builds so a `.pth` file can be
placed at the *site-packages root*.

Why not `data_files`?
- Some wheel installers place `data_files` into platform-specific paths.
- We want the `.pth` in purelib so CPython always processes it.

Hard rule: this file must stay tiny and must not introduce import-time
dependencies.
"""

from __future__ import annotations

import os

from setuptools import setup
from setuptools.command.build_py import build_py as _build_py


class build_py(_build_py):
    def run(self):
        super().run()

        # Ensure `zmfh_autoboot.pth` ends up in the wheel root (purelib).
        src = os.path.join(os.path.dirname(__file__), "zmfh_autoboot.pth")
        if os.path.exists(src):
            os.makedirs(self.build_lib, exist_ok=True)
            dst = os.path.join(self.build_lib, "zmfh_autoboot.pth")
            self.copy_file(src, dst)


setup(cmdclass={"build_py": build_py})
