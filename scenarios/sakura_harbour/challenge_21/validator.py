from challenge_files import challenge_constants
from services import resource_inspector


def validate():
    namespace = challenge_constants.NAMESPACE_SAKURA_HARBOUR
    deployment_name = challenge_constants.CHALLENGE_21_DEPLOYMENT_NAME
    app_label = challenge_constants.CHALLENGE_21_APP_LABEL
    min_replicas = challenge_constants.CHALLENGE_21_MIN_REPLICAS
    label_selector = f"app={app_label}"

    ok, deployment = resource_inspector.get_deployment(deployment_name, namespace)
    if not ok:
        return False, deployment

    selector = (
        deployment.get("spec", {})
        .get("selector", {})
        .get("matchLabels", {})
        .get("app")
    )
    template_label = (
        deployment.get("spec", {})
        .get("template", {})
        .get("metadata", {})
        .get("labels", {})
        .get("app")
    )
    if selector != app_label or template_label != app_label:
        return (
            False,
            "The ferry-guide roster is still looking at the wrong name tags. "
            f"Match selector and template labels to app={app_label}.",
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
            "Pier Two still does not have enough ferry-guide PokePods running. "
            "Fix the labels and re-apply the roster.",
        )

    ready_replicas = deployment.get("status", {}).get("readyReplicas", 0) or 0
    if ready_replicas < min_replicas:
        return (
            False,
            "Ferry-guide PokePods are still joining the roster. Try again shortly.",
        )

    return True, "Pier Two is staffed. The harbour board finally shows the guides."
