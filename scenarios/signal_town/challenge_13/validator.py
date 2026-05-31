from challenge_files import challenge_constants
from services import resource_inspector


def validate():
    """Validate Challenge 13: signal-town-gate Ingress must use the nginx class
    and route the expected host to bulba-baby-service:80."""
    namespace = challenge_constants.NAMESPACE_SIGNAL_TOWN
    service_name = challenge_constants.CHALLENGE_8_SERVICE_NAME
    ingress_name = challenge_constants.CHALLENGE_13_INGRESS_NAME

    # ---- 1. Service still has at least one endpoint ----
    ok, endpoints = resource_inspector.get_endpoints(service_name, namespace)
    if not ok:
        return False, endpoints

    address_count = sum(
        len(subset.get("addresses", []))
        for subset in endpoints.get("subsets", [])
    )
    if address_count < 1:
        return False, "bulba-baby-service has no endpoints. Ensure Bulba Baby's Pokepod is running."

    # ---- 2. Ingress exists ----
    ok, ingress = resource_inspector.get_ingress(ingress_name, namespace)
    if not ok:
        return False, ingress

    spec = ingress.get("spec", {})

    # ---- 3. Ingress class ----
    if spec.get("ingressClassName") != challenge_constants.CHALLENGE_13_INGRESS_CLASS:
        return False, f"Expected ingressClassName={challenge_constants.CHALLENGE_13_INGRESS_CLASS}."

    # ---- 4. Rule host ----
    rules = spec.get("rules", [])
    if not rules:
        return False, "Ingress has no routing rules configured."

    if rules[0].get("host") != challenge_constants.CHALLENGE_13_INGRESS_HOST:
        return False, f"Expected host={challenge_constants.CHALLENGE_13_INGRESS_HOST}."

    # ---- 5. Backend wiring ----
    paths = rules[0].get("http", {}).get("paths", [])
    if not paths:
        return False, "Ingress rule has no HTTP paths configured."

    backend = paths[0].get("backend", {}).get("service", {})
    if backend.get("name") != service_name:
        return False, f"Expected backend service name {service_name}."
    if backend.get("port", {}).get("number") != challenge_constants.CHALLENGE_8_SERVICE_PORT:
        return False, f"Expected backend port {challenge_constants.CHALLENGE_8_SERVICE_PORT}."

    return True, "Signal Town's front door routes to Bulba Baby. Ingress is configured."
