"""Yellow Olive Academy - a Pyxel lesson on how Kubernetes nests its objects.

Runs in the browser through the Pyxel WASM custom element (see index.html).
Space (or a tap) advances the lesson one beat at a time.
"""

import pyxel

SCREEN_WIDTH = 256
SCREEN_HEIGHT = 240

COLOR_BACKGROUND = 7
COLOR_INK = 1
COLOR_NODE = 6
COLOR_NAMESPACE = 15
COLOR_POD = 11
COLOR_CONTAINER = 3
COLOR_HIGHLIGHT = 8

FONT_WIDTH = 4
POP_FRAMES = 10

NODE_BOX = (12, 30, 232, 142)
NAMESPACES = (
    ("kube-system", 20),
    ("default", 96),
    ("oakwood", 172),
)
NAMESPACE_TOP = 48
NAMESPACE_WIDTH = 64
NAMESPACE_HEIGHT = 116
POD_WIDTH = 48
POD_HEIGHT = 42
POD_TOPS = (64, 116)
CONTAINER_SIZE = 14

# Pods per namespace, and how many containers each pod holds once
# the multi-container beat is reached.
PODS = (
    (("psyquack-api", 1),),
    (("electromon-web", 1), ("electromon-job", 1)),
    (("bald-cache", 2),),
)

STEP_TITLE = 0
STEP_NODE = 1
STEP_NAMESPACE = 2
STEP_POD = 3
STEP_CONTAINER = 4
STEP_SIDECAR = 5
STEP_RECAP = 6
LAST_STEP = STEP_RECAP

NARRATION = {
    STEP_NODE: (
        "A NODE IS ONE MACHINE IN YOUR CLUSTER.",
        "IT LENDS ITS CPU, MEMORY AND DISK TO KUBERNETES,",
        "AND EVERYTHING YOU DEPLOY HAS TO LAND ON ONE.",
    ),
    STEP_NAMESPACE: (
        "NAMESPACES ARE THE TOWNS INSIDE THE CLUSTER.",
        "THEY SPLIT ONE CLUSTER INTO SEPARATE NEIGHBOURHOODS",
        "SO NAMES, QUOTAS AND ACCESS DO NOT COLLIDE.",
    ),
    STEP_POD: (
        "A POD - A POKEPOD - IS THE SMALLEST THING YOU DEPLOY.",
        "IT IS SCHEDULED ONTO A NODE, INSIDE A NAMESPACE,",
        "AND IT CARRIES ITS OWN IP AND LIFECYCLE.",
    ),
    STEP_CONTAINER: (
        "A CONTAINER - A POSEMON - RUNS INSIDE THE POD.",
        "IT IS THE IMAGE, THE PORT AND THE PROCESS:",
        "THE PART THAT ACTUALLY SERVES YOUR TRAFFIC.",
    ),
    STEP_SIDECAR: (
        "A POD CAN HOLD MORE THAN ONE POSEMON.",
        "SIDECARS SHARE THE POD'S NETWORK AND VOLUMES,",
        "SO THEY START, MOVE AND DIE TOGETHER.",
    ),
    STEP_RECAP: (
        "NODE > NAMESPACE > POD > CONTAINER.",
        "EVERY CHALLENGE IN YELLOW OLIVE LIVES SOMEWHERE",
        "ON THAT MAP. NOW GO AND FIX A CLUSTER, TRAINER.",
    ),
}

TITLE_LINES = (
    "WELCOME TO YELLOW OLIVE ACADEMY",
    "THE RETRO TUI ACADEMY FOR LEARNING KUBERNETES",
)


def _centered_text(y, text, color):
    x = (SCREEN_WIDTH - len(text) * FONT_WIDTH) // 2
    pyxel.text(x, y, text, color)


def _eased(progress):
    """Ease-out so boxes overshoot slightly as they pop in."""
    return 1.0 - (1.0 - progress) ** 3


