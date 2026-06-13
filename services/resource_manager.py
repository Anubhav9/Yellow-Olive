from pathlib import Path
import subprocess
import textwrap
import global_constants
from utils import general_utils

MANIFEST_WARNING_LINE_WIDTH = 52


def _kubectl_apply_error_message(resource_path: Path, detail: str) -> str:
    filename = resource_path.name
    header = f"{filename} is waiting for your fix in the lab workspace."

    if not detail:
        return header

    detail_lower = detail.lower()
    if "unsupported value" in detail_lower and "spec.type" in detail_lower:
        return f"{header}\nInvalid Service type in spec.type."

    if "unsupported value" in detail_lower:
        return f"{header}\nManifest has an unsupported value."

    reason = detail.splitlines()[-1].strip()
    if len(reason) > MANIFEST_WARNING_LINE_WIDTH:
        return f"{header}\nkubectl rejected the manifest until you correct it."

    return f"{header}\n{reason}"


def format_manifest_warning_lines(message: str) -> list[str]:
    lines = []
    for paragraph in message.splitlines():
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        if len(paragraph) <= MANIFEST_WARNING_LINE_WIDTH:
            lines.append(paragraph)
            continue
        lines.extend(
            textwrap.wrap(
                paragraph,
                width=MANIFEST_WARNING_LINE_WIDTH,
                break_long_words=False,
                break_on_hyphens=False,
            )
        )
    return lines


def _kubectl_apply(resource_path: Path) -> None:
    result = subprocess.run(
        ["kubectl", "apply", "-f", str(resource_path)],
        capture_output=True,
        text=True,
        check=False,
        cwd=str(global_constants.PROJECT_ROOT),
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        raise RuntimeError(_kubectl_apply_error_message(resource_path, detail))


def iterate_resources(challenge_scenario, challenge_id):
    """Return the player's editable manifests for this challenge.

    Reads from the lab workspace (``yellow-olive-lab/scenarios/...``) so the
    game applies whatever the player has edited there, not the pristine source
    in the repo. ``ensure_lab_workspace`` is invoked to copy any new source
    manifests on first run without clobbering existing player edits."""
    lab_root = general_utils.ensure_lab_workspace()

    path = (
        lab_root
        / "scenarios"
        / challenge_scenario
        / f"challenge_{challenge_id}"
        / "k8s_resources"
    )

    if not path.exists():
        return []

    return sorted(
        file
        for file in path.iterdir()
        if file.is_file() and file.suffix in [".yaml", ".yml"]
    )


def apply_manifest(challenge_scenario, challenge_id, mode="all", file_name=None) -> list[str]:
    """Apply challenge manifests. Returns warnings for manifests kubectl rejected."""
    apply_prologue_resources(challenge_scenario)

    if mode == "all":
        resources = iterate_resources(challenge_scenario, challenge_id)
        if not resources:
            raise RuntimeError(
                f"No challenge manifests found for challenge {challenge_id}."
            )

        warnings = []
        for resource in resources:
            try:
                _kubectl_apply(resource)
            except RuntimeError as exc:
                warnings.append(str(exc))

        if len(warnings) == len(resources):
            raise RuntimeError("\n".join(warnings))
        return warnings

    if mode == "individual":
        _kubectl_apply(Path(f"{file_name}.yaml"))
        return []


def iterate_prologue_resources(challenge_scenario):
    project_root = Path(global_constants.PROJECT_ROOT)

    path = (
        project_root
        / "scenarios"
        / challenge_scenario
        / "prologue"
        / "k8s_resources"
    )

    if not path.exists():
        return []

    return [
        file
        for file in sorted(path.iterdir())
        if file.is_file() and file.suffix in [".yaml", ".yml"]
    ]


def apply_prologue_resources(challenge_scenario):
    """Apply every yaml under ``scenarios/<scenario>/prologue/k8s_resources/``.

    This is the scenario-level infra bootstrap (e.g. the namespace) that a
    scenario's prologue is responsible for putting in place before any of its
    challenges run. Callers are expected to ensure the cluster is up first."""
    for resource in iterate_prologue_resources(challenge_scenario):
        _kubectl_apply(resource)
