"""Full-page prompt: challenge background music on (yes) or off (no); matches other Input-based screens."""

from textual import on
from textual.app import ComposeResult
from textual.widgets import Input, Label, RichLog, Static

import global_constants
from utils import general_utils


class ChallengeMusicPreferenceScreen(Static):
    can_focus = True

    def __init__(self, challenge_screen_class: type, **kwargs):
        super().__init__(**kwargs)
        self.challenge_screen_class = challenge_screen_class

    def compose(self) -> ComposeResult:
        yield Label(
            f"[bold {global_constants.GLOBAL_DIALOGUE_COLOR}]"
            "Type `yes` if you want to keep background music on during challenges, "
            "or `no` if you want to keep it off during challenges.[/]"
        )
        yield Input(
            placeholder="Type yes or no...",
            id="music-pref-input",
        )
        yield RichLog(markup=True, id="music-pref-log")

    def on_mount(self) -> None:
        self.query_one("#music-pref-input", Input).focus()

    @on(Input.Submitted, "#music-pref-input")
    async def handle_answer(self, event: Input.Submitted) -> None:
        answer = (event.value or "").strip().lower()
        if not answer:
            # Ignore empty submit (e.g. Enter carried over from the previous screen).
            return
        log = self.query_one("#music-pref-log", RichLog)
        if answer == "yes":
            general_utils.update_progress(challenge_background_music=True)
            await self._continue_to_challenge()
            return
        if answer == "no":
            general_utils.update_progress(challenge_background_music=False)
            await self._continue_to_challenge()
            return
        general_utils.show_invalid_command(
            self,
            "PsyQuack tilts its head... type yes or no.",
        )
        log.write("[yellow]Try `yes` (music on challenges) or `no` (quiet on challenges).[/]")

    async def _continue_to_challenge(self) -> None:
        container = self.parent
        await self.remove()
        await container.mount(self.challenge_screen_class())
