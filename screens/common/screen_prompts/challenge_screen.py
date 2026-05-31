import global_constants


class ChallengeScreenPrompts:
    def __init__(self, challenge_id):
        self.challenge_id = challenge_id

    def challenge_text(self):
        return (
            f"[bold {global_constants.GLOBAL_DIALOGUE_COLOR}]"
            f"Challenge {self.challenge_id} of {global_constants.TOTAL_CHALLENGES} is ready, young engineer![/]"
        )

    def challenge_status_text(self):
        return (
            f"[bold]Meow Coins:[/] {global_constants.meow_coins}    "
            f"[bold]Expected Command:[/] `psyquack validate`"
        )

    def battle_challenge_text(self):
        return f"Battle Challenge {self.challenge_id}"

    def building_connection_text(self):
        return "[yellow]PsyQuack is building a local bridge to the cluster...[/]"

    def incorrect_answer_text(self):
        return "[yellow]Answer is incorrect.[/]"

    def correct_answer_text(self):
        return "[yellow]Answer is correct.[/]"

    def move_to_next_challenge_text(self):
        next_challenge_id = int(self.challenge_id) + 1
        if next_challenge_id <= global_constants.TOTAL_CHALLENGES:
            return (
                f"\n[reverse] Press Enter to Continue to Challenge {next_challenge_id} [/]"
            )
        return "\n[reverse] Press Enter to Return to the Lab [/]"

    def review_failed_attempt_text(self):
        return "\n[reverse] Press Enter to Review PsyQuack's feedback [/]"
