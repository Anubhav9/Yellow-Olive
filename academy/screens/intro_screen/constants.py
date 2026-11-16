"""Oakwood Meadows town map: what's on it and where the player starts."""

TOWN_MAP_ASSET_PATH = "assets/town_map.png"
TOWN_MAP_MUSIC_PATH= "assets/music/tutorial_screen.wav"

PLAYER_START_X = 180
PLAYER_START_Y = 148

# Walking: one step per arrow press. Only the player's feet bump into things,
# so his head can overlap a roof edge or a desk top.
SPEED = 3
FEET_X, FEET_Y, FEET_WIDTH, FEET_HEIGHT = 3, 24, 10, 8

# Hint at the top of the screen, telling the player where to go.
GOAL_PROMPT = "Enter the Yellow Olive Academy"
PROMPT_Y = 4
PROMPT_HEIGHT = 16

# Walking into this doorway of the middle building opens the classroom.
ACADEMY_DOOR = (176, 140, 16, 6)

# Name plate on the middle building: (x, y, width, height) and its two lines.
ACADEMY_SIGN = (140, 111, 56, 15)
ACADEMY_SIGN_LINES = ("YELLOW OLIVE", "ACADEMY")

# Things on town_map.png the player can't walk through, as (x, y, width, height).
SOLIDS = [
    # houses
    (2, 54, 76, 90),     # green house
    (130, 22, 76, 122),  # Academy
    (226, 54, 76, 90),   # grey house
    # trees
    (-11, -10, 42, 48), (103, -16, 42, 48), (209, -14, 42, 48), (299, -6, 42, 48),
    (87, 40, 42, 48), (303, 96, 42, 48), (-17, 90, 42, 48),
    # mailboxes and sign
    (89, 128, 10, 24), (303, 136, 10, 24),
    (206, 118, 16, 27),
    # hedges
    (0, 160, 144, 20), (224, 160, 96, 20),
]
