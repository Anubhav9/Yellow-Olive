#!/usr/bin/env python3
"""Build academy.pyxapp for Pyxel WASM browser playback."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ACADEMY_DIR = Path(__file__).resolve().parents[1] / "docs" / "academy"
PYXAPP_PATH = ACADEMY_DIR / "academy.pyxapp"
STARTUP_SCRIPT = ACADEMY_DIR / "academy.py"


def needs_rebuild() -> bool:
    if not PYXAPP_PATH.is_file():
        return True

    pyxapp_mtime = PYXAPP_PATH.stat().st_mtime
    for path in ACADEMY_DIR.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix == ".pyxapp" or path.name == ".pyxapp_startup_script":
            continue
        if path.stat().st_mtime > pyxapp_mtime:
            return True
    return False


def build(force: bool = False) -> None:
    if not force and not needs_rebuild():
        return

    result = subprocess.run(
        ["pyxel", "package", ".", "academy.py"],
        cwd=ACADEMY_DIR,
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit("Failed to build academy.pyxapp. Is pyxel installed?")


def main() -> None:
    force = "--force" in sys.argv
    build(force=force)
    print(f"Built {PYXAPP_PATH}")


if __name__ == "__main__":
    main()
