import string

import pyxel

import global_constants
import text_renderer
from global_constants import DOWN, LEFT, RIGHT, UP
from screens.classroom_screen import constants


def overlaps(ax, ay, aw, ah, bx, by, bw, bh):
    return ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah


def feet_at(x, y):
    return (x + constants.FEET_X, y + constants.FEET_Y, constants.FEET_WIDTH, constants.FEET_HEIGHT)


def can_stand_at(x, y, solids):
    if x < 0 or y < 0:
        return False
    if (x + global_constants.FRAME_WIDTH > global_constants.WINDOW_WIDTH
            or y + global_constants.FRAME_HEIGHT > global_constants.WINDOW_HEIGHT):
        return False
    return not any(overlaps(*feet_at(x, y), *solid) for solid in solids)


class ClassroomScreen:
    def __init__(self):
        # The map is 320 wide, more than an image bank (256), so it gets its own image.
        self.classroom_map = pyxel.Image(global_constants.WINDOW_WIDTH, global_constants.WINDOW_HEIGHT)
        self.classroom_map.load(0, 0, constants.CLASSROOM_MAP_ASSET_PATH)
        pyxel.images[global_constants.PROFESSOR_IMAGE_BANK].load(0, 0, constants.PROFESSOR_ASSET_PATH)

        self.player_x = constants.PLAYER_START_X
        self.player_y = constants.PLAYER_START_Y
        self.facing = UP
        self.talking = False
        self.dialogue_index = 0
        self.player_name = ""

    def update(self):
        if self.talking:
            self.update_dialogue()
            return

        if pyxel.btnp(pyxel.KEY_Z) and self.facing_professor():
            self.talking = True
            # Once he knows your name, he skips straight to the welcome.
            self.dialogue_index = constants.NAME_PROMPT_INDEX + 1 if self.player_name else 0
            return

        dx, dy = 0, 0
        if pyxel.btnp(pyxel.KEY_UP):
            dy = -constants.SPEED
            self.facing = UP
        elif pyxel.btnp(pyxel.KEY_DOWN):
            dy = constants.SPEED
            self.facing = DOWN
        elif pyxel.btnp(pyxel.KEY_LEFT):
            dx = -constants.SPEED
            self.facing = LEFT
        elif pyxel.btnp(pyxel.KEY_RIGHT):
            dx = constants.SPEED
            self.facing = RIGHT
        new_x, new_y = self.player_x + dx, self.player_y + dy

        # Only move if the new spot is free; he still turns to face the wall.
        if can_stand_at(new_x, new_y, constants.SOLIDS):
            self.player_x = new_x
            self.player_y = new_y

    def update_dialogue(self):
        enter = pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.KEY_KP_ENTER)
        if self.dialogue_index == constants.NAME_PROMPT_INDEX:
            for letter in string.ascii_uppercase:
                if pyxel.btnp(getattr(pyxel, "KEY_" + letter)) and len(self.player_name) < constants.NAME_MAX_LENGTH:
                    self.player_name += letter if not self.player_name else letter.lower()
            if pyxel.btnp(pyxel.KEY_BACKSPACE):
                self.player_name = self.player_name[:-1]
            if enter and self.player_name:
                self.dialogue_index += 1
        elif pyxel.btnp(pyxel.KEY_Z) or enter:
            self.dialogue_index += 1

        if self.dialogue_index >= len(constants.DIALOGUE):
            self.talking = False

    def facing_professor(self):
        step = {UP: (0, -1), DOWN: (0, 1), LEFT: (-1, 0), RIGHT: (1, 0)}[self.facing]
        x, y, w, h = feet_at(self.player_x, self.player_y)
        reach = constants.TALK_REACH
        return overlaps(x + step[0] * reach, y + step[1] * reach, w, h, *constants.PROFESSOR_TALK_BOX)

    def talk_prompt(self):
        if self.facing_professor():
            return constants.TALK_PROMPT
        # Until the first chat, remind the player how to start one.
        return "" if self.player_name else constants.FIND_PROFESSOR_PROMPT

    def draw(self):
        pyxel.cls(0)
        pyxel.blt(0, 0, self.classroom_map, 0, 0, global_constants.WINDOW_WIDTH, global_constants.WINDOW_HEIGHT)
        # Whoever stands lower on screen is drawn last, so they appear in front.
        people = sorted([
            (constants.PROFESSOR_Y, global_constants.PROFESSOR_IMAGE_BANK, constants.PROFESSOR_X, DOWN),
            (self.player_y, global_constants.PLAYER_IMAGE_BANK, self.player_x, self.facing),
        ])
        for y, bank, x, direction in people:
            self.draw_character(bank, x, y, direction)
        if self.talking:
            self.draw_dialogue(self.dialogue_index, self.player_name)
        else:
            self.draw_prompt(self.talk_prompt())

    def draw_prompt(self, prompt):
        w = text_renderer.text_width(prompt) + 12
        x = (global_constants.WINDOW_WIDTH - w) // 2
        y, h = constants.PROMPT_Y, constants.PROMPT_HEIGHT
        pyxel.rect(x, y, w, h, pyxel.COLOR_BLACK)
        pyxel.rectb(x, y, w, h, pyxel.COLOR_YELLOW)
        text_renderer.draw_text_centered(x, y + 2, w, prompt, pyxel.COLOR_WHITE)

    def draw_character(self, bank, x, y, facing):
        pyxel.blt(
            x, y, bank,
            global_constants.STANDING_FRAME * global_constants.FRAME_WIDTH,
            facing * global_constants.FRAME_HEIGHT,
            global_constants.FRAME_WIDTH, global_constants.FRAME_HEIGHT,
            global_constants.KEY,
        )

    def draw_dialogue(self, dialogue_index, player_name):
        x, y = constants.DIALOGUE_BOX_X, constants.DIALOGUE_BOX_Y
        w, h = constants.DIALOGUE_BOX_WIDTH, constants.DIALOGUE_BOX_HEIGHT
        pyxel.rect(x, y, w, h, pyxel.COLOR_BLACK)
        pyxel.rectb(x, y, w, h, pyxel.COLOR_YELLOW)
        text_renderer.draw_text(x + 6, y + 2, constants.PROFESSOR_NAME, pyxel.COLOR_YELLOW)

        line_a, line_b = constants.DIALOGUE[dialogue_index]
        asking_name = dialogue_index == constants.NAME_PROMPT_INDEX
        if asking_name:
            cursor = "_" if pyxel.frame_count // 15 % 2 == 0 else " "
            line_b = "> " + player_name + cursor
        for row, line in enumerate((line_a, line_b)):
            text_renderer.draw_text(
                x + 6, y + 2 + (row + 1) * text_renderer.LINE_HEIGHT,
                line.format(name=player_name), pyxel.COLOR_WHITE,
            )
        hint = constants.NAME_HINT if asking_name else constants.ADVANCE_HINT
        pyxel.text(x + w - len(hint) * 4 - 4, y + h - 8, hint, pyxel.COLOR_YELLOW)
