import asyncio
import pygame
from textual import on
from textual.widgets import Static, RichLog, Input, Label

from utils import general_utils
from dialouges import psyquack_failure_screen_dialogue


class PsyQuackFailureScreen(Static):
    can_focus = True
    def __init__(self,challenge_id,**kwargs):
        super().__init__(**kwargs)
        self.challenge_id=challenge_id
    def compose(self):
        yield RichLog(markup=True, highlight=True, id="failure-log")
        yield Label("", id="failure-prompt")
        yield Input(placeholder="Say something...", id="failure-input")

    def on_mount(self) -> None:
        self.focus()
        self.run_worker(self.render_failure_dialogue(), exclusive=True)

    async def render_failure_dialogue(self):
        log = self.query_one("#failure-log", RichLog)
        prompt = self.query_one("#failure-prompt", Label)
        inp = self.query_one("#failure-input", Input)

        pygame.mixer.init()
        pygame.mixer.music.load("psyquack_voice.mp3")
        pygame.mixer.music.play(loops=0)

        color = "#D4AF37"
        dialogues = psyquack_failure_screen_dialogue.PSYQUACK_FAILURE_DIALOGUES

        for line in dialogues.split("\n"):
            log.write(f"[bold {color}]{line}[/]\n")
            await asyncio.sleep(1)

        log.write(general_utils.convert_to_ascii("psyquack.png"))

        prompt.update(f"[bold {color}]Young Engineer, what would you like to do next?[/]")
        inp.focus()

    @on(Input.Submitted, selector="#failure-input")
    async def on_input(self, event: Input.Submitted) -> None:
        command = (event.value or "").strip().lower()

        pygame.mixer.music.stop()
        pygame.mixer.music.unload()

        if command == "psyquack back":
            ChallengeScreen = general_utils.load_challenge(self.challenge_id)
            container = self.parent
            # remove all children safely
            for child in list(container.children):
                await child.remove()

            await container.mount(ChallengeScreen())
