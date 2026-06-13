from scenarios.oakwood_meadows.challenge_1 import challenge_text
from screens.common.base_challenge_screen import BaseChallengeScreen
from utils import general_utils


class Challenge1(BaseChallengeScreen):
    challenge_id = "1"
    challenge_scenario = "oakwood_meadows"
    challenge_text = challenge_text.CHALLENGE_1_TEXT

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        manifest_path = general_utils.get_lab_challenge_file(
            self.challenge_scenario, self.challenge_id
        )
        self.challenge_text = (
            f"{challenge_text.CHALLENGE_1_TEXT}\n"
            "\nObjective:\n"
            f"Inspect the manifest at {manifest_path}\n"
            "Fix the issue, then delete and recreate the pod using that file."
        )
