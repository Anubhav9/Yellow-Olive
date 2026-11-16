import pyxel
import global_constants
import text_renderer
from screens.home_screen import constants


school_image = pyxel.Image(global_constants.WINDOW_WIDTH, global_constants.WINDOW_HEIGHT)
school_image.load(0, 0, "assets/school-image.png")


def _mouse_inside(x, y, width, height):
    return (
        x <= pyxel.mouse_x <= x + width
        and y <= pyxel.mouse_y <= y + height
    )


def _draw_button(x, y, width, height, label):
    hovered = _mouse_inside(x, y, width, height)
    fill = pyxel.COLOR_YELLOW if hovered else pyxel.COLOR_BLACK
    text_color = pyxel.COLOR_BLACK if hovered else pyxel.COLOR_WHITE

    pyxel.rect(x, y, width, height, fill)
    pyxel.rectb(x, y, width, height, pyxel.COLOR_YELLOW)
    text_renderer.draw_text_centered(x, y + 2, width, label, text_color)


class HomeScreen:
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

        pyxel.rect(
            constants.TITLE_X,
            constants.TITLE_Y,
            constants.TITLE_WIDTH,
            constants.TITLE_HEIGHT,
            pyxel.COLOR_BLACK,
        )
        pyxel.rectb(
            constants.TITLE_X,
            constants.TITLE_Y,
            constants.TITLE_WIDTH,
            constants.TITLE_HEIGHT,
            pyxel.COLOR_YELLOW,
        )
        text_renderer.draw_text_centered(
            constants.TITLE_X, constants.TITLE_Y + 3,
            constants.TITLE_WIDTH, constants.YELLOW_OLIVE, pyxel.COLOR_YELLOW,
        )
        text_renderer.draw_text_centered(
            constants.TITLE_X, constants.TITLE_Y + 15,
            constants.TITLE_WIDTH, constants.ACADEMY, pyxel.COLOR_WHITE,
        )
        text_renderer.draw_text_centered(
            constants.TITLE_X, constants.TITLE_Y + 27,
            constants.TITLE_WIDTH, constants.LEARN_KUBERNETES_VISUALLY, pyxel.COLOR_WHITE,
        )

        _draw_button(
            constants.BUTTON_X, constants.START_BUTTON_Y,
            constants.BUTTON_WIDTH, constants.BUTTON_HEIGHT, constants.START,
        )
        _draw_button(
            constants.BUTTON_X, constants.LESSONS_BUTTON_Y,
            constants.BUTTON_WIDTH, constants.BUTTON_HEIGHT, constants.LESSON,
        )
        _draw_button(
            constants.BUTTON_X, constants.EXIT_BUTTON_Y,
            constants.BUTTON_WIDTH, constants.BUTTON_HEIGHT, constants.EXIT,
        )
