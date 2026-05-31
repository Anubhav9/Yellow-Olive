from challenge_files import challenge_constants
from services import resource_inspector


EXPECTED_COMMAND_PHRASE = "electromon show your power"


def validate():
    """Validate Challenge 3: container command must print 'Electromon show your power'."""
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

    # ---- 3. command/args contain the expected phrase ----
    container = containers[0]
    rendered = " ".join(
        str(token) for token in container.get("command", []) + container.get("args", [])
    ).lower()

    if EXPECTED_COMMAND_PHRASE not in rendered:
        return False, "Expected container command to print: Electromon show your power"

    return True, "Container command looks correct."
