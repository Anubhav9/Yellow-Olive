from challenge_files import challenge_constants
from services import resource_inspector


def validate():
    """Validate Challenge 14: claim-inspector uses its own ServiceAccount."""
    namespace = challenge_constants.NAMESPACE_GOLD_RUSH_CITY
    pod_name = challenge_constants.CHALLENGE_14_POD_NAME
    service_account_name = challenge_constants.CHALLENGE_14_SERVICE_ACCOUNT_NAME

    ok, service_account = resource_inspector.get_service_account(
        service_account_name, namespace
    )
    if not ok:
        return False, service_account

    ok, pod = resource_inspector.get_pod(pod_name, namespace)
    if not ok:
        return False, pod

    spec = pod.get("spec", {})
    if spec.get("serviceAccountName") != service_account_name:
        return (
            False,
            "claim-inspector is still not using ServiceAccount claim-inspector-sa.",
        )

    phase = pod.get("status", {}).get("phase")
    if phase != "Running":
        return False, "claim-inspector should be Running with its new identity."

    return True, "The claim inspector now has a clear identity in Gold Rush City."
