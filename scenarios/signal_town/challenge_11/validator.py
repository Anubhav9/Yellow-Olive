from challenge_files import challenge_constants
from services import resource_inspector


def validate():
    """Validate Challenge 11: bulba-baby-service must be flipped to NodePort
    with the required port/targetPort/nodePort, and have at least one endpoint."""
    namespace = challenge_constants.NAMESPACE_SIGNAL_TOWN
    service_name = challenge_constants.CHALLENGE_8_SERVICE_NAME

    # ---- 1. Service exists ----
    ok, service = resource_inspector.get_service(service_name, namespace)
    if not ok:
        return False, "Signal path not found. Is bulba-baby-service deployed in signal-town?"

    spec = service.get("spec", {})

    # ---- 2. Service type ----
    if spec.get("type") != "NodePort":
        return False, "Expected Service type NodePort."

    # ---- 3. Port / targetPort / nodePort ----
    ports = spec.get("ports", [])
    if not ports:
        return False, "No ports configured on the Service."

    port = ports[0].get("port")
    target_port = ports[0].get("targetPort")
    node_port = ports[0].get("nodePort")

    if port != challenge_constants.CHALLENGE_11_SERVICE_PORT:
        return False, f"Expected port={challenge_constants.CHALLENGE_11_SERVICE_PORT}."
    if str(target_port) != str(challenge_constants.CHALLENGE_11_TARGET_PORT):
        return False, f"Expected targetPort={challenge_constants.CHALLENGE_11_TARGET_PORT}."
    if node_port != challenge_constants.CHALLENGE_11_NODE_PORT:
        return False, f"Expected nodePort={challenge_constants.CHALLENGE_11_NODE_PORT}."

    # ---- 4. Endpoints actually wired up ----
    ok, endpoints = resource_inspector.get_endpoints(service_name, namespace)
    if not ok:
        return False, endpoints

    has_ready_address = any(
        subset.get("addresses")
        for subset in endpoints.get("subsets", [])
        if subset.get("addresses")
    )
    if not has_ready_address:
        return False, "No endpoints found. Bulba Baby must be reachable behind the gate."

    return True, "NodePort gate is open. Outsiders can reach Signal Town."
