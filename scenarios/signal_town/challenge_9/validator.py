from challenge_files import challenge_constants
from services import resource_inspector


def validate():
    """Validate Challenge 9: cool-turtle-relay-pod must call bulba-baby-service
    by name (not the wrong name) and the call must actually succeed."""
    namespace = challenge_constants.NAMESPACE_SIGNAL_TOWN
    service_name = challenge_constants.CHALLENGE_8_SERVICE_NAME
    relay_pod = challenge_constants.CHALLENGE_9_RELAY_POD_NAME
    expected_host = challenge_constants.CHALLENGE_9_SERVICE_DNS_HOST.lower()
    wrong_host = challenge_constants.CHALLENGE_9_WRONG_DNS_HOST.lower()

    # ---- 1. bulba-baby-service is reachable (has endpoints) ----
    ok, endpoints = resource_inspector.get_endpoints(service_name, namespace)
    if not ok:
        return False, endpoints

    has_ready_address = any(
        subset.get("addresses")
        for subset in endpoints.get("subsets", [])
        if subset.get("addresses")
    )
    if not has_ready_address:
        return (
            False,
            "Bulba Baby's Service has no endpoints. "
            "Ensure bulba-baby-service can reach bulba-baby-pod first.",
        )

    # ---- 2. Relay pod exists and has a container ----
    ok, pod = resource_inspector.get_pod(relay_pod, namespace)
    if not ok:
        return False, pod

    containers = pod.get("spec", {}).get("containers", [])
    if not containers:
        return False, "No containers found in the relay Pokepod."

    container = containers[0]
    rendered_command = " ".join(
        str(token) for token in container.get("command", []) + container.get("args", [])
    ).lower()

    # ---- 3. Relay calls the right host ----
    if wrong_host in rendered_command:
        return False, f"Relay is still calling the wrong name. Use http://{expected_host}/"
    if expected_host not in rendered_command:
        return False, f"Expected relay to call Bulba Baby at http://{expected_host}/"

    # ---- 4. DNS actually resolves and the curl succeeds ----
    ok, _stdout = resource_inspector.exec_in_pod(
        relay_pod,
        namespace,
        ["curl", "-sf", f"http://{expected_host}/"],
    )
    if not ok:
        return (
            False,
            "Relay manifest looks closer, but DNS reachability failed. "
            "Delete and recreate cool-turtle-relay-pod after fixing the manifest.",
        )

    return True, "Cool Turtle reaches Bulba Baby by name. Service DNS is working."
