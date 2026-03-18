"""
Configuration for the disk/academics MCP. Base path is configurable via environment.
"""
from __future__ import annotations

import os
from pathlib import Path

# Default: E:/ on Windows so Path resolves to drive root
_DEFAULT_BASE = "E:/"


def get_academics_base() -> Path:
    """
    Return the base path for academics (e.g. E:/). Course dir is base/academics/{school}/{course}.
    Set ACADEMICS_BASE in .env to override (e.g. E:/ or /data).
    """
    raw = os.environ.get("ACADEMICS_BASE", _DEFAULT_BASE).strip()
    path = Path(raw)
    # On Windows, "E:" alone can be wrong; use E:/ for drive root
    if raw.upper() == "E:":
        path = Path("E:/")
    return path
