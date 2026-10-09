"""Where each piece of licensed art goes in the village and the Academy hall."""
import random

import global_constants
from screens.intro import art

TILE = 16
COLUMNS = 20
ROWS = 12

# RedVoxel tile ids (13 columns per row)
TILE_COLUMNS = 13
GRASS_TILES = (8, 8, 8, 9)
PATH_TILE = 35
PATH_EDGE_TILES = (
    ((1, 0), 34), ((-1, 0), 36), ((0, 1), 22), ((0, -1), 48),
    ((1, 1), 21), ((-1, 1), 23), ((1, -1), 47), ((-1, -1), 49),
)
HEDGE_TILES = ((78, 79, 80), (91, 92, 93), (104, 105, 106))
GRASS_SEED = 7

PATH_CELLS = frozenset(
    [(column, 9) for column in range(3, 18)] + [(11, row) for row in range(10, ROWS)]
)
HEDGES = ((0, 10, 8, 12), (14, 10, 19, 12))

# (sheet, u, v, width, height)
TREE = (art.TILES, 80, 48, 48, 48)
MAILBOX = (art.TILES, 128, 64, 16, 32)
GREEN_HOUSE = (art.TILES, 0, 0, 80, 96)
GREY_HOUSE = (art.HOUSES, 0, 0, 76, 90)
ACADEMY = (art.HOUSES, 0, 112, 76, 122)
SIGN = (art.FURNITURE, 0, 0, 16, 32)

VILLAGE_PROPS = (
    (TREE, -14, -10), (TREE, 100, -16), (TREE, 206, -14), (TREE, 296, -6), (TREE, 84, 40),
    (GREEN_HOUSE, 0, 48), (ACADEMY, 130, 22), (GREY_HOUSE, 226, 54),
    (MAILBOX, 86, 120), (MAILBOX, 300, 128), (SIGN, 206, 118),
    (TREE, 300, 96), (TREE, -20, 90),
)

# The player walks on the street below the houses; feet can't go above this line.
WALK_TOP = 142
# (x, y, width, height) of things the player bumps into.
HEDGE_BLOCKERS = ((0, 160, 144, 20), (224, 160, 96, 20))
SIGN_RECT = (208, 140, 12, 10)
MAILBOX_RECTS = ((88, 142, 12, 10), (302, 150, 12, 10))
# Door openings along WALK_TOP as (left x, right x).
ACADEMY_DOOR = (176, 193)
GREEN_HOUSE_DOOR = (48, 64)
GREY_HOUSE_DOOR = (272, 289)

FLOOR = (art.FLOORS, 64, 16, 16, 16)
WALL = (art.INTERIOR, 0, 32, 16, 16)
WAINSCOT = (art.WALLS, 16, 64, 16, 16)
WALL_ROWS = 2
FLOOR_FIRST_ROW = 3

HALL_PROPS = (
    ((art.INTERIOR, 0, 112, 48, 64), 136, 84),
    ((art.INTERIOR, 144, 64, 32, 32), 16, 4),
    ((art.INTERIOR, 144, 64, 32, 32), 256, 4),
    ((art.INTERIOR, 96, 160, 48, 32), 96, 10),
    ((art.INTERIOR, 144, 160, 48, 32), 200, 10),
    ((art.INTERIOR, 144, 192, 48, 32), 56, 20),
    ((art.INTERIOR, 192, 192, 48, 32), 216, 20),
    ((art.FURNITURE, 48, 48, 32, 32), 180, 16),
    ((art.FURNITURE, 48, 48, 32, 32), 108, 16),
    ((art.INTERIOR, 160, 16, 48, 48), 136, 38),
    ((art.INTERIOR, 128, 192, 16, 48), 6, 40),
    ((art.INTERIOR, 128, 192, 16, 48), 296, 40),
    ((art.FURNITURE, 96, 16, 32, 32), 40, 56),
    ((art.FURNITURE, 96, 16, 32, 32), 264, 56),
    ((art.FURNITURE, 128, 16, 16, 16), 24, 120),
    ((art.FURNITURE, 128, 16, 16, 16), 280, 120),
)


def _tile(canvas, index, column, row):
    u = (index % TILE_COLUMNS) * TILE
    v = (index // TILE_COLUMNS) * TILE
    art.blt(canvas, art.TILES, u, v, TILE, TILE, column * TILE, row * TILE)


def _path_edge(column, row):
    for (dx, dy), index in PATH_EDGE_TILES:
        if (column + dx, row + dy) in PATH_CELLS:
            return index
    return None


def _draw_props(canvas, props):
    for (sheet, u, v, width, height), x, y in props:
        art.blt(canvas, sheet, u, v, width, height, x, y)


def bake_village():
    canvas = art.new_canvas(global_constants.WINDOW_WIDTH, global_constants.WINDOW_HEIGHT)
    grass = random.Random(GRASS_SEED)
    for row in range(ROWS):
        for column in range(COLUMNS):
            _tile(canvas, grass.choice(GRASS_TILES), column, row)
            if (column, row) in PATH_CELLS:
                _tile(canvas, PATH_TILE, column, row)
            elif (edge := _path_edge(column, row)) is not None:
                _tile(canvas, edge, column, row)
    for first_column, first_row, last_column, last_row in HEDGES:
        for row in range(first_row, last_row + 1):
            for column in range(first_column, last_column + 1):
                across = 0 if column == first_column else 2 if column == last_column else 1
                down = 0 if row == first_row else 2 if row == last_row else 1
                _tile(canvas, HEDGE_TILES[down][across], column, row)
    _draw_props(canvas, VILLAGE_PROPS)
    return canvas


def bake_hall():
    canvas = art.new_canvas(global_constants.WINDOW_WIDTH, global_constants.WINDOW_HEIGHT)
    for column in range(COLUMNS):
        x = column * TILE
        for row in range(WALL_ROWS):
            art.blt(canvas, *WALL, x, row * TILE)
        art.blt(canvas, *WAINSCOT, x, WALL_ROWS * TILE)
        for row in range(FLOOR_FIRST_ROW, ROWS):
            art.blt(canvas, *FLOOR, x, row * TILE)
    _draw_props(canvas, HALL_PROPS)
    return canvas
