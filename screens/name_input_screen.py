import asyncio

from textual.app import App,ComposeResult
from textual.widgets import RichLog, Input, Static,Label
from textual import on
from textual import events
from dialouges import professor_bald_dialogue_name_input_screen
import pygame

from screens.game_initialisation_and_reference_screen import GameInitialisationScreen
from utils import general_utils

class NameInputScreen(Static):
    can_focus = True
    def compose(self) -> ComposeResult:
        color="#D4AF37"
        pygame.mixer.init()
        pygame.mixer.music.load("screen_2_music.mp3")
        pygame.mixer.music.play(loops=0)
        styled_line = f"[bold {color}]Before we begin, what is your name, young engineer?[/]"
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
            name = event.value
            log=self.query_one("#after-name-selection")
            all_dialouges=professor_bald_dialogue_name_input_screen.PROFESSOR_BALD_DIALOGUE_NAME_INPUT_SCREEN
            all_dialouges=all_dialouges.split("\n")
            all_dialouges[0]=all_dialouges[0].replace("{user_name}",name)
            color="#D4AF37"
            for i in range(0,len(all_dialouges)):
                styled_line = f"[bold {color}]{all_dialouges[i]}[/]"
                log.write(styled_line+"\n")
                await asyncio.sleep(1.5)
            output_ascii=general_utils.convert_to_ascii("electromon.png")
            log.write(output_ascii)
            self.ready_to_continue=True
            log.write("\n[reverse] Press Enter to Continue [/]")

        # Here you would trigger the next part of the game

    async def on_key(self, event: events.Key) -> None:
        if event.key == "enter" and self.ready_to_continue==True:
            # Clear the log and move to the next game state
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            container = self.parent

            # 2. Remove this log widget
            self.remove()

            # 3. Mount the new input screen to that same container

            await container.mount(GameInitialisationScreen())
