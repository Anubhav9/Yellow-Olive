import asyncio
import shutil
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

    for manifest in source_challenge_dir.glob("pod-*.yaml"):
        target_manifest = lab_challenge_dir / manifest.name
        if not target_manifest.exists():
            shutil.copy2(manifest, target_manifest)

    return lab_root


def get_lab_challenge_file(challenge_id):
    lab_root = ensure_lab_workspace()
    return lab_root / "challenge_files" / f"pod-q{challenge_id}.yaml"


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

