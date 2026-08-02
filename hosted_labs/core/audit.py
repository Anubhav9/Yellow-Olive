"""Session audit logs for hosted labs (abuse review and activity trail)."""

from __future__ import annotations

import json
import logging
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

HOSTED_LABS_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_AUDIT_ROOT = HOSTED_LABS_ROOT / "logs" / "audit"


def get_audit_root() -> Path:
    override = os.getenv("HOSTED_LABS_AUDIT_DIR", "").strip()
    if override:
        return Path(override)
    return DEFAULT_AUDIT_ROOT


def client_ip_from_request(request: Any) -> str | None:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return None


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _session_start_date(session_started_at: str) -> str:
    return session_started_at[:10]


def _safe_session_filename(lab_session_id: str) -> str:
    safe_id = re.sub(r"[^\w.-]", "_", lab_session_id)
    return f"{safe_id}.json"


def session_audit_path(lab_session_id: str, session_started_at: str) -> Path:
    date_folder = _session_start_date(session_started_at)
    return get_audit_root() / date_folder / _safe_session_filename(lab_session_id)


def incident_audit_path(incident_id: str, occurred_at: str | None = None) -> Path:
    occurred = occurred_at or _utc_now()
    date_folder = _session_start_date(occurred)
    safe_id = re.sub(r"[^\w.-]", "_", incident_id)
    return get_audit_root() / date_folder / f"{safe_id}.json"


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
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


def _load_session(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def start_session(
    *,
    lab_session_id: str,
    github_login: str,
    github_user_id: int,
    namespace: str,
    client_ip: str | None,
    user_agent: str | None,
    started_at: str | None = None,
) -> Path:
    started = started_at or _utc_now()
    path = session_audit_path(lab_session_id, started)
    if path.is_file():
        return path

    payload = {
        "meta": {
            "lab_session_id": lab_session_id,
            "github_login": github_login,
            "github_user_id": github_user_id,
            "namespace": namespace,
            "client_ip": client_ip,
            "user_agent": user_agent,
            "started_at": started,
            "ended_at": None,
        },
        "activity": [],
    }
    _atomic_write_json(path, payload)
    return path


def record_activity(
    *,
    lab_session_id: str,
    session_started_at: str,
    level: str,
    category: str,
    event: str,
    **fields: Any,
) -> None:
    path = session_audit_path(lab_session_id, session_started_at)
    try:
        payload = _load_session(path)
        entry: dict[str, Any] = {
            "ts": _utc_now(),
            "level": level,
            "category": category,
            "event": event,
        }
        for key, value in fields.items():
            if value is not None:
                entry[key] = value
        payload["activity"].append(entry)
        _atomic_write_json(path, payload)
    except FileNotFoundError:
        logger.warning("audit session file missing for %s", lab_session_id)
    except Exception:
        logger.exception("failed to record audit activity for session %s", lab_session_id)


def end_session(
    *,
    lab_session_id: str,
    session_started_at: str,
    reason: str = "logout",
    challenge_failed: bool | None = None,
) -> None:
    path = session_audit_path(lab_session_id, session_started_at)
    try:
        payload = _load_session(path)
        ended_at = _utc_now()
        payload["meta"]["ended_at"] = ended_at
        payload["meta"]["end_reason"] = reason
        if challenge_failed is not None:
            payload["meta"]["challenge_failed"] = challenge_failed
        payload["activity"].append(
            {
                "ts": ended_at,
                "level": "WARN" if challenge_failed else "INFO",
                "category": "session",
                "event": reason,
                "challenge_failed": challenge_failed,
            }
        )
        _atomic_write_json(path, payload)
    except FileNotFoundError:
        pass
    except Exception:
        logger.exception("failed to end audit session %s", lab_session_id)


def record_incident(
    *,
    incident_id: str,
    meta: dict[str, Any],
    level: str,
    category: str,
    event: str,
    **fields: Any,
) -> Path:
    """Write a one-off audit file for events without a full lab session."""
    occurred_at = str(meta.get("occurred_at") or _utc_now())
    path = incident_audit_path(incident_id, occurred_at)
    entry: dict[str, Any] = {
        "ts": occurred_at,
        "level": level,
        "category": category,
        "event": event,
    }
    for key, value in fields.items():
        if value is not None:
            entry[key] = value

    payload = {
        "meta": {
            **meta,
            "incident_id": incident_id,
            "occurred_at": occurred_at,
            "ended_at": occurred_at,
        },
        "activity": [entry],
    }
    _atomic_write_json(path, payload)
    return path
