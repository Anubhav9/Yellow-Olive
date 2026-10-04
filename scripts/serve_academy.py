#!/usr/bin/env python3
"""Serve Yellow Olive Academy for local browser testing."""

from __future__ import annotations

import argparse
import http.server
import os
import socketserver
import webbrowser
from pathlib import Path

ACADEMY_DIR = Path(__file__).resolve().parents[1] / "docs" / "academy"
DEFAULT_PORT = 8765
DEFAULT_URL = f"http://localhost:{DEFAULT_PORT}/"

def build_academy_pyxapp() -> None:
    import importlib.util

    build_script = Path(__file__).resolve().parent / "build_academy_pyxapp.py"
    spec = importlib.util.spec_from_file_location("build_academy_pyxapp", build_script)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load build script: {build_script}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.build()


def is_academy_running(url: str = DEFAULT_URL, timeout: float = 0.5) -> bool:
    import urllib.error
    import urllib.request

    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return response.status == 200
    except (OSError, urllib.error.URLError, ValueError):
        return False


def main(open_browser: bool = True) -> None:
    build_academy_pyxapp()
    os.chdir(ACADEMY_DIR)
    handler = http.server.SimpleHTTPRequestHandler

    with socketserver.TCPServer(("", DEFAULT_PORT), handler) as httpd:
        print(f"Yellow Olive Academy running at {DEFAULT_URL}")
        print("Press Ctrl+C to stop.")
        if open_browser:
            webbrowser.open(DEFAULT_URL)
        httpd.serve_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Serve Yellow Olive Academy in the browser")
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Do not open a browser tab automatically",
    )
    args = parser.parse_args()
    main(open_browser=not args.no_browser)
