"""Opt-in diagnostics helper for Yellow Olive.

Game code should call only:
    init_diagnostics()
    track("event_name", key=value)
    track_exception(exc, event="optional_name", key=value)
    shutdown_diagnostics()

Consent helpers are for future UI wiring:
    grant_consent(), decline_consent(), revoke_consent(), is_consent_granted()
"""

from __future__ import annotations

import logging
from typing import Any

from services.diagnostics import context, settings, transport

logger = logging.getLogger(__name__)

_ANONYMOUS_CONSENT_EVENTS = frozenset({"consent_declined", "consent_revoked"})


def init_diagnostics() -> None:
    """Prepare a new diagnostics session for this game run."""
    context.new_session_id()
    if not settings.is_consent_granted():
        return

    current = settings.load_settings()
    if current.installation_id is None:
        return

    transport.init_sentry(
        installation_id=current.installation_id,
        app_version=context.get_app_version(),
    )


def _build_payload(event: str, data: dict[str, Any]) -> dict[str, Any]:
    current = settings.load_settings()
    installation_id = current.installation_id if current.consent == "granted" else None
    return context.build_envelope(event, installation_id, data)


def track(event: str, **data: Any) -> None:
    """Send a structured diagnostics event.

    Example:
        track("challenge_completed", challenge_id="20", scenario="sakura_harbour")
    """
    try:
        payload = _build_payload(event, data)

        if event in _ANONYMOUS_CONSENT_EVENTS:
            transport.send_anonymous_consent_event(payload)
            return

        if not settings.is_consent_granted():
            return

        transport.send_opt_in_event(payload)
    except Exception:
        logger.exception("failed to record diagnostics event: %s", event)


def track_exception(exc: BaseException, event: str = "unhandled_exception", **data: Any) -> None:
    """Record a caught exception for opted-in users."""
    try:
        if not settings.is_consent_granted():
            return

        payload = _build_payload(event, data)
        transport.send_exception(payload, exc)
    except Exception:
        logger.exception("failed to record diagnostics exception: %s", event)


def shutdown_diagnostics() -> None:
    """Flush pending diagnostics before the app exits."""
    try:
        transport.flush()
    except Exception:
        logger.exception("failed to flush diagnostics")


def is_consent_granted() -> bool:
    return settings.is_consent_granted()


def needs_consent_prompt() -> bool:
    return settings.needs_consent_prompt()


def grant_consent() -> None:
    current = settings.grant_consent()
    transport.init_sentry(
        installation_id=current.installation_id or "",
        app_version=context.get_app_version(),
    )
    track("consent_granted")


def decline_consent() -> None:
    settings.decline_consent()
    track("consent_declined")


def revoke_consent() -> None:
    settings.revoke_consent()
    track("consent_revoked")
