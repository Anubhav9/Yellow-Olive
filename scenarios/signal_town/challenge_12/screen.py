from scenarios.signal_town.challenge_12 import challenge_text
from screens.common.base_challenge_screen import BaseChallengeScreen


class Challenge12(BaseChallengeScreen):
    challenge_id = "12"
    challenge_scenario = "signal_town"
    challenge_text = challenge_text.CHALLENGE_12_TEXT

    def create_resources_for_challenge(self) -> None:
        self.apply_challenge_manifests("8", self.challenge_id)
