from challenge_files import challenge_constants
from services import resource_inspector


def validate():
    namespace = challenge_constants.NAMESPACE_SAKURA_HARBOUR
    deployment_name = challenge_constants.CHALLENGE_23_DEPLOYMENT_NAME
    expected_image = challenge_constants.CHALLENGE_23_IMAGE
    expected_replicas = challenge_constants.CHALLENGE_23_REPLICAS

    ok, deployment = resource_inspector.get_deployment(deployment_name, namespace)
    if not ok:
        return False, deployment

    containers = (
        deployment.get("spec", {})
        .get("template", {})
        .get("spec", {})
        .get("containers", [])
    )
    if not containers or containers[0].get("image") != expected_image:
        return (
            False,
            f"The boarding-gate rollout is still pointed at a bad image. "
            f"Use {expected_image}.",
        )

    replicas = deployment.get("spec", {}).get("replicas", 0)
    if replicas != expected_replicas:
        return (
            False,
            f"The boarding-gate roster should keep {expected_replicas} PokePods.",
        )

    status = deployment.get("status", {})
    ready_replicas = status.get("readyReplicas", 0) or 0
    updated_replicas = status.get("updatedReplicas", 0) or 0
    if ready_replicas < expected_replicas or updated_replicas < expected_replicas:
        return (
            False,
            "The boarding-gate rollout is still in progress. "
            "Wait for every PokePod to become ready.",
        )

    return True, "The gates finished upgrading. The queue never closed."
