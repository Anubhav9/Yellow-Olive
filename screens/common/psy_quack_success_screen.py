from utils import general_utils
from screens.dialouges import psyquack_success_dialogue
from media import background_music_utility
import global_constants
import asyncio
from textual.widgets import RichLog
from textual import events


class PsyQuackSuccessScreen(RichLog):
    can_focus = True

    def __init__(self, challenge_id, **kwargs):
        super().__init__(markup=True, highlight=True, **kwargs)
        self.challenge_id = str(challenge_id)

    def on_mount(self) -> None:
        self.focus()
        self.run_worker(self.render_psyquack_success_screen(psyquack_success_dialogue.PSYQUACK_SUCCESS_DIALOGUES, "#D4AF37"))

    async def render_psyquack_success_screen(self, dialogues, color):
        background_music_utility.start_background_music(f"{global_constants.MUSIC_MEDIA_PATH}/win_music.ogg")
        all_lines = dialogues.split("\n")
        for line in all_lines:
            styled_line = f"[bold {color}]{line}[/]"
            self.write(styled_line+"\n")
            # RichLog adds newlines automatically with .write()
            await asyncio.sleep(1)

        output_ascii=general_utils.convert_to_ascii(f"{global_constants.IMAGE_MEDIA_PATH}/psyquack_happy.png")
        self.write(output_ascii)
        self.write(
            f"[bold]Mission {self.challenge_id} cleared.[/] "
            f"You now have [bold]{global_constants.meow_coins}[/] Meow Coins."
        )
        next_challenge_id = general_utils.get_next_challenge_id(self.challenge_id)
        if self.challenge_id == "7" and general_utils.is_story_intro_pending():
            self.write(
                "[bold #D4AF37]Electromon's pod training is complete.[/]"
            )
            self.write("The road beyond the laboratory leads to Signal Town.")
            self.write(global_constants.PRESS_ENTER_TO_CONTINUE_ACTION_TEXT)
        elif next_challenge_id is None:
            self.write("[bold #D4AF37]Every mission in the lab is complete. Professor Bald would be proud.[/]")
            self.write("\n[reverse] Press Enter to Return to the Lab [/]")
        else:
            self.write(
                f"[bold #D4AF37]Next stop:[/] Challenge {next_challenge_id}. "
                "Press Enter to continue your journey."
            )
            self.write(global_constants.PRESS_ENTER_TO_CONTINUE_ACTION_TEXT)

    async def on_key(self, event: events.Key) -> None:
        if event.key == "enter":
            background_music_utility.stop_background_music()
            container = self.parent
            await self.remove()
            next_challenge_id = general_utils.get_next_challenge_id(self.challenge_id)
            if self.challenge_id == "7" and general_utils.is_story_intro_pending():
                from scenarios.signal_town.prologue.screens.signal_town_intro_screen import SignalTownIntroScreen

                await container.mount(SignalTownIntroScreen())
                return
            if next_challenge_id is None:
                return
            next_challenge = general_utils.load_challenge(next_challenge_id)
            await container.mount(next_challenge())
