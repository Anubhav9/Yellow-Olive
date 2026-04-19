import subprocess

import global_constants
from challenge_files import challenge_constants
from core_logic.challenge_validation import ChallengeValidation
from media import background_music_utility
from rich.panel import Panel
from rich.text import Text
from screen_prompts.screen_challenge_1.screen_prompts import ChallengeScreenPrompts
from textual import events, on
from textual.app import ComposeResult
from textual.widgets import Input, Label, RichLog, Static
from utils import general_utils


class BaseChallengeScreen(Static):
    can_focus = True

    challenge_id = "1"
    challenge_text = ""
    auto_apply_challenge_pod = True

    @property
    def challenge_log_id(self) -> str:
        return f"challenge-{self.challenge_id}"

    def compose(self) -> ComposeResult:
        background_music_utility.start_background_music(
            f"{global_constants.MUSIC_MEDIA_PATH}/battle_music.ogg"
        )
        challenge_screen_prompts = ChallengeScreenPrompts(self.challenge_id)
        yield Label(challenge_screen_prompts.challenge_text())
        yield Label(challenge_screen_prompts.challenge_status_text())
        yield Input(
            placeholder="Type psyquack validate when you are ready...",
            id="player-response",
        )
        yield RichLog(markup=True, id=self.challenge_log_id)

    def on_mount(self) -> None:
        self.focus()
        self.move_to_next_screen = False
        self.correct_solution = False
        self.proxy_process = None
        self.render_challenge_panel()
        if self.auto_apply_challenge_pod:
            self.apply_challenge_pod()

    def render_challenge_panel(self) -> None:
        challenge_screen_prompts = ChallengeScreenPrompts(self.challenge_id)
        challenge_lines = self.challenge_text.split("\n")
        log = self.query_one(f"#{self.challenge_log_id}", RichLog)
        text = Text()
        for line in challenge_lines:
            text.append(line, style=f"bold {global_constants.GLOBAL_DIALOGUE_COLOR}")
            text.append("\n\n")
        panel = Panel(text, title=challenge_screen_prompts.battle_challenge_text())
        log.write(panel)

    def apply_challenge_pod(self) -> None:
        try:
            manifest_path = general_utils.get_lab_challenge_file(self.challenge_id)
            subprocess.Popen(
                [
                    "sh",
                    str(global_constants.PROJECT_ROOT / "scripts" / "generic-script-pods.sh"),
                    str(self.challenge_id),
                    str(manifest_path),
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
                cwd=str(global_constants.PROJECT_ROOT),
            )
        except Exception as error:
            log = self.query_one(f"#{self.challenge_log_id}", RichLog)
            log.write("[red]Failed to start challenge pod script[/red]")
            log.write(str(error))

    @on(Input.Submitted)
    async def handle_validation(self, event: Input.Submitted):
        player_response = (event.value or "").strip().lower()
        log = self.query_one(f"#{self.challenge_log_id}", RichLog)
        if player_response != "psyquack validate":
            general_utils.show_invalid_command(self)
            log.write(general_utils.invalid_command_text("psyquack validate"))
            return

        challenge_screen_prompts = ChallengeScreenPrompts(self.challenge_id)
        challenge_validation = ChallengeValidation(self.challenge_id)
        log.write(challenge_screen_prompts.building_connection_text())

        if self.challenge_id == "1":
            result = challenge_validation.validate_pod_status(
                challenge_constants.CHALLENGE_1_POD_NAME,
                challenge_constants.NAMESPACE_DEFAULT,
            )
            log.write(str(result))
            is_correct = result is True
        else:
            is_correct, validation_message = challenge_validation.validate_challenge(
                self.challenge_id,
                challenge_constants.CHALLENGE_1_POD_NAME,
                challenge_constants.NAMESPACE_DEFAULT,
            )
            log.write(validation_message)

        if is_correct:
            self.correct_solution = True
            log.write(challenge_screen_prompts.correct_answer_text())
            global_constants.meow_coins = global_constants.meow_coins + int(self.challenge_id)
            log.write(challenge_screen_prompts.move_to_next_challenge_text())
        else:
            self.correct_solution = False
            log.write(challenge_screen_prompts.incorrect_answer_text())
            log.write(challenge_screen_prompts.review_failed_attempt_text())
        self.move_to_next_screen = True

    async def on_key(self, event: events.Key) -> None:
        if event.key == "enter" and self.move_to_next_screen:
            background_music_utility.stop_background_music()
            container = self.parent
            self.remove()
            if self.correct_solution:
                from screens.psy_quack_success_screen import PsyQuackSuccessScreen

                screen = PsyQuackSuccessScreen(self.challenge_id)
                await container.mount(screen)
            else:
                from screens.psy_quack_failure_screen import PsyQuackFailureScreen

                failure_screen = PsyQuackFailureScreen(self.challenge_id)
                await container.mount(failure_screen)

    def on_unmount(self) -> None:
        if self.proxy_process:
            self.proxy_process.terminate()
