import global_constants
class ChallengeScreenPrompts():
    def __init__(self,challenge_id):
        self.challenge_id=challenge_id
    def challenge_text(self):
        CHALLENGE_1_TEXT = (
            f"[bold {global_constants.GLOBAL_DIALOGUE_COLOR}]"
            f"Challenge {self.challenge_id} of {global_constants.TOTAL_CHALLENGES} is ready, young engineer![/]"
        )
        return CHALLENGE_1_TEXT
    def challenge_status_text(self):
        CHALLENGE_STATUS_TEXT = (
            f"[bold]Meow Coins:[/] {global_constants.meow_coins}    "
            f"[bold]Expected Command:[/] `psyquack validate`"
        )
        return CHALLENGE_STATUS_TEXT
    def battle_challenge_text(self):
        BATTLE_CHALLENGE_TEXT = f"Battle Challenge {self.challenge_id}"
        return BATTLE_CHALLENGE_TEXT
    def building_connection_text(self):
        BUILDING_CONNECTION_TEXT = "[yellow]PsyQuack is building a local bridge to the cluster...[/]"
        return BUILDING_CONNECTION_TEXT
    def incorrect_answer_text(self):
        INCORRECT_ANSWER_TEXT = "[yellow]Answer is incorrect.[/]"
        return INCORRECT_ANSWER_TEXT
    def correct_answer_text(self):
        CORRECT_ANSWER_TEXT = "[yellow]Answer is correct.[/]"
        return CORRECT_ANSWER_TEXT
    def move_to_next_challenge_text(self):
        next_challenge_id = int(self.challenge_id) + 1
        if next_challenge_id <= global_constants.TOTAL_CHALLENGES:
            MOVE_TO_NEXT_CHALLENGE = (
                f"\n[reverse] Press Enter to Continue to Challenge {next_challenge_id} [/]"
            )
        else:
            MOVE_TO_NEXT_CHALLENGE = "\n[reverse] Press Enter to Return to the Lab [/]"
        return MOVE_TO_NEXT_CHALLENGE
    def review_failed_attempt_text(self):
        REVIEW_FAILED_ATTEMPT_TEXT = "\n[reverse] Press Enter to Review PsyQuack's feedback [/]"
        return REVIEW_FAILED_ATTEMPT_TEXT







