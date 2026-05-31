from challenge_files import challenge_constants
from services import resource_inspector


def validate():
    """Validate Challenge 5: container env must include BATTLE_MODE=ON."""
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

    # ---- 3. env var BATTLE_MODE=ON ----
    env_pairs = {
        item.get("name"): item.get("value")
        for item in containers[0].get("env", [])
        if item.get("name")
    }
    if env_pairs.get("BATTLE_MODE") != "ON":
        return False, "Expected env variable BATTLE_MODE=ON."

    return True, "Battle mode env variable is set correctly."
