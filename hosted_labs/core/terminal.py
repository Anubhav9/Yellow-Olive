import os
import shlex
import subprocess
from pathlib import Path

HOSTED_LABS_ROOT = Path(__file__).resolve().parents[1]
SESSIONS_DIR = HOSTED_LABS_ROOT / "sessions"

BLOCKED_KUBECTL_FLAGS = {
    "-n",
    "--namespace",
    "--as",
    "--as-group",
    "--token",
    "--kubeconfig",
    "--context",
    "--server",
    "--cluster",
    "--user",
}

SHELL_METACHARACTERS = (";", "|", "&", "`", "$(", ">", "<", "\n", "\r")


class TerminalError(Exception):
    pass


def get_user_kubeconfig_path(formatted_github_user_id: str) -> Path | None:
    kubeconfig_path = SESSIONS_DIR / formatted_github_user_id / "kubeconfig"
    if kubeconfig_path.is_file():
        return kubeconfig_path
    return None


def welcome_message(namespace: str) -> str:
    return (
        "Yellow Olive Hosted Labs — kubectl session\r\n"
        f"Namespace: {namespace}\r\n"
        "Type kubectl commands (example: kubectl get pods)\r\n"
        "\r\n"
    )


def build_kubectl_argv(command_line: str, namespace: str) -> list[str]:
    command_line = command_line.strip()
    if not command_line:
        raise TerminalError("")

    if not command_line.startswith("kubectl"):
        raise TerminalError("Only kubectl commands are allowed.")

    for character in SHELL_METACHARACTERS:
        if character in command_line:
            raise TerminalError("Shell operators are not allowed.")

    tokens = shlex.split(command_line)
    if not tokens or tokens[0] != "kubectl":
        raise TerminalError("Only kubectl commands are allowed.")

    filtered_tokens: list[str] = []
    skip_next = False
    for token in tokens[1:]:
        if skip_next:
            skip_next = False
            continue

        if token in BLOCKED_KUBECTL_FLAGS:
            skip_next = True
            continue

        if any(token.startswith(f"{flag}=") for flag in BLOCKED_KUBECTL_FLAGS):
            continue

        filtered_tokens.append(token)

    return ["kubectl", "--namespace", namespace, *filtered_tokens]


def run_kubectl_command(
    command_line: str,
    namespace: str,
    formatted_github_user_id: str,
) -> str:
    argv = build_kubectl_argv(command_line, namespace)
    if not argv:
        return ""

    env = os.environ.copy()
    kubeconfig_path = get_user_kubeconfig_path(formatted_github_user_id)
    if kubeconfig_path is not None:
        env["KUBECONFIG"] = str(kubeconfig_path)

    result = subprocess.run(
        argv,
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    output = (result.stdout or "") + (result.stderr or "")
    if not output:
        return f"(exit code {result.returncode})\r\n"
    return output.replace("\n", "\r\n") + ("\r\n" if not output.endswith("\n") else "\r\n")


def execute_terminal_line(
    command_line: str,
    namespace: str,
    formatted_github_user_id: str,
) -> str:
    try:
        return run_kubectl_command(command_line, namespace, formatted_github_user_id)
    except TerminalError as exc:
        message = str(exc).strip()
        if not message:
            return ""
        return f"{message}\r\n"
