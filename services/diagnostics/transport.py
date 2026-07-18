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


def _payload_log_attributes(payload: dict[str, Any]) -> dict[str, str]:
    attributes: dict[str, str] = {
        "app_version": str(payload.get("app_version", "")),
        "python_version": str(payload.get("python_version", "")),
        "platform": str(payload.get("platform", "")),
        "session_id": str(payload.get("session_id", "")),
        "timestamp": str(payload.get("timestamp", "")),
    }
    installation_id = payload.get("installation_id")
    if installation_id:
        attributes["installation_id"] = str(installation_id)

    data = payload.get("data") or {}
    if isinstance(data, dict):
        for key, value in data.items():
            if value is not None:
                attributes[str(key)] = str(value)
    return attributes


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

    try:
        from sentry_sdk.integrations.logging import LoggingIntegration

        try:
            # Gameplay telemetry should land in Sentry Logs, not Issues (SDK 2.19+).
            logging_integration = LoggingIntegration(
                level=None,
                event_level=logging.CRITICAL,
                sentry_logs_level=logging.INFO,
            )
        except TypeError:
            logging_integration = LoggingIntegration(
                level=logging.CRITICAL,
                event_level=logging.CRITICAL,
            )
    except ImportError:
        logging_integration = None

    try:
        # Yellow Olive only sends manual gameplay events — skip boto3/Django/etc.
        # integrations that can break in minimal or mixed Python environments.
        init_kwargs: dict[str, Any] = {
            "dsn": dsn,
            "release": f"yellow-olive@{app_version}",
            "before_send": before_send,
            "default_integrations": False,
        }
        if logging_integration is not None:
            init_kwargs["integrations"] = [logging_integration]

        try:
            sentry_sdk.init(enable_logs=True, **init_kwargs)
        except TypeError:
            sentry_sdk.init(**init_kwargs)

        if installation_id:
            sentry_sdk.set_user({"id": installation_id})
    except Exception:
        logger.exception("failed to initialize Sentry; diagnostics will stay local")
        return

    _sentry_initialized = True


def send_opt_in_event(payload: dict[str, Any]) -> None:
    try:
        import sentry_sdk
    except ImportError:
        logger.info("diagnostics event: %s", json.dumps(payload, sort_keys=True))
        return

    if not _get_sentry_dsn() or not _sentry_initialized:
        logger.info("diagnostics event: %s", json.dumps(payload, sort_keys=True))
        return

    try:
        attributes = _payload_log_attributes(payload)
        event_name = str(payload["event"])

        if hasattr(sentry_sdk, "logger"):
            sentry_sdk.logger.info(event_name, attributes=attributes)
            return

        telemetry_logger = logging.getLogger("yellow_olive.diagnostics")
        if telemetry_logger.level == logging.NOTSET:
            telemetry_logger.setLevel(logging.INFO)
        telemetry_logger.info("%s | %s", event_name, json.dumps(attributes, sort_keys=True))
    except Exception:
        logger.exception("failed to send diagnostics event: %s", payload.get("event"))


def send_exception(payload: dict[str, Any], exc: BaseException) -> None:
    try:
        import sentry_sdk
    except ImportError:
        logger.exception("diagnostics exception for %s", payload.get("event"), exc_info=exc)
        return

    if not _get_sentry_dsn() or not _sentry_initialized:
        logger.exception("diagnostics exception for %s", payload.get("event"), exc_info=exc)
        return

    try:
        sentry_sdk.set_context("diagnostics", payload)
        sentry_sdk.capture_exception(exc)
    except Exception:
        logger.exception("failed to send diagnostics exception: %s", payload.get("event"))


def send_anonymous_consent_event(payload: dict[str, Any]) -> None:
    endpoint = _get_consent_endpoint()
    if endpoint:
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
            return

    # No custom endpoint: record an anonymous opt-out ping in Sentry Logs
    # (no installation_id) so maintainers can measure consent rates.
    app_version = str(payload.get("app_version") or "unknown")
    init_sentry(installation_id="", app_version=app_version)
    send_opt_in_event(payload)
    flush()


def flush() -> None:
    if not _get_sentry_dsn():
        return
    try:
        import sentry_sdk

        sentry_sdk.flush(timeout=2)
    except ImportError:
        return
