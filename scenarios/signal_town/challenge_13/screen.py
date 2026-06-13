from scenarios.signal_town.challenge_13 import challenge_text
from screens.common.base_challenge_screen import BaseChallengeScreen


class Challenge13(BaseChallengeScreen):
    challenge_id = "13"
    challenge_scenario = "signal_town"
    challenge_text = challenge_text.CHALLENGE_13_TEXT

    def create_resources_for_challenge(self) -> None:
        self.apply_challenge_manifests("8", self.challenge_id)
