import pyxel

TILE_SIZE = 16
SHEET_WIDTH = 192
SHEET_HEIGHT = 176
SHEET_COLUMNS = 12
TRANSPARENT_COLOR = 0

TOWN = "town"
DUNGEON = "dungeon"
SHEET_PATHS = {
    TOWN: "assets/kenney/tiny_town.png",
    DUNGEON: "assets/kenney/tiny_dungeon.png",
}

_sheets = {}


def _colors_used_by(path):
    probe = pyxel.Image(SHEET_WIDTH, SHEET_HEIGHT)
    probe.load(0, 0, path, include_colors=True)
    return list(pyxel.colors)


def init_sheets():
    """Load the Kenney sheets, extending the palette so tiles keep their colours."""
    if _sheets:
        return

    palette = list(pyxel.colors)
    for path in SHEET_PATHS.values():
        sheet_colors = _colors_used_by(path)
        pyxel.colors[:] = palette
        for color in sheet_colors:
            if color not in palette:
                palette.append(color)
    pyxel.colors[:] = palette

    for name, path in SHEET_PATHS.items():
        sheet = pyxel.Image(SHEET_WIDTH, SHEET_HEIGHT)
        sheet.load(0, 0, path)
        _sheets[name] = sheet


def _tile_source(index):
    return (
        (index % SHEET_COLUMNS) * TILE_SIZE,
        (index // SHEET_COLUMNS) * TILE_SIZE,
    )


def draw_tile(sheet_name, index, x, y, flip=False, scale=1):
    u, v = _tile_source(index)
    width = -TILE_SIZE if flip else TILE_SIZE
    offset = TILE_SIZE * (scale - 1) / 2
    pyxel.blt(
        x + offset, y + offset, _sheets[sheet_name],
        u, v, width, TILE_SIZE,
        TRANSPARENT_COLOR, scale=scale,
    )


def bake_map(sheet_name, *layers):
    """Pre-render tile layers into one image so each frame is a single blt."""
    rows = len(layers[0])
    columns = len(layers[0][0])
    baked = pyxel.Image(columns * TILE_SIZE, rows * TILE_SIZE)
    baked.cls(0)
    for layer in layers:
        for row, tile_row in enumerate(layer):
            for column, index in enumerate(tile_row):
                if index is None:
                    continue
                u, v = _tile_source(index)
                baked.blt(
                    column * TILE_SIZE, row * TILE_SIZE, _sheets[sheet_name],
                    u, v, TILE_SIZE, TILE_SIZE, TRANSPARENT_COLOR,
                )
    return baked


def draw_fade(progress):
    """Cover the screen with black; progress 0 is clear, 1 is fully black."""
    if progress <= 0:
        return
    pyxel.dither(min(progress, 1.0))
    pyxel.rect(0, 0, pyxel.width, pyxel.height, pyxel.COLOR_BLACK)
    pyxel.dither(1.0)
