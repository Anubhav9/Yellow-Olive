import asyncio

from screens.dialouges import game_reference_dialogue
from screens.common.challenge_music_preference_screen import ChallengeMusicPreferenceScreen
from media import background_music_utility
import global_constants
from screens.common.screen_prompts import game_initialisation as screen_prompts
from rich.panel import Panel
from services import resource_manager
from textual.app import ComposeResult
from textual.widgets import RichLog, Input, Static, Label
from rich.text import Text
from textual import on
from textual import events
from utils import general_utils
class GameInitialisationScreen(Static):
    can_focus = True
    def compose(self) -> ComposeResult:
        background_music_utility.start_background_music(f"{global_constants.MUSIC_MEDIA_PATH}/battle_music_2.mp3")
        styled_line = screen_prompts.READY_PROMPT
        yield Label(styled_line)
        yield Input(placeholder="Type yes to begin your mission...", id="player-response")
        yield RichLog(markup=True,id="game-reference")

    def on_mount(self) -> None:
        """Automatically grab focus when this widget appears."""
        self.focus()
        self.move_to_next_screen=False

    @on(Input.Submitted)
    async def handle_name(self, event: Input.Submitted):
        player_response = (event.value or "").strip().lower()
        log=self.query_one("#game-reference")
        if player_response == "yes":
            player_input = self.query_one("#player-response", Input)
            player_input.disabled = True
            log.write(screen_prompts.CLUSTER_BOOTSTRAP_MESSAGE)

            try:
                await self._bootstrap_oakwood_meadows_infra()
            except Exception:
                general_utils.notify_cluster_startup_failure(self)
                log.write(f"[red]{general_utils.CLUSTER_STARTUP_FAILURE_MESSAGE}[/]")
                player_input.disabled = False
                return

            text = Text()
            all_dialouges = game_reference_dialogue.GAME_REFERENCE_DIALOGUE.split("\n")
            for i in range(0, len(all_dialouges)):
                line = all_dialouges[i]

                if i % 2 == 0:
                    text.append(line, style=f"bold {global_constants.GLOBAL_DIALOGUE_COLOR}")
                    text.append("\n")
                    text.append("\n")
                else:
                    text.append(line, style=f"bold {global_constants.GLOBAL_DIALOGUE_COLOR}")
                    text.append("\n")
            panel = Panel(text, title=screen_prompts.TITLE_PROFESSOR_BALD_ADVICE)
            log.write("\n")
            log.write(panel)
            advice_line = screen_prompts.ACTION_OPEN_SEPARATE_TERMINAL
            log.write("\n")
            log.write(advice_line)
            self.move_to_next_screen = True
            log.write(screen_prompts.PROCEED_TO_CHALLENGE_1)
            self.focus()
            return
        general_utils.show_invalid_command(self)
        log.write(general_utils.invalid_command_text("yes"))

    async def on_key(self, event: events.Key) -> None:
        if event.key == "enter" and self.move_to_next_screen == True:
            background_music_utility.stop_background_music()
            container = self.parent
            await self.remove()
            challenge_one = general_utils.load_challenge("1")
            if general_utils.needs_challenge_music_preference(
                general_utils.load_progress()
            ):
                await container.mount(ChallengeMusicPreferenceScreen(challenge_one))
            else:
                await container.mount(challenge_one())

    async def _bootstrap_oakwood_meadows_infra(self) -> None:
        """Start the lab cluster, then apply the oakwood-meadows prologue resources.

        Mirrors the prior fire-and-forget ``start_core_infra()`` call but
        chains the namespace apply onto it, so the namespace is created as
        soon as the cluster is ready. Runs in a Textual worker so the UI keeps
        rendering the game reference text while this happens."""
        await asyncio.to_thread(general_utils.start_core_infra, True)
        await asyncio.to_thread(
            resource_manager.apply_prologue_resources, "oakwood_meadows"
        )
