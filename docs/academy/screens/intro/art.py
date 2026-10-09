"""Loads the intro's licensed art (see assets/intro/CREDITS.md) and draws UI pieces."""
import pyxel

import text_renderer

ASSET_DIR = "assets/intro/"

TILES = "tiles"
HOUSES = "houses"
INTERIOR = "interior"
FURNITURE = "furniture"
FLOORS = "floors"
WALLS = "walls"
PLAYER = "player"
PROFESSOR = "professor"
PORTRAIT = "portrait"

SHEETS = {
    TILES: ("redvoxel_tiles.png", 208, 144),
    HOUSES: ("tuxemon_houses.png", 76, 234),
    INTERIOR: ("armm_interior.png", 352, 272),
    FURNITURE: ("george_furniture.png", 160, 176),
    FLOORS: ("george_floors.png", 144, 96),
    WALLS: ("george_walls.png", 240, 224),
    PLAYER: ("tuxemon_cooldude.png", 48, 128),
    PROFESSOR: ("tuxemon_monk.png", 48, 128),
    PORTRAIT: ("tuxemon_monk_portrait.png", 56, 53),
}

# Transparent pixels are stored as magenta so they never clash with black outlines.
KEY_RGB = 0xFF00FF

UI_RGB = {
    "white": 0xF8F8F8,
    "text": 0x404048,
    "text_shadow": 0xD0D0D8,
    "outline": 0x282830,
    "blue": 0x4870A0,
    "red": 0xC84848,
    "red_shadow": 0xF0C8C8,
    "gold": 0xC8A028,
    "brown": 0x785014,
    "parchment": 0xE8E0C8,
}

_sheets = {}
_colors = {}
_key = 0


def _sheet_colors(path, width, height):
    probe = pyxel.Image(width, height)
    probe.load(0, 0, path, include_colors=True)
    return list(pyxel.colors)


def init_sheets():
    """Load every sheet, extending the palette so the art keeps its exact colours."""
    global _key
    if _sheets:
        return

    palette = list(pyxel.colors)
    for file_name, width, height in SHEETS.values():
        sheet_colors = _sheet_colors(ASSET_DIR + file_name, width, height)
        pyxel.colors[:] = palette
        for color in sheet_colors:
            if color not in palette:
                palette.append(color)
    for color in UI_RGB.values():
        if color not in palette:
            palette.append(color)
    pyxel.colors[:] = palette

    for name, (file_name, width, height) in SHEETS.items():
        sheet = pyxel.Image(width, height)
        sheet.load(0, 0, ASSET_DIR + file_name)
        _sheets[name] = sheet
    _key = palette.index(KEY_RGB)
    for name, rgb in UI_RGB.items():
        _colors[name] = palette.index(rgb)


def color(name):
    return _colors[name]


def blt(target, sheet, u, v, width, height, x, y):
    (target or pyxel).blt(x, y, _sheets[sheet], u, v, width, height, _key)


def new_canvas(width, height):
    canvas = pyxel.Image(width, height)
    canvas.cls(pyxel.COLOR_BLACK)
    return canvas


def draw_shadow(centre_x, feet_y):
    pyxel.dither(0.5)
    pyxel.elli(centre_x - 6, feet_y - 3, 12, 5, pyxel.COLOR_BLACK)
    pyxel.dither(1.0)


def _rounded_rect(x, y, width, height, color_index):
    pyxel.rect(x + 1, y, width - 2, height, color_index)
    pyxel.rect(x, y + 1, width, height - 2, color_index)


def draw_box(x, y, width, height, accent="blue", fill="white"):
    """Pokémon-style text box: dark outline, coloured trim, light inside."""
    _rounded_rect(x, y, width, height, color("outline"))
    _rounded_rect(x + 1, y + 1, width - 2, height - 2, color(accent))
    _rounded_rect(x + 3, y + 3, width - 6, height - 6, color(fill))


def draw_text(x, y, text, color_name="text", shadow_name="text_shadow"):
    text_renderer.draw_text(x + 1, y + 1, text, color(shadow_name))
    text_renderer.draw_text(x, y, text, color(color_name))


def draw_text_centered(x, y, width, text, color_name="text", shadow_name="text_shadow"):
    text_x = x + max(0, (width - text_renderer.text_width(text)) // 2)
    draw_text(text_x, y, text, color_name, shadow_name)


def draw_fade(progress):
    """Cover the screen with black; progress 0 is clear, 1 is fully black."""
    if progress <= 0:
        return
    pyxel.dither(min(progress, 1.0))
    pyxel.rect(0, 0, pyxel.width, pyxel.height, pyxel.COLOR_BLACK)
    pyxel.dither(1.0)
