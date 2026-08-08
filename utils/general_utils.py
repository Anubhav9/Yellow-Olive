import asyncio
import importlib
import json
import shutil
import subprocess
import threading
import time
from pathlib import Path
import ascii_magic
from PIL import Image, ImageOps, ImageEnhance, ImageFilter
from PIL.DdsImagePlugin import module
from rich.text import Text
import global_constants


CHALLENGE_SCENARIO_MAP = {
    "1": "oakwood_meadows",
    "2": "oakwood_meadows",
    "3": "oakwood_meadows",
    "4": "oakwood_meadows",
    "5": "oakwood_meadows",
    "6": "oakwood_meadows",
    "7": "oakwood_meadows",
    "8": "signal_town",
    "9": "signal_town",
    "10": "signal_town",
    "11": "signal_town",
    "12": "signal_town",
    "13": "signal_town",
    "14": "gold_rush_city",
    "15": "gold_rush_city",
    "16": "gold_rush_city",
    "17": "gold_rush_city",
    "18": "gold_rush_city",
    "19": "gold_rush_city",
    "20": "sakura_harbour",
    "21": "sakura_harbour",
    "22": "sakura_harbour",
    "23": "sakura_harbour",
    "24": "sakura_harbour",
}

async def simulate_dialogue(dialogue, color):
    all_lines = dialogue.split("\n")
    for line in all_lines:
        line = f"[bold {color}]{line}[/]"
        line=line+"\n"
        yield line

def convert_to_ascii(image_path, target_rows=global_constants.PORTRAIT_TARGET_ROWS):
    img = Image.open(image_path).convert("RGB")

    # Center-crop to square, biased slightly upward for face framing
    img = ImageOps.fit(
        img,
        (min(img.size), min(img.size)),
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.35),
    )

    # We will encode TWO image rows per ONE terminal row using '▀'
    # So resize image height to target_rows * 2
    aspect = img.width / img.height
    cols = max(20, int(target_rows * aspect * 2.1))  # tweak 2.0–2.4 if needed

    # Area-average to a small multiple of the target first. Going straight to
    # final size with a sharp filter rings against the hard outlines in the
    # portraits and leaves grey halos around hair and edges.
    img = img.resize(
        (
            cols * global_constants.PORTRAIT_PREFILTER_SCALE,
            target_rows * 2 * global_constants.PORTRAIT_PREFILTER_SCALE,
        ),
        Image.Resampling.BOX,
    )

    # Punch so eyes/edges survive downscaling
    img = ImageEnhance.Contrast(img).enhance(1.35)
    img = ImageEnhance.Color(img).enhance(1.25)

    img = img.resize((cols, target_rows * 2), Image.Resampling.BOX)
    img = img.filter(ImageFilter.UnsharpMask(radius=1, percent=90, threshold=0))

    # Collapse the near-identical shades that averaging produces into a small
    # flat palette, so the portrait reads as deliberate pixel art.
    img = img.quantize(
        colors=global_constants.PORTRAIT_COLOR_COUNT,
        method=Image.Quantize.MEDIANCUT,
        dither=Image.Dither.NONE,
    ).convert("RGB")

    px = img.load()
    t = Text()

    for y in range(0, img.height, 2):
        for x in range(img.width):
            top = px[x, y]
            bottom = px[x, y + 1] if y + 1 < img.height else top

            # '▀' uses foreground for top-half, background for bottom-half
            t.append(
                "▀",
                style=f"rgb({top[0]},{top[1]},{top[2]}) on rgb({bottom[0]},{bottom[1]},{bottom[2]})",
            )
        t.append("\n")

    return t


CLUSTER_STARTUP_FAILURE_MESSAGE = (
    "Something went wrong starting the lab cluster. "
    "Please contact the developer for now."
)
LAB_MINIKUBE_PROFILE = "project-yellow-olive"
LAB_CLUSTER_STARTUP_TIMEOUT_SECONDS = 300
LAB_CLUSTER_READY_POLL_SECONDS = 2
LAB_CLUSTER_BOOTSTRAP_REMINDER_SECONDS = 60


