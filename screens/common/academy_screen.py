import shutil
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

from textual import on, work
from textual.widgets import Static, RichLog, Input, Label

import global_constants
from screens.dialouges import academy_screen_dialogue
from screens.common.screen_prompts.academy_screen import ACADEMY_PROMPT
from utils import general_utils

SERVE_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "serve_academy.py"


def _is_academy_running(url: str) -> bool:
    import urllib.error
    import urllib.request

    try:
        with urllib.request.urlopen(url, timeout=0.5) as response:
            return response.status == 200
    except (OSError, urllib.error.URLError, ValueError):
        return False


def open_url(url: str) -> bool:
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
        self.ensure_academy_server()
        if not open_url(global_constants.ACADEMY_URL):
            self.app.call_from_thread(self.report_browser_failure)

    def ensure_academy_server(self) -> None:
        if _is_academy_running(global_constants.ACADEMY_URL):
            return

        if not SERVE_SCRIPT.is_file():
            return

        subprocess.Popen(
            [sys.executable, str(SERVE_SCRIPT), "--no-browser"],
            cwd=SERVE_SCRIPT.parents[1],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )

        for _ in range(20):
            if _is_academy_running(global_constants.ACADEMY_URL):
                return
            time.sleep(0.25)

    def report_browser_failure(self) -> None:
        log = self.query_one("#academy-log", RichLog)
        log.write(
            f"[bold {global_constants.GLOBAL_DIALOGUE_COLOR}]"
            "COULD NOT OPEN A BROWSER - COPY THE LINK ABOVE INSTEAD.[/]"
        )

    @on(Input.Submitted, selector="#academy-input")
    async def handle_academy_input(self, event: Input.Submitted) -> None:
        player_command = (event.value or "").strip().lower()
        if player_command == "psyquack back":
            await self.remove()
            return
        general_utils.show_invalid_command(self)
        log = self.query_one("#academy-log", RichLog)
        log.write(general_utils.invalid_command_text("psyquack back"))
