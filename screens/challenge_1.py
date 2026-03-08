from challenge_files import challenge_1_text
import global_constants
from core_logic.challenge_validation import ChallengeValidation
from global_constants import meow_coins
from media import background_music_utility
from screen_prompts.screen_challenge_1.screen_prompts import ChallengeScreenPrompts
from challenge_files import challenge_constants
from rich.panel import Panel
from rich.text import Text
from textual.app import ComposeResult
from textual.widgets import RichLog, Input, Static, Label
from textual import on, events
import global_constants
challenge_id="1"


challenge_screen_prompts=ChallengeScreenPrompts(challenge_id)

class Challenge1(Static):
    can_focus = True

    def compose(self) -> ComposeResult:
        # Initialize Music
        background_music_utility.start_background_music(f"{global_constants.MUSIC_MEDIA_PATH}/battle_music.mp3")
        styled_line = challenge_screen_prompts.challenge_text()
        yield Label(styled_line)
        yield Input(placeholder="Ready to move ahead...", id="player-response")
        yield RichLog(markup=True, id="challenge-1")

    def on_mount(self) -> None:
        self.focus()
        self.move_to_next_screen = False
        self.correct_solution = False
        self.proxy_process = None
        self.render_challenge_1()
        self.challenge_id=challenge_id

    def render_challenge_1(self):
        challenge_text = challenge_1_text.CHALLENGE_1_TEXT.split("\n")
        log = self.query_one("#challenge-1")
        text = Text()
        for line in challenge_text:
            text.append(line, style=f"bold {global_constants.GLOBAL_DIALOGUE_COLOR}")
            text.append("\n\n")
        panel = Panel(text, title=challenge_screen_prompts.battle_challenge_text())
        log.write(panel)


    @on(Input.Submitted)
    async def handle_validation(self, event: Input.Submitted):
        player_response = event.value.lower()
        log = self.query_one("#challenge-1")

        if player_response == "psyquack validate":
            challenge_validation=ChallengeValidation(self.challenge_id)
            log.write(challenge_screen_prompts.building_connection_text())
            result_challenge=challenge_validation.validate_pod_status(challenge_constants.CHALLENGE_1_POD_NAME,challenge_constants.NAMESPACE_DEFAULT)
            log.write(result_challenge)
            if(result_challenge):
                self.correct_solution=True
                log.write(challenge_screen_prompts.correct_answer_text())
                global_constants.meow_coins=global_constants.meow_coins+int(challenge_id)
            else:
                self.correct_solution=False
                log.write(challenge_screen_prompts.incorrect_answer_text())
            log.write(challenge_screen_prompts.move_to_next_challenge_text())
            self.move_to_next_screen=True

    async def on_key(self, event: events.Key) -> None:
        if event.key == "enter" and self.move_to_next_screen:
            # Stop music
            background_music_utility.stop_background_music()
            container = self.parent
            self.remove()
            if self.correct_solution:
                from screens.psy_quack_success_screen import PsyQuackSuccessScreen
                screen=PsyQuackSuccessScreen()
                await container.mount(screen)
            else:
                from screens.psy_quack_failure_screen import PsyQuackFailureScreen
                screenFailure=PsyQuackFailureScreen(self.challenge_id)
                await container.mount(screenFailure)




    def on_unmount(self) -> None:
        """Ensure the bridge is closed if the widget is removed."""
        if self.proxy_process:
            self.proxy_process.terminate()
