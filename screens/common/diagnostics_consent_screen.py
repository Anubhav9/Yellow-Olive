"""Pre-game opt-in prompt for anonymous diagnostics."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from textual import on
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Button, RichLog, Static

from screens.common.screen_prompts import diagnostics_consent as screen_prompts
from services.diagnostics import decline_consent, grant_consent


class DiagnosticsConsentScreen(Vertical):
    can_focus = True
    DEFAULT_CSS = """
    DiagnosticsConsentScreen {
        width: 100%;
        height: 1fr;
        align: center middle;
        padding: 0 1;
    }

    #consent-card {
        width: 100%;
        height: auto;
        background: #121212;
        border: double #D4AF37;
        padding: 1 2;
    }

    #consent-copy {
        width: 100%;
        height: auto;
        max-height: 14;
        background: transparent;
        border: none;
        margin-bottom: 1;
    }

    #consent-actions {
        width: 100%;
        height: auto;
        margin-top: 1;
    }

    #consent-actions Button {
        width: 100%;
        background: #1a1a1a;
        border: double #666666;
        color: #DDDDDD;
        height: 3;
        margin-bottom: 1;
        padding: 0 1;
        content-align: center middle;
        text-style: bold;
    }

    #consent-yes {
        border: double #D4AF37;
        color: #FFDE00;
    }

    #consent-yes:hover,
    #consent-yes:focus {
        background: #2a2418;
        border: double #FFDE00;
        color: #FFDE00;
        text-style: bold;
    }

    #consent-no:hover,
    #consent-no:focus {
        background: #222222;
        border: double #888888;
        color: #FFFFFF;
    }
    """

    def __init__(
        self,
        continue_callback: Callable[[], Awaitable[None]],
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._continue_callback = continue_callback

    def compose(self) -> ComposeResult:
        with Vertical(id="consent-card"):
            yield RichLog(markup=True, highlight=False, id="consent-copy", wrap=True)
            with Vertical(id="consent-actions"):
                yield Button(screen_prompts.CONSENT_YES_LABEL, id="consent-yes")
                yield Button(screen_prompts.CONSENT_NO_LABEL, id="consent-no")

    def on_mount(self) -> None:
        copy = self.query_one("#consent-copy", RichLog)
        copy.write(screen_prompts.CONSENT_TITLE)
        copy.write("")
        copy.write(f"[bold #FFDE00]{screen_prompts.CONSENT_LEAD}[/]")
        copy.write("")
        for line in screen_prompts.CONSENT_BODY_LINES:
            copy.write(f"[#E8E8E8]{line}[/]")
        copy.write("")
        for line in screen_prompts.CONSENT_FOOTNOTE_LINES:
            copy.write(f"[#CFCFCF]{line}[/]")

        self.query_one("#consent-yes", Button).focus()

    @on(Button.Pressed, "#consent-yes")
    async def handle_opt_in(self) -> None:
        grant_consent()
        await self._continue()

    @on(Button.Pressed, "#consent-no")
    async def handle_opt_out(self) -> None:
        decline_consent()
        await self._continue()

    async def _continue(self) -> None:
        default_text = self.app.query_one("#default-text", Static)
        default_text.display = True
        await self.remove()
        await self._continue_callback()
