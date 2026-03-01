from utils import general_utils
from dialouges import psyquack_failure_screen_dialogue
import global_constants
from media import background_music_utility
from screen_prompts.screen_psyquack_failure_screen import screen_prompts
import asyncio
from textual import on
from textual.widgets import Static, RichLog, Input, Label

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
        background_music_utility.start_background_music(f"{global_constants.MUSIC_MEDIA_PATH}/psyquack_voice.mp3")
        dialogues = psyquack_failure_screen_dialogue.PSYQUACK_FAILURE_DIALOGUES
        for line in dialogues.split("\n"):
            log.write(f"[bold {global_constants.GLOBAL_DIALOGUE_COLOR}]{line}[/]\n")
            await asyncio.sleep(1)
        log.write(general_utils.convert_to_ascii(f"{global_constants.IMAGE_MEDIA_PATH}/psyquack.png"))
        prompt.update(screen_prompts.BACK_TO_PREVIOUS_SCREEN)
        inp.focus()

    @on(Input.Submitted, selector="#failure-input")
    async def on_input(self, event: Input.Submitted) -> None:
        command = (event.value or "").strip().lower()
        background_music_utility.stop_background_music()
        if command == "psyquack back":
            ChallengeScreen = general_utils.load_challenge(self.challenge_id)
            container = self.parent
            # remove all children safely
            for child in list(container.children):
                await child.remove()
            await container.mount(ChallengeScreen())
