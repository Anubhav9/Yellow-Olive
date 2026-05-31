from challenge_files import challenge_constants
from services import resource_inspector


def validate():
    """Validate Challenge 8: bulba-baby-service must be a ClusterIP that selects
    bulba-baby pods on port 80, with at least one ready endpoint."""
    namespace = challenge_constants.NAMESPACE_SIGNAL_TOWN
    service_name = challenge_constants.CHALLENGE_8_SERVICE_NAME

    # ---- 1. Service exists ----
    ok, service = resource_inspector.get_service(service_name, namespace)
    if not ok:
        return False, "Signal path not found. Is bulba-baby-service deployed in signal-town?"

    spec = service.get("spec", {})

    # ---- 2. Service type ----
    if spec.get("type") != "ClusterIP":
        return False, "Expected Service type ClusterIP."

    # ---- 3. Selector ----
    selector_app = spec.get("selector", {}).get("app")
    if selector_app != challenge_constants.CHALLENGE_8_SELECTOR_APP:
        return False, f"Expected selector app={challenge_constants.CHALLENGE_8_SELECTOR_APP}."

    # ---- 4. Port + targetPort ----
    ports = spec.get("ports", [])
    if not ports:
        return False, "No ports configured on the Service."

    expected_port = challenge_constants.CHALLENGE_8_SERVICE_PORT
    expected_target = challenge_constants.CHALLENGE_8_TARGET_PORT
    if ports[0].get("port") != expected_port:
        return False, f"Expected port={expected_port}."
    if str(ports[0].get("targetPort")) != str(expected_target):
        return False, f"Expected targetPort={expected_target}."

    # ---- 5. Endpoints actually wired up ----
    ok, endpoints = resource_inspector.get_endpoints(service_name, namespace)
    if not ok:
        return False, endpoints

    has_ready_address = any(
        subset.get("addresses")
        for subset in endpoints.get("subsets", [])
        if subset.get("addresses")
    )
    if not has_ready_address:
        return False, "No endpoints found. The Service still cannot find Bulba Baby's Pokepod."

    return True, "Signal path restored. Cool Turtle can reach Bulba Baby."
