from utils import general_utils
from dialouges import psyquack_success_dialogue
from media import background_music_utility
import global_constants
import asyncio
from textual.widgets import RichLog,Input
from textual import events


class PsyQuackSuccessScreen(RichLog):
    can_focus = True

    def __init__(self,meow_coins, **kwargs):
        # We pass markup=True here so you don't have to remember it later
        super().__init__(markup=True, highlight=True, **kwargs)
        self.meow_coins=meow_coins

    def on_mount(self) -> None:
        """Automatically grab focus when this widget appears."""
        self.focus()
        self.run_worker(self.render_psyquack_success_screen(psyquack_success_dialogue.PSYQUACK_SUCCESS_DIALOGUES,"#D4AF37"))

    async def render_psyquack_success_screen(self, dialogues, color):
        background_music_utility.start_background_music(f"{global_constants.MUSIC_MEDIA_PATH}/psyquack_happy_song.mp3")
        all_lines = dialogues.split("\n")
        for line in all_lines:
            styled_line = f"[bold {color}]{line}[/]"
            self.write(styled_line+"\n")
            # RichLog adds newlines automatically with .write()
            await asyncio.sleep(1)

        output_ascii=general_utils.convert_to_ascii(f"{global_constants.IMAGE_MEDIA_PATH}/psyquack_happy.png")
        self.write(output_ascii)
        self.write(f"Congratulations! You have also earned {self.meow_coins} Meow Meow Coins. Meow Boi is also happy:)")
        self.write(global_constants.PRESS_ENTER_TO_CONTINUE_ACTION_TEXT)

    async def on_key(self, event: events.Key) -> None:
        if event.key == "enter":
            # Clear the log and move to the next game state
            background_music_utility.stop_background_music()
            container = self.parent
            # 2. Remove this log widget
            self.remove()
            # 3. Mount the new input screen to that same container
