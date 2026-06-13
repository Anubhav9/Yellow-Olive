from pathlib import Path
import subprocess
import global_constants
from utils import general_utils


def _kubectl_apply_error_message(resource_path: Path, detail: str) -> str:
    summary = f"{resource_path.name} needs a fix before it can be applied."
    if not detail:
        return summary

    reason_lines = [line.strip() for line in detail.splitlines() if line.strip()]
    if not reason_lines:
        return summary

    return f"{summary}\n{reason_lines[-1]}"


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
