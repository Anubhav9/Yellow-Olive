import pyxel

from screens.pods import constants
from screens.pods.base_screen import BaseScreen
import text_renderer


class RestartPolicyScreen(BaseScreen):

    def draw(self):
        super().draw(
            constants.NUMBER_1,
            constants.PODS,
            constants.LESSON_BADGE_17,
            constants.LESSON_TITLE_RESTART,
            constants.LESSON_17_A,
            constants.LESSON_17_B,
            constants.LESSON_17_C,
            constants.DIALOGUE_17_A,
            constants.DIALOGUE_17_B,
            constants.DIALOGUE_17_C,
        )
        self.draw_diagram()

    def draw_diagram(self):
        labels = ("Always", "OnFailure", "Never")
        x = 186
        y = 36
        for index, label in enumerate(labels):
            box_y = y + index * 22
            pyxel.rect(x, box_y, 100, 18, pyxel.COLOR_NAVY)
            pyxel.rectb(x, box_y, 100, 18, pyxel.COLOR_YELLOW)
            text_renderer.draw_text_centered(x, box_y + 3, 100, label, pyxel.COLOR_WHITE)
