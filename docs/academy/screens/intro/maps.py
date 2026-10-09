"""Tile layouts for the intro scenes (Kenney Tiny Town / Tiny Dungeon tile ids)."""

COLUMNS = 20
ROWS = 12

# Tiny Town tiles
GRASS = 0
GRASS_TUFT = 1
GRASS_FLOWERS = 2
STONE_PATH = 43
TREE = 16
TREE_SMALL = 28
BUSH = 17
MUSHROOMS = 29
BEEHIVE = 94
SIGNPOST = 83
FENCE_LEFT_END = 80
FENCE = 81
FENCE_RIGHT_END = 82

ACADEMY_TILES = (
    (96, 97, 97, 97, 97, 98),
    (108, 125, 103, 103, 125, 110),
    (120, 121, 113, 114, 121, 122),
)
ACADEMY_COLUMN = 7
ACADEMY_ROW = 1
ACADEMY_DOOR_CELLS = ((9, 3), (10, 3))

BLUE_HOUSE_TILES = ((48, 51, 50), (60, 63, 62), (84, 86, 75))
BLUE_HOUSE_COLUMN = 2
BLUE_HOUSE_ROW = 3
BLUE_HOUSE_DOOR_CELL = (3, 5)

RED_HOUSE_TILES = ((52, 55, 54), (64, 67, 66), (88, 89, 79))
RED_HOUSE_COLUMN = 15
RED_HOUSE_ROW = 3
RED_HOUSE_DOOR_CELL = (16, 5)

SIGNPOST_CELL = (12, 5)
FENCE_ROW = 10
PATH_GAP_COLUMNS = (9, 10)


def _empty(fill=None):
    return [[fill] * COLUMNS for _ in range(ROWS)]


def _stamp(layer, column, row, tiles):
    for row_offset, tile_row in enumerate(tiles):
        for column_offset, index in enumerate(tile_row):
            layer[row + row_offset][column + column_offset] = index


def village_ground():
    ground = _empty(GRASS)
    for row in range(ROWS):
        for column in range(COLUMNS):
            noise = (column * 7 + row * 13 + column * row) % 17
            if noise == 0:
                ground[row][column] = GRASS_FLOWERS
            elif noise in (3, 9):
                ground[row][column] = GRASS_TUFT

    for row in range(ACADEMY_ROW + len(ACADEMY_TILES), ROWS):
        for column in PATH_GAP_COLUMNS:
            ground[row][column] = STONE_PATH
    for column in range(BLUE_HOUSE_COLUMN, RED_HOUSE_COLUMN + 3):
        ground[7][column] = STONE_PATH
    ground[6][BLUE_HOUSE_DOOR_CELL[0]] = STONE_PATH
    ground[6][RED_HOUSE_DOOR_CELL[0]] = STONE_PATH
    return ground


def village_objects():
    objects = _empty()
    _stamp(objects, ACADEMY_COLUMN, ACADEMY_ROW, ACADEMY_TILES)
    _stamp(objects, BLUE_HOUSE_COLUMN, BLUE_HOUSE_ROW, BLUE_HOUSE_TILES)
    _stamp(objects, RED_HOUSE_COLUMN, RED_HOUSE_ROW, RED_HOUSE_TILES)

    for row in range(FENCE_ROW + 1):
        objects[row][0] = TREE if row % 2 else TREE_SMALL
        objects[row][COLUMNS - 1] = TREE_SMALL if row % 2 else TREE

    left_end, right_end = PATH_GAP_COLUMNS
    for column in range(1, COLUMNS - 1):
        if column in PATH_GAP_COLUMNS:
            continue
        objects[FENCE_ROW][column] = FENCE
    objects[FENCE_ROW][1] = FENCE_LEFT_END
    objects[FENCE_ROW][left_end - 1] = FENCE_RIGHT_END
    objects[FENCE_ROW][right_end + 1] = FENCE_LEFT_END
    objects[FENCE_ROW][COLUMNS - 2] = FENCE_RIGHT_END

    column, row = SIGNPOST_CELL
    objects[row][column] = SIGNPOST
    objects[1][3] = TREE_SMALL
    objects[1][16] = TREE_SMALL
    objects[9][3] = BEEHIVE
    objects[9][5] = BUSH
    objects[9][14] = MUSHROOMS
    objects[5][6] = TREE
    objects[5][13] = TREE
    return objects


# Tiny Dungeon tiles
FLOOR = 48
FLOOR_SPECKLED = 49
FLOOR_PEBBLES = 51
BRICK_WALL = 40
WALL_BANNER = 29
BOOKSHELF = 63
BOOKSHELF_TALL = 75
TABLE = 72
STOOL = 73
BARREL = 82
CHEST = 89
WALL_ROWS = 2


def hall_floor():
    floor = _empty(FLOOR)
    for row in range(ROWS):
        for column in range(COLUMNS):
            if row < WALL_ROWS:
                floor[row][column] = BRICK_WALL
                continue
            noise = (column * 5 + row * 11) % 13
            if noise == 0:
                floor[row][column] = FLOOR_SPECKLED
            elif noise == 7:
                floor[row][column] = FLOOR_PEBBLES
    floor[1][4] = WALL_BANNER
    floor[1][15] = WALL_BANNER
    return floor


def hall_objects():
    objects = _empty()
    for column in (1, 2, 17, 18):
        objects[2][column] = BOOKSHELF if column % 2 else BOOKSHELF_TALL
    objects[2][6] = CHEST
    objects[2][13] = CHEST
    for column in (3, 5, 14, 16):
        objects[5][column] = TABLE
        objects[6][column] = STOOL
    objects[4][1] = BARREL
    objects[4][18] = BARREL
    return objects
