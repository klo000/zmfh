"""Constants.

Keep this module small and dependency-free.
"""

from __future__ import annotations

# Environment variables
ENV_DISABLE = "ZMFH_DISABLE"     # 1/true disables ZMFH entirely
ENV_MODE = "ZMFH_MODE"           # off | passive | enforce | diag
ENV_DIAG = "ZMFH_DIAG"           # 1/true enables diagnostic logging
ENV_POLICY = "ZMFH_POLICY"       # path to JSON policy file
ENV_ROOT = "ZMFH_ROOT"           # optional project root override (os.pathsep separated)
ENV_TRACE_FILE = "ZMFH_TRACE_FILE"  # optional JSONL evidence/trace file path

# Defaults
DEFAULT_MODE = "passive"

DEFAULT_EXCLUDE_DIRS = [
    ".git",
    ".hg",
    ".svn",
    ".tox",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "__pycache__",
    ".venv",
    "venv",
    "env",
    "build",
    "dist",
    "site-packages",
    "node_modules",
]

DEFAULT_MAX_SCAN_FILES = 20000
DEFAULT_SCAN_TTL_SECONDS = 1.0

TRACE_RING_SIZE = 200
