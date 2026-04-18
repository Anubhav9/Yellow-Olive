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

    def _get_pod_json(self, pod_name, namespace="default"):
        """Fetch pod json from cluster and return (success, data_or_error)."""
        try:
            cmd = ["kubectl", "get", "pod", pod_name, "-n", namespace, "-o", "json"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                if "not found" in result.stderr.lower():
                    return False, "Pokepod not found. Is Electromon deployed in this namespace?"
                return False, result.stderr.strip() or "Unable to fetch pod details."
            return True, json.loads(result.stdout)
        except subprocess.TimeoutExpired:
            return False, "Cluster connection timed out while checking the Pokepod."
        except Exception:
            return False, "Internal validation error."

    def validate_challenge(self, challenge_id, pod_name, namespace="default"):
        """
        Challenge-aware validator for challenges 2-7.
        Returns: (is_valid: bool, message: str)
        """
        is_success, pod_data_or_error = self._get_pod_json(pod_name, namespace)
        if not is_success:
            return False, pod_data_or_error

        pod_data = pod_data_or_error
        spec = pod_data.get("spec", {})
        containers = spec.get("containers", [])
        if not containers:
            return False, "No containers found in the Pokepod."
        container = containers[0]

        if challenge_id == "2":
            return self._validate_challenge_2(container)
        if challenge_id == "3":
            return self._validate_challenge_3(container)
        if challenge_id == "4":
            return self._validate_challenge_4(pod_data)
        if challenge_id == "5":
            return self._validate_challenge_5(container)
        if challenge_id == "6":
            return self._validate_challenge_6(container)
        if challenge_id == "7":
            return self._validate_challenge_7(spec)

        return False, f"No validation rule configured for challenge {challenge_id}."

    def _validate_challenge_2(self, container):
        liveness_probe = container.get("livenessProbe", {})
        http_get = liveness_probe.get("httpGet", {})
        probe_path = http_get.get("path")
        probe_port = http_get.get("port")

        if probe_path != "/" or str(probe_port) != "80":
            return False, "Expected livenessProbe httpGet path='/' and port=80."
        return True, "Liveness probe is correctly configured."

    def _validate_challenge_3(self, container):
        command = container.get("command", [])
        args = container.get("args", [])
        rendered_command = " ".join([str(x) for x in command + args]).lower()
        expected_text = "electromon show your power"

        if expected_text not in rendered_command:
            return False, "Expected container command to print: Electromon show your power"
        return True, "Container command looks correct."

    def _validate_challenge_4(self, pod_data):
        labels = pod_data.get("metadata", {}).get("labels", {})
        pod_type = labels.get("type")
        relationship = labels.get("relationship")

        if pod_type != "electric" or relationship != "best-buddy":
            return False, "Expected labels: type=electric and relationship=best-buddy."
        return True, "Pod labels are correctly configured."

    def _validate_challenge_5(self, container):
        env_vars = container.get("env", [])
        env_map = {}
        for item in env_vars:
            env_name = item.get("name")
            env_value = item.get("value")
            if env_name:
                env_map[env_name] = env_value

        if env_map.get("BATTLE_MODE") != "ON":
            return False, "Expected env variable BATTLE_MODE=ON."
        return True, "Battle mode env variable is set correctly."

    def _validate_challenge_6(self, container):
        limits = container.get("resources", {}).get("limits", {})
        cpu_limit = limits.get("cpu")
        memory_limit = limits.get("memory")

        if cpu_limit != "500m" or memory_limit != "256Mi":
            return False, "Expected resource limits: cpu=500m and memory=256Mi."
        return True, "Resource limits are configured correctly."

    def _validate_challenge_7(self, pod_spec):
        restart_policy = pod_spec.get("restartPolicy")
        if restart_policy != "Always":
            return False, "Expected restartPolicy=Always."
        return True, "Restart policy is correctly configured."
