import asyncio
from pathlib import Path

from textual import events
from textual.widgets import RichLog

import global_constants
from media import background_music_utility
from scenarios.gold_rush_city.prologue.dialogues import gold_rush_city_intro_dialogue
from services import resource_manager
from utils import general_utils


class GoldRushCityIntroScreen(RichLog):
    can_focus = True

    def __init__(self, **kwargs):
        super().__init__(markup=True, highlight=True, **kwargs)

    def on_mount(self) -> None:
        self.focus()
        self.run_worker(self._bootstrap_gold_rush_city_infra(), exclusive=False)
        self.run_worker(
            self.render_gold_rush_city_intro(global_constants.GLOBAL_DIALOGUE_COLOR)
        )

    async def _bootstrap_gold_rush_city_infra(self) -> None:
        """Apply gold-rush-city's prologue resources when entering the arc."""
        await asyncio.to_thread(
            resource_manager.apply_prologue_resources, "gold_rush_city"
        )

    async def render_gold_rush_city_intro(self, color: str) -> None:
        background_music_utility.start_background_music(
            f"{global_constants.MUSIC_MEDIA_PATH}/gold_rush_city_intro_music.ogg"
        )
        progress = general_utils.load_progress()
        player_name = progress.get("player_name") or "Trainer"
        dialogues = gold_rush_city_intro_dialogue.GOLD_RUSH_CITY_INTRO_DIALOGUES.replace(
            "{user_name}", player_name
        )

        for line in dialogues.split("\n"):
            styled_line = f"[bold {color}]{line}[/]"
            self.write(styled_line + "\n")
            await asyncio.sleep(1.2)

        image_path = Path(global_constants.IMAGE_MEDIA_PATH) / "mayor.png"
        if image_path.exists():
            self.write(general_utils.convert_to_ascii(str(image_path)))

        self.write(global_constants.PRESS_ENTER_TO_CONTINUE_ACTION_TEXT)

    async def on_key(self, event: events.Key) -> None:
        if event.key == "enter":
            background_music_utility.stop_background_music()
            general_utils.update_progress(
                story_intro_act=global_constants.STORY_ACT_GOLD_RUSH_VAULT,
            )
            container = self.parent
            await self.remove()
            from scenarios.gold_rush_city.prologue.screens.mayor_vault_intro_screen import (
                MayorVaultIntroScreen,
            )

            await container.mount(MayorVaultIntroScreen())
