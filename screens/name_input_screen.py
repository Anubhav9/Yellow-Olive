from dialouges import professor_bald_dialogue_name_input_screen
from screens.game_initialisation_and_reference_screen import GameInitialisationScreen
from utils import general_utils
from media import background_music_utility
from screen_prompts.screen_name_input_screen import screen_prompts
import global_constants
import asyncio
from textual.app import App,ComposeResult
from textual.widgets import RichLog, Input, Static,Label
from textual import on
from textual import events


class NameInputScreen(Static):
    can_focus = True
    def compose(self) -> ComposeResult:
        background_music_utility.start_background_music(f"{global_constants.MUSIC_MEDIA_PATH}/screen_2_music.mp3")
        styled_line = screen_prompts.NAME_PROMPT
        yield Label(styled_line)
        yield Input(placeholder="Enter your name...", id="player-name-input")
        yield RichLog(markup=True,id="after-name-selection")

    def on_mount(self) -> None:
        """Automatically grab focus when this widget appears."""
        self.ready_to_continue=False
        self.focus()

    @on(Input.Submitted)
    async def handle_name(self, event: Input.Submitted):
        if self.ready_to_continue==False:
            name = (event.value or "").strip() or "Trainer"
            general_utils.update_progress(
                player_name=name,
                active_challenge_id="1",
            )
            log=self.query_one("#after-name-selection")
            all_dialouges=professor_bald_dialogue_name_input_screen.PROFESSOR_BALD_DIALOGUE_NAME_INPUT_SCREEN
            all_dialouges=all_dialouges.split("\n")
            all_dialouges[0]=all_dialouges[0].replace("{user_name}",name)
            for i in range(0,len(all_dialouges)):
                styled_line = f"[bold {global_constants.GLOBAL_DIALOGUE_COLOR}]{all_dialouges[i]}[/]"
                log.write(styled_line+"\n")
                await asyncio.sleep(1.5)
            output_ascii = general_utils.convert_to_ascii(f"{global_constants.IMAGE_MEDIA_PATH}/electromon.png")
            log.write(output_ascii)
            self.ready_to_continue=True
            log.write(global_constants.PRESS_ENTER_TO_CONTINUE_ACTION_TEXT)

        # Here you would trigger the next part of the game

    async def on_key(self, event: events.Key) -> None:
        if event.key == "enter" and self.ready_to_continue==True:
            # Clear the log and move to the next game state
            background_music_utility.stop_background_music()
            container = self.parent
            # 2. Remove this log widget
            self.remove()
            # 3. Mount the new input screen to that same container
            await container.mount(GameInitialisationScreen())
