import asyncio

from textual import on
from textual.app import ComposeResult
from textual.widgets import Input, Label, RichLog, Static

import global_constants
from dialouges import professor_bald_dialogue
from screens.challenge_music_preference_screen import ChallengeMusicPreferenceScreen
from screens.professor_bald_intro import ProfessorBaldIntro
from utils import general_utils


class ResumeGameScreen(Static):
    can_focus = True

    def compose(self) -> ComposeResult:
        progress = general_utils.load_progress()
        player_name = progress.get("player_name") or "Trainer"
        challenge_id = progress.get("active_challenge_id", "1")
        meow_coins = general_utils.calculate_meow_coins(challenge_id)
        story_act = progress.get("story_intro_act")
        if general_utils.is_story_intro_pending(progress):
            story_labels = {
                global_constants.STORY_ACT_SIGNAL_TOWN: "Arrival at Signal Town",
                global_constants.STORY_ACT_COOL_TURTLE: "Cool Turtle at the tower",
                global_constants.STORY_ACT_TEAM_EVIL: "Team Evil's trail",
            }
            mission_text = story_labels.get(story_act, "Signal Town journey")
        elif general_utils.is_campaign_complete(challenge_id):
            mission_text = "All missions complete"
        else:
            mission_text = f"Challenge {challenge_id}"
        continue_text = (
            "Type `start fresh` to begin again from the laboratory."
            if general_utils.is_campaign_complete(challenge_id)
            else "Type `continue` to resume your journey.\n"
            "Type `start fresh` to begin again from the laboratory."
        )

        yield Label(
            f"[bold {global_constants.GLOBAL_DIALOGUE_COLOR}]"
            "Professor Bald found your old trainer log.[/]"
        )
        yield RichLog(markup=True, highlight=True, id="resume-log")
        yield Input(
            placeholder="Type continue or start fresh...",
            id="resume-input",
        )

        self.resume_summary = (
            f"[bold]Trainer:[/] {player_name}\n"
            f"[bold]Current Mission:[/] {mission_text}\n"
            f"[bold]Meow Coins:[/] {meow_coins}\n\n"
            f"{continue_text}"
        )

    def on_mount(self) -> None:
        self.focus()
        self.query_one("#resume-log", RichLog).write(self.resume_summary)
        self.query_one("#resume-input", Input).focus()

    @on(Input.Submitted, selector="#resume-input")
    async def handle_resume_input(self, event: Input.Submitted) -> None:
        command = (event.value or "").strip().lower()
        log = self.query_one("#resume-log", RichLog)

        if command == "continue":
            progress = general_utils.restore_progress_to_runtime()
            if general_utils.is_campaign_complete(progress["active_challenge_id"]):
                log.write("[yellow]Every mission is already complete. Type `start fresh` to begin again.[/]")
                return
            log.write("[yellow]Professor Bald is reinitializing the lab cluster...[/]")
            await asyncio.to_thread(general_utils.start_core_infra, True)
            if general_utils.is_story_intro_pending(progress):
                story_screen = general_utils.load_story_intro_screen(
                    progress["story_intro_act"]
                )
                await self._replace_self_with(story_screen())
                return
            challenge_screen = general_utils.load_challenge(progress["active_challenge_id"])
            if general_utils.needs_challenge_music_preference(progress):
                await self._replace_self_with(
                    ChallengeMusicPreferenceScreen(challenge_screen)
                )
            else:
                await self._replace_self_with(challenge_screen())
            return

        if command == "start fresh":
            general_utils.reset_progress()
            professor_bald_intro = ProfessorBaldIntro()
            await self._replace_self_with(professor_bald_intro)
            self.app.run_worker(
                professor_bald_intro.render_professor_bald_intro(
                    professor_bald_dialogue.PROFESSOR_BALD_DIALOGUES,
                    global_constants.GLOBAL_DIALOGUE_COLOR,
                )
            )
            return

        general_utils.show_invalid_command(
            self,
            "PsyQuack tilts its head... type continue or start fresh.",
        )
        log.write("[yellow]Try `continue` or `start fresh`.[/]")

    async def _replace_self_with(self, widget):
        container = self.parent
        await self.remove()
        await container.mount(widget)
