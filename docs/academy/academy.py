"""Browser entry point for Yellow Olive Academy (Pyxel WASM)."""

import string

import pyxel

import global_constants
import text_renderer
from screens.classroom_screen import constants as classroom
from screens.intro_screen import constants as town


CHARACTER_ASSET_PATH = "assets/tilesets/Characters/character_1.png"

FRAME_WIDTH = 16
FRAME_HEIGHT = 32
STANDING_FRAME = 1
DOWN, LEFT, RIGHT, UP = 0, 1, 2, 3
SPEED=3

TOWN, CLASSROOM = "town", "classroom"

# Every colour used by the town map, the classroom and both character sheets.
# 0-15 are Pyxel's default colours, so pyxel.COLOR_BLACK etc. still work.
PALETTE = [
    0x000000, 0x2B335F, 0x7E2072, 0x19959C, 0x8B4852, 0x395C98, 0xA9C1FF, 0xEEEEEE,
    0xD4186C, 0xD38441, 0xE9C35B, 0x70C6A9, 0x7696DE, 0xA3A3A3, 0xFF9798, 0xEDC7B0,
    0x4B692F, 0x6ABE30, 0x99E550, 0x524B24, 0x222034, 0x1E0301, 0x663931, 0x45283C,
    0x8F563B, 0xA33C1F, 0x3E1F27, 0x342F29, 0xB7B9C9, 0x464447, 0x323C39, 0x696A6A,
    0x595652, 0x5F616F, 0x4F514E, 0x896030, 0xCEA462, 0x8A6F30, 0xD9A066, 0x693F1F,
    0x4E3042, 0x8DA1B2, 0x68B9F3, 0x3F8CE6, 0xF6F9F6, 0x9BADB7, 0x639BFF, 0x5B6EE1,
    0xFFFFFF, 0x5FCDE4, 0x352434, 0xC16F59, 0xE3A97D, 0x753C4D, 0x954A4D, 0x474856,
    0xD95763, 0xAC3232, 0xFBF236, 0x60607A, 0x808089, 0xFF00FF, 0x855353, 0xD2A3A3,
    0x4B1C1C, 0xDA8A68, 0xFFD1AD, 0xF6B68A, 0x703838, 0x949494, 0xC4C4C4, 0x4F4F4F,
    0xDBDBDB, 0x272727, 0x823847, 0xC0C0D1, 0x383838, 0x82828A, 0x3F2828, 0x808088,
    0xF8F8F8, 0x3A3A50, 0xF3EFE3, 0xA4A4A4, 0xC4DAE8, 0xC3DBDE, 0xB5CDCF, 0xCCE3E5,
    0xE4E1D7, 0xBEB5A6, 0x32675A, 0x46756A, 0xA79888, 0x588278, 0xA6E4AF, 0xB9ECC1,
    0x898D6D, 0xA79796, 0xC4BEB6, 0xB3AAA5, 0xF1CE8E, 0xC78C59, 0xE0B870, 0x9D8367,
    0xA2866B, 0xA4886D, 0xAA8E73, 0xAE9276, 0x917A62, 0x9D8873, 0xA28C77, 0xA48E79,
    0xAA947F, 0xA85F46, 0xAE9882, 0x942454, 0xFFF7F0, 0xB4393E, 0xF8D239, 0xF2B22B,
    0xF0E2DB, 0x8D7963, 0x927C67, 0x947E68, 0x99836E, 0xB5754D, 0x9D8771, 0x447E70,
    0x356267, 0xC5D583, 0xD5839F, 0x946A5B, 0x83D5C7, 0xAF927B, 0xA4846C, 0x9D866E,
    0xA28A72, 0xA48C74, 0xAA927A, 0xAE967D, 0x285B5B, 0xCAB27F, 0xA03258, 0xCA8854,
    0x5E92A5, 0x9EC6D5, 0xE4B05D, 0xBE7149, 0xBBE4E4, 0xB5704A, 0xC38952, 0x35535E,
    0xE4C47C, 0xD9A16A, 0x4A8580, 0x373F50, 0xE8E8F6, 0xAAA2C8, 0x6F4F32, 0xA9672C,
    0xE58D3E, 0xC46817,
]
KEY = PALETTE.index(0xFF00FF)  # magenta = see-through

# Only the player's feet bump into things, so his head can overlap a roof edge.
FEET_X, FEET_Y, FEET_WIDTH, FEET_HEIGHT = 3, 24, 10, 8


def overlaps(ax, ay, aw, ah, bx, by, bw, bh):
    return ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah


def feet_at(x, y):
    return (x + FEET_X, y + FEET_Y, FEET_WIDTH, FEET_HEIGHT)


def can_stand_at(x, y, solids):
    if x < 0 or y < 0:
        return False
    if x + FRAME_WIDTH > global_constants.WINDOW_WIDTH or y + FRAME_HEIGHT > global_constants.WINDOW_HEIGHT:
        return False
    return not any(overlaps(*feet_at(x, y), *solid) for solid in solids)


