from importlib import import_module
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, Template

BASE_DIR = Path(__file__).resolve().parents[1]

POLICIES_DIR = BASE_DIR / "policies"
CHALLENGES_DIR = BASE_DIR / "challenges"
DEFAULTS_FILE = POLICIES_DIR / "defaults.yaml"

ABSOLUTE_TEMPLATE_DIR = POLICIES_DIR / "absolute"
SPECIFIC_TEMPLATE_DIR = POLICIES_DIR / "specific"

ABSOLUTE_POLICY_TEMPLATES = [
    ("namespace", "namespace_creation/v1/namespace_creation.yaml.j2"),
    ("resource-quota", "resource_quota/v1/resource_quota_creation.yaml.j2"),
    ("network-policy", "network_allow/v1/network_policies.yaml.j2"),
]

CHALLENGE_RBAC_TEMPLATES = [
    ("role", "role_creation/v1/role_creation.yaml.j2"),
    ("service-account", "service_account/v1/service_account.yaml.j2"),
    ("role-binding", "role_binding/v1/role_binding.yaml.j2"),
]


def get_challenge_dir(challenge_slug: str) -> Path:
    challenge_dir = CHALLENGES_DIR / challenge_slug
    if not challenge_dir.is_dir():
        raise FileNotFoundError(f"Challenge not found: {challenge_slug}")
    return challenge_dir


def load_defaults() -> dict:
    with DEFAULTS_FILE.open() as defaults_file:
        return yaml.safe_load(defaults_file)


def build_session_context(
    formatted_github_user_id: str,
    session_id: str,
    defaults: dict,
) -> dict:
    return {
        "formatted_github_user_id": formatted_github_user_id,
        "session_id": session_id,
        **defaults["quota"],
    }


def load_challenge_rbac(challenge_dir: Path) -> dict:
    rbac_file = challenge_dir / "delicate" / "rbac.yaml"
    if not rbac_file.is_file():
        raise FileNotFoundError(f"Missing challenge RBAC config: {rbac_file}")

    with rbac_file.open() as rbac_handle:
        return yaml.safe_load(rbac_handle)


def build_role_context(session_context: dict, rbac: dict) -> dict:
    return {
        **session_context,
        **rbac,
    }


def build_jinja_env(template_dir: Path) -> Environment:
    return Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )


def render_template(env: Environment, template_name: str, context: dict) -> str:
    return env.get_template(template_name).render(**context)


def render_challenge_resources(challenge_dir: Path, context: dict) -> list[tuple[str, str]]:
    resources_dir = challenge_dir / "resources"
    if not resources_dir.is_dir():
        return []

    rendered_resources = []
    for resource_file in sorted(resources_dir.iterdir()):
        if not resource_file.is_file():
            continue
        if resource_file.suffix not in {".yaml", ".yml", ".j2"}:
            continue

        template_source = resource_file.read_text()
        if resource_file.suffix == ".j2" or "{{" in template_source:
            rendered_yaml = Template(template_source).render(**context)
        else:
            rendered_yaml = template_source

        rendered_resources.append((resource_file.name, rendered_yaml))

    return rendered_resources


def apply_manifest(manifest_yaml: str) -> str:
    import subprocess

    from hosted_labs.core.kubeconfig import admin_kubectl_env

    result = subprocess.run(
        ["kubectl", "apply", "-f", "-"],
        input=manifest_yaml,
        capture_output=True,
        text=True,
        check=False,
        env=admin_kubectl_env(),
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        raise RuntimeError(detail or "kubectl apply failed")

    return (result.stdout or result.stderr or "").strip()


def list_challenge_slugs() -> list[str]:
    return sorted(
        challenge_dir.name
        for challenge_dir in CHALLENGES_DIR.iterdir()
        if challenge_dir.is_dir() and challenge_dir.name != "__pycache__"
    )


# POC defaults until GitHub auth is wired up.
POC_GITHUB_ID = "github-12345678"
POC_SESSION_ID = "yo-sess-a8f31"


def load_challenge_text(challenge_slug: str) -> str:
    challenge_module = import_module(f"hosted_labs.challenges.{challenge_slug}.challenge_text")
    for attribute_name in dir(challenge_module):
        if attribute_name.endswith("_TEXT"):
            return getattr(challenge_module, attribute_name)
    raise AttributeError(f"No challenge text constant found for {challenge_slug}")


def bootstrap_challenge_session(
    challenge_slug: str,
    formatted_github_user_id: str,
    session_id: str,
    *,
    apply: bool = True,
) -> dict:
    """Provision absolute policies, challenge RBAC, and starter manifests."""
    challenge_dir = get_challenge_dir(challenge_slug)
    defaults = load_defaults()
    session_context = build_session_context(
        formatted_github_user_id,
        session_id,
        defaults,
    )
    role_context = build_role_context(
        session_context,
        load_challenge_rbac(challenge_dir),
    )

    env_abs = build_jinja_env(ABSOLUTE_TEMPLATE_DIR)
    env_specific = build_jinja_env(SPECIFIC_TEMPLATE_DIR)

    manifests: list[tuple[str, str]] = []

    for policy_name, template_name in ABSOLUTE_POLICY_TEMPLATES:
        manifests.append(
            (
                policy_name,
                render_template(env_abs, template_name, session_context),
            )
        )

    for policy_name, template_name in CHALLENGE_RBAC_TEMPLATES:
        manifests.append(
            (
                policy_name,
                render_template(env_specific, template_name, role_context),
            )
        )

    for resource_name, rendered_yaml in render_challenge_resources(
        challenge_dir,
        session_context,
    ):
        manifests.append((f"resource/{resource_name}", rendered_yaml))

    apply_messages = []
    if apply:
        for manifest_name, manifest_yaml in manifests:
            message = apply_manifest(manifest_yaml)
            apply_messages.append({"name": manifest_name, "message": message})

        from hosted_labs.core.kubeconfig import generate_player_kubeconfig

        kubeconfig_path = generate_player_kubeconfig(formatted_github_user_id)
        apply_messages.append(
            {
                "name": "kubeconfig",
                "message": f"player kubeconfig written to {kubeconfig_path}",
            }
        )

    return {
        "challenge_slug": challenge_slug,
        "formatted_github_user_id": formatted_github_user_id,
        "session_id": session_id,
        "challenge_text": load_challenge_text(challenge_slug),
        "manifests": [{"name": name, "yaml": yaml_content} for name, yaml_content in manifests],
        "apply_messages": apply_messages,
    }


def validate_challenge_session(
    challenge_slug: str,
    formatted_github_user_id: str,
) -> dict:
    """Validate challenge resources against resources/validation.yaml."""
    from hosted_labs.core.validation import validate_challenge_resources

    get_challenge_dir(challenge_slug)
    return validate_challenge_resources(challenge_slug, formatted_github_user_id)
