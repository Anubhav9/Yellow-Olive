"""Japanese-style classroom inside Yellow Olive Academy, where the player meets Professor Bald Uncle."""

CLASSROOM_MAP_ASSET_PATH = "assets/japanese_classroom.png"
PROFESSOR_ASSET_PATH = "assets/tilesets/Characters/professor_bald_uncle.png"

PLAYER_START_X = 160
PLAYER_START_Y = 146

PROFESSOR_X = 130
PROFESSOR_Y = 46

# Things on japanese_classroom.png the player can't walk through, as (x, y, width, height).
SOLIDS = [
    # front wall with the chalkboard and windows
    (0, 0, 320, 48),
    # bookshelves
    (4, 44, 32, 34), (284, 44, 32, 34),
    # teacher's desk and the professor
    (146, 54, 28, 23),
    (130, 66, 16, 12),
    # student desks with their chairs, 3 rows of 6
    *[(x, y, 16, 28) for y in (86, 114, 142) for x in (56, 98, 140, 180, 222, 264)],
]

PROFESSOR_NAME = "PROFESSOR BALD UNCLE"
NAME_PROMPT_INDEX = 1
NAME_MAX_LENGTH = 10
ADVANCE_HINT = "ENTER"

# Each entry is one dialogue box, up to two lines. {name} is the player's name.
DIALOGUE = [
    ("Hello there! I am Professor Bald Uncle.", "Welcome to my classroom."),
    ("Before we begin, what is your name?", ""),
    ("Welcome to Yellow Olive Academy,", "{name}!"),
    ("Get ready for the journey ahead!", ""),
]

DIALOGUE_BOX_X = 8
DIALOGUE_BOX_Y = 2
DIALOGUE_BOX_WIDTH = 304
DIALOGUE_BOX_HEIGHT = 42
