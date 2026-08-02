import base64
import os
import subprocess
from pathlib import Path

import yaml

HOSTED_LABS_ROOT = Path(__file__).resolve().parents[1]
SESSIONS_DIR = HOSTED_LABS_ROOT / "sessions"
DEFAULT_K3S_KUBECONFIG = Path("/etc/rancher/k3s/k3s.yaml")

PLAYER_SERVICE_ACCOUNT = "player"
TOKEN_DURATION = "24h"
CLUSTER_NAME = "yellow-olive-labs"


def resolve_admin_kubeconfig() -> Path:
    kubeconfig_env = os.environ.get("KUBECONFIG", "").strip()
    if kubeconfig_env:
        first_path = Path(kubeconfig_env.split(os.pathsep)[0])
        if first_path.is_file():
            return first_path

    user_config = Path.home() / ".kube" / "config"
    if user_config.is_file():
        return user_config

    if DEFAULT_K3S_KUBECONFIG.is_file():
        return DEFAULT_K3S_KUBECONFIG

    raise RuntimeError(
        "Admin kubeconfig not found. Copy k3s config to ~/.kube/config or set KUBECONFIG."
    )


def admin_kubectl_env() -> dict[str, str]:
    env = os.environ.copy()
    env["KUBECONFIG"] = str(resolve_admin_kubeconfig())
    return env


def load_admin_cluster_info() -> tuple[str, str]:
    with resolve_admin_kubeconfig().open() as kubeconfig_handle:
        config = yaml.safe_load(kubeconfig_handle)

    context_name = config.get("current-context")
    if not context_name:
        raise RuntimeError("Admin kubeconfig has no current-context")

    context = next(
        entry["context"]
        for entry in config["contexts"]
        if entry["name"] == context_name
    )
    cluster_name = context["cluster"]
    cluster = next(
        entry["cluster"]
        for entry in config["clusters"]
        if entry["name"] == cluster_name
    )

    server = cluster["server"]
    certificate_authority_data = cluster.get("certificate-authority-data", "")
    if not certificate_authority_data and "certificate-authority" in cluster:
        certificate_authority_data = base64.b64encode(
            Path(cluster["certificate-authority"]).read_bytes()
        ).decode()

    if not server or not certificate_authority_data:
        raise RuntimeError("Admin kubeconfig is missing cluster server or CA data")

    return server, certificate_authority_data


def create_service_account_token(namespace: str) -> str:
    result = subprocess.run(
        [
            "kubectl",
            "create",
            "token",
            PLAYER_SERVICE_ACCOUNT,
            "-n",
            namespace,
            f"--duration={TOKEN_DURATION}",
        ],
        capture_output=True,
        text=True,
        check=False,
        env=admin_kubectl_env(),
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        raise RuntimeError(detail or "kubectl create token failed")

    token = result.stdout.strip()
    if not token:
        raise RuntimeError("kubectl create token returned an empty token")
    return token


def write_player_kubeconfig(namespace: str) -> Path:
    server, certificate_authority_data = load_admin_cluster_info()
    token = create_service_account_token(namespace)

    kubeconfig = {
        "apiVersion": "v1",
        "kind": "Config",
        "clusters": [
            {
                "name": CLUSTER_NAME,
                "cluster": {
                    "server": server,
                    "certificate-authority-data": certificate_authority_data,
                },
            }
        ],
        "users": [{"name": namespace, "user": {"token": token}}],
        "contexts": [
            {
                "name": namespace,
                "context": {
                    "cluster": CLUSTER_NAME,
                    "user": namespace,
                    "namespace": namespace,
                },
            }
        ],
        "current-context": namespace,
    }

    session_dir = SESSIONS_DIR / namespace
    session_dir.mkdir(parents=True, exist_ok=True)
    os.chmod(session_dir, 0o700)

    kubeconfig_path = session_dir / "kubeconfig"
    with kubeconfig_path.open("w") as kubeconfig_handle:
        yaml.safe_dump(kubeconfig, kubeconfig_handle, default_flow_style=False)
    os.chmod(kubeconfig_path, 0o600)

    return kubeconfig_path


def generate_player_kubeconfig(namespace: str) -> Path:
    return write_player_kubeconfig(namespace)
