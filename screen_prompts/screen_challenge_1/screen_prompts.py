import global_constants
class ChallengeScreenPrompts():
    def __init__(self,challenge_id):
        self.challenge_id=challenge_id
    def challenge_text(self):
        CHALLENGE_1_TEXT = f"[bold {global_constants.GLOBAL_DIALOGUE_COLOR}]So, here is your {self.challenge_id} challenge young engineer![/]"
        return CHALLENGE_1_TEXT
    def battle_challenge_text(self):
        BATTLE_CHALLENGE_TEXT = f"Battle out Challenge {self.challenge_id}"
        return BATTLE_CHALLENGE_TEXT
    def building_connection_text(self):
        BUILDING_CONNECTION_TEXT = "[yellow]PsyQuack is building a local bridge to the cluster...[/]"
        return BUILDING_CONNECTION_TEXT
    def incorrect_answer_text(self):
        INCORRECT_ANSWER_TEXT = "[yellow]Answer is incorrect"
        return INCORRECT_ANSWER_TEXT
    def correct_answer_text(self):
        CORRECT_ANSWER_TEXT = "[yellow]Answer is correct"
        return CORRECT_ANSWER_TEXT
    def move_to_next_challenge_text(self):
        MOVE_TO_NEXT_CHALLENGE = "\n[reverse] Press Enter to Continue and Proceed to Challenge 2 [/]"
        return MOVE_TO_NEXT_CHALLENGE







