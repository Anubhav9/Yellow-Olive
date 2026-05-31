from pathlib import Path
import argparse
import asyncio

from textual.app import App,ComposeResult
from textual.widgets import Static, Button, Header
from textual.containers import Horizontal,Vertical
from textual import on
from scenarios.oakwood_meadows.prologue.dialogues import professor_bald_dialogue
from scenarios.oakwood_meadows.prologue.screens.professor_bald_intro import ProfessorBaldIntro
from screens.common.author_info import AuthorInfo
from screens.common.help_screen import HelpScreen
from screens.common.resume_game_screen import ResumeGameScreen
from utils import general_utils


class ProjectOlive(App):
    TITLE = ("Welcome to Professor Bald's Laboratory")
    CSS_PATH = str(Path(__file__).resolve().with_name("app.tcss"))
    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with Vertical(id="menu-option"):
                yield Static("Menu",id="menu-text")
                yield Button("Start Game",id="start-game")
                yield Button("Help",id="help")
                yield Button("About the Author",id="about-the-author")
                yield Button("Quit", id="quit")
            with Vertical(id="game-area"):

                yield Static("Project Yellow Olive - A Pokemon inspired Kubernetes game!",id="default-text")
                yield Vertical(id="game-flow")

    @on(Button.Pressed, "#start-game")
    async def button_press_start_game(self,event=Button.Pressed):
        game_area=self.query_one("#game-flow")
        for child in list(game_area.children):
            await child.remove()
        if general_utils.has_saved_progress():
            await game_area.mount(ResumeGameScreen())
            return
        professor_bald_intro=ProfessorBaldIntro()
        await game_area.mount(professor_bald_intro)
        self.run_worker(professor_bald_intro.render_professor_bald_intro(professor_bald_dialogue.PROFESSOR_BALD_DIALOGUES,"#D4AF37"))

    @on(Button.Pressed, "#help")
    async def button_press_help(self, event=Button.Pressed):
        game_area = self.query_one("#game-flow")
        for child in list(game_area.children):
            await child.remove()
        help_screen = HelpScreen()
        await game_area.mount(help_screen)

    @on(Button.Pressed, "#about-the-author")
    async def button_press_about_the_author(self, event=Button.Pressed):
        game_area = self.query_one("#game-flow")
        for child in list(game_area.children):
            await child.remove()
        author_info = AuthorInfo()
        await game_area.mount(author_info)
        self.run_worker(author_info.details_about_author("#D4AF37"))

    @on(Button.Pressed, "#quit")
    async def button_press_quit(self, event=Button.Pressed):
        self.exit()

    async def on_exit(self) -> None:
        await asyncio.to_thread(general_utils.teardown_core_infra)



def main():
    general_utils.ensure_lab_workspace()
    app = ProjectOlive()
    app.run()


def cli():
    parser = argparse.ArgumentParser(prog="yellow-olive")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("start", help="Start Project Yellow Olive")

    args = parser.parse_args()

    if args.command == "start":
        main()
        return

    parser.print_help()


if __name__ == "__main__":
    main()
