import os
import subprocess
import time
import pygame
from pygame.examples.scrap_clipboard import screen
from rich.panel import Panel
from rich.text import Text
from textual.app import ComposeResult
from textual.widgets import RichLog, Input, Static, Label
from textual import on, events
from kubernetes import client

# Import your custom dialogues and screens
from challenge_files import challenge_1_text
from dialouges import psyquack_failure_screen_dialogue, psyquack_success_dialogue


class Challenge1(Static):
    can_focus = True

    def compose(self) -> ComposeResult:
        color = "#D4AF37"
        # Initialize Music
        pygame.mixer.init()
        pygame.mixer.music.load("battle_music.mp3")
        pygame.mixer.music.play(loops=0)

        styled_line = f"[bold {color}]So, here is your first challenge young engineer![/]"
        yield Label(styled_line)
        yield Input(placeholder="Ready to move ahead...", id="player-response")
        yield RichLog(markup=True, id="challenge-1")

    def on_mount(self) -> None:
        self.focus()
        self.move_to_next_screen = False
        self.correct_solution = False
        self.proxy_process = None
        self.render_challenge_1()
        self.challenge_id="1"

    def render_challenge_1(self):
        color = "#D4AF37"
        challenge_text = challenge_1_text.CHALLENGE_1_TEXT.split("\n")
        log = self.query_one("#challenge-1")
        text = Text()
        for line in challenge_text:
            text.append(line, style=f"bold {color}")
            text.append("\n\n")

        panel = Panel(text, title="Battle out Challenge 1")
        log.write(panel)


    @on(Input.Submitted)
    async def handle_validation(self, event: Input.Submitted):
        player_response = event.value.lower()
        log = self.query_one("#challenge-1")

        if player_response == "psyquack validate":
            log.write("[yellow]PsyQuack is building a local bridge to the cluster...[/]")
            self.correct_solution=False
            log.write("[yellow]Answer is incorrect")
            self.move_to_next_screen=True
            log.write("\n[reverse] Press Enter to Continue and Proceed to Challenge 1 [/]")


    async def on_key(self, event: events.Key) -> None:
        if event.key == "enter" and self.move_to_next_screen:
            # Stop music
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()

            container = self.parent
            self.remove()
            if self.correct_solution:
                from screens.psy_quack_success_screen import PsyQuackSuccessScreen
                screen=PsyQuackSuccessScreen()
                await container.mount(screen)
                ##self.run_worker(screen.render_psyquack_success_screen(psyquack_success_dialogue.PSYQUACK_SUCCESS_DIALOGUES,"#D4AF37"))
            else:
                from screens.psy_quack_failure_screen import PsyQuackFailureScreen
                screenFailure=PsyQuackFailureScreen(self.challenge_id)
                await container.mount(screenFailure)
                ##self.run_worker(screenFailure.render_psyquack_failure_screen(psyquack_failure_screen_dialogue.PSYQUACK_FAILURE_DIALOGUES,"#D4AF37"))




    def on_unmount(self) -> None:
        """Ensure the bridge is closed if the widget is removed."""
        if self.proxy_process:
            self.proxy_process.terminate()
