import pyxel

from screens.pods import constants
from screens.pods.base_screen import BaseScreen
import text_renderer


class ContainersScreen(BaseScreen):
    page_name = "screen_2_containers"

    def draw(self):
        super().draw(
            constants.NUMBER_1,
            constants.PODS,
            constants.LESSON_BADGE_12,
            constants.LESSON_TITLE_CONTAINERS,
            constants.LESSON_12_A,
            constants.LESSON_12_B,
            constants.LESSON_12_C,
            constants.DIALOGUE_12_A,
            constants.DIALOGUE_12_B,
            constants.DIALOGUE_12_C,
        )
        self.draw_diagram()

    def draw_diagram(self):
        pod_x = 178
        pod_y = 40
        pod_w = 120
        pod_h = 56

        pyxel.rect(pod_x, pod_y, pod_w, pod_h, 1)
        pyxel.rectb(pod_x, pod_y, pod_w, pod_h, pyxel.COLOR_CYAN)
        text_renderer.draw_text_centered(pod_x, pod_y + 4, pod_w, "Pod", pyxel.COLOR_WHITE)

        self._container(pod_x + 8, pod_y + 20, "App")
        self._container(pod_x + 66, pod_y + 20, "Log")

    def _container(self, x, y, label):
        pyxel.rect(x, y, 46, 28, pyxel.COLOR_ORANGE)
        pyxel.rectb(x, y, 46, 28, pyxel.COLOR_YELLOW)
        pyxel.rect(x + 4, y + 8, 38, 12, pyxel.COLOR_WHITE)
        text_renderer.draw_text_centered(x + 4, y + 8, 38, label, pyxel.COLOR_BLACK)