class YellowOliveAcademy:
    def __init__(self):
        pyxel.init(
            global_constants.WINDOW_WIDTH,
            global_constants.WINDOW_HEIGHT,
            title=global_constants.WINDOW_TITLE,
            fps=30,
            quit_key=pyxel.KEY_Q,
        )

        # Set the full palette before loading, so images keep their exact colours.
        pyxel.colors[:] = PALETTE

        # The maps are 320 wide, more than an image bank (256), so each gets its own image.
        self.town = pyxel.Image(global_constants.WINDOW_WIDTH, global_constants.WINDOW_HEIGHT)
        self.town.load(0, 0, town.TOWN_MAP_ASSET_PATH)
        self.classroom = pyxel.Image(global_constants.WINDOW_WIDTH, global_constants.WINDOW_HEIGHT)
        self.classroom.load(0, 0, classroom.CLASSROOM_MAP_ASSET_PATH)

        self.music=pyxel.sounds[0].pcm(town.TOWN_MAP_MUSIC_PATH)
        # Set background music volume
        pyxel.channels[0].gain = 0.5

        # Play continuously
        pyxel.play(0, 0, loop=True)

        pyxel.images[1].load(0, 0, CHARACTER_ASSET_PATH)
        pyxel.images[2].load(0, 0, classroom.PROFESSOR_ASSET_PATH)

        self.screen = TOWN
        self.player_x = town.PLAYER_START_X
        self.player_y = town.PLAYER_START_Y
        self.facing = UP

        self.dialogue_index = 0
        self.player_name = ""

        pyxel.run(self.update, self.draw)

    def enter_classroom(self):
        self.screen = CLASSROOM
        self.player_x = classroom.PLAYER_START_X
        self.player_y = classroom.PLAYER_START_Y
        self.facing = UP

    def in_dialogue(self):
        return self.screen == CLASSROOM and self.dialogue_index < len(classroom.DIALOGUE)

    def update(self):
        if self.in_dialogue():
            self.update_dialogue()
            return

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

        new_x, new_y = self.player_x + dx, self.player_y + dy
        if self.screen == TOWN and overlaps(*feet_at(new_x, new_y), *town.ACADEMY_DOOR):
            self.enter_classroom()
            return

        solids = town.SOLIDS if self.screen == TOWN else classroom.SOLIDS
        # Only move if the new spot is free; he still turns to face the wall.
        if can_stand_at(new_x, new_y, solids):
            self.player_x = new_x
            self.player_y = new_y

    def update_dialogue(self):
        enter = pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.KEY_KP_ENTER)
        if self.dialogue_index == classroom.NAME_PROMPT_INDEX:
            for letter in string.ascii_uppercase:
                if pyxel.btnp(getattr(pyxel, "KEY_" + letter)) and len(self.player_name) < classroom.NAME_MAX_LENGTH:
                    self.player_name += letter if not self.player_name else letter.lower()
            if pyxel.btnp(pyxel.KEY_BACKSPACE):
                self.player_name = self.player_name[:-1]
            if enter and self.player_name:
                self.dialogue_index += 1
        elif enter or pyxel.btnp(pyxel.KEY_SPACE):
            self.dialogue_index += 1

    def draw(self):
        pyxel.cls(0)
        if self.screen == TOWN:
            pyxel.blt(0, 0, self.town, 0, 0, global_constants.WINDOW_WIDTH, global_constants.WINDOW_HEIGHT)
            self.draw_academy_sign()
            self.draw_character(1, self.player_x, self.player_y, self.facing)
            return

        pyxel.blt(0, 0, self.classroom, 0, 0, global_constants.WINDOW_WIDTH, global_constants.WINDOW_HEIGHT)
        # Whoever stands lower on screen is drawn last, so they appear in front.
        people = sorted([
            (classroom.PROFESSOR_Y, 2, classroom.PROFESSOR_X, DOWN),
            (self.player_y, 1, self.player_x, self.facing),
        ])
        for y, bank, x, facing in people:
            self.draw_character(bank, x, y, facing)
        if self.in_dialogue():
            self.draw_dialogue()

    def draw_character(self, bank, x, y, facing):
        pyxel.blt(x, y, bank, STANDING_FRAME * FRAME_WIDTH, facing * FRAME_HEIGHT, FRAME_WIDTH, FRAME_HEIGHT, KEY)

    def draw_academy_sign(self):
        x, y, w, h = town.ACADEMY_SIGN
        pyxel.rect(x, y, w, h, pyxel.COLOR_BLACK)
        pyxel.rectb(x, y, w, h, pyxel.COLOR_YELLOW)
        for row, line in enumerate(town.ACADEMY_SIGN_LINES):
            pyxel.text(x + (w - len(line) * 4) // 2 + 1, y + 2 + row * 6, line, pyxel.COLOR_YELLOW)

    def draw_dialogue(self):
        x, y = classroom.DIALOGUE_BOX_X, classroom.DIALOGUE_BOX_Y
        w, h = classroom.DIALOGUE_BOX_WIDTH, classroom.DIALOGUE_BOX_HEIGHT
        pyxel.rect(x, y, w, h, pyxel.COLOR_BLACK)
        pyxel.rectb(x, y, w, h, pyxel.COLOR_YELLOW)
        text_renderer.draw_text(x + 6, y + 2, classroom.PROFESSOR_NAME, pyxel.COLOR_YELLOW)

        line_a, line_b = classroom.DIALOGUE[self.dialogue_index]
        if self.dialogue_index == classroom.NAME_PROMPT_INDEX:
            cursor = "_" if pyxel.frame_count // 15 % 2 == 0 else " "
            line_b = "> " + self.player_name + cursor
        for row, line in enumerate((line_a, line_b)):
            text_renderer.draw_text(
                x + 6, y + 2 + (row + 1) * text_renderer.LINE_HEIGHT,
                line.format(name=self.player_name), pyxel.COLOR_WHITE,
            )
        hint = classroom.ADVANCE_HINT
        pyxel.text(x + w - len(hint) * 4 - 4, y + h - 8, hint, pyxel.COLOR_YELLOW)


YellowOliveAcademy()