def show_invalid_command(widget, message="PsyQuack tilts its head... please check that command."):
    widget.app.notify(message, title="Invalid command", severity="warning")


def notify_cluster_startup_failure(widget):
    widget.app.notify(
        CLUSTER_STARTUP_FAILURE_MESSAGE,
        title="Lab cluster failed",
        severity="error",
    )


def get_lab_root():
    return Path.cwd() / "yellow-olive-lab"


def ensure_lab_workspace():
    """Materialise the player's lab workspace under ``yellow-olive-lab/``.

    Copies *source* manifests into the lab on first run so the player can edit
    those copies without touching the repo. Subsequent runs preserve existing
    lab files (we only copy when the target is missing), so player edits are
    never overwritten."""
    lab_root = get_lab_root()
    project_root = Path(global_constants.PROJECT_ROOT)

    # Legacy challenge_files mirror (kept for residual references).
    lab_challenge_dir = lab_root / "challenge_files"
    source_challenge_dir = project_root / "challenge_files"
    lab_challenge_dir.mkdir(parents=True, exist_ok=True)
    for pattern in ("pod-*.yaml", "svc-*.yaml", "namespace-*.yaml", "ingress-*.yaml"):
        for manifest in source_challenge_dir.glob(pattern):
            target_manifest = lab_challenge_dir / manifest.name
            if not target_manifest.exists():
                shutil.copy2(manifest, target_manifest)

    # Scenario challenge manifests mirror: scenarios/<scenario>/challenge_<id>/k8s_resources/*.
    # Prologue resources are intentionally NOT mirrored - they are infrastructure
    # the game manages, not files the player edits.
    source_scenarios_dir = project_root / "scenarios"
    if source_scenarios_dir.exists():
        for pattern in (
            "*/challenge_*/k8s_resources/*.yaml",
            "*/challenge_*/k8s_resources/*.yml",
        ):
            for manifest in source_scenarios_dir.glob(pattern):
                target_manifest = lab_root / manifest.relative_to(project_root)
                if not target_manifest.exists():
                    target_manifest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(manifest, target_manifest)

    return lab_root


def get_lab_challenge_file(challenge_scenario, challenge_id):
    lab_root = ensure_lab_workspace()
    return (
        lab_root
        / "scenarios"
        / f"{challenge_scenario}"
        / f"challenge_{challenge_id}"
        / "k8s_resources"
        / f"pod-q{challenge_id}.yaml"
    )


def get_lab_service_file(challenge_scenario, challenge_id):
    lab_root = ensure_lab_workspace()
    return (
        lab_root
        / "scenarios"
        / f"{challenge_scenario}"
        / f"challenge_{challenge_id}"
        / "k8s_resources"
        / f"svc-q{challenge_id}.yaml"
    )


def get_lab_deployment_file(challenge_scenario, challenge_id, file_name=None):
    lab_root = ensure_lab_workspace()
    filename = file_name or f"deployment-q{challenge_id}.yaml"
    return (
        lab_root
        / "scenarios"
        / f"{challenge_scenario}"
        / f"challenge_{challenge_id}"
        / "k8s_resources"
        / filename
    )





def get_progress_file():
    return ensure_lab_workspace() / "progress.json"


PENDING_EPILOGUE_ARCS = frozenset(
    {"oakwood_meadows", "signal_town", "gold_rush_city"}
)

PENDING_EPILOGUE_LABELS = {
    "oakwood_meadows": "Oakwood Meadows victory",
    "signal_town": "Signal Town victory",
    "gold_rush_city": "Gold Rush City victory",
}


def default_progress():
    return {
        "version": 1,
        "player_name": "",
        "active_challenge_id": "1",
        "challenge_background_music": None,
        "story_intro_act": None,
        "pending_epilogue": None,
    }


