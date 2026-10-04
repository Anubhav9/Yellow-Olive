import pyxel
import global_constants
import text_renderer
from screens.home_screen import constants
from screens.home_screen.home_screen import school_image, _draw_button, _mouse_inside


class LessonsScreen:
    def __init__(self):
        pass

    def draw(self):
        pyxel.cls(0)
        pyxel.blt(
            0, 0, school_image,
            0, 0,
            global_constants.WINDOW_WIDTH,
            global_constants.WINDOW_HEIGHT,
        )

        pyxel.rect(24, 8, 272, 168, pyxel.COLOR_BLACK)
        pyxel.rectb(24, 8, 272, 168, pyxel.COLOR_YELLOW)
        text_renderer.draw_text_centered(
            24, 14, 272, constants.LESSONS_TITLE, pyxel.COLOR_YELLOW,
        )

        for index, (_page_name, label) in enumerate(constants.LESSON_PAGES):
            row_y = (
                constants.LESSON_ROW_Y
                + index * (constants.LESSON_ROW_HEIGHT + constants.LESSON_ROW_GAP)
            )
            hovered = _mouse_inside(
                constants.LESSON_ROW_X, row_y,
                constants.LESSON_ROW_WIDTH, constants.LESSON_ROW_HEIGHT,
            )
            fill = pyxel.COLOR_YELLOW if hovered else 1
            text_color = pyxel.COLOR_BLACK if hovered else pyxel.COLOR_WHITE
            pyxel.rect(
                constants.LESSON_ROW_X, row_y,
                constants.LESSON_ROW_WIDTH, constants.LESSON_ROW_HEIGHT, fill,
            )
            pyxel.rectb(
                constants.LESSON_ROW_X, row_y,
                constants.LESSON_ROW_WIDTH, constants.LESSON_ROW_HEIGHT, pyxel.COLOR_YELLOW,
            )
            text_renderer.draw_text(
                constants.LESSON_ROW_X + 8, row_y + 2, label, text_color,
            )

        _draw_button(
            constants.BACK_BUTTON_X, constants.BACK_BUTTON_Y,
            constants.BACK_BUTTON_WIDTH, constants.BACK_BUTTON_HEIGHT, constants.BACK,
        )
