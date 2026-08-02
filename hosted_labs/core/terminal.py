import os
import shlex
import subprocess
from dataclasses import dataclass, field
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
    def __init__(self, message: str, *, violation: dict | None = None) -> None:
        super().__init__(message)
        self.violation = violation


@dataclass
class TerminalResult:
    output: str
    command_raw: str
    command_executed: str | None = None
    exit_code: int | None = None
    blocked: bool = False
    block_reason: str | None = None
    policy_violations: list[dict] = field(default_factory=list)


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


def _argv_to_command_line(argv: list[str]) -> str:
    return " ".join(shlex.quote(token) for token in argv)


def build_kubectl_argv(command_line: str, namespace: str) -> tuple[list[str], list[dict]]:
    command_line = command_line.strip()
    if not command_line:
        raise TerminalError("")

    if not command_line.startswith("kubectl"):
        raise TerminalError(
            "Only kubectl commands are allowed.",
            violation={"type": "non_kubectl_command", "command_raw": command_line},
        )

    for character in SHELL_METACHARACTERS:
        if character in command_line:
            raise TerminalError(
                "Shell operators are not allowed.",
                violation={
                    "type": "shell_operator",
                    "command_raw": command_line,
                    "character": character,
                },
            )

    tokens = shlex.split(command_line)
    if not tokens or tokens[0] != "kubectl":
        raise TerminalError(
            "Only kubectl commands are allowed.",
            violation={"type": "non_kubectl_command", "command_raw": command_line},
        )

    policy_violations: list[dict] = []
    filtered_tokens: list[str] = []
    skip_next = False
    for token in tokens[1:]:
        if skip_next:
            policy_violations.append(
                {
                    "type": "blocked_flag_value",
                    "command_raw": command_line,
                    "value": token,
                }
            )
            skip_next = False
            continue

        if token in BLOCKED_KUBECTL_FLAGS:
            policy_violations.append(
                {
                    "type": "blocked_flag",
                    "command_raw": command_line,
                    "flag": token,
                }
            )
            skip_next = True
            continue

        blocked_prefix = next(
            (flag for flag in BLOCKED_KUBECTL_FLAGS if token.startswith(f"{flag}=")),
            None,
        )
        if blocked_prefix is not None:
            policy_violations.append(
                {
                    "type": "blocked_flag_assignment",
                    "command_raw": command_line,
                    "assignment": token,
                }
            )
            continue

        filtered_tokens.append(token)

    argv = ["kubectl", "--namespace", namespace, *filtered_tokens]
    return argv, policy_violations


def run_kubectl_command(
    command_line: str,
    namespace: str,
    formatted_github_user_id: str,
) -> TerminalResult:
    argv, policy_violations = build_kubectl_argv(command_line, namespace)
    if not argv:
        return TerminalResult(output="", command_raw=command_line)

    kubeconfig_path = get_user_kubeconfig_path(formatted_github_user_id)
    if kubeconfig_path is None:
        raise TerminalError(
            "Session not bootstrapped. Click Start session before using the terminal.",
            violation={"type": "session_not_bootstrapped", "command_raw": command_line},
        )

    env = os.environ.copy()
    env["KUBECONFIG"] = str(kubeconfig_path)
    command_executed = _argv_to_command_line(argv)

    result = subprocess.run(
        argv,
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    output = (result.stdout or "") + (result.stderr or "")
    if not output:
        output = f"(exit code {result.returncode})\r\n"
    else:
        output = output.replace("\n", "\r\n") + ("\r\n" if not output.endswith("\n") else "\r\n")

    return TerminalResult(
        output=output,
        command_raw=command_line,
        command_executed=command_executed,
        exit_code=result.returncode,
        policy_violations=policy_violations,
    )


def execute_terminal_line(
    command_line: str,
    namespace: str,
    formatted_github_user_id: str,
) -> TerminalResult:
    try:
        return run_kubectl_command(command_line, namespace, formatted_github_user_id)
    except TerminalError as exc:
        message = str(exc).strip()
        violation = exc.violation or {"type": "terminal_error", "command_raw": command_line}
        output = f"{message}\r\n" if message else ""
        return TerminalResult(
            output=output,
            command_raw=command_line,
            blocked=True,
            block_reason=message or violation.get("type"),
            policy_violations=[violation],
        )