def has_saved_progress():
    return get_progress_file().exists()


def load_progress():
    progress_file = get_progress_file()
    if not progress_file.exists():
        return default_progress()

    try:
        with progress_file.open("r", encoding="utf-8") as file:
            progress = json.load(file)
    except (json.JSONDecodeError, OSError):
        return default_progress()

    saved_progress = default_progress()
    saved_progress.update(progress)
    saved_progress["active_challenge_id"] = str(saved_progress["active_challenge_id"])
    music = saved_progress.get("challenge_background_music")
    if not isinstance(music, bool):
        saved_progress["challenge_background_music"] = None
    epilogue = saved_progress.get("pending_epilogue")
    if epilogue not in PENDING_EPILOGUE_ARCS:
        saved_progress["pending_epilogue"] = None
    return normalize_story_progress(saved_progress)


def normalize_story_progress(progress):
    """Treat legacy saves on challenges 8-13 as having finished the story intro."""
    challenge_id = int(progress["active_challenge_id"])
    if (
        8 <= challenge_id <= 13
        and progress.get("story_intro_act") is None
    ):
        progress = dict(progress)
        progress["story_intro_act"] = global_constants.STORY_ACT_DONE
        save_progress(progress)
    return progress


def get_pending_epilogue(progress=None):
    progress = progress or load_progress()
    epilogue = progress.get("pending_epilogue")
    if epilogue in PENDING_EPILOGUE_ARCS:
        return epilogue
    return None


def has_pending_epilogue(progress=None):
    return get_pending_epilogue(progress) is not None


def load_epilogue_screen(pending_epilogue):
    if pending_epilogue == "oakwood_meadows":
        from scenarios.oakwood_meadows.epilogue.screens.arc_complete_screen import (
            OakwoodMeadowsArcCompleteScreen,
        )

        return OakwoodMeadowsArcCompleteScreen
    if pending_epilogue == "signal_town":
        from scenarios.signal_town.epilogue.screens.arc_complete_screen import (
            SignalTownArcCompleteScreen,
        )

        return SignalTownArcCompleteScreen
    if pending_epilogue == "gold_rush_city":
        from scenarios.gold_rush_city.epilogue.screens.arc_complete_screen import (
            GoldRushCityArcCompleteScreen,
        )

        return GoldRushCityArcCompleteScreen
    raise ValueError(f"Unknown pending epilogue: {pending_epilogue}")


def is_story_intro_pending(progress=None):
    progress = progress or load_progress()
    return progress.get("story_intro_act") in (
        global_constants.STORY_ACT_SIGNAL_TOWN,
        global_constants.STORY_ACT_COOL_TURTLE,
        global_constants.STORY_ACT_TEAM_EVIL,
        global_constants.STORY_ACT_GOLD_RUSH_CITY,
        global_constants.STORY_ACT_GOLD_RUSH_VAULT,
        global_constants.STORY_ACT_GOLD_RUSH_TEAM_EVIL,
        global_constants.STORY_ACT_GOLD_RUSH_EPILOGUE,
        global_constants.STORY_ACT_SAKURA_HARBOUR,
        global_constants.STORY_ACT_SAKURA_HANA,
        global_constants.STORY_ACT_SAKURA_GATE,
    )


