import pyxel

from screens.pods import constants
from screens.pods.base_screen import BaseScreen
import text_renderer


class LabelsScreen(BaseScreen):

    def draw(self):
        super().draw(
            constants.NUMBER_1,
            constants.PODS,
            constants.LESSON_BADGE_16,
            constants.LESSON_TITLE_LABELS,
            constants.LESSON_16_A,
            constants.LESSON_16_B,
            constants.LESSON_16_C,
            constants.DIALOGUE_16_A,
            constants.DIALOGUE_16_B,
            constants.DIALOGUE_16_C,
        )
        self.draw_diagram()

    def draw_diagram(self):
        pod_x = 186
        pod_y = 48
        pod_w = 100
        pod_h = 42

        pyxel.rect(pod_x, pod_y, pod_w, pod_h, 1)
        pyxel.rectb(pod_x, pod_y, pod_w, pod_h, pyxel.COLOR_CYAN)
        text_renderer.draw_text_centered(pod_x, pod_y + 15, pod_w, "Pod", pyxel.COLOR_WHITE)

        self._tag(pod_x + 8, pod_y - 16, "app=web")
        self._tag(pod_x + 8, pod_y + pod_h + 4, "tier=front")

    def _tag(self, x, y, label):
        pyxel.rect(x, y, 84, 14, pyxel.COLOR_YELLOW)
        pyxel.rectb(x, y, 84, 14, pyxel.COLOR_WHITE)
        text_renderer.draw_text_centered(x, y + 1, 84, label, pyxel.COLOR_BLACK)
