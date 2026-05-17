import subprocess

import global_constants
from challenge_files import challenge_12_text
from screens.base_challenge_screen import BaseChallengeScreen
from textual.widgets import RichLog
from utils import general_utils


class Challenge12(BaseChallengeScreen):
    challenge_id = "12"
    challenge_text = challenge_12_text.CHALLENGE_12_TEXT

    def apply_challenge_pod(self) -> None:
        try:
            namespace_path = general_utils.get_lab_namespace_file()
            bulba_pod_path = general_utils.get_lab_challenge_file("8")
            service_path = general_utils.get_lab_service_file(self.challenge_id)
            apply_commands = (
                f'kubectl apply -f "{namespace_path}" && '
                f'kubectl delete pods,service --all -n signal-town --ignore-not-found=true && '
                f'kubectl apply -f "{bulba_pod_path}" && '
                f'kubectl apply -f "{service_path}"'
            )
            subprocess.Popen(
                ["sh", "-c", apply_commands],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
                cwd=str(global_constants.PROJECT_ROOT),
            )
        except Exception as error:
            log = self.query_one(f"#{self.challenge_log_id}", RichLog)
            log.write("[red]Failed to start challenge 12 setup[/red]")
            log.write(str(error))