def load_story_intro_screen(story_intro_act):
    if story_intro_act == global_constants.STORY_ACT_SIGNAL_TOWN:
        from scenarios.signal_town.prologue.screens.signal_town_intro_screen import SignalTownIntroScreen

        return SignalTownIntroScreen
    if story_intro_act == global_constants.STORY_ACT_COOL_TURTLE:
        from scenarios.signal_town.prologue.screens.cool_turtle_intro_screen import CoolTurtleIntroScreen

        return CoolTurtleIntroScreen
    if story_intro_act == global_constants.STORY_ACT_TEAM_EVIL:
        from scenarios.signal_town.prologue.screens.team_evil_intro_screen import TeamEvilIntroScreen

        return TeamEvilIntroScreen
    if story_intro_act == global_constants.STORY_ACT_GOLD_RUSH_CITY:
        from scenarios.gold_rush_city.prologue.screens.gold_rush_city_intro_screen import GoldRushCityIntroScreen

        return GoldRushCityIntroScreen
    if story_intro_act == global_constants.STORY_ACT_GOLD_RUSH_VAULT:
        from scenarios.gold_rush_city.prologue.screens.mayor_vault_intro_screen import MayorVaultIntroScreen

        return MayorVaultIntroScreen
    if story_intro_act == global_constants.STORY_ACT_GOLD_RUSH_TEAM_EVIL:
        from scenarios.gold_rush_city.prologue.screens.team_evil_license_intro_screen import TeamEvilLicenseIntroScreen

        return TeamEvilLicenseIntroScreen
    if story_intro_act == global_constants.STORY_ACT_GOLD_RUSH_EPILOGUE:
        from scenarios.gold_rush_city.epilogue.screens.arc_complete_screen import GoldRushCityArcCompleteScreen

        return GoldRushCityArcCompleteScreen
    if story_intro_act == global_constants.STORY_ACT_SAKURA_HARBOUR:
        from scenarios.sakura_harbour.prologue.screens.sakura_harbour_intro_screen import (
            SakuraHarbourIntroScreen,
        )

        return SakuraHarbourIntroScreen
    if story_intro_act == global_constants.STORY_ACT_SAKURA_HANA:
        from scenarios.sakura_harbour.prologue.screens.master_hana_intro_screen import (
            MasterHanaIntroScreen,
        )

        return MasterHanaIntroScreen
    if story_intro_act == global_constants.STORY_ACT_SAKURA_GATE:
        from scenarios.sakura_harbour.prologue.screens.gate_three_intro_screen import (
            GateThreeIntroScreen,
        )

        return GateThreeIntroScreen
    raise ValueError(f"Unknown story intro act: {story_intro_act}")


def needs_challenge_music_preference(progress):
    """True until the player has chosen yes/no (stored as bool in progress.json)."""
    return not isinstance(progress.get("challenge_background_music"), bool)


def save_progress(progress):
    progress_file = get_progress_file()
    progress_file.parent.mkdir(parents=True, exist_ok=True)
    with progress_file.open("w", encoding="utf-8") as file:
        json.dump(progress, file, indent=2)


def _track_story_section_completed(previous_act, new_act) -> None:
    if previous_act == new_act:
        return

    from services.diagnostics import track

    done_transitions = {
        (global_constants.STORY_ACT_TEAM_EVIL, global_constants.STORY_ACT_DONE): (
            "team_evil_intro",
            "signal_town",
        ),
        (global_constants.STORY_ACT_GOLD_RUSH_TEAM_EVIL, global_constants.STORY_ACT_DONE): (
            "team_evil_license_intro",
            "gold_rush_city",
        ),
        (global_constants.STORY_ACT_SAKURA_GATE, global_constants.STORY_ACT_DONE): (
            "gate_three_intro",
            "sakura_harbour",
        ),
    }
    transition = done_transitions.get((previous_act, new_act))
    if transition:
        section, scenario = transition
        track("section_completed", section=section, scenario=scenario)
        return

    section_by_act = {
        global_constants.STORY_ACT_SIGNAL_TOWN: ("signal_town_intro", "signal_town"),
        global_constants.STORY_ACT_COOL_TURTLE: ("cool_turtle_intro", "signal_town"),
        global_constants.STORY_ACT_GOLD_RUSH_CITY: ("gold_rush_city_intro", "gold_rush_city"),
        global_constants.STORY_ACT_GOLD_RUSH_VAULT: ("mayor_vault_intro", "gold_rush_city"),
        global_constants.STORY_ACT_GOLD_RUSH_TEAM_EVIL: (
            "team_evil_license_intro",
            "gold_rush_city",
        ),
        global_constants.STORY_ACT_GOLD_RUSH_EPILOGUE: (
            "gold_rush_city_epilogue",
            "gold_rush_city",
        ),
        global_constants.STORY_ACT_SAKURA_HARBOUR: ("sakura_harbour_intro", "sakura_harbour"),
        global_constants.STORY_ACT_SAKURA_HANA: ("master_hana_intro", "sakura_harbour"),
        global_constants.STORY_ACT_SAKURA_GATE: ("gate_three_intro", "sakura_harbour"),
    }
    completed = section_by_act.get(previous_act)
    if completed:
        section, scenario = completed
        track("section_completed", section=section, scenario=scenario)


