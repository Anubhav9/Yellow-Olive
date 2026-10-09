# Characters (Kenney Tiny Dungeon tile ids)
PLAYER_TILE = 85
PROFESSOR_TILE = 86

# Village
VILLAGE_PLAYER_START_X = 152
VILLAGE_PLAYER_START_Y = 120
WALK_SPEED = 2
HITBOX_LEFT = 3
HITBOX_RIGHT = 12
HITBOX_TOP = 8
HITBOX_BOTTOM = 15
TOUCH_MARGIN = 2
BOB_FRAMES = 6

ACADEMY_LABEL = "YELLOW OLIVE ACADEMY"
ACADEMY_LABEL_X = 96
ACADEMY_LABEL_Y = 1
ACADEMY_LABEL_WIDTH = 128
ACADEMY_LABEL_HEIGHT = 14

WELCOME_MESSAGE = "Walk to the Academy! (Arrows / WASD / tap)"
WELCOME_MESSAGE_FRAMES = 150
BLUE_HOUSE_MESSAGE = "Nobody is home. Try the Academy!"
RED_HOUSE_MESSAGE = "Locked. A note says: 'Gone to class.'"
SIGNPOST_MESSAGE = "YELLOW OLIVE ACADEMY - Kubernetes for all!"
MESSAGE_FRAMES = 75
MESSAGE_BOX_X = 16
MESSAGE_BOX_Y = 148
MESSAGE_BOX_WIDTH = 288
MESSAGE_BOX_HEIGHT = 16

SKIP_HINT = "[TAB] Skip"
SKIP_HINT_X = 252
SKIP_HINT_Y = 2
SKIP_HINT_WIDTH = 64
SKIP_HINT_HEIGHT = 14

FADE_FRAMES = 15

# Academy hall
HALL_CHARACTER_X = 152
HALL_PLAYER_START_Y = 180
HALL_PLAYER_STOP_Y = 104
HALL_PROFESSOR_START_Y = 36
HALL_PROFESSOR_STOP_Y = 76
PROFESSOR_WALK_SPEED = 1

DIALOGUE_BOX_X = 4
DIALOGUE_BOX_Y = 126
DIALOGUE_BOX_WIDTH = 312
DIALOGUE_BOX_HEIGHT = 50
DIALOGUE_TEXT_X = 50
DIALOGUE_TEXT_Y = 131
DIALOGUE_LINE_SPACING = 13
PORTRAIT_X = 11
PORTRAIT_Y = 134
NAME_TAG = "PROF. BALD"
NAME_TAG_X = 10
NAME_TAG_Y = 114
NAME_TAG_WIDTH = 70
NAME_TAG_HEIGHT = 13
TYPEWRITER_CHARS_PER_FRAME = 1
BLIP_EVERY_CHARS = 3

NAME_MAX_LENGTH = 10
DEFAULT_PLAYER_NAME = "Learner"

# Professor Bald's script. "jingle" plays the ta-da sound when the line starts.
PROFESSOR_INTRO = (
    {"lines": ("Ahem! Hello there, young one!", "Come in, come in. Don't be shy.")},
    {"lines": ("I am Professor Bald.", "Yes, the head shines on purpose.")},
    {"lines": ("Welcome to the", "YELLOW OLIVE ACADEMY!", "Ta-da!"), "jingle": True},
    {"lines": ("Here you will learn Kubernetes,", "one tiny lesson at a time.")},
    {"lines": ("But first things first...", "What is your name?")},
)
NAME_PROMPT_LINES = ("What is your name?", "> {name}{cursor}", "Type it, then press ENTER.")
PROFESSOR_OUTRO = (
    {"lines": ("{name}! What a splendid name.",)},
    {"lines": ("Alright {name}, your adventure", "starts now. Pick a lesson and", "let's begin!")},
)
