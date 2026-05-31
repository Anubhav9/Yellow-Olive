from challenge_files import challenge_constants
from services import resource_inspector


def validate():
    """Validate Challenge 12: at least two bulba-baby market stalls must be
    Running, and bulba-baby-service must list at least two endpoint addresses."""
    namespace = challenge_constants.NAMESPACE_SIGNAL_TOWN
    service_name = challenge_constants.CHALLENGE_8_SERVICE_NAME
    label_selector = f"app={challenge_constants.CHALLENGE_8_SELECTOR_APP}"
    min_pods = challenge_constants.CHALLENGE_12_MIN_BULBA_PODS

    # ---- 1. Enough labeled pods are Running ----
    ok, pods = resource_inspector.get_pods(namespace, label_selector=label_selector)
    if not ok:
        return False, pods

    running_count = sum(
        1 for pod in pods if pod.get("status", {}).get("phase") == "Running"
    )
    if running_count < min_pods:
        return (
            False,
            "Only one stall is running. Apply pod-q12-stall-two.yaml "
            "so at least two bulba-baby Pokepods are running.",
        )

    # ---- 2. Service has at least two endpoint addresses ----
    ok, endpoints = resource_inspector.get_endpoints(service_name, namespace)
    if not ok:
        return False, endpoints

    address_count = sum(
        len(subset.get("addresses", []))
        for subset in endpoints.get("subsets", [])
    )
    if address_count < min_pods:
        return (
            False,
            "bulba-baby-service does not have enough endpoints yet. "
            "Ensure both stalls use label app=bulba-baby.",
        )

    return True, "The market district is fully online. Multiple stalls answer the call."
