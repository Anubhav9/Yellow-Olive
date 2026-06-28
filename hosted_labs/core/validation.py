import json
import subprocess
from pathlib import Path

import yaml

from hosted_labs.core.session import get_challenge_dir

SUPPORTED_KINDS = {"Pod"}


def load_validation_spec(challenge_slug: str) -> dict:
    validation_file = get_challenge_dir(challenge_slug) / "resources" / "validation.yaml"
    if not validation_file.is_file():
        raise FileNotFoundError(f"Missing validation spec: {validation_file}")

    with validation_file.open() as validation_handle:
        return yaml.safe_load(validation_handle)


def _kubectl_get_json(kind: str, name: str, namespace: str) -> tuple[bool, dict | None, str]:
    resource_type = kind.lower()
    result = subprocess.run(
        ["kubectl", "get", resource_type, name, "-n", namespace, "-o", "json"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return False, None, (result.stderr or result.stdout or "").strip()

    return True, json.loads(result.stdout), ""


def _validate_pod(namespace: str, check: dict) -> dict:
    messages = check.get("messages", {})
    pod_name = check["name"]

    found, pod, detail = _kubectl_get_json("Pod", pod_name, namespace)
    if not found:
        return {
            "kind": "Pod",
            "name": pod_name,
            "passed": False,
            "message": messages.get("missing", f"Pod {pod_name} not found in namespace {namespace}."),
            "detail": detail,
        }

    if check.get("ready"):
        container_statuses = pod.get("status", {}).get("containerStatuses", [])
        if not container_statuses:
            return {
                "kind": "Pod",
                "name": pod_name,
                "passed": False,
                "message": messages.get(
                    "pending",
                    f"Pod {pod_name} has no container status yet.",
                ),
            }

        if container_statuses[0].get("ready") is not True:
            return {
                "kind": "Pod",
                "name": pod_name,
                "passed": False,
                "message": messages.get(
                    "not_ready",
                    f"Pod {pod_name} is not ready yet.",
                ),
            }

    return {
        "kind": "Pod",
        "name": pod_name,
        "passed": True,
        "message": messages.get("success", f"Pod {pod_name} passed validation."),
    }


def validate_resource_check(namespace: str, check: dict) -> dict:
    kind = check["kind"]
    if kind not in SUPPORTED_KINDS:
        raise ValueError(f"Unsupported validation kind: {kind}")

    if kind == "Pod":
        return _validate_pod(namespace, check)

    raise ValueError(f"No validator implemented for kind: {kind}")


def validate_challenge_resources(challenge_slug: str, namespace: str) -> dict:
    """Validate challenge resources declared in resources/validation.yaml."""
    spec = load_validation_spec(challenge_slug)
    checks = []

    for resource_check in spec.get("resources", []):
        checks.append(validate_resource_check(namespace, resource_check))

    passed = all(check["passed"] for check in checks)
    if passed:
        message = checks[-1]["message"] if checks else "Challenge passed."
    else:
        message = next(check["message"] for check in checks if not check["passed"])

    return {
        "challenge_slug": challenge_slug,
        "namespace": namespace,
        "passed": passed,
        "message": message,
        "checks": checks,
    }
