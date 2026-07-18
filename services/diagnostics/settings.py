"""Persist opt-in diagnostics settings under the lab workspace."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from utils.general_utils import ensure_lab_workspace

ConsentState = Literal["unknown", "granted", "declined"]

SETTINGS_VERSION = 1


@dataclass
class DiagnosticsSettings:
    consent: ConsentState = "unknown"
    installation_id: str | None = None
    consent_prompted_at: str | None = None
    consent_updated_at: str | None = None

    @classmethod
    def from_dict(cls, raw: dict) -> DiagnosticsSettings:
        diagnostics = raw.get("diagnostics", {})
        consent = diagnostics.get("consent", "unknown")
        if consent not in {"unknown", "granted", "declined"}:
            consent = "unknown"
        installation_id = diagnostics.get("installation_id")
        if installation_id is not None:
            installation_id = str(installation_id)
        return cls(
            consent=consent,
            installation_id=installation_id,
            consent_prompted_at=diagnostics.get("consent_prompted_at"),
            consent_updated_at=diagnostics.get("consent_updated_at"),
        )

    def to_dict(self) -> dict:
        return {
            "version": SETTINGS_VERSION,
            "diagnostics": {
                "consent": self.consent,
                "installation_id": self.installation_id,
                "consent_prompted_at": self.consent_prompted_at,
                "consent_updated_at": self.consent_updated_at,
            },
        }


def _settings_path() -> Path:
    return ensure_lab_workspace() / "settings.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_settings() -> DiagnosticsSettings:
    settings_path = _settings_path()
    if not settings_path.is_file():
        return DiagnosticsSettings()

    try:
        with settings_path.open("r", encoding="utf-8") as settings_file:
            raw = json.load(settings_file)
    except (OSError, json.JSONDecodeError):
        return DiagnosticsSettings()

    if not isinstance(raw, dict):
        return DiagnosticsSettings()
    return DiagnosticsSettings.from_dict(raw)


def save_settings(settings: DiagnosticsSettings) -> None:
    settings_path = _settings_path()
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    with settings_path.open("w", encoding="utf-8") as settings_file:
        json.dump(settings.to_dict(), settings_file, indent=2)


def is_consent_granted() -> bool:
    return load_settings().consent == "granted"


def needs_consent_prompt() -> bool:
    return load_settings().consent == "unknown"


def grant_consent() -> DiagnosticsSettings:
    settings = load_settings()
    if settings.installation_id is None:
        settings.installation_id = str(uuid.uuid4())
    settings.consent = "granted"
    settings.consent_updated_at = _utc_now()
    if settings.consent_prompted_at is None:
        settings.consent_prompted_at = settings.consent_updated_at
    save_settings(settings)
    return settings


def decline_consent() -> DiagnosticsSettings:
    settings = load_settings()
    settings.consent = "declined"
    settings.consent_updated_at = _utc_now()
    if settings.consent_prompted_at is None:
        settings.consent_prompted_at = settings.consent_updated_at
    save_settings(settings)
    return settings


def revoke_consent() -> DiagnosticsSettings:
    return decline_consent()
