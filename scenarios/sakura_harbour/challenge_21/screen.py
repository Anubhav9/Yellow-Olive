from scenarios.sakura_harbour.challenge_21 import challenge_text
from screens.common.base_challenge_screen import BaseChallengeScreen
from utils import general_utils


class Challenge21(BaseChallengeScreen):
    challenge_id = "21"
    challenge_scenario = "sakura_harbour"
    challenge_text = challenge_text.CHALLENGE_21_TEXT

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        manifest_path = general_utils.get_lab_deployment_file(
            self.challenge_scenario, self.challenge_id
        )
        self.challenge_text = (
            f"{challenge_text.CHALLENGE_21_TEXT}\n"
            f"\nInspect the manifest at {manifest_path}\n"
            "Fix the roster, then apply it from your Command Chamber."
        )
