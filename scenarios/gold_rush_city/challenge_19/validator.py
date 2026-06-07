from challenge_files import challenge_constants
from services import resource_inspector


def validate():
    """Validate Challenge 19: close Team Evil's forged path to the Vault."""
    namespace = challenge_constants.NAMESPACE_GOLD_RUSH_CITY
    claim_inspector_sa = challenge_constants.CHALLENGE_16_SERVICE_ACCOUNT_NAME
    mayor_audit_sa = challenge_constants.CHALLENGE_17_MAYOR_AUDIT_SERVICE_ACCOUNT_NAME
    team_evil_sa = challenge_constants.CHALLENGE_19_TEAM_EVIL_SERVICE_ACCOUNT_NAME
    notice_role = challenge_constants.CHALLENGE_15_ROLE_NAME
    vault_role = challenge_constants.CHALLENGE_17_ROLE_NAME
    role_binding_name = challenge_constants.CHALLENGE_19_ROLE_BINDING_NAME
    vault_secret = challenge_constants.CHALLENGE_17_VAULT_SECRET_NAME

    ok, service_account = resource_inspector.get_service_account(team_evil_sa, namespace)
    if not ok:
        return False, service_account

    ok, role_binding = resource_inspector.get_role_binding(role_binding_name, namespace)
    if not ok:
        return False, role_binding

    role_ref = role_binding.get("roleRef", {})
    if role_ref.get("kind") != "Role":
        return False, "forged-vault-path should point to a namespace Role."
    if role_ref.get("name") == vault_role:
        return False, "The forged prospector still holds the Vault access licence."
    if role_ref.get("name") != notice_role:
        return (
            False,
            f"Contain the forged identity with the safe notice-board licence ({notice_role}).",
        )

    expected_subject = {
        "kind": "ServiceAccount",
        "name": team_evil_sa,
        "namespace": namespace,
    }
    subjects = role_binding.get("subjects", [])
    if subjects != [expected_subject]:
        return False, "forged-vault-path should still reference team-evil-prospector-sa."

    ok, evil_can_read_vault = resource_inspector.can_i(
        "get", "secret", namespace, team_evil_sa, resource_name=vault_secret
    )
    if not ok:
        return False, evil_can_read_vault
    if evil_can_read_vault:
        return False, "team-evil-prospector-sa can still read the Vault Secret."

    ok, mayor_can_read_vault = resource_inspector.can_i(
        "get", "secret", namespace, mayor_audit_sa, resource_name=vault_secret
    )
    if not ok:
        return False, mayor_can_read_vault
    if not mayor_can_read_vault:
        return False, "mayor-audit-sa should still be able to read the Vault Secret."

    ok, inspector_can_read_notices = resource_inspector.can_i(
        "list", "configmaps", namespace, claim_inspector_sa
    )
    if not ok:
        return False, inspector_can_read_notices
    if not inspector_can_read_notices:
        return False, "claim-inspector-sa should still read public claim notices."

    ok, inspector_can_read_vault = resource_inspector.can_i(
        "get", "secret", namespace, claim_inspector_sa, resource_name=vault_secret
    )
    if not ok:
        return False, inspector_can_read_vault
    if inspector_can_read_vault:
        return False, "claim-inspector-sa should not read the Vault Secret."

    return True, "The theft path is closed. Gold Rush City's access ledger is secure."
