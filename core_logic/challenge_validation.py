import subprocess
import json

from challenge_files import challenge_constants


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
        Challenge-aware validator for challenges 2-13.
        Returns: (is_valid: bool, message: str)
        """
        if challenge_id == "8":
            return self._validate_challenge_8(namespace)

        if challenge_id == "9":
            return self._validate_challenge_9(pod_name, namespace)

        if challenge_id == "10":
            return self._validate_challenge_10(pod_name, namespace)

        if challenge_id == "11":
            return self._validate_challenge_11(namespace)

        if challenge_id == "12":
            return self._validate_challenge_12(namespace)

        if challenge_id == "13":
            return self._validate_challenge_13(namespace)

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

    def _get_service_json(self, service_name, namespace):
        try:
            cmd = [
                "kubectl",
                "get",
                "service",
                service_name,
                "-n",
                namespace,
                "-o",
                "json",
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                if "not found" in result.stderr.lower():
                    return False, (
                        "Signal path not found. "
                        f"Is {service_name} deployed in namespace {namespace}?"
                    )
                return False, result.stderr.strip() or "Unable to fetch Service details."
            return True, json.loads(result.stdout)
        except subprocess.TimeoutExpired:
            return False, "Cluster connection timed out while checking the Service."
        except Exception:
            return False, "Internal validation error."

    def _get_endpoints_json(self, service_name, namespace):
        try:
            cmd = [
                "kubectl",
                "get",
                "endpoints",
                service_name,
                "-n",
                namespace,
                "-o",
                "json",
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                if "not found" in result.stderr.lower():
                    return False, "Endpoints not found for the Service."
                return False, result.stderr.strip() or "Unable to fetch Endpoints."
            return True, json.loads(result.stdout)
        except subprocess.TimeoutExpired:
            return False, "Cluster connection timed out while checking Endpoints."
        except Exception:
            return False, "Internal validation error."

    def _validate_challenge_8(self, namespace):
        service_name = challenge_constants.CHALLENGE_8_SERVICE_NAME
        is_success, service_data_or_error = self._get_service_json(
            service_name, namespace
        )
        if not is_success:
            return False, service_data_or_error

        service_data = service_data_or_error
        spec = service_data.get("spec", {})

        if spec.get("type") != "ClusterIP":
            return False, "Expected Service type ClusterIP."

        selector = spec.get("selector", {})
        if selector.get("app") != challenge_constants.CHALLENGE_8_SELECTOR_APP:
            return False, (
                f"Expected selector app={challenge_constants.CHALLENGE_8_SELECTOR_APP}."
            )

        ports = spec.get("ports", [])
        if not ports:
            return False, "No ports configured on the Service."

        service_port = ports[0].get("port")
        target_port = ports[0].get("targetPort")
        expected_port = challenge_constants.CHALLENGE_8_SERVICE_PORT
        expected_target = challenge_constants.CHALLENGE_8_TARGET_PORT

        if service_port != expected_port or str(target_port) != str(expected_target):
            return False, (
                f"Expected port={expected_port} and targetPort={expected_target}."
            )

        is_success, endpoints_data_or_error = self._get_endpoints_json(
            service_name, namespace
        )
        if not is_success:
            return False, endpoints_data_or_error

        endpoints_data = endpoints_data_or_error
        subsets = endpoints_data.get("subsets", [])
        has_ready_address = any(
            subset.get("addresses") for subset in subsets if subset.get("addresses")
        )
        if not has_ready_address:
            return False, (
                "No endpoints found. The Service still cannot find Bulba Baby's Pokepod."
            )

        return True, "Signal path restored. Cool Turtle can reach Bulba Baby."

    def _validate_challenge_9(self, relay_pod_name, namespace):
        is_success, endpoints_data_or_error = self._get_endpoints_json(
            challenge_constants.CHALLENGE_8_SERVICE_NAME, namespace
        )
        if not is_success:
            return False, endpoints_data_or_error

        endpoints_data = endpoints_data_or_error
        subsets = endpoints_data.get("subsets", [])
        has_ready_address = any(
            subset.get("addresses") for subset in subsets if subset.get("addresses")
        )
        if not has_ready_address:
            return (
                False,
                "Bulba Baby's Service has no endpoints. "
                "Ensure bulba-baby-service can reach bulba-baby-pod first.",
            )

        is_success, pod_data_or_error = self._get_pod_json(relay_pod_name, namespace)
        if not is_success:
            return False, pod_data_or_error

        pod_data = pod_data_or_error
        containers = pod_data.get("spec", {}).get("containers", [])
        if not containers:
            return False, "No containers found in the relay Pokepod."

        container = containers[0]
        command = container.get("command", [])
        args = container.get("args", [])
        rendered_command = " ".join([str(x) for x in command + args]).lower()
        service_host = challenge_constants.CHALLENGE_9_SERVICE_DNS_HOST.lower()
        wrong_host = challenge_constants.CHALLENGE_9_WRONG_DNS_HOST.lower()

        if wrong_host in rendered_command:
            return (
                False,
                f"Relay is still calling the wrong name. Use http://{service_host}/",
            )
        if service_host not in rendered_command:
            return (
                False,
                f"Expected relay to call Bulba Baby at http://{service_host}/",
            )

        try:
            exec_cmd = [
                "kubectl",
                "exec",
                relay_pod_name,
                "-n",
                namespace,
                "--",
                "curl",
                "-sf",
                f"http://{service_host}/",
            ]
            result = subprocess.run(exec_cmd, capture_output=True, text=True, timeout=15)
            if result.returncode != 0:
                return (
                    False,
                    "Relay manifest looks closer, but DNS reachability failed. "
                    "Delete and recreate cool-turtle-relay-pod after fixing the manifest.",
                )
        except subprocess.TimeoutExpired:
            return False, "Timed out while testing Service DNS from the relay Pokepod."
        except Exception:
            return False, "Internal validation error while testing Service DNS."

        return (
            True,
            "Cool Turtle reaches Bulba Baby by name. Service DNS is working.",
        )

    def _validate_challenge_10(self, relay_pod_name, relay_namespace):
        signal_town = challenge_constants.NAMESPACE_SIGNAL_TOWN
        is_success, endpoints_data_or_error = self._get_endpoints_json(
            challenge_constants.CHALLENGE_8_SERVICE_NAME, signal_town
        )
        if not is_success:
            return False, endpoints_data_or_error

        endpoints_data = endpoints_data_or_error
        subsets = endpoints_data.get("subsets", [])
        has_ready_address = any(
            subset.get("addresses") for subset in subsets if subset.get("addresses")
        )
        if not has_ready_address:
            return (
                False,
                "Bulba Baby's Service in signal-town has no endpoints. "
                "Ensure bulba-baby-pod and bulba-baby-service are healthy.",
            )

        is_success, pod_data_or_error = self._get_pod_json(relay_pod_name, relay_namespace)
        if not is_success:
            return False, pod_data_or_error

        pod_data = pod_data_or_error
        containers = pod_data.get("spec", {}).get("containers", [])
        if not containers:
            return False, "No containers found in the trainer relay Pokepod."

        container = containers[0]
        command = container.get("command", [])
        args = container.get("args", [])
        rendered_command = " ".join([str(x) for x in command + args]).lower()
        service_fqdn = challenge_constants.CHALLENGE_10_SERVICE_FQDN.lower()
        short_host = challenge_constants.CHALLENGE_10_SHORT_DNS_HOST.lower()

        if service_fqdn not in rendered_command:
            return (
                False,
                f"Expected cross-town call to http://{service_fqdn}/",
            )

        short_url = f"http://{short_host}/"
        if short_url in rendered_command:
            return (
                False,
                "Short Service names only work inside the same namespace. "
                f"Use the full FQDN: {challenge_constants.CHALLENGE_10_SERVICE_FQDN}",
            )

        try:
            exec_cmd = [
                "kubectl",
                "exec",
                relay_pod_name,
                "-n",
                relay_namespace,
                "--",
                "curl",
                "-sf",
                f"http://{service_fqdn}/",
            ]
            result = subprocess.run(exec_cmd, capture_output=True, text=True, timeout=15)
            if result.returncode != 0:
                return (
                    False,
                    "FQDN looks correct in the manifest, but the call still failed. "
                    "Delete and recreate trainer-relay-pod after fixing the manifest.",
                )
        except subprocess.TimeoutExpired:
            return False, "Timed out while testing cross-namespace Service DNS."
        except Exception:
            return False, "Internal validation error while testing Service DNS."

        return (
            True,
            "Trainer relay reaches Signal Town across namespaces. FQDN DNS is working.",
        )

    def _get_ingress_json(self, ingress_name, namespace):
        try:
            cmd = [
                "kubectl",
                "get",
                "ingress",
                ingress_name,
                "-n",
                namespace,
                "-o",
                "json",
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                if "not found" in result.stderr.lower():
                    return False, (
                        f"Ingress {ingress_name} not found in namespace {namespace}."
                    )
                return False, result.stderr.strip() or "Unable to fetch Ingress details."
            return True, json.loads(result.stdout)
        except subprocess.TimeoutExpired:
            return False, "Cluster connection timed out while checking the Ingress."
        except Exception:
            return False, "Internal validation error."

    def _count_running_labeled_pods(self, namespace, label_selector):
        try:
            cmd = [
                "kubectl",
                "get",
                "pods",
                "-n",
                namespace,
                "-l",
                label_selector,
                "--field-selector=status.phase=Running",
                "-o",
                "json",
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                return False, result.stderr.strip() or "Unable to list Pokepods."
            pod_list = json.loads(result.stdout)
            return True, len(pod_list.get("items", []))
        except subprocess.TimeoutExpired:
            return False, "Cluster connection timed out while listing Pokepods."
        except Exception:
            return False, "Internal validation error."

    def _count_endpoint_addresses(self, service_name, namespace):
        is_success, endpoints_data_or_error = self._get_endpoints_json(
            service_name, namespace
        )
        if not is_success:
            return False, endpoints_data_or_error

        endpoints_data = endpoints_data_or_error
        address_count = 0
        for subset in endpoints_data.get("subsets", []):
            address_count += len(subset.get("addresses", []))
        return True, address_count

    def _validate_challenge_11(self, namespace):
        service_name = challenge_constants.CHALLENGE_8_SERVICE_NAME
        is_success, service_data_or_error = self._get_service_json(
            service_name, namespace
        )
        if not is_success:
            return False, service_data_or_error

        spec = service_data_or_error.get("spec", {})
        if spec.get("type") != "NodePort":
            return False, "Expected Service type NodePort."

        ports = spec.get("ports", [])
        if not ports:
            return False, "No ports configured on the Service."

        service_port = ports[0].get("port")
        target_port = ports[0].get("targetPort")
        node_port = ports[0].get("nodePort")

        if service_port != challenge_constants.CHALLENGE_11_SERVICE_PORT:
            return False, f"Expected port={challenge_constants.CHALLENGE_11_SERVICE_PORT}."
        if str(target_port) != str(challenge_constants.CHALLENGE_11_TARGET_PORT):
            return (
                False,
                f"Expected targetPort={challenge_constants.CHALLENGE_11_TARGET_PORT}.",
            )
        if node_port != challenge_constants.CHALLENGE_11_NODE_PORT:
            return (
                False,
                f"Expected nodePort={challenge_constants.CHALLENGE_11_NODE_PORT}.",
            )

        is_success, endpoints_data_or_error = self._get_endpoints_json(
            service_name, namespace
        )
        if not is_success:
            return False, endpoints_data_or_error

        subsets = endpoints_data_or_error.get("subsets", [])
        has_ready_address = any(
            subset.get("addresses") for subset in subsets if subset.get("addresses")
        )
        if not has_ready_address:
            return False, "No endpoints found. Bulba Baby must be reachable behind the gate."

        return True, "NodePort gate is open. Outsiders can reach Signal Town."

    def _validate_challenge_12(self, namespace):
        service_name = challenge_constants.CHALLENGE_8_SERVICE_NAME
        label_selector = f"app={challenge_constants.CHALLENGE_8_SELECTOR_APP}"

        is_success, running_count_or_error = self._count_running_labeled_pods(
            namespace, label_selector
        )
        if not is_success:
            return False, running_count_or_error

        if running_count_or_error < challenge_constants.CHALLENGE_12_MIN_BULBA_PODS:
            return (
                False,
                "Only one stall is running. Apply pod-q12-stall-two.yaml "
                "so at least two bulba-baby Pokepods are running.",
            )

        is_success, address_count_or_error = self._count_endpoint_addresses(
            service_name, namespace
        )
        if not is_success:
            return False, address_count_or_error

        if address_count_or_error < challenge_constants.CHALLENGE_12_MIN_BULBA_PODS:
            return (
                False,
                "bulba-baby-service does not have enough endpoints yet. "
                "Ensure both stalls use label app=bulba-baby.",
            )

        return True, "The market district is fully online. Multiple stalls answer the call."

    def _validate_challenge_13(self, namespace):
        service_name = challenge_constants.CHALLENGE_8_SERVICE_NAME
        is_success, address_count_or_error = self._count_endpoint_addresses(
            service_name, namespace
        )
        if not is_success:
            return False, address_count_or_error

        if address_count_or_error < 1:
            return (
                False,
                "bulba-baby-service has no endpoints. Ensure Bulba Baby's Pokepod is running.",
            )

        ingress_name = challenge_constants.CHALLENGE_13_INGRESS_NAME
        is_success, ingress_data_or_error = self._get_ingress_json(ingress_name, namespace)
        if not is_success:
            return False, ingress_data_or_error

        ingress_data = ingress_data_or_error
        spec = ingress_data.get("spec", {})
        ingress_class = spec.get("ingressClassName")
        if ingress_class != challenge_constants.CHALLENGE_13_INGRESS_CLASS:
            return False, f"Expected ingressClassName={challenge_constants.CHALLENGE_13_INGRESS_CLASS}."

        rules = spec.get("rules", [])
        if not rules:
            return False, "Ingress has no routing rules configured."

        rule = rules[0]
        host = rule.get("host")
        if host != challenge_constants.CHALLENGE_13_INGRESS_HOST:
            return (
                False,
                f"Expected host={challenge_constants.CHALLENGE_13_INGRESS_HOST}.",
            )

        paths = rule.get("http", {}).get("paths", [])
        if not paths:
            return False, "Ingress rule has no HTTP paths configured."

        backend = paths[0].get("backend", {}).get("service", {})
        backend_name = backend.get("name")
        backend_port = backend.get("port", {}).get("number")

        if backend_name != service_name:
            return False, f"Expected backend service name {service_name}."
        if backend_port != challenge_constants.CHALLENGE_8_SERVICE_PORT:
            return False, f"Expected backend port {challenge_constants.CHALLENGE_8_SERVICE_PORT}."

        return True, "Signal Town's front door routes to Bulba Baby. Ingress is configured."
