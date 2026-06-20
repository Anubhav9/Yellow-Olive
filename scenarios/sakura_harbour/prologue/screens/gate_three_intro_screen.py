import asyncio

from textual import events
from textual.widgets import RichLog

import global_constants
from media import background_music_utility
from scenarios.sakura_harbour.prologue.dialogues import gate_three_intro_dialogue
from utils import general_utils


class GateThreeIntroScreen(RichLog):
    can_focus = True

    def __init__(self, **kwargs):
        super().__init__(markup=True, highlight=True, **kwargs)

    def on_mount(self) -> None:
        self.focus()
        self.run_worker(
            self.render_gate_three_intro(global_constants.GLOBAL_DIALOGUE_COLOR)
        )

    async def render_gate_three_intro(self, color: str) -> None:
        background_music_utility.start_background_music(
            f"{global_constants.MUSIC_MEDIA_PATH}/sakura_harbour_prologue_end.ogg"
        )
        dialogues = gate_three_intro_dialogue.GATE_THREE_INTRO_DIALOGUES

        for line in dialogues.split("\n"):
            styled_line = f"[bold {color}]{line}[/]"
            self.write(styled_line + "\n")
            await asyncio.sleep(1.2)

        self.write(global_constants.PRESS_ENTER_TO_CONTINUE_ACTION_TEXT)

    async def on_key(self, event: events.Key) -> None:
        if event.key == "enter":
            background_music_utility.stop_background_music()
            general_utils.update_progress(
                active_challenge_id="20",
                story_intro_act=global_constants.STORY_ACT_DONE,
            )
            container = self.parent
            await self.remove()
            challenge_20 = general_utils.load_challenge("20")
            await container.mount(challenge_20())
