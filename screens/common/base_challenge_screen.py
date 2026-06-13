import importlib

import global_constants
from media import background_music_utility
from rich.panel import Panel
from rich.text import Text
from screens.common.screen_prompts.challenge_screen import ChallengeScreenPrompts
from services import resource_manager
from textual import events, on
from textual.app import ComposeResult
from textual.widgets import Input, Label, RichLog, Static
from utils import general_utils


class BaseChallengeScreen(Static):
    can_focus = True

    challenge_id = "1"
    challenge_text = ""

    @property
    def challenge_log_id(self) -> str:
        return f"challenge-{self.challenge_id}"

    def compose(self) -> ComposeResult:
        if general_utils.load_progress().get("challenge_background_music") is True:
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
        general_utils.update_progress(
            active_challenge_id=self.challenge_id,
        )
        global_constants.meow_coins = general_utils.calculate_meow_coins(self.challenge_id)
        self.render_challenge_panel()
        self.create_resources_for_challenge()

    def apply_challenge_manifests(self, *challenge_ids: str) -> None:
        scenario = getattr(self, "challenge_scenario", None)
        if not scenario:
            raise NotImplementedError(
                f"Challenge {self.challenge_id} screen must set `challenge_scenario`."
            )

        log = self.query_one(f"#{self.challenge_log_id}", RichLog)
        try:
            for challenge_id in challenge_ids:
                warnings = resource_manager.apply_manifest(scenario, challenge_id)
                if warnings:
                    log.write("")
                    log.write(
                        "[yellow]Some lab manifests could not be applied yet.[/]"
                    )
                    log.write(
                        "[yellow]Edit them in yellow-olive-lab, then apply[/]"
                    )
                    log.write("[yellow]from your Command Chamber.[/]")
                    for warning in warnings:
                        for line in resource_manager.format_manifest_warning_lines(
                            warning
                        ):
                            log.write(f"[yellow]{line}[/]")
        except Exception as error:
            log.write("[red]Failed to apply challenge resources.[/red]")
            log.write("")
            for line in str(error).splitlines():
                log.write(f"[red]{line}[/red]")

    def create_resources_for_challenge(self) -> None:
        """Apply the kubernetes resources required for this challenge."""
        self.apply_challenge_manifests(self.challenge_id)

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

    @on(Input.Submitted)
    async def handle_validation(self, event: Input.Submitted):
        player_response = (event.value or "").strip().lower()
        log = self.query_one(f"#{self.challenge_log_id}", RichLog)
        if player_response != "psyquack validate":
            general_utils.show_invalid_command(self)
            log.write(general_utils.invalid_command_text("psyquack validate"))
            return

        challenge_screen_prompts = ChallengeScreenPrompts(self.challenge_id)
        log.write(challenge_screen_prompts.building_connection_text())

        is_correct, validation_message = self.run_validation()
        log.write(validation_message)

        if is_correct:
            self.correct_solution = True
            log.write(challenge_screen_prompts.correct_answer_text())
            next_challenge_id = general_utils.get_next_challenge_id(self.challenge_id)
            progress_challenge_id = next_challenge_id or str(int(self.challenge_id) + 1)
            if self.challenge_id == "7":
                general_utils.update_progress(
                    active_challenge_id=progress_challenge_id,
                    story_intro_act=global_constants.STORY_ACT_SIGNAL_TOWN,
                )
                global_constants.meow_coins = general_utils.calculate_meow_coins(
                    progress_challenge_id
                )
                log.write("\n[reverse] Press Enter to journey to Signal Town [/]")
            else:
                general_utils.update_progress(
                    active_challenge_id=progress_challenge_id,
                )
                global_constants.meow_coins = general_utils.calculate_meow_coins(
                    progress_challenge_id
                )
                log.write(challenge_screen_prompts.move_to_next_challenge_text())
        else:
            self.correct_solution = False
            log.write(challenge_screen_prompts.incorrect_answer_text())
            log.write(challenge_screen_prompts.review_failed_attempt_text())
        self.move_to_next_screen = True

    def run_validation(self):
        """Dispatch validation to the scenario's validator.

        Each scenario challenge exposes ``scenarios.<scenario>.challenge_<id>.validator.validate()``
        returning ``(is_correct: bool, message: str)``. This method just looks
        it up and calls it."""
        scenario = getattr(self, "challenge_scenario", None)
        if not scenario:
            raise RuntimeError(
                f"Challenge {self.challenge_id} screen is missing `challenge_scenario`."
            )

        validator_module = importlib.import_module(
            f"scenarios.{scenario}.challenge_{self.challenge_id}.validator"
        )
        return validator_module.validate()

    async def on_key(self, event: events.Key) -> None:
        if event.key == "enter" and self.move_to_next_screen:
            background_music_utility.stop_background_music()
            container = self.parent
            self.remove()
            if self.correct_solution:
                from screens.common.psy_quack_success_screen import PsyQuackSuccessScreen

                screen = PsyQuackSuccessScreen(self.challenge_id)
                await container.mount(screen)
            else:
                from screens.common.psy_quack_failure_screen import PsyQuackFailureScreen

                failure_screen = PsyQuackFailureScreen(self.challenge_id)
                await container.mount(failure_screen)

    def on_unmount(self) -> None:
        if self.proxy_process:
            self.proxy_process.terminate()
