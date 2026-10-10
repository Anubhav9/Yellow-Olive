import pyxel

from screens.pods import constants
from screens.pods.base_screen import BaseScreen
import text_renderer

class PodIntroductionScreen(BaseScreen):
    page_name = "screen_1_pods_introduction"

    def draw(self):
        super().draw(
            constants.NUMBER_1,
            constants.PODS,
            constants.LESSON_BADGE_11,
            constants.LESSON_TITLE_POD,
            constants.LESSON_EXPLAIN_A,
            constants.LESSON_EXPLAIN_B,
            constants.LESSON_EXPLAIN_C,
            constants.DIALOGUE_A,
            constants.DIALOGUE_B,
            constants.DIALOGUE_C,
        )
        self.draw_pod_diagram()

    def draw_pod_diagram(self):
        pod_x = 186
        pod_y = 42
        pod_w = 88
        pod_h = 52

        pyxel.rect(pod_x, pod_y, pod_w, pod_h, 1)
        pyxel.rectb(pod_x, pod_y, pod_w, pod_h, pyxel.COLOR_CYAN)

        label_x = pod_x + 28
        label_y = pod_y - 6
        pyxel.rect(label_x, label_y, 32, 14, pyxel.COLOR_GREEN)
        pyxel.rectb(label_x, label_y, 32, 14, pyxel.COLOR_CYAN)
        text_renderer.draw_text_centered(label_x, label_y + 1, 32, "Pod", pyxel.COLOR_WHITE)

        cx = pod_x + 14
        cy = pod_y + 14
        cw = 60
        ch = 28

        pyxel.rect(cx, cy, cw, ch, pyxel.COLOR_ORANGE)
        pyxel.rectb(cx, cy, cw, ch, pyxel.COLOR_YELLOW)
        pyxel.rectb(cx + 2, cy + 2, cw - 4, ch - 4, pyxel.COLOR_BROWN)

        pyxel.rect(cx + 2, cy + 7, cw - 4, 14, pyxel.COLOR_WHITE)
        text_renderer.draw_text_centered(cx + 2, cy + 8, cw - 4, "Container", pyxel.COLOR_BLACK)
