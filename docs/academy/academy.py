"""Browser entry point for Yellow Olive Academy (Pyxel WASM)."""
from re import purge

import pyxel

import global_constants
from screens.intro_screen import constants as town


CHARACTER_ASSET_PATH = "assets/tilesets/Characters/character_1.png"

FRAME_WIDTH = 16
FRAME_HEIGHT = 32
STANDING_FRAME = 1
DOWN, LEFT, RIGHT, UP = 0, 1, 2, 3
SPEED=3

# Every colour used by town_map.png and character_1.png.
# 0-15 are Pyxel's default colours, so pyxel.COLOR_BLACK etc. still work.
PALETTE = [
    0x000000, 0x2B335F, 0x7E2072, 0x19959C, 0x8B4852, 0x395C98, 0xA9C1FF, 0xEEEEEE,
    0xD4186C, 0xD38441, 0xE9C35B, 0x70C6A9, 0x7696DE, 0xA3A3A3, 0xFF9798, 0xEDC7B0,
    0xFFFFFF, 0xB7B9C9, 0x68B9F3, 0x9BADB7, 0xE3A97D, 0x639BFF, 0x808089, 0xC16F59,
    0x5B6EE1, 0x4B692F, 0x5F616F, 0xD95763, 0x8F563B, 0x954A4D, 0x464447, 0x693F1F,
    0xA33C1F, 0x753C4D, 0x323C39, 0x663931, 0x342F29, 0x3E1F27, 0x1E0301, 0xF6F9F6,
    0xFBF236, 0x99E550, 0x5FCDE4, 0x6ABE30, 0xCEA462, 0x8DA1B2, 0xD9A066, 0x3F8CE6,
    0x8A6F30, 0x696A6A, 0x896030, 0x60607A, 0x595652, 0x4F514E, 0x524B24, 0x474856,
    0xAC3232, 0x4E3042, 0x45283C, 0x352434, 0x222034, 0xDBDBDB, 0xFFD1AD, 0xC0C0D1,
    0xD2A3A3, 0x855353, 0x4F4F4F, 0x823847, 0x272727, 0xFF00FF, 0xC4C4C4, 0xF6B68A,
    0x949494, 0xDA8A68, 0x82828A, 0x703838, 0x383838, 0x3F2828, 0x4B1C1C, 0xC46817,
    0xE8E8F6, 0xAAA2C8, 0xE58D3E, 0xA9672C, 0x6F4F32, 0x373F50,
]
KEY = PALETTE.index(0xFF00FF)  # magenta = see-through

# Only the player's feet bump into things, so his head can overlap a roof edge.
FEET_X, FEET_Y, FEET_WIDTH, FEET_HEIGHT = 3, 24, 10, 8


def overlaps(ax, ay, aw, ah, bx, by, bw, bh):
    return ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah


def can_stand_at(x, y, solids):
    if x < 0 or y < 0:
        return False
    if x + FRAME_WIDTH > global_constants.WINDOW_WIDTH or y + FRAME_HEIGHT > global_constants.WINDOW_HEIGHT:
        return False
    feet = (x + FEET_X, y + FEET_Y, FEET_WIDTH, FEET_HEIGHT)
    return not any(overlaps(*feet, *solid) for solid in solids)


class YellowOliveAcademy:
    def __init__(self):
        pyxel.init(
            global_constants.WINDOW_WIDTH,
            global_constants.WINDOW_HEIGHT,
            title=global_constants.WINDOW_TITLE,
            fps=30,
            quit_key=pyxel.KEY_Q,
        )
        # text_renderer.initialize()
        # screen_manager.initialize()

        # Set the full palette before loading, so images keep their exact colours.
        pyxel.colors[:] = PALETTE

        # The map is 320 wide, more than an image bank (256), so it gets its own image.
        self.town = pyxel.Image(global_constants.WINDOW_WIDTH, global_constants.WINDOW_HEIGHT)
        self.town.load(0, 0, town.TOWN_MAP_ASSET_PATH)
        self.music=pyxel.sounds[0].pcm(town.TOWN_MAP_MUSIC_PATH)
        # Set background music volume
        pyxel.channels[0].gain = 0.5

        # Play continuously
        pyxel.play(0, 0, loop=True)

        pyxel.images[1].load(0, 0, CHARACTER_ASSET_PATH)

        self.player_x = town.PLAYER_START_X
        self.player_y = town.PLAYER_START_Y
        self.facing = UP

        pyxel.run(self.update, self.draw)

    def update(self):
        dx, dy = 0, 0
        if(pyxel.btnp(pyxel.KEY_UP)):
            dy = -SPEED
            self.facing = UP
        elif(pyxel.btnp(pyxel.KEY_DOWN)):
            dy = SPEED
            self.facing = DOWN
        elif(pyxel.btnp(pyxel.KEY_LEFT)):
            dx = -SPEED
            self.facing = LEFT
        elif(pyxel.btnp(pyxel.KEY_RIGHT)):
            dx = SPEED
            self.facing = RIGHT

        # Only move if the new spot is free; he still turns to face the wall.
        if can_stand_at(self.player_x + dx, self.player_y + dy, town.SOLIDS):
            self.player_x += dx
            self.player_y += dy

    def draw(self):
        pyxel.cls(0)
        pyxel.blt(0, 0, self.town, 0, 0, global_constants.WINDOW_WIDTH, global_constants.WINDOW_HEIGHT)
        pyxel.blt(
            self.player_x,
            self.player_y,
            1,
            STANDING_FRAME * FRAME_WIDTH,
            self.facing * FRAME_HEIGHT,
            FRAME_WIDTH,
            FRAME_HEIGHT,
            KEY,
        )


YellowOliveAcademy()
