import asyncio

from textual import events
from textual.widgets import RichLog

import global_constants
from media import background_music_utility
from scenarios.yumoto_springs.prologue.dialogues import yumoto_springs_intro_dialogue
from services import resource_manager
from utils import general_utils


class YumotoSpringsIntroScreen(RichLog):
    can_focus = True

    def __init__(self, **kwargs):
        super().__init__(markup=True, highlight=True, **kwargs)

    def on_mount(self) -> None:
        self.focus()
        self.run_worker(self._bootstrap_yumoto_springs_infra(), exclusive=False)
        self.run_worker(
            self.render_yumoto_springs_intro(global_constants.GLOBAL_DIALOGUE_COLOR)
        )

    async def _bootstrap_yumoto_springs_infra(self) -> None:
        await asyncio.to_thread(
            resource_manager.apply_prologue_resources, "yumoto_springs"
        )

    async def render_yumoto_springs_intro(self, color: str) -> None:
        background_music_utility.start_background_music(
            f"{global_constants.MUSIC_MEDIA_PATH}/yumoto_springs_intro.mp3"
        )
        progress = general_utils.load_progress()
        player_name = progress.get("player_name") or "Trainer"
        dialogues = yumoto_springs_intro_dialogue.YUMOTO_SPRINGS_INTRO_DIALOGUES.replace(
            "{user_name}", player_name
        )

        for line in dialogues.split("\n"):
            styled_line = f"[bold {color}]{line}[/]"
            self.write(styled_line + "\n")
            await asyncio.sleep(1.2)

        self.write(global_constants.PRESS_ENTER_TO_CONTINUE_ACTION_TEXT)

    async def on_key(self, event: events.Key) -> None:
        if event.key == "enter":
            background_music_utility.stop_background_music()
            general_utils.update_progress(
                story_intro_act=global_constants.STORY_ACT_YUMOTO_KEEPER,
            )
            container = self.parent
            await self.remove()
            from scenarios.yumoto_springs.prologue.screens.keeper_intro_screen import (
                KeeperIntroScreen,
            )

            await container.mount(KeeperIntroScreen())
