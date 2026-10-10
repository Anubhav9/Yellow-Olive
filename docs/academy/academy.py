"""Browser entry point for Yellow Olive Academy (Pyxel WASM)."""

import string

import pyxel

import global_constants
from global_constants import DOWN, LEFT, RIGHT, UP
from screens.classroom_screen import constants as classroom
from screens.intro_screen import constants as town


CHARACTER_ASSET_PATH = "assets/tilesets/Characters/character_1.png"

SPEED=3

TOWN, CLASSROOM = "town", "classroom"

# Only the player's feet bump into things, so his head can overlap a roof edge.
FEET_X, FEET_Y, FEET_WIDTH, FEET_HEIGHT = 3, 24, 10, 8


def overlaps(ax, ay, aw, ah, bx, by, bw, bh):
    return ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah


def feet_at(x, y):
    return (x + FEET_X, y + FEET_Y, FEET_WIDTH, FEET_HEIGHT)


def can_stand_at(x, y, solids):
    if x < 0 or y < 0:
        return False
    if (x + global_constants.FRAME_WIDTH > global_constants.WINDOW_WIDTH
            or y + global_constants.FRAME_HEIGHT > global_constants.WINDOW_HEIGHT):
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
        pyxel.colors[:] = global_constants.PALETTE

        # Screens load their images when created, so import them after the palette is set.
        from screens.classroom_screen.classroom_screen import ClassroomScreen
        from screens.intro_screen.intro_screen import IntroScreen
        self.intro_screen = IntroScreen()
        self.classroom_screen = ClassroomScreen()

        self.music=pyxel.sounds[0].pcm(town.TOWN_MAP_MUSIC_PATH)
        # Set background music volume
        pyxel.channels[0].gain = 0.5

        # Play continuously
        pyxel.play(0, 0, loop=True)

        pyxel.images[global_constants.PLAYER_IMAGE_BANK].load(0, 0, CHARACTER_ASSET_PATH)

        self.screen = TOWN
        self.player_x = town.PLAYER_START_X
        self.player_y = town.PLAYER_START_Y
        self.facing = UP

        self.talking = False
        self.dialogue_index = 0
        self.player_name = ""

        pyxel.run(self.update, self.draw)

    def enter_classroom(self):
        self.screen = CLASSROOM
        self.player_x = classroom.PLAYER_START_X
        self.player_y = classroom.PLAYER_START_Y
        self.facing = UP

    def in_dialogue(self):
        return self.screen == CLASSROOM and self.talking

    def facing_professor(self):
        step = {UP: (0, -1), DOWN: (0, 1), LEFT: (-1, 0), RIGHT: (1, 0)}[self.facing]
        x, y, w, h = feet_at(self.player_x, self.player_y)
        reach = classroom.TALK_REACH
        return overlaps(x + step[0] * reach, y + step[1] * reach, w, h, *classroom.PROFESSOR_TALK_BOX)

    def start_talking(self):
        self.talking = True
        # Once he knows your name, he skips straight to the welcome.
        self.dialogue_index = classroom.NAME_PROMPT_INDEX + 1 if self.player_name else 0

    def update(self):
        if self.in_dialogue():
            self.update_dialogue()
            return

        if self.screen == CLASSROOM and pyxel.btnp(pyxel.KEY_Z) and self.facing_professor():
            self.start_talking()
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
        elif pyxel.btnp(pyxel.KEY_Z) or enter:
            self.dialogue_index += 1
        if self.dialogue_index >= len(classroom.DIALOGUE):
            self.talking = False

    def draw(self):
        if self.screen == TOWN:
            self.intro_screen.draw(self.player_x, self.player_y, self.facing)
        else:
            self.classroom_screen.draw(
                self.player_x, self.player_y, self.facing,
                self.in_dialogue(), self.dialogue_index, self.player_name, self.talk_prompt(),
            )

    def talk_prompt(self):
        if self.facing_professor():
            return classroom.TALK_PROMPT
        # Until the first chat, remind the player how to start one.
        return "" if self.player_name else classroom.FIND_PROFESSOR_PROMPT


YellowOliveAcademy()
