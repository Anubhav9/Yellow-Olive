"""Oakwood Meadows town map: what's on it and where the player starts."""

TOWN_MAP_ASSET_PATH = "assets/town_map.png"
TOWN_MAP_MUSIC_PATH= "assets/music/intro_screen_music.wav"

PLAYER_START_X = 180
PLAYER_START_Y = 140

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
