from challenge_files import challenge_constants
from services import resource_inspector


def validate():
    """Validate Challenge 18: ClusterRole grants public notice access, not Vault access."""
    namespace = challenge_constants.NAMESPACE_GOLD_RUSH_CITY
    service_account = challenge_constants.CHALLENGE_16_SERVICE_ACCOUNT_NAME
    cluster_role_name = challenge_constants.CHALLENGE_18_CLUSTER_ROLE_NAME
    cluster_role_binding_name = challenge_constants.CHALLENGE_18_CLUSTER_ROLE_BINDING_NAME
    vault_secret = challenge_constants.CHALLENGE_17_VAULT_SECRET_NAME

    ok, cluster_role = resource_inspector.get_cluster_role(cluster_role_name)
    if not ok:
        return False, cluster_role

    rules = cluster_role.get("rules", [])
    if not rules:
        return False, "The territory permit has no rules yet."

    allowed_verbs = {"get", "list"}
    saw_notice_rule = False
    for rule in rules:
        api_groups = set(rule.get("apiGroups", []))
        resources = set(rule.get("resources", []))
        verbs = set(rule.get("verbs", []))

        if "*" in api_groups or api_groups - {""}:
            return False, "The territory permit should only use the core API group."
        if "*" in resources or resources - {"configmaps"}:
            return False, "The territory permit should only point to public claim notices."
        if "*" in verbs or verbs - allowed_verbs:
            return False, "The territory permit should only allow read-only access."
        if resources == {"configmaps"} and allowed_verbs.issubset(verbs):
            saw_notice_rule = True

    if not saw_notice_rule:
        return False, "Allow read-only access to public claim notices."

    ok, cluster_role_binding = resource_inspector.get_cluster_role_binding(
        cluster_role_binding_name
    )
    if not ok:
        return False, cluster_role_binding

    role_ref = cluster_role_binding.get("roleRef", {})
    if role_ref.get("kind") != "ClusterRole" or role_ref.get("name") != cluster_role_name:
        return False, f"ClusterRoleBinding should point to {cluster_role_name}."

    expected_subject = {
        "kind": "ServiceAccount",
        "name": service_account,
        "namespace": namespace,
    }
    subjects = cluster_role_binding.get("subjects", [])
    if subjects != [expected_subject]:
        return False, "Only claim-inspector-sa should hold the territory notice permit."

    ok, can_read_gold_vault = resource_inspector.can_i(
        "get", "secret", namespace, service_account, resource_name=vault_secret
    )
    if not ok:
        return False, can_read_gold_vault
    if can_read_gold_vault:
        return False, "claim-inspector-sa can still read the Gold Rush City Vault."

    ok, can_read_default_secrets = resource_inspector.can_i(
        "list",
        "secrets",
        challenge_constants.NAMESPACE_DEFAULT,
        service_account,
        service_account_namespace=namespace,
    )
    if not ok:
        return False, can_read_default_secrets
    if can_read_default_secrets:
        return False, "claim-inspector-sa can still read Vault records outside Gold Rush City."

    ok, can_read_notices = resource_inspector.can_i(
        "list", "configmaps", namespace, service_account
    )
    if not ok:
        return False, can_read_notices
    if not can_read_notices:
        return False, "claim-inspector-sa should still read public claim notices."

    return True, "The territory-wide permit is safe. Vault access is closed."
