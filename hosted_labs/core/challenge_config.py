"""Per-challenge session limits for hosted labs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from hosted_labs.core.session import get_challenge_dir

DEFAULT_TIME_LIMIT_MINUTES = 15
DEFAULT_IDLE_TIMEOUT_MINUTES = 4


@dataclass(frozen=True)
class ChallengeSessionConfig:
    time_limit_minutes: int
    idle_timeout_minutes: int


def load_challenge_session_config(challenge_slug: str) -> ChallengeSessionConfig:
    challenge_dir = get_challenge_dir(challenge_slug)
    config_path = challenge_dir / "challenge_config.yaml"
    if not config_path.is_file():
        return ChallengeSessionConfig(
            time_limit_minutes=DEFAULT_TIME_LIMIT_MINUTES,
            idle_timeout_minutes=DEFAULT_IDLE_TIMEOUT_MINUTES,
        )

    with config_path.open(encoding="utf-8") as config_file:
        raw = yaml.safe_load(config_file) or {}

    return ChallengeSessionConfig(
        time_limit_minutes=max(1, int(raw.get("time_limit_minutes", DEFAULT_TIME_LIMIT_MINUTES))),
        idle_timeout_minutes=max(
            1,
            int(raw.get("idle_timeout_minutes", DEFAULT_IDLE_TIMEOUT_MINUTES)),
        ),
    )
