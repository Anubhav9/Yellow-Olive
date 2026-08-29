import shutil
import subprocess
import sys
import webbrowser

from textual import on, work
from textual.widgets import Static, RichLog, Input, Label

import global_constants
from screens.dialouges import academy_screen_dialogue
from screens.common.screen_prompts.academy_screen import ACADEMY_PROMPT
from utils import general_utils


def open_url(url: str) -> bool:
    """Open `url` in a browser, falling back to the platform opener."""
    try:
        if webbrowser.open(url):
            return True
    except Exception:
        pass
    opener = "open" if sys.platform == "darwin" else "xdg-open"
    if shutil.which(opener) is None:
        return False
    try:
        return subprocess.run([opener, url], capture_output=True).returncode == 0
    except Exception:
        return False


class AcademyScreen(Static):
    can_focus = True

    def compose(self):
        yield RichLog(markup=True, highlight=True, id="academy-log")
        yield Label(ACADEMY_PROMPT, id="academy-prompt")
        yield Input(placeholder="Type psyquack back to return...", id="academy-input")

    def on_mount(self) -> None:
        self.focus()
        log = self.query_one("#academy-log", RichLog)
        for line in academy_screen_dialogue.ACADEMY_SCREEN_DIALOGUE.split("\n"):
            if line.strip():
                log.write(f"[bold {global_constants.GLOBAL_DIALOGUE_COLOR}]{line}[/]")
            else:
                log.write("")
        log.write(f"[bold {global_constants.GLOBAL_DIALOGUE_COLOR}]{global_constants.ACADEMY_URL}[/]")
        self.query_one("#academy-input", Input).focus()
        self.open_academy_in_browser()

    @work(thread=True)
    def open_academy_in_browser(self) -> None:
        if not open_url(global_constants.ACADEMY_URL):
            self.app.call_from_thread(self.report_browser_failure)

    def report_browser_failure(self) -> None:
        log = self.query_one("#academy-log", RichLog)
        log.write(
            f"[bold {global_constants.GLOBAL_DIALOGUE_COLOR}]"
            "COULD NOT OPEN A BROWSER - COPY THE LINK ABOVE INSTEAD.[/]"
        )

    @on(Input.Submitted, selector="#academy-input")
    async def handle_academy_input(self, event: Input.Submitted) -> None:
        player_command = (event.value or "").strip().lower()
        log = self.query_one("#academy-log", RichLog)
        if player_command == "psyquack back":
            await self.remove()
            return
        general_utils.show_invalid_command(self)
        log.write(general_utils.invalid_command_text("psyquack back"))
