from challenge_files import challenge_constants
from services import resource_inspector


def validate():
    """Validate Challenge 2: container must declare a livenessProbe at path '/' on port 80."""
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

    # ---- 3. livenessProbe httpGet shape ----
    http_get = containers[0].get("livenessProbe", {}).get("httpGet", {})
    if http_get.get("path") != "/" or str(http_get.get("port")) != "80":
        return False, "Expected livenessProbe httpGet path='/' and port=80."

    return True, "Liveness probe is correctly configured."
