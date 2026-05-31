from challenge_files import challenge_constants
from services import resource_inspector


def validate():
    """Validate Challenge 1: Electromon's Pokepod must be running and ready."""
    pod_name = challenge_constants.CHALLENGE_1_POD_NAME
    namespace = challenge_constants.NAMESPACE_OAKWOOD_MEADOWS

    # ---- 1. Pokepod exists ----
    ok, pod = resource_inspector.get_pod(pod_name, namespace)
    if not ok:
        return False, "Pokepod not found. Is Electromon deployed in this namespace?"

    # ---- 2. Container is ready ----
    container_statuses = pod.get("status", {}).get("containerStatuses", [])
    if not container_statuses:
        return False, "Electromon's Pokepod has no container status yet. Give it a moment, then try again."

    is_ready = container_statuses[0].get("ready") is True
    if not is_ready:
        return False, "Electromon's Pokepod is not ready yet. Inspect the manifest and fix the issue."

    return True, "Electromon is out of the Pokepod and ready for adventure."
