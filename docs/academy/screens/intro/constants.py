# Player hitbox (feet) relative to the 16x32 sprite's top-left corner
HITBOX_LEFT = 3
HITBOX_TOP = 24
HITBOX_WIDTH = 10
HITBOX_HEIGHT = 8
TOUCH_MARGIN = 2
WALK_SPEED = 2

# Village
VILLAGE_PLAYER_START_X = 56
VILLAGE_PLAYER_START_Y = 128

LOCATION_NAME = "OAKWOOD MEADOWS"
LOCATION_BOX_X = 4
LOCATION_BOX_WIDTH = 104
LOCATION_BOX_HEIGHT = 18
LOCATION_BOX_Y = 4
LOCATION_SLIDE_FRAMES = 10
LOCATION_SHOW_FRAMES = 150

ACADEMY_LABEL = "YELLOW OLIVE ACADEMY"
ACADEMY_LABEL_X = 106
ACADEMY_LABEL_Y = 4
ACADEMY_LABEL_WIDTH = 132
ACADEMY_LABEL_HEIGHT = 18

WELCOME_MESSAGE = "Walk into the Academy! (Arrows / WASD / tap)"
WELCOME_MESSAGE_FRAMES = 180
GREEN_HOUSE_MESSAGE = "Nobody is home. Try the Academy!"
GREY_HOUSE_MESSAGE = "Locked. A note says: 'Gone to class.'"
SIGN_MESSAGE = "YELLOW OLIVE ACADEMY - Kubernetes for all!"
MAILBOX_MESSAGE = "A letter: 'Pods are the smallest unit!'"
MESSAGE_FRAMES = 90
MESSAGE_BOX_X = 4
MESSAGE_BOX_Y = 26
MESSAGE_BOX_WIDTH = 312
MESSAGE_BOX_HEIGHT = 26

SKIP_HINT = "TAB: skip"
SKIP_HINT_X = 254
SKIP_HINT_Y = 4
SKIP_HINT_WIDTH = 62
SKIP_HINT_HEIGHT = 18

FADE_FRAMES = 15

# Academy hall
HALL_CHARACTER_X = 152
HALL_PLAYER_START_Y = 180
HALL_PLAYER_STOP_Y = 105
HALL_PROFESSOR_Y = 72
NOTICE_FRAMES = 30
NOTICE_BUBBLE_X = 155
NOTICE_BUBBLE_Y = 52
NOTICE_BUBBLE_WIDTH = 11
NOTICE_BUBBLE_HEIGHT = 18

DIALOGUE_BOX_X = 2
DIALOGUE_BOX_Y = 124
DIALOGUE_BOX_WIDTH = 316
DIALOGUE_BOX_HEIGHT = 54
PORTRAIT_FRAME_X = 8
PORTRAIT_FRAME_Y = 128
PORTRAIT_FRAME_WIDTH = 61
PORTRAIT_FRAME_HEIGHT = 46
PORTRAIT_X = 10
PORTRAIT_Y = 129
PORTRAIT_WIDTH = 56
PORTRAIT_HEIGHT = 53
NAME_TAG = "PROF. BALD"
DIALOGUE_TEXT_X = 76
NAME_TAG_Y = 130
DIALOGUE_TEXT_Y = 144
DIALOGUE_LINE_SPACING = 14
TYPEWRITER_CHARS_PER_FRAME = 1
BLIP_EVERY_CHARS = 3

NAME_MAX_LENGTH = 10
DEFAULT_PLAYER_NAME = "Learner"

# Professor Bald's script: at most two lines of ~38 characters per box.
# "jingle" plays the ta-da sound when the box opens.
PROFESSOR_INTRO = (
    {"lines": ("Ahem! Hello there, young one!", "Come in, don't be shy.")},
    {"lines": ("I am Professor Bald. Yes, the", "head shines on purpose.")},
    {"lines": ("Welcome to YELLOW OLIVE ACADEMY!", "Ta-da!"), "jingle": True},
    {"lines": ("Here you will learn Kubernetes,", "one tiny lesson at a time.")},
    {"lines": ("But first things first...", "what is your name?")},
)
NAME_PROMPT_LINES = ("Type your name, then press ENTER:", "> {name}{cursor}")
PROFESSOR_OUTRO = (
    {"lines": ("{name}! What a splendid name.",)},
    {"lines": ("Your adventure starts now,", "{name}. Pick a lesson!")},
)
