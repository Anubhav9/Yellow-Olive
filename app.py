from textual.app import App,ComposeResult
from textual.widgets import Static, Button, Header,RichLog
from textual.containers import Horizontal,Vertical
from textual import on
from screens import professor_bald_intro
from dialouges import professor_bald_dialogue
from screens.author_info import AuthorInfo
from screens.professor_bald_intro import ProfessorBaldIntro


class ProjectOlive(App):
    TITLE = ("Welcome to Professor Bald's Laboratory")
    CSS_PATH = "app.tcss"
    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with Vertical(id="menu-option"):
                yield Static("Menu",id="menu-text")
                yield Button("Start Game",id="start-game")
                yield Button("Help",id="help")
                yield Button("About the Author",id="about-the-author")
                yield Button("Quit")
            with Vertical(id="game-area"):

                yield Static("Project Yellow Olive - A Pokemon inspired Kubernetes game!",id="default-text")
                yield Vertical(id="game-flow")

    @on(Button.Pressed, "#start-game")
    async def button_press_start_game(self,event=Button.Pressed):
        game_area=self.query_one("#game-flow")
        professor_bald_intro=ProfessorBaldIntro()
        await game_area.mount(professor_bald_intro)
        self.run_worker(professor_bald_intro.render_professor_bald_intro(professor_bald_dialogue.PROFESSOR_BALD_DIALOGUES,"#D4AF37"))



if __name__ == "__main__":
    app=ProjectOlive()
    app.run()

