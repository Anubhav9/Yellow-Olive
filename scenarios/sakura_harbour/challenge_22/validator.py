from challenge_files import challenge_constants
from services import resource_inspector


def validate():
    namespace = challenge_constants.NAMESPACE_SAKURA_HARBOUR
    deployment_name = challenge_constants.CHALLENGE_22_DEPLOYMENT_NAME
    expected_image = challenge_constants.CHALLENGE_22_IMAGE

    ok, deployment = resource_inspector.get_deployment(deployment_name, namespace)
    if not ok:
        return False, deployment

    containers = (
        deployment.get("spec", {})
        .get("template", {})
        .get("spec", {})
        .get("containers", [])
    )
    if not containers:
        return False, "The luggage-scanner roster has no container defined."

    image = containers[0].get("image")
    if image != expected_image:
        return (
            False,
            f"The luggage-scanner roster still points at the wrong image. "
            f"Use {expected_image}.",
        )

    replicas = deployment.get("spec", {}).get("replicas", 0)
    ready_replicas = deployment.get("status", {}).get("readyReplicas", 0) or 0
    if ready_replicas < replicas:
        return (
            False,
            "Luggage-scanner PokePods are still rolling into place. "
            "Wait for the rollout, then validate again.",
        )

    return True, "The luggage scanners are awake. Bags move again."
