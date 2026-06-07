from scenarios.gold_rush_city.challenge_19 import challenge_text
from screens.common.base_challenge_screen import BaseChallengeScreen
from services import resource_manager
from textual.widgets import RichLog


class Challenge19(BaseChallengeScreen):
    challenge_id = "19"
    challenge_scenario = "gold_rush_city"
    challenge_text = challenge_text.CHALLENGE_19_TEXT

    def create_resources_for_challenge(self):
        try:
            resource_manager.apply_prologue_resources(self.challenge_scenario)
            resource_manager.apply_manifest(self.challenge_scenario, "15")
            resource_manager.apply_manifest(self.challenge_scenario, "16")
            resource_manager.apply_manifest(self.challenge_scenario, "17")
            resource_manager.apply_manifest(self.challenge_scenario, "18")
            resource_manager.apply_manifest(self.challenge_scenario, self.challenge_id)
        except Exception as error:
            log = self.query_one(f"#{self.challenge_log_id}", RichLog)
            log.write("[red]Failed to start challenge resources[/red]")
            log.write(str(error))
