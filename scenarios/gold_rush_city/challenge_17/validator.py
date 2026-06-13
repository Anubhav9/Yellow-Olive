from challenge_files import challenge_constants
from scenarios.gold_rush_city.challenge_16.validator import validate as validate_notice_binding
from services import resource_inspector


def validate():
    """Validate Challenge 17: Vault access belongs only to mayor-audit-sa."""
    namespace = challenge_constants.NAMESPACE_GOLD_RUSH_CITY
    claim_inspector_sa = challenge_constants.CHALLENGE_16_SERVICE_ACCOUNT_NAME
    mayor_audit_sa = challenge_constants.CHALLENGE_17_MAYOR_AUDIT_SERVICE_ACCOUNT_NAME
    role_name = challenge_constants.CHALLENGE_17_ROLE_NAME
    role_binding_name = challenge_constants.CHALLENGE_17_ROLE_BINDING_NAME
    vault_secret = challenge_constants.CHALLENGE_17_VAULT_SECRET_NAME

    notice_ok, notice_message = validate_notice_binding()
    if not notice_ok:
        return False, f"The notice-board licence is not fixed yet. {notice_message}"

    ok, service_account = resource_inspector.get_service_account(
        mayor_audit_sa, namespace
    )
    if not ok:
        return False, service_account

    ok, role = resource_inspector.get_role(role_name, namespace)
    if not ok:
        return False, role

    ok, role_binding = resource_inspector.get_role_binding(
        role_binding_name, namespace
    )
    if not ok:
        return False, role_binding

    role_ref = role_binding.get("roleRef", {})
    if role_ref.get("kind") != "Role" or role_ref.get("name") != role_name:
        return False, f"vault-access should point to Role {role_name}."

    expected_subject = {
        "kind": "ServiceAccount",
        "name": mayor_audit_sa,
        "namespace": namespace,
    }
    subjects = role_binding.get("subjects", [])
    if subjects != [expected_subject]:
        return False, "Only mayor-audit-sa should hold the Vault access licence."

    ok, claim_can_read_vault = resource_inspector.can_i(
        "get", "secret", namespace, claim_inspector_sa, resource_name=vault_secret
    )
    if not ok:
        return False, claim_can_read_vault
    if claim_can_read_vault:
        return False, "claim-inspector-sa can still read the Vault Secret."

    ok, mayor_can_read_vault = resource_inspector.can_i(
        "get", "secret", namespace, mayor_audit_sa, resource_name=vault_secret
    )
    if not ok:
        return False, mayor_can_read_vault
    if not mayor_can_read_vault:
        return False, "mayor-audit-sa should be able to read the Vault Secret."

    return True, "The Vault licence now belongs only to the Mayor's audit identity."
