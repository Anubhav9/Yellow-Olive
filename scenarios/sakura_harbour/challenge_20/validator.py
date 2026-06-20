from challenge_files import challenge_constants
from services import resource_inspector


def validate():
    namespace = challenge_constants.NAMESPACE_SAKURA_HARBOUR
    deployment_name = challenge_constants.CHALLENGE_20_DEPLOYMENT_NAME
    min_replicas = challenge_constants.CHALLENGE_20_MIN_REPLICAS
    label_selector = f"app={challenge_constants.CHALLENGE_20_APP_LABEL}"

    ok, deployment = resource_inspector.get_deployment(deployment_name, namespace)
    if not ok:
        return False, deployment

    replicas = deployment.get("spec", {}).get("replicas", 0)
    if replicas < min_replicas:
        return (
            False,
            "The roster still lists too few ticket checkers. "
            f"Set replicas to at least {min_replicas}.",
        )

    status = deployment.get("status", {})
    ready_replicas = status.get("readyReplicas", 0) or 0
    if ready_replicas < min_replicas:
        return (
            False,
            "Ticket-checker PokePods are still starting. "
            "Wait for the rollout, then validate again.",
        )

    ok, pods = resource_inspector.get_pods(namespace, label_selector=label_selector)
    if not ok:
        return False, pods

    running_count = sum(
        1 for pod in pods if pod.get("status", {}).get("phase") == "Running"
    )
    if running_count < min_replicas:
        return (
            False,
            "Not enough ticket-checker PokePods are running yet.",
        )

    return True, "Gate Three is open. The line finally moves."
