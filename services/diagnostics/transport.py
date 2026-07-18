"""Send diagnostics payloads to configured backends."""

from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.request
from typing import Any

logger = logging.getLogger(__name__)

_sentry_initialized = False

# Public client DSN from Sentry → Project Settings → Client Keys (DSN).
# Safe to ship in the app; opt-in consent still gates what is sent.
DEFAULT_SENTRY_DSN = (
    "https://814309becb3b1f6d465d8a73508997a8@o4508902758809600.ingest.us.sentry.io/4511756583436288"
)


def _get_sentry_dsn() -> str:
    override = os.getenv("YELLOW_OLIVE_SENTRY_DSN", "").strip()
    if override:
        return override
    return DEFAULT_SENTRY_DSN.strip()


def _get_consent_endpoint() -> str:
    return os.getenv("YELLOW_OLIVE_CONSENT_ENDPOINT", "").strip()


def init_sentry(installation_id: str, app_version: str) -> None:
    global _sentry_initialized
    if _sentry_initialized:
        return

    dsn = _get_sentry_dsn()
    if not dsn:
        return

    try:
        import sentry_sdk
    except ImportError:
        logger.debug("sentry-sdk is not installed; diagnostics events stay local")
        return

    def before_send(event: dict[str, Any], hint: dict[str, Any]) -> dict[str, Any] | None:
        return event

    sentry_sdk.init(
        dsn=dsn,
        release=f"yellow-olive@{app_version}",
        before_send=before_send,
    )
    sentry_sdk.set_user({"id": installation_id})
    _sentry_initialized = True


def send_opt_in_event(payload: dict[str, Any]) -> None:
    try:
        import sentry_sdk
    except ImportError:
        logger.info("diagnostics event: %s", json.dumps(payload, sort_keys=True))
        return

    if not _get_sentry_dsn():
        logger.info("diagnostics event: %s", json.dumps(payload, sort_keys=True))
        return

    sentry_sdk.set_tag("session_id", payload.get("session_id"))
    for key, value in payload.get("data", {}).items():
        if value is not None:
            sentry_sdk.set_tag(key, value)

    sentry_sdk.capture_message(
        payload["event"],
        level="info",
        extras={"diagnostics": payload},
    )


def send_exception(payload: dict[str, Any], exc: BaseException) -> None:
    try:
        import sentry_sdk
    except ImportError:
        logger.exception("diagnostics exception for %s", payload.get("event"), exc_info=exc)
        return

    if not _get_sentry_dsn():
        logger.exception("diagnostics exception for %s", payload.get("event"), exc_info=exc)
        return

    sentry_sdk.set_context("diagnostics", payload)
    sentry_sdk.capture_exception(exc)


def send_anonymous_consent_event(payload: dict[str, Any]) -> None:
    endpoint = _get_consent_endpoint()
    if not endpoint:
        logger.info("anonymous consent event: %s", json.dumps(payload, sort_keys=True))
        return

    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        endpoint,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=5):
            return
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        logger.debug("failed to send anonymous consent event: %s", exc)


def flush() -> None:
    if not _get_sentry_dsn():
        return
    try:
        import sentry_sdk

        sentry_sdk.flush(timeout=2)
    except ImportError:
        return
