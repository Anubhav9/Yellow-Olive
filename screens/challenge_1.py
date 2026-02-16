from rich.panel import Panel
from textual.app import App,ComposeResult
from textual.widgets import RichLog, Input, Static,Label
from rich.text import Text
from textual import on
from textual import events
from dialouges import game_reference_dialogue
import pygame
import subprocess
import os
from challenge_files import challenge_1_text


class Challenge1(Static):
    can_focus = True
    def compose(self) -> ComposeResult:
        color="#D4AF37"
        pygame.mixer.init()
        pygame.mixer.music.load("battle_music.mp3")
        pygame.mixer.music.play(loops=0)
        styled_line = f"[bold {color}]So, here is your first challenge young engineer![/]"
        yield Label(styled_line)
        yield RichLog(markup=True,id="challenge-1")

    def on_mount(self) -> None:
        """Automatically grab focus when this widget appears."""
        self.focus()
        self.move_to_next_screen=False
        self.render_challenge_1()

    def render_challenge_1(self):
        color = "#D4AF37"
        challenge_text=challenge_1_text.CHALLENGE_1_TEXT.split("\n")
        log = self.query_one("#challenge-1")
        text=Text()
        for i in range(0,len(challenge_text)):
            line=challenge_text[i]
            text.append(line,style=f"bold {color}")
            text.append("\n")
            text.append("\n")

        panel=Panel(text,title="Battle out Challenge 1")
        log.write(panel)
