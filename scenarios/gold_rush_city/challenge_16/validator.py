from challenge_files import challenge_constants
from scenarios.gold_rush_city.challenge_15.validator import validate as validate_role
from services import resource_inspector


def validate():
    """Validate Challenge 16: bind claim-inspector-sa to claim-notice-reader."""
    namespace = challenge_constants.NAMESPACE_GOLD_RUSH_CITY
    service_account_name = challenge_constants.CHALLENGE_16_SERVICE_ACCOUNT_NAME
    role_name = challenge_constants.CHALLENGE_15_ROLE_NAME
    role_binding_name = challenge_constants.CHALLENGE_16_ROLE_BINDING_NAME

    role_is_valid, role_message = validate_role()
    if not role_is_valid:
        return False, f"The notice-board licence is not safe yet. {role_message}"

    ok, service_account = resource_inspector.get_service_account(
        service_account_name, namespace
    )
    if not ok:
        return False, service_account

    ok, role_binding = resource_inspector.get_role_binding(
        role_binding_name, namespace
    )
    if not ok:
        return False, role_binding

    role_ref = role_binding.get("roleRef", {})
    if role_ref.get("apiGroup") != "rbac.authorization.k8s.io":
        return False, "RoleBinding roleRef apiGroup should be rbac.authorization.k8s.io."
    if role_ref.get("kind") != "Role":
        return False, "RoleBinding should point to a namespace Role."
    if role_ref.get("name") != role_name:
        return False, f"RoleBinding should point to Role {role_name}."

    subjects = role_binding.get("subjects", [])
    expected_subject = {
        "kind": "ServiceAccount",
        "name": service_account_name,
        "namespace": namespace,
    }
    if expected_subject not in subjects:
        return (
            False,
            "Bind the licence to ServiceAccount claim-inspector-sa in gold-rush-city.",
        )

    extra_subjects = [
        subject for subject in subjects if subject != expected_subject
    ]
    if extra_subjects:
        return False, "Only claim-inspector-sa should hold this licence."

    return True, "The claim inspector now holds the notice-board licence."
