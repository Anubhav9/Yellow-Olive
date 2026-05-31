from challenge_files import challenge_constants
from services import resource_inspector


def validate():
    """Validate Challenge 4: pod metadata must carry labels type=electric and relationship=best-buddy."""
    pod_name = challenge_constants.CHALLENGE_1_POD_NAME
    namespace = challenge_constants.NAMESPACE_OAKWOOD_MEADOWS

    # ---- 1. Pokepod exists ----
    ok, pod = resource_inspector.get_pod(pod_name, namespace)
    if not ok:
        return False, "Pokepod not found. Is Electromon deployed in this namespace?"

    # ---- 2. Labels ----
    labels = pod.get("metadata", {}).get("labels", {})
    if labels.get("type") != "electric" or labels.get("relationship") != "best-buddy":
        return False, "Expected labels: type=electric and relationship=best-buddy."

    return True, "Pod labels are correctly configured."
