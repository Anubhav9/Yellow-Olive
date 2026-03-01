import subprocess
import json


class ChallengeValidation():
    def __init__(self, challenge_id):
        self.challenge_id = challenge_id

    def validate_pod_status(self, pod_name, namespace="default"):
        """
        Calls kubectl directly to get pod status.
        Returns: 'Running', 'Pending', 'Failed', or 'NotFound'
        """
        try:
            # -o json gives us a structured response we can parse easily
            cmd = ["kubectl", "get", "pod", pod_name, "-n", namespace, "-o", "json"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)

            if result.returncode != 0:
                # If kubectl returns an error (e.g., pod not found)
                if "not found" in result.stderr.lower():
                    return "NotFound"
                else:
                    error_msg = result.stderr.strip()
                    return error_msg

            # Parse the JSON output
            pod_data = json.loads(result.stdout)
            phase = pod_data.get("status", {}).get("containerStatuses", "Unknown")
            phase=phase[0].get("ready")
            return phase

        except subprocess.TimeoutExpired:
            return "Timeout"
        except Exception:
            return "InternalError"
