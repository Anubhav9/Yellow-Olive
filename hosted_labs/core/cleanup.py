"""End hosted lab sessions without deleting cluster namespaces or local kubeconfigs."""

from __future__ import annotations

from typing import Any

from hosted_labs.core import audit
from hosted_labs.core.lab_slots import lab_slot_manager


def teardown_lab_session(
    lab_user: dict[str, Any],
    *,
    reason: str,
    challenge_failed: bool | None = None,
    detail: str | None = None,
) -> None:
    """Release the seat and close the audit file. Cluster namespaces are left intact."""
    audit.record_activity(
        lab_session_id=lab_user["lab_session_id"],
        session_started_at=lab_user["session_started_at"],
        level="INFO",
        category="session",
        event="session_teardown",
        reason=reason,
        challenge_failed=challenge_failed,
        detail=detail,
    )
    lab_slot_manager.release(int(lab_user["github_user_id"]))
    audit.end_session(
        lab_session_id=lab_user["lab_session_id"],
        session_started_at=lab_user["session_started_at"],
        reason=reason,
        challenge_failed=challenge_failed,
    )
