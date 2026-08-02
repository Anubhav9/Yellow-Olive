"""Hosted lab session runtime timers."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from hosted_labs.core.challenge_config import ChallengeSessionConfig
from hosted_labs.core.session_runtime import SessionRuntimeManager


def _lab_user() -> dict:
    return {
        "github_user_id": 42,
        "github_login": "player1",
        "namespace": "player1-42",
        "lab_session_id": "yo-sess-test1234",
        "session_started_at": "2026-07-19T08:00:00+00:00",
        "lab_granted": True,
    }


def test_idle_timeout_is_not_a_challenge_failure() -> None:
    manager = SessionRuntimeManager()
    config = ChallengeSessionConfig(time_limit_minutes=15, idle_timeout_minutes=4)
    manager.start_challenge(_lab_user(), "challenge_1", config)

    stale_time = datetime.now(timezone.utc) - timedelta(minutes=5)
    runtime = manager.get_runtime("yo-sess-test1234")
    assert runtime is not None
    runtime.last_activity_at = stale_time

    pending = manager.collect_pending_terminations()
    assert len(pending) == 1
    assert pending[0].reason == "idle_timeout"
    assert pending[0].challenge_failed is False


def test_challenge_timeout_marks_failure() -> None:
    manager = SessionRuntimeManager()
    config = ChallengeSessionConfig(time_limit_minutes=15, idle_timeout_minutes=4)
    manager.start_challenge(_lab_user(), "challenge_1", config)

    stale_time = datetime.now(timezone.utc) - timedelta(minutes=16)
    runtime = manager.get_runtime("yo-sess-test1234")
    assert runtime is not None
    runtime.challenge_started_at = stale_time
    runtime.last_activity_at = datetime.now(timezone.utc)

    pending = manager.collect_pending_terminations()
    assert len(pending) == 1
    assert pending[0].reason == "challenge_timeout"
    assert pending[0].challenge_failed is True


def test_passed_challenge_stops_challenge_timer() -> None:
    manager = SessionRuntimeManager()
    config = ChallengeSessionConfig(time_limit_minutes=15, idle_timeout_minutes=4)
    manager.start_challenge(_lab_user(), "challenge_1", config)
    manager.mark_challenge_passed("yo-sess-test1234")

    stale_time = datetime.now(timezone.utc) - timedelta(minutes=16)
    runtime = manager.get_runtime("yo-sess-test1234")
    assert runtime is not None
    runtime.challenge_started_at = stale_time

    pending = manager.collect_pending_terminations()
    assert pending == []
