from scenarios.oakwood_meadows.prologue.screens.name_input_screen import NameInputScreen
from utils import general_utils
from media import background_music_utility
import global_constants
import asyncio
from textual.widgets import RichLog,Input
from textual import events

class ProfessorBaldIntro(RichLog):
    can_focus = True

    def __init__(self, **kwargs):
        # We pass markup=True here so you don't have to remember it later
        super().__init__(markup=True, highlight=True, **kwargs)

    def on_mount(self) -> None:
        """Automatically grab focus when this widget appears."""
        self.focus()

    async def render_professor_bald_intro(self, dialogues, color):
        background_music_utility.start_background_music(f"{global_constants.MUSIC_MEDIA_PATH}/screen_1_opening_song.mp3")
        all_lines = dialogues.split("\n")
        for line in all_lines:
            styled_line = f"[bold {color}]{line}[/]"
            self.write(styled_line+"\n")  # RichLog adds newlines automatically with .write()
            await asyncio.sleep(1.5)
        output_ascii = general_utils.convert_to_ascii(f"{global_constants.IMAGE_MEDIA_PATH}/Professor Bald.png")
        self.write(output_ascii)
        self.write(f"{global_constants.PRESS_ENTER_TO_CONTINUE_ACTION_TEXT}")

    async def on_key(self, event: events.Key) -> None:
        if event.key == "enter":
            # Clear the log and move to the next game state
            background_music_utility.stop_background_music()
            container = self.parent
            # 2. Remove this log widget
            self.remove()
            # 3. Mount the new input screen to that same container
            await container.mount(NameInputScreen())

