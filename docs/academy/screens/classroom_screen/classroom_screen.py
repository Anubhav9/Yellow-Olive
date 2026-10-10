import pyxel

import global_constants
import text_renderer
from screens.classroom_screen import constants


class ClassroomScreen:
    def __init__(self):
        # The map is 320 wide, more than an image bank (256), so it gets its own image.
        self.classroom_map = pyxel.Image(global_constants.WINDOW_WIDTH, global_constants.WINDOW_HEIGHT)
        self.classroom_map.load(0, 0, constants.CLASSROOM_MAP_ASSET_PATH)
        pyxel.images[global_constants.PROFESSOR_IMAGE_BANK].load(0, 0, constants.PROFESSOR_ASSET_PATH)

    def draw(self, player_x, player_y, facing, talking, dialogue_index, player_name):
        pyxel.cls(0)
        pyxel.blt(0, 0, self.classroom_map, 0, 0, global_constants.WINDOW_WIDTH, global_constants.WINDOW_HEIGHT)
        # Whoever stands lower on screen is drawn last, so they appear in front.
        people = sorted([
            (constants.PROFESSOR_Y, global_constants.PROFESSOR_IMAGE_BANK, constants.PROFESSOR_X, global_constants.DOWN),
            (player_y, global_constants.PLAYER_IMAGE_BANK, player_x, facing),
        ])
        for y, bank, x, direction in people:
            self.draw_character(bank, x, y, direction)
        if talking:
            self.draw_dialogue(dialogue_index, player_name)

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
