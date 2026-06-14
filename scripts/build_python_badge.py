#!/usr/bin/env python3
"""Build shields.io endpoint JSON from PyPI smoke matrix results."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PYTHON_VERSIONS = ("3.10", "3.11", "3.12", "3.13", "3.14")


def load_outcomes(results_dir: Path) -> dict[str, bool]:
    outcomes: dict[str, bool] = {}
    for path in sorted(results_dir.rglob("result-*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        outcomes[str(payload["version"])] = bool(payload["ok"])
    return outcomes


def badge_color(passed: int, total: int) -> str:
    if passed > 0:
        return "brightgreen"
    if total > 0:
        return "red"
    return "lightgrey"


def format_message(outcomes: dict[str, bool]) -> str:
    passing = [version for version in PYTHON_VERSIONS if outcomes.get(version)]
    if passing:
        return " | ".join(passing)
    if outcomes:
        return "unsupported"
    return "unknown"


def main() -> None:
    results_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "results")
    outcomes = load_outcomes(results_dir)

    passed = sum(1 for version in PYTHON_VERSIONS if outcomes.get(version))
    payload = {
        "schemaVersion": 1,
        "label": "python",
        "message": format_message(outcomes),
        "color": badge_color(passed, len(PYTHON_VERSIONS)),
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
