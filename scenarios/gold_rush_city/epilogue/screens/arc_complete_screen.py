import asyncio

from textual import events
from textual.widgets import RichLog

import global_constants
from media import background_music_utility
from scenarios.gold_rush_city.epilogue.dialogues import arc_complete_dialogue
from utils import general_utils


class GoldRushCityArcCompleteScreen(RichLog):
    can_focus = True

    def __init__(self, **kwargs):
        super().__init__(markup=True, highlight=True, **kwargs)

    def on_mount(self) -> None:
        self.focus()
        self.run_worker(
            self.render_arc_complete(global_constants.GLOBAL_DIALOGUE_COLOR)
        )

    async def render_arc_complete(self, color: str) -> None:
        background_music_utility.start_background_music(
            f"{global_constants.MUSIC_MEDIA_PATH}/win_music.ogg"
        )
        progress = general_utils.load_progress()
        player_name = progress.get("player_name") or "Trainer"
        dialogues = arc_complete_dialogue.GOLD_RUSH_CITY_ARC_COMPLETE_DIALOGUES.replace(
            "{user_name}", player_name
        )

        for line in dialogues.split("\n"):
            styled_line = f"[bold {color}]{line}[/]"
            self.write(styled_line + "\n")
            await asyncio.sleep(1.2)

        title = global_constants.ARC_TITLE_GOLD_RUSH_CITY
        self.write(f"\n[bold {color}]TITLE EARNED[/]")
        self.write(f"[bold reverse {color}] {title} [/]")
        self.write(
            f"\n[bold]Meow Coins:[/] {global_constants.meow_coins}\n"
        )

        self.write(
            "\n[bold #D4AF37]The road east leads to Sakura Harbour.[/]"
        )
        self.write(global_constants.PRESS_ENTER_TO_CONTINUE_ACTION_TEXT)

    async def on_key(self, event: events.Key) -> None:
        if event.key == "enter":
            background_music_utility.stop_background_music()
            general_utils.update_progress(
                active_challenge_id="20",
                story_intro_act=global_constants.STORY_ACT_SAKURA_HARBOUR,
                pending_epilogue=None,
            )
            container = self.parent
            await self.remove()
            from scenarios.sakura_harbour.prologue.screens.sakura_harbour_intro_screen import (
                SakuraHarbourIntroScreen,
            )

            await container.mount(SakuraHarbourIntroScreen())
