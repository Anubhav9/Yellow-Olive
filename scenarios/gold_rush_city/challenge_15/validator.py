from challenge_files import challenge_constants
from services import resource_inspector


def validate():
    """Validate Challenge 15: claim-notice-reader only reads ConfigMaps."""
    namespace = challenge_constants.NAMESPACE_GOLD_RUSH_CITY
    role_name = challenge_constants.CHALLENGE_15_ROLE_NAME

    ok, role = resource_inspector.get_role(role_name, namespace)
    if not ok:
        return False, role

    rules = role.get("rules", [])
    if not rules:
        return False, "The claim-notice-reader licence has no rules yet."

    allowed_verbs = {"get", "list"}
    saw_notice_rule = False

    for rule in rules:
        api_groups = set(rule.get("apiGroups", []))
        resources = set(rule.get("resources", []))
        verbs = set(rule.get("verbs", []))

        if "*" in api_groups or api_groups - {""}:
            return False, "This licence should only use the core API group."
        if "*" in resources or resources - {"configmaps"}:
            return False, "This licence should only point to configmaps."
        if "*" in verbs or verbs - allowed_verbs:
            return False, "This licence should only allow get and list."
        if resources == {"configmaps"} and allowed_verbs.issubset(verbs):
            saw_notice_rule = True

    if not saw_notice_rule:
        return False, "Allow get and list access to configmaps for claim notices."

    return True, "The first licence is safe. It can only read public claim notices."
