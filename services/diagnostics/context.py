"""Build the shared event envelope for diagnostics payloads."""

from __future__ import annotations

import platform
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_session_id = str(uuid.uuid4())


def new_session_id() -> str:
    """Start a fresh session id for a new game run."""
    global _session_id
    _session_id = str(uuid.uuid4())
    return _session_id


def get_session_id() -> str:
    return _session_id


def _project_pyproject_path() -> Path | None:
    """pyproject.toml at repo root (services/diagnostics/ → ../../)."""
    candidate = Path(__file__).resolve().parents[2] / "pyproject.toml"
    return candidate if candidate.is_file() else None


def _read_version_from_pyproject(path: Path) -> str | None:
    text = path.read_text(encoding="utf-8")
    try:
        import tomllib

        version = tomllib.loads(text).get("project", {}).get("version")
        return str(version) if version else None
    except ImportError:
        match = re.search(r'^\s*version\s*=\s*"([^"]+)"\s*$', text, re.MULTILINE)
        return match.group(1) if match else None
    except Exception:
        return None


def get_app_version() -> str:
    try:
        from importlib.metadata import version

        return version("yellow-olive")
    except Exception:
        pass

    pyproject = _project_pyproject_path()
    if pyproject is not None:
        from_pyproject = _read_version_from_pyproject(pyproject)
        if from_pyproject:
            return from_pyproject

    return "unknown"


def get_python_version() -> str:
    return (
        f"{sys.version_info.major}."
        f"{sys.version_info.minor}."
        f"{sys.version_info.micro}"
    )


def get_platform_name() -> str:
    return platform.system().lower()


def build_envelope(event: str, installation_id: str | None, data: dict[str, Any]) -> dict[str, Any]:
    return {
        "event": event,
        "app_version": get_app_version(),
        "python_version": get_python_version(),
        "platform": get_platform_name(),
        "installation_id": installation_id,
        "session_id": get_session_id(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": data,
    }
