"""Pre-game opt-in prompt for anonymous diagnostics."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from textual import on
from textual.app import ComposeResult
from textual.widgets import Input, Label, RichLog, Static

from screens.common.screen_prompts import diagnostics_consent as screen_prompts
from services.diagnostics import decline_consent, grant_consent
from utils import general_utils


class DiagnosticsConsentScreen(Static):
    can_focus = True

    def __init__(
        self,
        continue_callback: Callable[[], Awaitable[None]],
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._continue_callback = continue_callback

    def compose(self) -> ComposeResult:
        yield Label(screen_prompts.CONSENT_BODY, id="consent-body")
        yield Label(screen_prompts.CONSENT_PROMPT, id="consent-prompt")
        yield Input(placeholder="Type yes or no...", id="consent-input")
        yield RichLog(markup=True, id="consent-log")

    def on_mount(self) -> None:
        self.query_one("#consent-input", Input).focus()

    @on(Input.Submitted, "#consent-input")
    async def handle_answer(self, event: Input.Submitted) -> None:
        answer = (event.value or "").strip().lower()
        if not answer:
            return

        if answer == "yes":
            grant_consent()
            await self._continue()
            return

        if answer == "no":
            decline_consent()
            await self._continue()
            return

        general_utils.show_invalid_command(
            self,
            "PsyQuack tilts its head... type yes or no.",
        )
        log = self.query_one("#consent-log", RichLog)
        log.write(screen_prompts.INVALID_ANSWER_HINT)

    async def _continue(self) -> None:
        await self.remove()
        await self._continue_callback()
