from scenarios.gold_rush_city.challenge_19 import challenge_text
from screens.common.base_challenge_screen import BaseChallengeScreen


class Challenge19(BaseChallengeScreen):
    challenge_id = "19"
    challenge_scenario = "gold_rush_city"
    challenge_text = challenge_text.CHALLENGE_19_TEXT

    def create_resources_for_challenge(self) -> None:
        self.apply_challenge_manifests("15", "16", "17", "18", self.challenge_id)
