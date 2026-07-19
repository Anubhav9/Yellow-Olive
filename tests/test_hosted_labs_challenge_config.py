"""Challenge session timer configuration."""

from __future__ import annotations

from hosted_labs.core.challenge_config import load_challenge_session_config


def test_challenge_1_loads_custom_timer_config() -> None:
    config = load_challenge_session_config("challenge_1")
    assert config.time_limit_minutes == 15
    assert config.idle_timeout_minutes == 4
