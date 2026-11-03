"""Resolve data files consistently in source and packaged installations."""

from __future__ import annotations

import sys
from pathlib import Path


def resource_path(name: str) -> Path:
    """Return a resource path in both source and PyInstaller builds.

    PyInstaller sets ``sys._MEIPASS`` to the directory containing extracted
    bundled resources. During development, resources live at the repository root.
    """
    bundle_directory = getattr(sys, "_MEIPASS", None)
    base = Path(bundle_directory) if bundle_directory else Path(__file__).resolve().parents[1]
    return base / name
