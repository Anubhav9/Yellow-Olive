import asyncio

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

from screens.challenge_1 import Challenge1


class GameInitialisationScreen(Static):
    can_focus = True
    def compose(self) -> ComposeResult:
        color="#D4AF37"
        pygame.mixer.init()
        pygame.mixer.music.load("game_initialise_music.mp3")
        pygame.mixer.music.play(loops=0)
        styled_line = f"[bold {color}]So, young engineer, are you ready to battle it out and step\n into the world of Yellow Olive?[/]"
        yield Label(styled_line)
        yield Input(placeholder="Enter your response...", id="player-response")
        yield RichLog(markup=True,id="game-reference")

    def on_mount(self) -> None:
        """Automatically grab focus when this widget appears."""
        self.focus()
        self.move_to_next_screen=False

    @on(Input.Submitted)
    async def handle_name(self, event: Input.Submitted):
        player_response = event.value
        player_response=player_response.lower()
        color = "#D4AF37"
        if(player_response=="yes"):
            current_working_directory = os.getcwd()
            subprocess.Popen(
                ["sh", f"{current_working_directory}/script.sh"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            log=self.query_one("#game-reference")
            text = Text()
            all_dialouges=game_reference_dialogue.GAME_REFERENCE_DIALOGUE.split("\n")
            styled_lines=[]
            for i in range(0,len(all_dialouges)):
                line=all_dialouges[i]

                if(i%2==0):
                    text.append(line,style=f"bold {color}")
                    text.append("\n")
                    text.append("\n")
                else:
                    text.append(line,style=f"bold {color}")
                    text.append("\n")
            panel=Panel(text,title="Professor Bald's Advice")
            log.write("\n")
            log.write(panel)
            advice_line=f"[bold red]Open a separate Command Chamber (terminal tab) to speak to the cluster using kubectl.[/]"
            log.write("\n")
            log.write(advice_line)
            self.move_to_next_screen=True
            log.write("\n[reverse] Press Enter to Continue and Proceed to Challenge 1 [/]")

    async def on_key(self, event: events.Key) -> None:
        if event.key == "enter" and self.move_to_next_screen == True:
            # Clear the log and move to the next game state
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            container = self.parent

            # 2. Remove this log widget
            self.remove()

            # 3. Mount the new input screen to that same container

            await container.mount(Challenge1())
        # Here you would trigger the next part of the game
