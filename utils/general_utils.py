import asyncio
import json
import shutil
import subprocess
from pathlib import Path
import ascii_magic
from PIL import Image, ImageOps, ImageEnhance
from rich.text import Text
import global_constants

async def simulate_dialogue(dialogue, color):
    all_lines = dialogue.split("\n")
    for line in all_lines:
        line = f"[bold {color}]{line}[/]"
        line=line+"\n"
        yield line

def convert_to_ascii(image_path):
    target_rows=20
    img = Image.open(image_path).convert("RGB")

    # Center-crop to square, biased slightly upward for face framing
    img = ImageOps.fit(
        img,
        (min(img.size), min(img.size)),
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.35),
    )

    # Slight punch so eyes/edges survive downscaling
    img = ImageEnhance.Contrast(img).enhance(1.25)
    img = ImageEnhance.Color(img).enhance(1.10)

    # We will encode TWO image rows per ONE terminal row using '▀'
    # So resize image height to target_rows * 2
    aspect = img.width / img.height
    cols = max(20, int(target_rows * aspect * 2.1))  # tweak 2.0–2.4 if needed
    img = img.resize((cols, target_rows * 2), Image.Resampling.LANCZOS)

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


def show_invalid_command(widget, message="PsyQuack tilts its head... please check that command."):
    widget.app.notify(message, title="Invalid command", severity="warning")


def get_lab_root():
    return Path.cwd() / "yellow-olive-lab"


def ensure_lab_workspace():
    lab_root = get_lab_root()
    lab_challenge_dir = lab_root / "challenge_files"
    source_challenge_dir = Path(global_constants.PROJECT_ROOT) / "challenge_files"

    lab_challenge_dir.mkdir(parents=True, exist_ok=True)

    for pattern in ("pod-*.yaml", "svc-*.yaml", "namespace-*.yaml", "ingress-*.yaml"):
        for manifest in source_challenge_dir.glob(pattern):
            target_manifest = lab_challenge_dir / manifest.name
            if not target_manifest.exists():
                shutil.copy2(manifest, target_manifest)

    return lab_root


def get_lab_challenge_file(challenge_id):
    lab_root = ensure_lab_workspace()
    return lab_root / "challenge_files" / f"pod-q{challenge_id}.yaml"


def get_lab_service_file(challenge_id):
    lab_root = ensure_lab_workspace()
    return lab_root / "challenge_files" / f"svc-q{challenge_id}.yaml"


def get_lab_namespace_file():
    lab_root = ensure_lab_workspace()
    return lab_root / "challenge_files" / "namespace-signal-town.yaml"


def get_lab_ingress_file(challenge_id):
    lab_root = ensure_lab_workspace()
    return lab_root / "challenge_files" / f"ingress-q{challenge_id}.yaml"


def get_lab_manifest_file(filename):
    lab_root = ensure_lab_workspace()
    return lab_root / "challenge_files" / filename


def get_progress_file():
    return ensure_lab_workspace() / "progress.json"


def default_progress():
    return {
        "version": 1,
        "player_name": "",
        "active_challenge_id": "1",
        "challenge_background_music": None,
        "story_intro_act": None,
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
    return normalize_story_progress(saved_progress)


def normalize_story_progress(progress):
    """Treat legacy saves on challenge 8+ as having finished the story intro."""
    if (
        int(progress["active_challenge_id"]) >= 8
        and progress.get("story_intro_act") is None
    ):
        progress = dict(progress)
        progress["story_intro_act"] = global_constants.STORY_ACT_DONE
        save_progress(progress)
    return progress


def is_story_intro_pending(progress=None):
    progress = progress or load_progress()
    return progress.get("story_intro_act") in (
        global_constants.STORY_ACT_SIGNAL_TOWN,
        global_constants.STORY_ACT_COOL_TURTLE,
        global_constants.STORY_ACT_TEAM_EVIL,
    )


def load_story_intro_screen(story_intro_act):
    if story_intro_act == global_constants.STORY_ACT_SIGNAL_TOWN:
        from screens.signal_town_intro_screen import SignalTownIntroScreen

        return SignalTownIntroScreen
    if story_intro_act == global_constants.STORY_ACT_COOL_TURTLE:
        from screens.cool_turtle_intro_screen import CoolTurtleIntroScreen

        return CoolTurtleIntroScreen
    if story_intro_act == global_constants.STORY_ACT_TEAM_EVIL:
        from screens.team_evil_intro_screen import TeamEvilIntroScreen

        return TeamEvilIntroScreen
    raise ValueError(f"Unknown story intro act: {story_intro_act}")


def needs_challenge_music_preference(progress):
    """True until the player has chosen yes/no (stored as bool in progress.json)."""
    return not isinstance(progress.get("challenge_background_music"), bool)


def save_progress(progress):
    progress_file = get_progress_file()
    progress_file.parent.mkdir(parents=True, exist_ok=True)
    with progress_file.open("w", encoding="utf-8") as file:
        json.dump(progress, file, indent=2)


def update_progress(**updates):
    progress = load_progress()
    progress.update(updates)
    progress["active_challenge_id"] = str(progress["active_challenge_id"])
    progress.pop("meow_coins", None)
    save_progress(progress)
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
    if is_story_intro_pending():
        return False
    return int(active_challenge_id) > global_constants.TOTAL_CHALLENGES


def start_core_infra(wait=False):
    command = ["sh", str(global_constants.PROJECT_ROOT / "scripts" / "script.sh")]
    if wait:
        subprocess.run(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=str(global_constants.PROJECT_ROOT),
            check=False,
        )
        return

    subprocess.Popen(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
        cwd=str(global_constants.PROJECT_ROOT),
    )


def stop_core_infra():
    subprocess.Popen(
        ["minikube", "stop", "-p", "project-yellow-olive"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )


def invalid_command_text(expected_command=None):
    message = "PsyQuack tilts its head... please check that command."
    if expected_command:
        return f"[yellow]{message} Try `{expected_command}`.[/]"
    return f"[yellow]{message}[/]"


def load_challenge(challenge_id):
    challenge_map = {
        "1": "Challenge1",
        "2": "Challenge2",
        "3": "Challenge3",
        "4": "Challenge4",
        "5": "Challenge5",
        "6": "Challenge6",
        "7": "Challenge7",
        "8": "Challenge8",
        "9": "Challenge9",
        "10": "Challenge10",
        "11": "Challenge11",
        "12": "Challenge12",
        "13": "Challenge13",
    }
    challenge_name = challenge_map.get(str(challenge_id))
    if challenge_name is None:
        raise ValueError(f"Unknown challenge id: {challenge_id}")

    module = __import__(
        f"screens.challenge_{challenge_id}",
        fromlist=[challenge_name],
    )
    return getattr(module, challenge_name)


def get_next_challenge_id(challenge_id):
    current_challenge_id = int(challenge_id)
    if current_challenge_id >= global_constants.TOTAL_CHALLENGES:
        return None
    return str(current_challenge_id + 1)