def update_progress(**updates):
    from services.diagnostics import track

    section_completed = updates.pop("section_completed", None)
    section_scenario = updates.pop("section_scenario", None)

    progress = load_progress()
    previous_story_act = progress.get("story_intro_act")
    progress.update(updates)
    progress["active_challenge_id"] = str(progress["active_challenge_id"])
    progress.pop("meow_coins", None)
    save_progress(progress)

    if section_completed:
        track(
            "section_completed",
            section=section_completed,
            scenario=section_scenario or "unknown",
        )

    if "story_intro_act" in updates:
        _track_story_section_completed(previous_story_act, updates["story_intro_act"])

    return progress


def reset_progress():
    lab_root = get_lab_root()
    if lab_root.exists():
        shutil.rmtree(lab_root)
    ensure_lab_workspace()
    global_constants.meow_coins = 0


def restore_progress_to_runtime():
    progress = load_progress()
    global_constants.meow_coins = calculate_meow_coins(progress["active_challenge_id"])
    return progress


def calculate_meow_coins(active_challenge_id):
    completed_challenge_count = max(int(active_challenge_id) - 1, 0)
    completed_challenge_count = min(completed_challenge_count, global_constants.TOTAL_CHALLENGES)
    return completed_challenge_count * (completed_challenge_count + 1) // 2


def is_campaign_complete(active_challenge_id):
    if has_pending_epilogue():
        return False
    if is_story_intro_pending():
        return False
    return int(active_challenge_id) > global_constants.TOTAL_CHALLENGES


def start_core_infra_v1() -> None:
    """Start the lab Minikube cluster and select its kubectl context.

    Portable replacement for ``scripts/script.sh`` (POSIX subprocess, no shell).
    """
    if shutil.which("minikube") is None:
        raise RuntimeError("Minikube not found.")

    profile = LAB_MINIKUBE_PROFILE
    deadline = time.monotonic() + LAB_CLUSTER_STARTUP_TIMEOUT_SECONDS

    remaining = _remaining_cluster_startup_seconds(deadline)
    if remaining <= 0:
        _raise_cluster_startup_timeout()

    try:
        start_result = subprocess.run(
            ["minikube", "start", "--nodes", "1", "-p", profile],
            capture_output=True,
            text=True,
            check=False,
            timeout=remaining,
        )
    except subprocess.TimeoutExpired as exc:
        raise _cluster_startup_timeout_error() from exc

    if start_result.returncode != 0:
        detail = (start_result.stderr or start_result.stdout or "").strip()
        raise RuntimeError(detail or CLUSTER_STARTUP_FAILURE_MESSAGE)

    while not _minikube_cluster_is_ready(profile):
        if _remaining_cluster_startup_seconds(deadline) <= 0:
            _raise_cluster_startup_timeout()
        time.sleep(LAB_CLUSTER_READY_POLL_SECONDS)

    remaining = _remaining_cluster_startup_seconds(deadline)
    context_result = subprocess.run(
        ["kubectl", "config", "use-context", profile],
        capture_output=True,
        text=True,
        check=False,
        timeout=max(remaining, 1),
    )
    if context_result.returncode != 0:
        detail = (context_result.stderr or context_result.stdout or "").strip()
        raise RuntimeError(detail or CLUSTER_STARTUP_FAILURE_MESSAGE)


