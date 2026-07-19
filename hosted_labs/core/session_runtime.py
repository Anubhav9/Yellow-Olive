"""In-memory challenge timers, idle tracking, and live terminal connections."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import WebSocket

from hosted_labs.core.challenge_config import ChallengeSessionConfig
from hosted_labs.core.cleanup import teardown_lab_session

logger = logging.getLogger(__name__)

SWEEP_INTERVAL_SECONDS = 15


@dataclass
class ActiveChallengeRuntime:
    lab_user: dict[str, Any]
    challenge_slug: str
    challenge_started_at: datetime
    last_activity_at: datetime
    config: ChallengeSessionConfig
    challenge_passed: bool = False
    terminated: bool = False


@dataclass
class PendingTermination:
    lab_session_id: str
    reason: str
    challenge_failed: bool | None = None
    detail: str | None = None


class SessionRuntimeManager:
    def __init__(self) -> None:
        self._sessions: dict[str, ActiveChallengeRuntime] = {}
        self._websockets: dict[str, WebSocket] = {}
        self._terminated_session_ids: set[str] = set()
        self._lock = asyncio.Lock()

    def is_terminated(self, lab_session_id: str) -> bool:
        return lab_session_id in self._terminated_session_ids

    def get_runtime(self, lab_session_id: str) -> ActiveChallengeRuntime | None:
        runtime = self._sessions.get(lab_session_id)
        if runtime is None or runtime.terminated:
            return None
        return runtime

    def start_challenge(
        self,
        lab_user: dict[str, Any],
        challenge_slug: str,
        config: ChallengeSessionConfig,
    ) -> None:
        now = datetime.now(timezone.utc)
        self._sessions[lab_user["lab_session_id"]] = ActiveChallengeRuntime(
            lab_user=dict(lab_user),
            challenge_slug=challenge_slug,
            challenge_started_at=now,
            last_activity_at=now,
            config=config,
        )

    def bump_activity(self, lab_session_id: str) -> None:
        runtime = self._sessions.get(lab_session_id)
        if runtime is None or runtime.terminated:
            return
        runtime.last_activity_at = datetime.now(timezone.utc)

    def mark_challenge_passed(self, lab_session_id: str) -> None:
        runtime = self._sessions.get(lab_session_id)
        if runtime is None or runtime.terminated:
            return
        runtime.challenge_passed = True
        runtime.last_activity_at = datetime.now(timezone.utc)

    def register_websocket(self, lab_session_id: str, websocket: WebSocket) -> None:
        self._websockets[lab_session_id] = websocket

    def unregister_websocket(self, lab_session_id: str) -> None:
        self._websockets.pop(lab_session_id, None)

    def clear_runtime(self, lab_session_id: str) -> None:
        self._sessions.pop(lab_session_id, None)
        self.unregister_websocket(lab_session_id)

    def mark_terminated(self, lab_session_id: str) -> None:
        self._terminated_session_ids.add(lab_session_id)

    def build_status(self, lab_session_id: str) -> dict[str, Any] | None:
        runtime = self.get_runtime(lab_session_id)
        if runtime is None:
            return None

        now = datetime.now(timezone.utc)
        idle_limit = timedelta(minutes=runtime.config.idle_timeout_minutes)
        idle_elapsed = now - runtime.last_activity_at
        idle_seconds_remaining = max(0, int((idle_limit - idle_elapsed).total_seconds()))

        challenge_seconds_remaining: int | None
        if runtime.challenge_passed:
            challenge_seconds_remaining = None
        else:
            challenge_limit = timedelta(minutes=runtime.config.time_limit_minutes)
            challenge_elapsed = now - runtime.challenge_started_at
            challenge_seconds_remaining = max(
                0,
                int((challenge_limit - challenge_elapsed).total_seconds()),
            )

        return {
            "challenge_slug": runtime.challenge_slug,
            "challenge_started": True,
            "challenge_passed": runtime.challenge_passed,
            "idle_timeout_minutes": runtime.config.idle_timeout_minutes,
            "time_limit_minutes": runtime.config.time_limit_minutes,
            "idle_seconds_remaining": idle_seconds_remaining,
            "challenge_seconds_remaining": challenge_seconds_remaining,
        }

    def collect_pending_terminations(self) -> list[PendingTermination]:
        now = datetime.now(timezone.utc)
        pending: list[PendingTermination] = []

        for runtime in self._sessions.values():
            if runtime.terminated:
                continue

            idle_limit = timedelta(minutes=runtime.config.idle_timeout_minutes)
            if now - runtime.last_activity_at >= idle_limit:
                pending.append(
                    PendingTermination(
                        lab_session_id=runtime.lab_user["lab_session_id"],
                        reason="idle_timeout",
                        challenge_failed=False,
                        detail="No activity before idle timeout.",
                    )
                )
                continue

            if runtime.challenge_passed:
                continue

            challenge_limit = timedelta(minutes=runtime.config.time_limit_minutes)
            if now - runtime.challenge_started_at >= challenge_limit:
                pending.append(
                    PendingTermination(
                        lab_session_id=runtime.lab_user["lab_session_id"],
                        reason="challenge_timeout",
                        challenge_failed=True,
                        detail="Challenge time limit reached.",
                    )
                )

        return pending

    async def terminate_session(self, pending: PendingTermination) -> None:
        async with self._lock:
            runtime = self._sessions.get(pending.lab_session_id)
            if runtime is None or runtime.terminated:
                return

            runtime.terminated = True
            lab_user = runtime.lab_user
            websocket = self._websockets.get(pending.lab_session_id)

        self.mark_terminated(pending.lab_session_id)

        teardown_lab_session(
            lab_user,
            reason=pending.reason,
            challenge_failed=pending.challenge_failed,
            detail=pending.detail,
        )

        self.clear_runtime(pending.lab_session_id)

        if websocket is not None:
            try:
                await websocket.send_json(
                    {
                        "type": "session_ended",
                        "reason": pending.reason,
                        "challenge_failed": pending.challenge_failed,
                        "redirect_url": f"/login?ended={pending.reason}",
                    }
                )
                await websocket.close(code=4403)
            except Exception:
                logger.debug("websocket already closed for %s", pending.lab_session_id)

    async def run_timeout_sweep(self) -> None:
        for pending in self.collect_pending_terminations():
            await self.terminate_session(pending)


session_runtime_manager = SessionRuntimeManager()


async def session_timeout_sweep_loop() -> None:
    while True:
        try:
            await session_runtime_manager.run_timeout_sweep()
        except Exception:
            logger.exception("hosted labs session timeout sweep failed")
        await asyncio.sleep(SWEEP_INTERVAL_SECONDS)
