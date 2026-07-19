"""Challenge completion ledger."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from hosted_labs.core import completions


@pytest.fixture
def completions_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    path = tmp_path / "completions.json"
    monkeypatch.setenv("HOSTED_LABS_COMPLETIONS_FILE", str(path))
    return path


def test_record_completion_appends_to_json_array(completions_path: Path) -> None:
    started_at = datetime(2026, 7, 19, 8, 0, tzinfo=timezone.utc)
    completed_at = datetime(2026, 7, 19, 8, 8, 43, tzinfo=timezone.utc)

    entry = completions.record_completion(
        github_login="anubhav9",
        github_user_id=12345,
        challenge_slug="challenge_1",
        lab_session_id="yo-sess-abcd1234",
        challenge_started_at=started_at,
        completed_at=completed_at,
    )

    assert entry["duration_seconds"] == 523
    assert entry["duration_display"] == "8m 43s"

    payload = json.loads(completions_path.read_text(encoding="utf-8"))
    assert isinstance(payload, list)
    assert len(payload) == 1
    assert payload[0]["github_login"] == "anubhav9"
    assert payload[0]["challenge_slug"] == "challenge_1"


def test_record_completion_appends_second_entry(completions_path: Path) -> None:
    started_at = datetime(2026, 7, 19, 8, 0, tzinfo=timezone.utc)
    completed_at = datetime(2026, 7, 19, 8, 5, 0, tzinfo=timezone.utc)

    completions.record_completion(
        github_login="player1",
        github_user_id=1,
        challenge_slug="challenge_1",
        lab_session_id="yo-sess-1",
        challenge_started_at=started_at,
        completed_at=completed_at,
    )
    completions.record_completion(
        github_login="player2",
        github_user_id=2,
        challenge_slug="challenge_1",
        lab_session_id="yo-sess-2",
        challenge_started_at=started_at,
        completed_at=completed_at,
    )

    payload = json.loads(completions_path.read_text(encoding="utf-8"))
    assert len(payload) == 2
    assert payload[1]["github_login"] == "player2"
