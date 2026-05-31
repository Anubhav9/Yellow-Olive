from challenge_files import challenge_constants
from services import resource_inspector


def validate():
    """Validate Challenge 6: container resource limits must be cpu=500m and memory=256Mi."""
    pod_name = challenge_constants.CHALLENGE_1_POD_NAME
    namespace = challenge_constants.NAMESPACE_OAKWOOD_MEADOWS

    # ---- 1. Pokepod exists ----
    ok, pod = resource_inspector.get_pod(pod_name, namespace)
    if not ok:
        return False, "Pokepod not found. Is Electromon deployed in this namespace?"

    # ---- 2. Container present ----
    containers = pod.get("spec", {}).get("containers", [])
    if not containers:
        return False, "No containers found in the Pokepod."

    # ---- 3. resources.limits ----
    limits = containers[0].get("resources", {}).get("limits", {})
    if limits.get("cpu") != "500m" or limits.get("memory") != "256Mi":
        return False, "Expected resource limits: cpu=500m and memory=256Mi."

    return True, "Resource limits are configured correctly."
