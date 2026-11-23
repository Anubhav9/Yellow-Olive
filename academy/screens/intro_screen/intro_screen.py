import pyxel

import global_constants
import text_renderer
from global_constants import DOWN, LEFT, RIGHT, UP
from screens.classroom_screen.classroom_screen import ClassroomScreen
from screens.intro_screen import constants


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


class IntroScreen:
    def __init__(self):
        # The map is 320 wide, more than an image bank (256), so it gets its own image.
        self.town_map = pyxel.Image(global_constants.WINDOW_WIDTH, global_constants.WINDOW_HEIGHT)
        self.town_map.load(0, 0, constants.TOWN_MAP_ASSET_PATH)

        self.player_x = constants.PLAYER_START_X
        self.player_y = constants.PLAYER_START_Y
        self.facing = UP
        # Set this to hand control over to the next page.
        self.next_screen = None

    def update(self):
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

        if overlaps(*feet_at(new_x, new_y), *constants.ACADEMY_DOOR):
            self.next_screen = ClassroomScreen()
            return

        # Only move if the new spot is free; he still turns to face the wall.
        if can_stand_at(new_x, new_y, constants.SOLIDS):
            self.player_x = new_x
            self.player_y = new_y

    def draw(self):
        pyxel.cls(0)
        pyxel.blt(0, 0, self.town_map, 0, 0, global_constants.WINDOW_WIDTH, global_constants.WINDOW_HEIGHT)
        self.draw_academy_sign()
        pyxel.blt(
            self.player_x, self.player_y, global_constants.PLAYER_IMAGE_BANK,
            global_constants.STANDING_FRAME * global_constants.FRAME_WIDTH,
            self.facing * global_constants.FRAME_HEIGHT,
            global_constants.FRAME_WIDTH, global_constants.FRAME_HEIGHT,
            global_constants.KEY,
        )
        self.draw_prompt(constants.GOAL_PROMPT)

    def draw_prompt(self, prompt):
        w = text_renderer.text_width(prompt) + 12
        x = (global_constants.WINDOW_WIDTH - w) // 2
        y, h = constants.PROMPT_Y, constants.PROMPT_HEIGHT
        pyxel.rect(x, y, w, h, pyxel.COLOR_BLACK)
        pyxel.rectb(x, y, w, h, pyxel.COLOR_YELLOW)
        text_renderer.draw_text_centered(x, y + 2, w, prompt, pyxel.COLOR_WHITE)

    def draw_academy_sign(self):
        x, y, w, h = constants.ACADEMY_SIGN
        pyxel.rect(x, y, w, h, pyxel.COLOR_BLACK)
        pyxel.rectb(x, y, w, h, pyxel.COLOR_YELLOW)
        for row, line in enumerate(constants.ACADEMY_SIGN_LINES):
            pyxel.text(x + (w - len(line) * 4) // 2 + 1, y + 2 + row * 6, line, pyxel.COLOR_YELLOW)
