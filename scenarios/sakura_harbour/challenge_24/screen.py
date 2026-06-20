from scenarios.sakura_harbour.challenge_24 import challenge_text
from screens.common.base_challenge_screen import BaseChallengeScreen
from utils import general_utils


class Challenge24(BaseChallengeScreen):
    challenge_id = "24"
    challenge_scenario = "sakura_harbour"
    challenge_text = challenge_text.CHALLENGE_24_TEXT

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        stable_path = general_utils.get_lab_deployment_file(
            self.challenge_scenario,
            self.challenge_id,
            file_name="deployment-q24-stable.yaml",
        )
        canary_path = general_utils.get_lab_deployment_file(
            self.challenge_scenario,
            self.challenge_id,
            file_name="deployment-q24-canary.yaml",
        )
        self.challenge_text = (
            f"{challenge_text.CHALLENGE_24_TEXT}\n"
            f"\nStable manifest: {stable_path}\n"
            f"Canary manifest: {canary_path}\n"
            "Fix the canary roster, then apply it from your Command Chamber."
        )
