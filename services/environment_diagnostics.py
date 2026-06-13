"""Preflight checks for Yellow Olive lab dependencies."""

from __future__ import annotations

from dataclasses import dataclass
import grp
import os
import platform
import shutil
import subprocess
import sys

MIN_PYTHON_VERSION = (3, 10)
COMMAND_TIMEOUT_SECONDS = 10

MINIKUBE_INSTALL_HINT = (
    "Install Minikube before starting Yellow Olive.\n"
    "See: https://minikube.sigs.k8s.io/docs/start/"
)
KUBECTL_INSTALL_HINT = (
    "Install kubectl before starting Yellow Olive.\n"
    "See: https://kubernetes.io/docs/tasks/tools/"
)
LINUX_DOCKER_GROUP_HINT = (
    "Your user cannot access Docker yet.\n"
    "Run in your terminal:\n"
    "  sudo usermod -aG docker $USER\n"
    "Then log out and log back in (or reboot).\n"
    "Verify with: docker ps"
)
LINUX_DOCKER_STALE_SESSION_HINT = (
    "Your user is in the docker group, but this terminal session has not picked it up yet.\n"
    "Log out and log back in (or reboot), then verify with: docker ps"
)


@dataclass(frozen=True)
class CheckResult:
    name: str
    passed: bool
    status_line: str
    fix_hint: str | None = None


@dataclass(frozen=True)
class EnvironmentReport:
    system_info: str
    checks: tuple[CheckResult, ...]

    @property
    def all_passed(self) -> bool:
        return all(check.passed for check in self.checks)


def get_system_info() -> str:
    python_version = (
        f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    )
    system = platform.system()

    if system == "Linux":
        try:
            os_release = platform.freedesktop_os_release()
            os_label = os_release.get("PRETTY_NAME", f"Linux ({platform.release()})")
        except OSError:
            os_label = f"Linux ({platform.release()})"
    elif system == "Darwin":
        mac_version = platform.mac_ver()[0] or platform.release()
        os_label = f"macOS ({mac_version})"
    elif system == "Windows":
        os_label = f"Windows ({platform.release()})"
    else:
        os_label = f"{system} ({platform.release()})"

    return f"Python {python_version} · {os_label}"


def _docker_install_hint() -> str:
    return (
        "Install Docker before starting Yellow Olive.\n"
        "See: https://docs.docker.com/get-docker/"
    )


def _docker_daemon_not_running_hint() -> str:
    system = platform.system()
    if system == "Linux":
        return (
            "Docker is installed, but the daemon is not running.\n"
            "Start the Docker service, then verify with: docker info\n"
            "Example: sudo systemctl start docker"
        )
    if system in {"Darwin", "Windows"}:
        return (
            "Docker is installed, but the daemon is not running.\n"
            "Open Docker Desktop, wait until it finishes starting, then verify with: docker info"
        )
    return (
        "Docker is installed, but the daemon is not running.\n"
        "Start Docker, then verify with: docker info"
    )


def _docker_permission_denied_hint() -> str:
    if platform.system() == "Linux":
        if _user_in_docker_group():
            return LINUX_DOCKER_STALE_SESSION_HINT
        return LINUX_DOCKER_GROUP_HINT

    return (
        "Docker is installed, but this user cannot access the Docker socket.\n"
        "Open Docker Desktop, wait until it finishes starting, then verify with: docker info"
    )


def _docker_unreachable_hint(detail: str | None = None) -> str:
    lines = [
        "Docker is installed, but Yellow Olive could not reach the daemon.",
        "Run `docker info` in your terminal for details.",
    ]
    if detail:
        lines.append(f"Docker reported: {detail}")
    lines.append("See: https://docs.docker.com/get-docker/")
    return "\n".join(lines)


def _run_command(command: list[str]) -> subprocess.CompletedProcess[str] | None:
    try:
        return subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=COMMAND_TIMEOUT_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return None


def _user_in_docker_group() -> bool:
    if platform.system() != "Linux":
        return False

    try:
        docker_group = grp.getgrnam("docker")
    except KeyError:
        return False

    if docker_group.gr_gid in os.getgroups():
        return True

    try:
        import pwd

        username = pwd.getpwuid(os.getuid()).pw_name
    except (ImportError, KeyError, OSError):
        return False

    return username in docker_group.gr_mem


def _command_output_snippet(result: subprocess.CompletedProcess[str]) -> str | None:
    for stream in (result.stderr, result.stdout):
        if not stream:
            continue
        line = stream.strip().splitlines()[0].strip()
        if line:
            return line
    return None


