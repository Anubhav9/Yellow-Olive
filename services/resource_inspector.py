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


def get_pod(name, namespace):
    return _fetch_resource("pod", name, namespace)


def get_pods(namespace, label_selector=None):
    return _list_resources("pods", namespace, label_selector=label_selector)


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


def exec_in_pod(pod_name, namespace, command, timeout=EXEC_TIMEOUT_SECONDS):
    """Run ``command`` (list of args) inside ``pod_name`` via ``kubectl exec``.

    Returns ``(ok, stdout_or_error_message)``. ``ok`` is True iff the command
    exited with returncode 0."""
    returncode, stdout, stderr, timed_out = _run_kubectl(
        ["exec", pod_name, "-n", namespace, "--", *command], timeout=timeout
    )
    if timed_out:
        return False, f"Timed out executing in pod '{pod_name}'."
    if returncode != 0:
        return False, (stderr or "").strip() or f"Command failed inside pod '{pod_name}'."
    return True, stdout
