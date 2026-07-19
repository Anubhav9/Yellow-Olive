"""Audit log storage for hosted lab sessions."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from hosted_labs.core import audit


@pytest.fixture
def audit_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "audit"
    monkeypatch.setenv("HOSTED_LABS_AUDIT_DIR", str(root))
    return root


def test_start_session_creates_meta_and_empty_activity(audit_root: Path) -> None:
    started_at = "2026-07-19T08:00:00+00:00"
    path = audit.start_session(
        lab_session_id="yo-sess-abcd1234",
        github_login="player1",
        github_user_id=99,
        namespace="player1-99",
        client_ip="127.0.0.1",
        user_agent="pytest",
        started_at=started_at,
    )

    assert path == audit_root / "2026-07-19" / "yo-sess-abcd1234.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["meta"]["github_login"] == "player1"
    assert payload["meta"]["ended_at"] is None
    assert payload["activity"] == []


def test_record_activity_appends_to_session_file(audit_root: Path) -> None:
    started_at = "2026-07-19T08:00:00+00:00"
    audit.start_session(
        lab_session_id="yo-sess-abcd1234",
        github_login="player1",
        github_user_id=99,
        namespace="player1-99",
        client_ip="127.0.0.1",
        user_agent="pytest",
        started_at=started_at,
    )
    audit.record_activity(
        lab_session_id="yo-sess-abcd1234",
        session_started_at=started_at,
        level="INFO",
        category="terminal",
        event="kubectl_executed",
        command_raw="kubectl get pods",
        exit_code=0,
    )

    payload = json.loads((audit_root / "2026-07-19" / "yo-sess-abcd1234.json").read_text(encoding="utf-8"))
    assert len(payload["activity"]) == 1
    assert payload["activity"][0]["event"] == "kubectl_executed"
    assert payload["activity"][0]["command_raw"] == "kubectl get pods"


def test_end_session_sets_ended_at_and_logs_logout(audit_root: Path) -> None:
    started_at = "2026-07-19T08:00:00+00:00"
    audit.start_session(
        lab_session_id="yo-sess-abcd1234",
        github_login="player1",
        github_user_id=99,
        namespace="player1-99",
        client_ip="127.0.0.1",
        user_agent="pytest",
        started_at=started_at,
    )
    audit.end_session(lab_session_id="yo-sess-abcd1234", session_started_at=started_at)

    payload = json.loads((audit_root / "2026-07-19" / "yo-sess-abcd1234.json").read_text(encoding="utf-8"))
    assert payload["meta"]["ended_at"] is not None
    assert payload["activity"][-1]["event"] == "logout"


def test_record_incident_writes_single_file(audit_root: Path) -> None:
    occurred_at = "2026-07-19T09:00:00+00:00"
    path = audit.record_incident(
        incident_id="incident-oauth-fail-1",
        meta={"client_ip": "127.0.0.1", "occurred_at": occurred_at},
        level="WARN",
        category="auth",
        event="login_failed",
        detail="invalid code",
    )

    assert path.name == "incident-oauth-fail-1.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["meta"]["incident_id"] == "incident-oauth-fail-1"
    assert len(payload["activity"]) == 1
    assert payload["activity"][0]["event"] == "login_failed"
