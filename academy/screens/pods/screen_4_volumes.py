import pyxel

from screens.pods import constants
from screens.pods.base_screen import BaseScreen
import text_renderer


class VolumesScreen(BaseScreen):
    page_name = "screen_4_volumes"

    def draw(self):
        super().draw(
            constants.NUMBER_1,
            constants.PODS,
            constants.LESSON_BADGE_14,
            constants.LESSON_TITLE_VOLUMES,
            constants.LESSON_14_A,
            constants.LESSON_14_B,
            constants.LESSON_14_C,
            constants.DIALOGUE_14_A,
            constants.DIALOGUE_14_B,
            constants.DIALOGUE_14_C,
        )
        self.draw_diagram()

    def draw_diagram(self):
        pod_x = 178
        pod_y = 36
        pod_w = 120
        pod_h = 60

        pyxel.rect(pod_x, pod_y, pod_w, pod_h, 1)
        pyxel.rectb(pod_x, pod_y, pod_w, pod_h, pyxel.COLOR_CYAN)

        pyxel.rect(pod_x + 10, pod_y + 8, 44, 22, pyxel.COLOR_ORANGE)
        pyxel.rectb(pod_x + 10, pod_y + 8, 44, 22, pyxel.COLOR_YELLOW)
        text_renderer.draw_text_centered(pod_x + 10, pod_y + 13, 44, "App", pyxel.COLOR_BLACK)

        pyxel.rect(pod_x + 66, pod_y + 8, 44, 22, pyxel.COLOR_ORANGE)
        pyxel.rectb(pod_x + 66, pod_y + 8, 44, 22, pyxel.COLOR_YELLOW)
        text_renderer.draw_text_centered(pod_x + 66, pod_y + 13, 44, "Log", pyxel.COLOR_BLACK)

        pyxel.rect(pod_x + 8, pod_y + 38, 104, 16, 5)
        pyxel.rectb(pod_x + 8, pod_y + 38, 104, 16, pyxel.COLOR_WHITE)
        text_renderer.draw_text_centered(pod_x + 8, pod_y + 40, 104, "Volume", pyxel.COLOR_WHITE)