def _remaining_cluster_startup_seconds(deadline: float) -> float:
    return deadline - time.monotonic()


def _cluster_startup_timeout_error() -> RuntimeError:
    return RuntimeError(
        f"The lab cluster did not become ready within "
        f"{LAB_CLUSTER_STARTUP_TIMEOUT_SECONDS} seconds. "
        "First run can take several minutes while images download. "
        "Check Docker and your network, then try again."
    )


def _raise_cluster_startup_timeout() -> None:
    raise _cluster_startup_timeout_error()


def _infra_setup_failure_reason(error: BaseException) -> str:
    message = str(error).lower()
    if "minikube not found" in message:
        return "minikube_missing"
    if "did not become ready" in message or isinstance(error, subprocess.TimeoutExpired):
        return "cluster_startup_timeout"
    if "kubectl" in message and ("not found" in message or "no such file" in message):
        return "kubectl_missing"
    if "docker" in message:
        return "docker_unavailable"
    return "unknown"


async def wait_for_cluster_bootstrap(log) -> None:
    """Start the lab cluster and surface progress hints in the game log."""
    from screens.common.screen_prompts import game_initialisation as screen_prompts
    from services.diagnostics import track

    track("infra_setup_started")
    log.write(screen_prompts.CLUSTER_BOOTSTRAP_MESSAGE)
    bootstrap_task = asyncio.create_task(asyncio.to_thread(start_core_infra, True))
    try:
        try:
            await asyncio.wait_for(
                asyncio.shield(bootstrap_task),
                timeout=LAB_CLUSTER_BOOTSTRAP_REMINDER_SECONDS,
            )
        except asyncio.TimeoutError:
            log.write("")
            log.write(screen_prompts.CLUSTER_BOOTSTRAP_STILL_WORKING_MESSAGE)
        await bootstrap_task
    except Exception as exc:
        track("infra_setup_failed", reason=_infra_setup_failure_reason(exc))
        raise
    track("infra_setup_succeeded")


def _minikube_cluster_is_ready(profile: str) -> bool:
    result = subprocess.run(
        ["minikube", "status", "-p", profile],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


def _start_core_infra_v1_background() -> None:
    try:
        start_core_infra_v1()
    except RuntimeError:
        return


def start_core_infra(wait=False):
    if wait:
        start_core_infra_v1()
        return

    threading.Thread(target=_start_core_infra_v1_background, daemon=True).start()


def teardown_core_infra_background() -> None:
    """Delete the lab minikube profile without blocking app shutdown."""
    subprocess.Popen(
        ["minikube", "delete", "-p", LAB_MINIKUBE_PROFILE, "--purge"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )


def teardown_core_infra():
    """Delete the lab minikube profile and its docker container."""
    subprocess.run(
        ["minikube", "delete", "-p", LAB_MINIKUBE_PROFILE, "--purge"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
        timeout=120,
    )


def stop_core_infra():
    teardown_core_infra()


def invalid_command_text(expected_command=None):
    message = "PsyQuack tilts its head... please check that command."
    if expected_command:
        return f"[yellow]{message} Try `{expected_command}`.[/]"
    return f"[yellow]{message}[/]"


def load_challenge(challenge_id):
    challenge_id_str = str(challenge_id)
    scenario = CHALLENGE_SCENARIO_MAP.get(challenge_id_str)
    if scenario is None:
        raise ValueError(f"Unknown challenge id: {challenge_id}")

    module = importlib.import_module(
        f"scenarios.{scenario}.challenge_{challenge_id_str}.screen"
    )
    return getattr(module, f"Challenge{challenge_id_str}")


def get_next_challenge_id(challenge_id):
    current_challenge_id = int(challenge_id)
    if current_challenge_id >= global_constants.TOTAL_CHALLENGES:
        return None
    return str(current_challenge_id + 1)

