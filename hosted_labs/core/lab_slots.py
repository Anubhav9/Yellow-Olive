from dataclasses import dataclass
from datetime import datetime, timezone

from hosted_labs.core.auth_config import format_github_namespace, get_max_lab_slots


@dataclass
class LabSeat:
    github_user_id: int
    github_login: str
    namespace: str
    lab_session_id: str
    claimed_at: str


class LabSlotManager:
    def __init__(self) -> None:
        self._seats: dict[int, LabSeat] = {}

    def active_count(self) -> int:
        return len(self._seats)

    def max_slots(self) -> int:
        return get_max_lab_slots()

    def get_seat(self, github_user_id: int) -> LabSeat | None:
        return self._seats.get(github_user_id)

    def claim(self, github_user_id: int, github_login: str, lab_session_id: str) -> tuple[bool, LabSeat | None]:
        existing = self._seats.get(github_user_id)
        if existing is not None:
            return True, existing

        if len(self._seats) >= self.max_slots():
            return False, None

        seat = LabSeat(
            github_user_id=github_user_id,
            github_login=github_login,
            namespace=format_github_namespace(github_login, github_user_id),
            lab_session_id=lab_session_id,
            claimed_at=datetime.now(timezone.utc).isoformat(),
        )
        self._seats[github_user_id] = seat
        return True, seat

    def release(self, github_user_id: int) -> None:
        self._seats.pop(github_user_id, None)


lab_slot_manager = LabSlotManager()
