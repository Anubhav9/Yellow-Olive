from scenarios.signal_town.challenge_10 import challenge_text
from screens.common.base_challenge_screen import BaseChallengeScreen
from textual.widgets import RichLog
from services import resource_manager


class Challenge10(BaseChallengeScreen):
    challenge_id = "10"
    challenge_scenario = "signal_town"
    challenge_text = challenge_text.CHALLENGE_10_TEXT

    def create_resources_for_challenge(self):
        try:
            resource_manager.apply_manifest(self.challenge_scenario, "8")
            resource_manager.apply_manifest(self.challenge_scenario, self.challenge_id)
        except Exception as error:
            log = self.query_one(f"#{self.challenge_log_id}", RichLog)
            log.write("[red]Failed to start challenge pod script[/red]")
            log.write(str(error))
