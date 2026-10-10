import pyxel

import global_constants
from screens.intro_screen import constants


class IntroScreen:
    def __init__(self):
        # The map is 320 wide, more than an image bank (256), so it gets its own image.
        self.town_map = pyxel.Image(global_constants.WINDOW_WIDTH, global_constants.WINDOW_HEIGHT)
        self.town_map.load(0, 0, constants.TOWN_MAP_ASSET_PATH)

    def draw(self, player_x, player_y, facing):
        pyxel.cls(0)
        pyxel.blt(0, 0, self.town_map, 0, 0, global_constants.WINDOW_WIDTH, global_constants.WINDOW_HEIGHT)
        self.draw_academy_sign()
        pyxel.blt(
            player_x, player_y, global_constants.PLAYER_IMAGE_BANK,
            global_constants.STANDING_FRAME * global_constants.FRAME_WIDTH,
            facing * global_constants.FRAME_HEIGHT,
            global_constants.FRAME_WIDTH, global_constants.FRAME_HEIGHT,
            global_constants.KEY,
        )

    def draw_academy_sign(self):
        x, y, w, h = constants.ACADEMY_SIGN
        pyxel.rect(x, y, w, h, pyxel.COLOR_BLACK)
        pyxel.rectb(x, y, w, h, pyxel.COLOR_YELLOW)
        for row, line in enumerate(constants.ACADEMY_SIGN_LINES):
            pyxel.text(x + (w - len(line) * 4) // 2 + 1, y + 2 + row * 6, line, pyxel.COLOR_YELLOW)
