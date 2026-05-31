from challenge_files import challenge_constants
from services import resource_inspector


def validate():
    """Validate Challenge 10: trainer-relay-pod in `default` must call
    bulba-baby-service in signal-town using the cross-namespace FQDN."""
    signal_town = challenge_constants.NAMESPACE_SIGNAL_TOWN
    service_name = challenge_constants.CHALLENGE_8_SERVICE_NAME
    relay_pod = challenge_constants.CHALLENGE_10_RELAY_POD_NAME
    relay_namespace = challenge_constants.CHALLENGE_10_RELAY_NAMESPACE
    service_fqdn = challenge_constants.CHALLENGE_10_SERVICE_FQDN.lower()
    short_host = challenge_constants.CHALLENGE_10_SHORT_DNS_HOST.lower()

    # ---- 1. bulba-baby-service in signal-town has endpoints ----
    ok, endpoints = resource_inspector.get_endpoints(service_name, signal_town)
    if not ok:
        return False, endpoints

    has_ready_address = any(
        subset.get("addresses")
        for subset in endpoints.get("subsets", [])
        if subset.get("addresses")
    )
    if not has_ready_address:
        return (
            False,
            "Bulba Baby's Service in signal-town has no endpoints. "
            "Ensure bulba-baby-pod and bulba-baby-service are healthy.",
        )

    # ---- 2. Relay pod exists with a container ----
    ok, pod = resource_inspector.get_pod(relay_pod, relay_namespace)
    if not ok:
        return False, pod

    containers = pod.get("spec", {}).get("containers", [])
    if not containers:
        return False, "No containers found in the trainer relay Pokepod."

    container = containers[0]
    rendered_command = " ".join(
        str(token) for token in container.get("command", []) + container.get("args", [])
    ).lower()

    # ---- 3. Calls the FQDN, not the short host (short host won't resolve cross-ns) ----
    if service_fqdn not in rendered_command:
        return False, f"Expected cross-town call to http://{service_fqdn}/"
    if f"http://{short_host}/" in rendered_command:
        return (
            False,
            "Short Service names only work inside the same namespace. "
            f"Use the full FQDN: {service_fqdn}",
        )

    # ---- 4. The FQDN curl actually succeeds ----
    ok, _stdout = resource_inspector.exec_in_pod(
        relay_pod,
        relay_namespace,
        ["curl", "-sf", f"http://{service_fqdn}/"],
    )
    if not ok:
        return (
            False,
            "FQDN looks correct in the manifest, but the call still failed. "
            "Delete and recreate trainer-relay-pod after fixing the manifest.",
        )

    return True, "Trainer relay reaches Signal Town across namespaces. FQDN DNS is working."