class Academy:
    def __init__(self):
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="Yellow Olive Academy", fps=30)
        pyxel.mouse(True)
        self.step = STEP_TITLE
        self.step_frame = 0
        pyxel.run(self.update, self.draw)

    def update(self):
        self.step_frame += 1
        if not self._advance_pressed():
            return
        self.step = STEP_TITLE if self.step >= LAST_STEP else self.step + 1
        self.step_frame = 0

    def _advance_pressed(self):
        return (
            pyxel.btnp(pyxel.KEY_SPACE)
            or pyxel.btnp(pyxel.KEY_RETURN)
            or pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)
            or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A)
        )

    def _pop(self, step):
        """0.0 -> 1.0 growth factor for elements revealed at `step`."""
        if self.step < step:
            return 0.0
        if self.step > step:
            return 1.0
        return _eased(min(self.step_frame, POP_FRAMES) / POP_FRAMES)

    def draw(self):
        pyxel.cls(COLOR_BACKGROUND)
        if self.step == STEP_TITLE:
            self._draw_title()
        else:
            self._draw_header()
            self._draw_diagram()
            self._draw_narration()
        self._draw_prompt()

    def _draw_title(self):
        pyxel.rectb(16, 76, SCREEN_WIDTH - 32, 60, COLOR_INK)
        pyxel.rect(16, 76, SCREEN_WIDTH - 32, 10, COLOR_NAMESPACE)
        _centered_text(78, "* YELLOW OLIVE ACADEMY *", COLOR_INK)
        _centered_text(100, TITLE_LINES[0], COLOR_INK)
        _centered_text(112, TITLE_LINES[1], COLOR_CONTAINER)

    def _draw_header(self):
        pyxel.rect(0, 0, SCREEN_WIDTH, 12, COLOR_NAMESPACE)
        pyxel.text(6, 3, "YELLOW OLIVE ACADEMY", COLOR_INK)
        pyxel.text(SCREEN_WIDTH - 46, 3, f"LESSON {self.step}/{LAST_STEP}", COLOR_INK)

    def _draw_diagram(self):
        self._draw_box(NODE_BOX, COLOR_NODE, "NODE  minikube-01", self._pop(STEP_NODE))
        namespace_pop = self._pop(STEP_NAMESPACE)
        if namespace_pop <= 0.0:
            return
        for index, (name, x) in enumerate(NAMESPACES):
            self._draw_box(
                (x, NAMESPACE_TOP, NAMESPACE_WIDTH, NAMESPACE_HEIGHT),
                COLOR_NAMESPACE,
                f"NS {name}",
                namespace_pop,
            )
            self._draw_pods(index, x)

    def _draw_pods(self, namespace_index, namespace_x):
        pod_pop = self._pop(STEP_POD)
        if pod_pop <= 0.0:
            return
        for pod_index, (pod_name, container_count) in enumerate(PODS[namespace_index]):
            pod_x = namespace_x + 8
            pod_y = POD_TOPS[pod_index]
            self._draw_box(
                (pod_x, pod_y, POD_WIDTH, POD_HEIGHT), COLOR_POD, f"POD {pod_name}", pod_pop
            )
            self._draw_containers(pod_x, pod_y, container_count)

    def _draw_containers(self, pod_x, pod_y, container_count):
        container_pop = self._pop(STEP_CONTAINER)
        if container_pop <= 0.0:
            return
        self._draw_box(
            (pod_x + 6, pod_y + 16, CONTAINER_SIZE, CONTAINER_SIZE),
            COLOR_CONTAINER,
            None,
            container_pop,
        )
        if container_count < 2:
            return
        sidecar_pop = self._pop(STEP_SIDECAR)
        if sidecar_pop <= 0.0:
            return
        self._draw_box(
            (pod_x + 26, pod_y + 16, CONTAINER_SIZE, CONTAINER_SIZE),
            COLOR_HIGHLIGHT,
            None,
            sidecar_pop,
        )
        if self.step == STEP_SIDECAR:
            pyxel.text(pod_x + 4, pod_y + 34, "SIDECAR", COLOR_HIGHLIGHT)

    def _draw_box(self, box, fill, label, pop):
        if pop <= 0.0:
            return
        x, y, width, height = box
        drawn_width = max(2, int(width * pop))
        drawn_height = max(2, int(height * pop))
        drawn_x = x + (width - drawn_width) // 2
        drawn_y = y + (height - drawn_height) // 2
        pyxel.rect(drawn_x, drawn_y, drawn_width, drawn_height, fill)
        pyxel.rectb(drawn_x, drawn_y, drawn_width, drawn_height, COLOR_INK)
        if label and pop >= 1.0:
            pyxel.text(x + 3, y + 3, label[: (width - 4) // FONT_WIDTH], COLOR_INK)

    def _draw_narration(self):
        pyxel.rect(0, 180, SCREEN_WIDTH, SCREEN_HEIGHT - 180, COLOR_INK)
        for line_index, line in enumerate(NARRATION[self.step]):
            pyxel.text(8, 190 + line_index * 10, line, COLOR_BACKGROUND)

    def _draw_prompt(self):
        if pyxel.frame_count % 30 < 20:
            _centered_text(
                SCREEN_HEIGHT - 12,
                "PRESS SPACE TO CONTINUE",
                COLOR_INK if self.step == STEP_TITLE else COLOR_NAMESPACE,
            )


Academy()
