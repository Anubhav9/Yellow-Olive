import pyxel

from screens.pods import constants
from screens.pods.base_screen import BaseScreen
import text_renderer


class PodPhasesScreen(BaseScreen):

    def draw(self):
        super().draw(
            constants.NUMBER_1,
            constants.PODS,
            constants.LESSON_BADGE_15,
            constants.LESSON_TITLE_PHASES,
            constants.LESSON_15_A,
            constants.LESSON_15_B,
            constants.LESSON_15_C,
            constants.DIALOGUE_15_A,
            constants.DIALOGUE_15_B,
            constants.DIALOGUE_15_C,
        )
        self.draw_diagram()

    def draw_diagram(self):
        labels = ("Pending", "Running", "Succeeded")
        colors = (pyxel.COLOR_YELLOW, pyxel.COLOR_GREEN, pyxel.COLOR_CYAN)
        x = 176
        y = 40
        for index, label in enumerate(labels):
            box_y = y + index * 20
            pyxel.rect(x, box_y, 110, 16, colors[index])
            pyxel.rectb(x, box_y, 110, 16, pyxel.COLOR_WHITE)
            text_renderer.draw_text_centered(x, box_y + 2, 110, label, pyxel.COLOR_BLACK)
