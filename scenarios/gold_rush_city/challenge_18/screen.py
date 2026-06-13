from scenarios.gold_rush_city.challenge_18 import challenge_text
from screens.common.base_challenge_screen import BaseChallengeScreen


class Challenge18(BaseChallengeScreen):
    challenge_id = "18"
    challenge_scenario = "gold_rush_city"
    challenge_text = challenge_text.CHALLENGE_18_TEXT

    def create_resources_for_challenge(self) -> None:
        self.apply_challenge_manifests("15", "16", self.challenge_id)