def _check_python_version() -> CheckResult:
    current = sys.version_info[:3]
    version_label = f"{current[0]}.{current[1]}.{current[2]}"
    required_label = f"{MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]}+"

    if current[:2] >= MIN_PYTHON_VERSION:
        return CheckResult(
            name="Python",
            passed=True,
            status_line=f"{version_label} (requires {required_label})",
        )

    return CheckResult(
        name="Python",
        passed=False,
        status_line=f"{version_label} (requires {required_label})",
        fix_hint=(
            f"Install Python {required_label} and run Yellow Olive with that interpreter."
        ),
    )


def _check_docker() -> CheckResult:
    if shutil.which("docker") is None:
        return CheckResult(
            name="Docker",
            passed=False,
            status_line="not installed",
            fix_hint=_docker_install_hint(),
        )

    result = _run_command(["docker", "info"])
    if result is None:
        return CheckResult(
            name="Docker",
            passed=False,
            status_line="daemon check timed out",
            fix_hint=(
                "Docker did not respond within 10 seconds.\n"
                "Make sure the Docker daemon is running, then verify with: docker info"
            ),
        )

    if result.returncode == 0:
        return CheckResult(
            name="Docker",
            passed=True,
            status_line="installed and running",
        )

    combined_output = f"{result.stderr or ''}\n{result.stdout or ''}".lower()
    detail = _command_output_snippet(result)

    if "permission denied" in combined_output:
        if platform.system() == "Linux":
            if _user_in_docker_group():
                status_line = "permission denied (docker group not active in this session)"
            else:
                status_line = "permission denied (user not in docker group)"
        else:
            status_line = "permission denied"
        return CheckResult(
            name="Docker",
            passed=False,
            status_line=status_line,
            fix_hint=_docker_permission_denied_hint(),
        )

    if (
        "cannot connect to the docker daemon" in combined_output
        or "is the docker daemon running" in combined_output
        or "error during connect" in combined_output
    ):
        return CheckResult(
            name="Docker",
            passed=False,
            status_line="installed but not running",
            fix_hint=_docker_daemon_not_running_hint(),
        )

    return CheckResult(
        name="Docker",
        passed=False,
        status_line="installed but not reachable",
        fix_hint=_docker_unreachable_hint(detail),
    )


def _check_minikube() -> CheckResult:
    if shutil.which("minikube") is None:
        return CheckResult(
            name="Minikube",
            passed=False,
            status_line="not installed",
            fix_hint=MINIKUBE_INSTALL_HINT,
        )

    return CheckResult(
        name="Minikube",
        passed=True,
        status_line="installed",
    )


def _check_kubectl() -> CheckResult:
    if shutil.which("kubectl") is None:
        return CheckResult(
            name="kubectl",
            passed=False,
            status_line="not installed",
            fix_hint=KUBECTL_INSTALL_HINT,
        )

    return CheckResult(
        name="kubectl",
        passed=True,
        status_line="installed",
    )


def run_environment_checks() -> EnvironmentReport:
    return EnvironmentReport(
        system_info=get_system_info(),
        checks=(
            _check_python_version(),
            _check_docker(),
            _check_minikube(),
            _check_kubectl(),
        ),
    )


def format_report_for_display(
    report: EnvironmentReport,
    *,
    include_quit_footer: bool = True,
) -> str:
    lines = [
        "[bold]Lab equipment check[/]",
        report.system_info,
        "",
    ]

    for check in report.checks:
        marker = "[green]✓[/]" if check.passed else "[red]✗[/]"
        lines.append(f"{marker} [bold]{check.name}:[/] {check.status_line}")

    if report.all_passed:
        lines.extend(
            [
                "",
                "[green]All basic requirements are met.[/]",
            ]
        )
        return "\n".join(lines)

    lines.extend(
        [
            "",
            "[bold red]Basic requirements for Yellow Olive are not met.[/]",
            "Fix the failed checks below, then quit and start the game again.",
            "",
        ]
    )

    for check in report.checks:
        if check.passed or not check.fix_hint:
            continue
        lines.append(f"[bold]{check.name} - how to fix[/]")
        lines.append(check.fix_hint)
        lines.append("")

    if include_quit_footer:
        lines.append(
            "[yellow]Use Quit from the menu, fix the issues above, and come back when ready.[/]"
        )
    return "\n".join(lines)
