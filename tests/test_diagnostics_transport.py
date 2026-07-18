"""Diagnostics transport behaviour."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from services.diagnostics import transport


def test_anonymous_consent_event_falls_back_to_sentry_logs() -> None:
    payload = {
        "event": "consent_declined",
        "app_version": "0.6",
        "python_version": "3.12.0",
        "platform": "linux",
        "installation_id": None,
        "session_id": "session-123",
        "timestamp": "2026-07-18T00:00:00+00:00",
        "data": {},
    }

    with (
        patch.object(transport, "_get_consent_endpoint", return_value=""),
        patch.object(transport, "init_sentry") as init_sentry,
        patch.object(transport, "send_opt_in_event") as send_opt_in_event,
        patch.object(transport, "flush") as flush,
    ):
        transport.send_anonymous_consent_event(payload)

    init_sentry.assert_called_once_with(installation_id="", app_version="0.6")
    send_opt_in_event.assert_called_once_with(payload)
    flush.assert_called_once_with()


def test_anonymous_consent_event_uses_custom_endpoint_when_configured() -> None:
    payload = {"event": "consent_declined", "app_version": "0.6", "data": {}}

    with (
        patch.object(transport, "_get_consent_endpoint", return_value="https://example.com/consent"),
        patch("urllib.request.urlopen") as urlopen,
        patch.object(transport, "init_sentry") as init_sentry,
        patch.object(transport, "send_opt_in_event") as send_opt_in_event,
    ):
        urlopen.return_value.__enter__ = MagicMock(return_value=None)
        urlopen.return_value.__exit__ = MagicMock(return_value=False)
        transport.send_anonymous_consent_event(payload)

    init_sentry.assert_not_called()
    send_opt_in_event.assert_not_called()
