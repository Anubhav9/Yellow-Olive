from scenarios.signal_town.challenge_10 import challenge_text
from screens.common.base_challenge_screen import BaseChallengeScreen


class Challenge10(BaseChallengeScreen):
    challenge_id = "10"
    challenge_scenario = "signal_town"
    challenge_text = challenge_text.CHALLENGE_10_TEXT

    def create_resources_for_challenge(self) -> None:
        self.apply_challenge_manifests("8", self.challenge_id)
