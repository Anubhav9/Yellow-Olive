from pathlib import Path
import subprocess
import global_constants
from utils import general_utils


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

    return [
        file
        for file in path.iterdir()
        if file.is_file() and file.suffix in [".yaml", ".yml"]
    ]


def apply_manifest(challenge_scenario, challenge_id,mode="all",file_name=None):
    if mode=="all":
        resources = iterate_resources(challenge_scenario, challenge_id)
        for resource in resources:
            subprocess.run(
                ["kubectl", "apply", "-f", str(resource)],
                check=True,
                cwd=str(global_constants.PROJECT_ROOT),
            )
    if mode=="individual":
        subprocess.run(
            ["kubectl", "apply", "-f", file_name+".yaml"],
            check=True,
            cwd=str(global_constants.PROJECT_ROOT),
        )


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
        subprocess.run(
            ["kubectl", "apply", "-f", str(resource)],
            check=True,
            cwd=str(global_constants.PROJECT_ROOT),
        )