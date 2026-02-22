import asyncio
from textual.widgets import RichLog,Input
from textual import events

from utils import general_utils
import pygame
from dialouges import psyquack_success_dialogue


class PsyQuackSuccessScreen(RichLog):
    can_focus = True

    def __init__(self, **kwargs):
        # We pass markup=True here so you don't have to remember it later
        super().__init__(markup=True, highlight=True, **kwargs)

    def on_mount(self) -> None:
        """Automatically grab focus when this widget appears."""
        self.focus()
        self.run_worker(self.render_psyquack_success_screen(psyquack_success_dialogue.PSYQUACK_SUCCESS_DIALOGUES,"#D4AF37"))

    async def render_psyquack_success_screen(self, dialogues, color):
        pygame.mixer.init()
        pygame.mixer.music.load("psyquack_happy_song.mp3")
        pygame.mixer.music.play(loops=0)
        all_lines = dialogues.split("\n")
        for line in all_lines:
            styled_line = f"[bold {color}]{line}[/]"
            self.write(styled_line+"\n")
            # RichLog adds newlines automatically with .write()
            await asyncio.sleep(1)

        output_ascii=general_utils.convert_to_ascii("psyquack_happy.png")
        self.write(output_ascii)
        self.write("\n[reverse] Press Enter to Continue [/]")

    async def on_key(self, event: events.Key) -> None:
        if event.key == "enter":
            # Clear the log and move to the next game state
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            container = self.parent

            # 2. Remove this log widget
            self.remove()

            # 3. Mount the new input screen to that same container

