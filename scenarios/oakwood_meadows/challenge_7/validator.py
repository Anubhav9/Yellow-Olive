from challenge_files import challenge_constants
from services import resource_inspector


def validate():
    """Validate Challenge 7: pod spec must set restartPolicy=Always."""
    pod_name = challenge_constants.CHALLENGE_1_POD_NAME
    namespace = challenge_constants.NAMESPACE_OAKWOOD_MEADOWS

    # ---- 1. Pokepod exists ----
    ok, pod = resource_inspector.get_pod(pod_name, namespace)
    if not ok:
        return False, "Pokepod not found. Is Electromon deployed in this namespace?"

    # ---- 2. restartPolicy ----
    if pod.get("spec", {}).get("restartPolicy") != "Always":
        return False, "Expected restartPolicy=Always."

    return True, "Restart policy is correctly configured."
