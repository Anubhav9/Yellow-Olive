import asyncio
from pathlib import Path

from textual import events
from textual.widgets import RichLog

import global_constants
from scenarios.signal_town.prologue.dialogues import team_evil_intro_dialogue
from media import background_music_utility
from utils import general_utils


class TeamEvilIntroScreen(RichLog):
    can_focus = True

    def __init__(self, **kwargs):
        super().__init__(markup=True, highlight=True, **kwargs)

    def on_mount(self) -> None:
        self.focus()
        self.run_worker(
            self.render_team_evil_intro(global_constants.GLOBAL_DIALOGUE_COLOR)
        )

    async def render_team_evil_intro(self, color: str) -> None:
        background_music_utility.start_background_music(
            f"{global_constants.MUSIC_MEDIA_PATH}/team_evil_intro_music.mp3"
        )
        progress = general_utils.load_progress()
        player_name = progress.get("player_name") or "Trainer"
        dialogues = team_evil_intro_dialogue.TEAM_EVIL_INTRO_DIALOGUES.replace(
            "{user_name}", player_name
        )

        for line in dialogues.split("\n"):
            styled_line = f"[bold {color}]{line}[/]"
            self.write(styled_line + "\n")
            await asyncio.sleep(1.2)

        image_path = Path(global_constants.IMAGE_MEDIA_PATH) / "team_evil.png"
        if image_path.exists():
            self.write(general_utils.convert_to_ascii(str(image_path)))

        self.write(global_constants.PRESS_ENTER_TO_CONTINUE_ACTION_TEXT)

    async def on_key(self, event: events.Key) -> None:
        if event.key == "enter":
            background_music_utility.stop_background_music()
            general_utils.update_progress(
                story_intro_act=global_constants.STORY_ACT_DONE,
            )
            container = self.parent
            await self.remove()
            challenge_8 = general_utils.load_challenge("8")
            await container.mount(challenge_8())
