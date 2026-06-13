from scenarios.gold_rush_city.challenge_16 import challenge_text
from screens.common.base_challenge_screen import BaseChallengeScreen


class Challenge16(BaseChallengeScreen):
    challenge_id = "16"
    challenge_scenario = "gold_rush_city"
    challenge_text = challenge_text.CHALLENGE_16_TEXT

    def create_resources_for_challenge(self) -> None:
        self.apply_challenge_manifests("15", self.challenge_id)
