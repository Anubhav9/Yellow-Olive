from textual import on
from textual.widgets import Static, RichLog, Input, Label

import global_constants
from screens.dialouges import help_screen_dialogue
from screens.common.screen_prompts.help_screen import HELP_PROMPT
from utils import general_utils


class HelpScreen(Static):
    can_focus = True

    def compose(self):
        yield RichLog(markup=True, highlight=True, id="help-log")
        yield Label(HELP_PROMPT, id="help-prompt")
        yield Input(placeholder="Type psyquack back to return...", id="help-input")

    def on_mount(self) -> None:
        self.focus()
        log = self.query_one("#help-log", RichLog)
        for line in help_screen_dialogue.HELP_SCREEN_DIALOGUE.split("\n"):
            if line.strip():
                log.write(f"[bold {global_constants.GLOBAL_DIALOGUE_COLOR}]{line}[/]")
            else:
                log.write("")
        self.query_one("#help-input", Input).focus()

    @on(Input.Submitted, selector="#help-input")
    async def handle_help_input(self, event: Input.Submitted) -> None:
        player_command = (event.value or "").strip().lower()
        log = self.query_one("#help-log", RichLog)
        if player_command == "psyquack back":
            await self.remove()
            return
        general_utils.show_invalid_command(self)
        log.write(general_utils.invalid_command_text("psyquack back"))
