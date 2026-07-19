"""Record challenge completions in a single JSON array file."""

from __future__ import annotations

import json
import logging
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

HOSTED_LABS_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_COMPLETIONS_PATH = HOSTED_LABS_ROOT / "logs" / "completions.json"


def get_completions_path() -> Path:
    override = os.getenv("HOSTED_LABS_COMPLETIONS_FILE", "").strip()
    if override:
        return Path(override)
    return DEFAULT_COMPLETIONS_PATH


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _format_duration(duration_seconds: int) -> str:
    minutes, seconds = divmod(max(0, duration_seconds), 60)
    if minutes:
        return f"{minutes}m {seconds}s"
    return f"{seconds}s"


def _atomic_write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    tmp_path: str | None = None
    try:
        fd, tmp_path = tempfile.mkstemp(
            dir=path.parent,
            prefix=f".{path.stem}-",
            suffix=".tmp",
        )
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
        os.replace(tmp_path, path)
    except Exception:
        if tmp_path:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
        raise


def _load_completions(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []

    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)

    if not isinstance(payload, list):
        raise ValueError(f"Expected a JSON array in {path}")
    return payload


def record_completion(
    *,
    github_login: str,
    github_user_id: int,
    challenge_slug: str,
    lab_session_id: str,
    challenge_started_at: datetime,
    completed_at: datetime | None = None,
) -> dict[str, Any]:
    """Append one completion entry to the completions JSON array."""
    completed = completed_at or datetime.now(timezone.utc)
    if challenge_started_at.tzinfo is None:
        challenge_started_at = challenge_started_at.replace(tzinfo=timezone.utc)
    if completed.tzinfo is None:
        completed = completed.replace(tzinfo=timezone.utc)

    duration_seconds = max(0, int((completed - challenge_started_at).total_seconds()))
    entry = {
        "github_login": github_login,
        "github_user_id": github_user_id,
        "challenge_slug": challenge_slug,
        "lab_session_id": lab_session_id,
        "completed_at": completed.isoformat(),
        "duration_seconds": duration_seconds,
        "duration_display": _format_duration(duration_seconds),
    }

    path = get_completions_path()
    try:
        completions = _load_completions(path)
        completions.append(entry)
        _atomic_write_json(path, completions)
    except Exception:
        logger.exception("failed to record challenge completion for %s", github_login)
        return entry

    return entry
