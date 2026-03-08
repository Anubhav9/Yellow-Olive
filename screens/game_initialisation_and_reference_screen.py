from dialouges import game_reference_dialogue
from screens.challenge_1 import Challenge1
from media import background_music_utility
import global_constants
from screen_prompts.screen_game_initialisation_and_reference import screen_prompts
import subprocess
import os
from rich.panel import Panel
from textual.app import App,ComposeResult
from textual.widgets import RichLog, Input, Static,Label
from rich.text import Text
from textual import on
from textual import events
class GameInitialisationScreen(Static):
    can_focus = True
    def compose(self) -> ComposeResult:
        background_music_utility.start_background_music(f"{global_constants.MUSIC_MEDIA_PATH}/game_initialise_music.mp3")
        styled_line = screen_prompts.READY_PROMPT
        yield Label(styled_line)
        yield Input(placeholder="Enter your response...", id="player-response")
        yield RichLog(markup=True,id="game-reference")

    def on_mount(self) -> None:
        """Automatically grab focus when this widget appears."""
        self.focus()
        self.move_to_next_screen=False

    @on(Input.Submitted)
    async def handle_name(self, event: Input.Submitted):
        player_response = event.value
        player_response=player_response.lower()
        if(player_response=="yes"):
            current_working_directory = os.getcwd()
            subprocess.Popen(
                ["sh", f"{current_working_directory}/script.sh"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            log=self.query_one("#game-reference")
            text = Text()
            all_dialouges=game_reference_dialogue.GAME_REFERENCE_DIALOGUE.split("\n")
            for i in range(0,len(all_dialouges)):
                line=all_dialouges[i]

                if(i%2==0):
                    text.append(line,style=f"bold {global_constants.GLOBAL_DIALOGUE_COLOR}")
                    text.append("\n")
                    text.append("\n")
                else:
                    text.append(line,style=f"bold {global_constants.GLOBAL_DIALOGUE_COLOR}")
                    text.append("\n")
            panel=Panel(text,title=screen_prompts.TITLE_PROFESSOR_BALD_ADVICE)
            log.write("\n")
            log.write(panel)
            advice_line=screen_prompts.ACTION_OPEN_SEPARATE_TERMINAL
            log.write("\n")
            log.write(advice_line)
            self.move_to_next_screen=True
            log.write(screen_prompts.PROCEED_TO_CHALLENGE_1)

    async def on_key(self, event: events.Key) -> None:
        if event.key == "enter" and self.move_to_next_screen == True:
            # Clear the log and move to the next game state
            background_music_utility.stop_background_music()
            container = self.parent
            self.remove()
            await container.mount(Challenge1())
