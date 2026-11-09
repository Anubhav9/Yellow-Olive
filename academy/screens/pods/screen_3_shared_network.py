import pyxel

from screens.pods import constants
from screens.pods.base_screen import BaseScreen
import text_renderer


class SharedNetworkScreen(BaseScreen):
    page_name = "screen_3_shared_network"

    def draw(self):
        super().draw(
            constants.NUMBER_1,
            constants.PODS,
            constants.LESSON_BADGE_13,
            constants.LESSON_TITLE_NETWORK,
            constants.LESSON_13_A,
            constants.LESSON_13_B,
            constants.LESSON_13_C,
            constants.DIALOGUE_13_A,
            constants.DIALOGUE_13_B,
            constants.DIALOGUE_13_C,
        )
        self.draw_diagram()

    def draw_diagram(self):
        pod_x = 178
        pod_y = 44
        pod_w = 120
        pod_h = 50

        pyxel.rect(pod_x, pod_y, pod_w, pod_h, 1)
        pyxel.rectb(pod_x, pod_y, pod_w, pod_h, pyxel.COLOR_CYAN)

        pyxel.rect(pod_x + 24, pod_y - 8, 72, 14, pyxel.COLOR_GREEN)
        pyxel.rectb(pod_x + 24, pod_y - 8, 72, 14, pyxel.COLOR_CYAN)
        text_renderer.draw_text_centered(pod_x + 24, pod_y - 7, 72, "10.0.0.8", pyxel.COLOR_WHITE)

        pyxel.rect(pod_x + 10, pod_y + 16, 44, 24, pyxel.COLOR_ORANGE)
        pyxel.rectb(pod_x + 10, pod_y + 16, 44, 24, pyxel.COLOR_YELLOW)
        text_renderer.draw_text_centered(pod_x + 10, pod_y + 22, 44, "App", pyxel.COLOR_BLACK)

        pyxel.rect(pod_x + 66, pod_y + 16, 44, 24, pyxel.COLOR_ORANGE)
        pyxel.rectb(pod_x + 66, pod_y + 16, 44, 24, pyxel.COLOR_YELLOW)
        text_renderer.draw_text_centered(pod_x + 66, pod_y + 22, 44, "Log", pyxel.COLOR_BLACK)
