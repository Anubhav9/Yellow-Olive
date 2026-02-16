import asyncio
import ascii_magic
from PIL import Image, ImageOps, ImageEnhance
from rich.text import Text

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

