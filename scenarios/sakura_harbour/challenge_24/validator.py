from challenge_files import challenge_constants
from services import resource_inspector


def validate():
    namespace = challenge_constants.NAMESPACE_SAKURA_HARBOUR
    stable_name = challenge_constants.CHALLENGE_24_STABLE_DEPLOYMENT_NAME
    canary_name = challenge_constants.CHALLENGE_24_CANARY_DEPLOYMENT_NAME
    expected_image = challenge_constants.CHALLENGE_24_IMAGE
    stable_replicas = challenge_constants.CHALLENGE_24_STABLE_REPLICAS
    canary_replicas = challenge_constants.CHALLENGE_24_CANARY_REPLICAS

    ok, stable = resource_inspector.get_deployment(stable_name, namespace)
    if not ok:
        return False, stable

    stable_ready = stable.get("status", {}).get("readyReplicas", 0) or 0
    if stable_ready < stable_replicas:
        return (
            False,
            "The main customs lanes are still coming online. Try again shortly.",
        )

    ok, canary = resource_inspector.get_deployment(canary_name, namespace)
    if not ok:
        return False, canary

    containers = (
        canary.get("spec", {})
        .get("template", {})
        .get("spec", {})
        .get("containers", [])
    )
    if not containers or containers[0].get("image") != expected_image:
        return (
            False,
            "Lane B is still using the broken scanner image. "
            f"Set customs-canary to {expected_image}.",
        )

    canary_ready = canary.get("status", {}).get("readyReplicas", 0) or 0
    if canary_ready < canary_replicas:
        return (
            False,
            "Lane B is still rolling out. Wait for the canary PokePod to become ready.",
        )

    return True, "Lane B holds. Master Hana nods. The trial lane is safe."
