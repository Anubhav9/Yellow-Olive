import subprocess

import global_constants
from challenge_files import challenge_11_text
from screens.base_challenge_screen import BaseChallengeScreen
from textual.widgets import RichLog
from utils import general_utils


class Challenge11(BaseChallengeScreen):
    challenge_id = "11"
    challenge_text = challenge_11_text.CHALLENGE_11_TEXT

    def apply_challenge_pod(self) -> None:
        try:
            bulba_pod_path = general_utils.get_lab_challenge_file("8")
            service_path = general_utils.get_lab_service_file(self.challenge_id)
            subprocess.Popen(
                [
                    "sh",
                    str(global_constants.PROJECT_ROOT / "scripts" / "generic-script-pods.sh"),
                    str(self.challenge_id),
                    str(bulba_pod_path),
                    str(service_path),
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
                cwd=str(global_constants.PROJECT_ROOT),
            )
        except Exception as error:
            log = self.query_one(f"#{self.challenge_log_id}", RichLog)
            log.write("[red]Failed to start challenge pod script[/red]")
            log.write(str(error))
