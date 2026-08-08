"""Read-only access to the Kubernetes cluster via kubectl.

Each function returns a uniform ``(success: bool, payload)`` tuple. ``payload``
is the parsed JSON (a dict for singular resources, a list for plural) on
success, and a player-readable error string on failure. Validators consume
these tuples with a simple ``if not ok: return False, payload`` pattern."""

import json
import subprocess


DEFAULT_TIMEOUT_SECONDS = 5
EXEC_TIMEOUT_SECONDS = 15


def _run_kubectl(args, timeout=DEFAULT_TIMEOUT_SECONDS):
    """Invoke kubectl with ``args``. Returns (returncode, stdout, stderr, timed_out)."""
    try:
        result = subprocess.run(
            ["kubectl", *args],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.returncode, result.stdout, result.stderr, False
    except subprocess.TimeoutExpired:
        return None, "", "", True


def _fetch_resource(kind, name, namespace, timeout=DEFAULT_TIMEOUT_SECONDS):
    """Fetch a single named resource. Returns (ok, dict_or_error_message)."""
    returncode, stdout, stderr, timed_out = _run_kubectl(
        ["get", kind, name, "-n", namespace, "-o", "json"], timeout=timeout
    )
    if timed_out:
        return False, f"Cluster connection timed out while fetching {kind} '{name}'."
    if returncode != 0:
        if "not found" in (stderr or "").lower():
            return False, f"{kind.capitalize()} '{name}' not found in namespace '{namespace}'."
        return False, (stderr or "").strip() or f"Unable to fetch {kind} '{name}'."
    try:
        return True, json.loads(stdout)
    except json.JSONDecodeError:
        return False, f"Could not parse {kind} '{name}' as JSON."


def _fetch_cluster_resource(kind, name, timeout=DEFAULT_TIMEOUT_SECONDS):
    """Fetch a single cluster-scoped resource. Returns (ok, dict_or_error_message)."""
    returncode, stdout, stderr, timed_out = _run_kubectl(
        ["get", kind, name, "-o", "json"], timeout=timeout
    )
    if timed_out:
        return False, f"Cluster connection timed out while fetching {kind} '{name}'."
    if returncode != 0:
        if "not found" in (stderr or "").lower():
            return False, f"{kind.capitalize()} '{name}' not found."
        return False, (stderr or "").strip() or f"Unable to fetch {kind} '{name}'."
    try:
        return True, json.loads(stdout)
    except json.JSONDecodeError:
        return False, f"Could not parse {kind} '{name}' as JSON."


def _list_resources(kind, namespace, label_selector=None, timeout=DEFAULT_TIMEOUT_SECONDS):
    """List resources of ``kind`` in ``namespace``. Returns (ok, list_or_error_message)."""
    args = ["get", kind, "-n", namespace, "-o", "json"]
    if label_selector:
        args.extend(["-l", label_selector])
    returncode, stdout, stderr, timed_out = _run_kubectl(args, timeout=timeout)
    if timed_out:
        return False, f"Cluster connection timed out while listing {kind} in '{namespace}'."
    if returncode != 0:
        return False, (stderr or "").strip() or f"Unable to list {kind} in '{namespace}'."
    try:
        parsed = json.loads(stdout)
    except json.JSONDecodeError:
        return False, f"Could not parse {kind} list as JSON."
    return True, parsed.get("items", [])


def get_deployments(namespace, label_selector=None):
    return _list_resources("deployments", namespace, label_selector=label_selector)


def get_deployment(name, namespace):
    return _fetch_resource("deployment", name, namespace)


def get_pod(name, namespace):
    return _fetch_resource("pod", name, namespace)


def get_pods(namespace, label_selector=None):
    return _list_resources("pods", namespace, label_selector=label_selector)


def get_service_account(name, namespace):
    return _fetch_resource("serviceaccount", name, namespace)


def get_service(name, namespace):
    return _fetch_resource("service", name, namespace)


def get_services(namespace):
    return _list_resources("services", namespace)


def get_endpoints(name, namespace):
    """Fetch the Endpoints object that shares ``name`` with its Service."""
    return _fetch_resource("endpoints", name, namespace)


def get_ingress(name, namespace):
    return _fetch_resource("ingress", name, namespace)


def get_ingresses(namespace):
    return _list_resources("ingresses", namespace)


def get_config_map(name, namespace):
    return _fetch_resource("configmap", name, namespace)


def get_secret(name, namespace):
    return _fetch_resource("secret", name, namespace)


def get_persistent_volume_claim(name, namespace):
    return _fetch_resource("persistentvolumeclaim", name, namespace)


def get_persistent_volume(name):
    return _fetch_cluster_resource("persistentvolume", name)


def get_storage_class(name):
    return _fetch_cluster_resource("storageclass", name)


def get_role(name, namespace):
    return _fetch_resource("role", name, namespace)


def get_role_binding(name, namespace):
    return _fetch_resource("rolebinding", name, namespace)


def get_cluster_role(name):
    return _fetch_cluster_resource("clusterrole", name)


def get_cluster_role_binding(name):
    return _fetch_cluster_resource("clusterrolebinding", name)


def can_i(
    verb,
    resource,
    namespace,
    service_account,
    resource_name=None,
    service_account_namespace=None,
):
    """Return whether a ServiceAccount can perform an action via kubectl auth can-i."""
    service_account_namespace = service_account_namespace or namespace
    resource_arg = f"{resource}/{resource_name}" if resource_name else resource
    args = ["auth", "can-i", verb, resource_arg]
    args.extend([
        "-n",
        namespace,
        f"--as=system:serviceaccount:{service_account_namespace}:{service_account}",
    ])
    returncode, stdout, stderr, timed_out = _run_kubectl(args)
    if timed_out:
        return False, "Cluster connection timed out while checking access."
    if returncode != 0:
        return False, (stderr or "").strip() or "Unable to check access."
    answer = stdout.strip().lower()
    if answer not in {"yes", "no"}:
        return False, f"Unexpected access check response: {stdout.strip()}"
    return True, answer == "yes"


def exec_in_pod(pod_name, namespace, command, container=None, timeout=EXEC_TIMEOUT_SECONDS):
    """Run ``command`` (list of args) inside ``pod_name`` via ``kubectl exec``.

    ``container`` selects one container of a multi-container Pod; without it
    kubectl targets the default container.

    Returns ``(ok, stdout_or_error_message)``. ``ok`` is True iff the command
    exited with returncode 0."""
    args = ["exec", pod_name, "-n", namespace]
    if container:
        args.extend(["-c", container])
    args.append("--")
    args.extend(command)
    returncode, stdout, stderr, timed_out = _run_kubectl(args, timeout=timeout)
    if timed_out:
        return False, f"Timed out executing in pod '{pod_name}'."
    if returncode != 0:
        return False, (stderr or "").strip() or f"Command failed inside pod '{pod_name}'."
    return True, stdout
