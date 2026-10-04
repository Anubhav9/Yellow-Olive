import pyxel
from screens.pods import constants
import global_constants
import text_renderer
from manager import screen_manager



classroom_image = pyxel.Image(
    global_constants.WINDOW_WIDTH,
    global_constants.WINDOW_HEIGHT
)
classroom_image.load(0, 0, "assets/classroom.png")

PROFESSOR_TRANSPARENT_COLOR = 15


def _remove_edge_connected_color(image, width, height, color):
    transparent_key = PROFESSOR_TRANSPARENT_COLOR
    visited = set()
    queue = []

    for x in range(width):
        for y in (0, height - 1):
            if image.pget(x, y) == color:
                queue.append((x, y))
    for y in range(height):
        for x in (0, width - 1):
            if image.pget(x, y) == color:
                queue.append((x, y))

    while queue:
        x, y = queue.pop()
        if (x, y) in visited:
            continue
        if x < 0 or x >= width or y < 0 or y >= height:
            continue
        if image.pget(x, y) != color:
            continue

        visited.add((x, y))
        image.pset(x, y, transparent_key)
        queue.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))

    return transparent_key


def _load_professor_image():
    source = pyxel.Image(
        global_constants.PROFESSOR_SOURCE_WIDTH,
        global_constants.PROFESSOR_SOURCE_HEIGHT,
    )
    source.load(0, 0, "assets/professor.png")
    transparent_key = _remove_edge_connected_color(
        source,
        global_constants.PROFESSOR_SOURCE_WIDTH,
        global_constants.PROFESSOR_SOURCE_HEIGHT,
        pyxel.COLOR_BLACK,
    )
    return source, transparent_key


professor_image, professor_transparent_color = _load_professor_image()


class BaseScreen:
    def __init__(self):
        self.current_page_name="screen_1_pods_introduction"

    def update(self):
        pass

    def draw(self, lesson_number, lesson_name, lesson_badge, lesson_header,
             lesson_explain_text_a, lesson_explanation_text_b, lesson_explanation_text_c,
             dialogue_text_a, dialogue_text_b, dialogue_text_c):
        self.draw_background()
        self.draw_header(lesson_number, lesson_name)
        self.draw_lesson_panel(
            lesson_badge, lesson_header,
            lesson_explain_text_a, lesson_explanation_text_b, lesson_explanation_text_c
        )
        self.draw_professor()
        self.draw_dialogue_box(dialogue_text_a, dialogue_text_b, dialogue_text_c)
        self.draw_next_button()

    def draw_background(self):
        pyxel.cls(0)
        pyxel.blt(
            0, 0, classroom_image,
            0, 0,
            global_constants.WINDOW_WIDTH,
            global_constants.WINDOW_HEIGHT,
        )

    def draw_header(self, chapter_number, chapter_name):
        x = global_constants.HEADER_X_CORDINATE
        y = global_constants.HEADER_Y_CORDINATE
        w = global_constants.HEADER_WIDTH
        h = global_constants.HEADER_HEIGHT

        pyxel.rect(x, y, w, h, pyxel.COLOR_BLACK)
        pyxel.rectb(x, y, w, h, pyxel.COLOR_YELLOW)

        text_renderer.draw_text(
            global_constants.HEADER_TEXT_YELLOW_OLIVE_X_CORDINATE,
            global_constants.HEADER_TEXT_YELLOW_OLIVE_Y_CORDINATE,
            constants.YELLOW_OLIVE,
            pyxel.COLOR_YELLOW,
        )
        text_renderer.draw_text(
            global_constants.HEADER_TEXT_ACADEMY_X_CORDINATE,
            global_constants.HEADER_TEXT_ACADEMY_Y_CORDINATE,
            constants.ACADEMY,
            pyxel.COLOR_WHITE,
        )
        text_renderer.draw_text(
            global_constants.HEADER_TEXT_DIVIDER_X_CORDINATE,
            global_constants.HEADER_TEXT_DIVIDER_Y_CORDINATE,
            constants.DIVIDER,
            pyxel.COLOR_WHITE,
        )
        text_renderer.draw_text(
            global_constants.HEADER_TEXT_CHAPTER_NUMBER_X_CORDINATE,
            global_constants.HEADER_TEXT_CHAPTER_NUMBER_Y_CORDINATE,
            chapter_number,
            pyxel.COLOR_WHITE,
        )
        text_renderer.draw_text(
            global_constants.HEADER_TEXT_CHAPTER_NAME_X_CORDINATE,
            global_constants.HEADER_TEXT_CHAPTER_NAME_Y_CORDINATE,
            chapter_name,
            pyxel.COLOR_WHITE,
        )

    def draw_lesson_panel(self, lesson_badge, lesson_text,
                          lesson_explain_text_a, lesson_explanation_text_b, lesson_explanation_text_c):
        x = global_constants.LESSON_PANEL_X_CORDINATE
        y = global_constants.LESSON_PANEL_Y_CORDINATE
        w = global_constants.LESSON_PANEL_WIDTH
        h = global_constants.LESSON_PANEL_HEIGHT

        pyxel.rect(x, y, w, h, pyxel.COLOR_BLACK)
        pyxel.rectb(x, y, w, h, pyxel.COLOR_YELLOW)

        # Lesson badge tab
        pyxel.rect(
            global_constants.LESSON_SUBHEADING_X_CORDINATE,
            global_constants.LESSON_SUBHEADING_Y_CORDINATE,
            global_constants.LESSON_SUBHEADING_WIDTH,
            global_constants.LESSON_SUBHEADING_HEIGHT,
            pyxel.COLOR_YELLOW,
        )
        text_renderer.draw_text(
            global_constants.LESSON_TEXT_X_CORDINATE,
            global_constants.LESSON_TEXT_Y_CORDINATE,
            lesson_badge,
            pyxel.COLOR_BLACK,
        )

        text_renderer.draw_text(
            global_constants.LESSON_TITLE_X_CORDINATE,
            global_constants.LESSON_TITLE_Y_CORDINATE,
            lesson_text,
            pyxel.COLOR_YELLOW,
        )
        text_renderer.draw_text(
            global_constants.LESSON_EXPLAINATION_TEXT_A_X_CORDINATE,
            global_constants.LESSON_EXPLAINATION_TEXT_A_Y_CORDINATE,
            lesson_explain_text_a,
            pyxel.COLOR_WHITE,
        )
        text_renderer.draw_text(
            global_constants.LESSON_EXPLAINATION_TEXT_B_X_CORDINATE,
            global_constants.LESSON_EXPLAINATION_TEXT_B_Y_CORDINATE,
            lesson_explanation_text_b,
            pyxel.COLOR_WHITE,
        )
        text_renderer.draw_text(
            global_constants.LESSON_EXPLAINATION_TEXT_C_X_CORDINATE,
            global_constants.LESSON_EXPLAINATION_TEXT_C_Y_CORDINATE,
            lesson_explanation_text_c,
            pyxel.COLOR_WHITE,
        )

    def draw_professor(self):
        x = global_constants.PROFESSOR_X_CORDINATE
        y = global_constants.PROFESSOR_Y_CORDINATE
        w = global_constants.PROFESSOR_WIDTH
        h = global_constants.PROFESSOR_HEIGHT

        pyxel.elli(x + 14, y + h - 6, 36, 6, 1)
        pyxel.blt(
            x, y, professor_image,
            0, 0, w, h,
            professor_transparent_color,
        )

    def draw_dialogue_box(self, dialogue_text_a, dialogue_text_b, dialogue_text_c):
        x = global_constants.DIALOGUE_BOX_X_CORDINATE
        y = global_constants.DIALOGUE_BOX_Y_CORDINATE
        w = global_constants.DIALOGUE_BOX_WIDTH
        h = global_constants.DIALOGUE_BOX_HEIGHT
        text_x = x + global_constants.DIALOGUE_TEXT_X_OFFSET
        text_y = y + global_constants.DIALOGUE_TEXT_Y_OFFSET
        line_spacing = global_constants.DIALOGUE_TEXT_LINE_SPACING

        pyxel.rect(x, y, w, h, pyxel.COLOR_YELLOW)
        pyxel.rect(x + 1, y + 1, w - 2, h - 2, pyxel.COLOR_WHITE)

        # Pointer toward professor
        pyxel.tri(x, y + 6, x, y + 16, x - 8, y + 11, pyxel.COLOR_YELLOW)
        pyxel.tri(x + 1, y + 8, x + 1, y + 14, x - 5, y + 11, pyxel.COLOR_WHITE)

        text_renderer.draw_text(text_x, text_y, dialogue_text_a, pyxel.COLOR_NAVY)
        text_renderer.draw_text(text_x, text_y + line_spacing, dialogue_text_b, pyxel.COLOR_NAVY)
        text_renderer.draw_text(text_x, text_y + line_spacing * 2, dialogue_text_c, pyxel.COLOR_NAVY)

        pyxel.tri(
            x + w - 12, y + h - 9,
            x + w - 5, y + h - 9,
            x + w - 8, y + h - 5,
            pyxel.COLOR_NAVY,
        )

    def draw_next_button(self):
        x = global_constants.NEXT_BUTTON_X_CORDINATE
        y = global_constants.NEXT_BUTTON_Y_CORDINATE
        w = global_constants.NEXT_BUTTON_WIDTH
        h = global_constants.NEXT_BUTTON_HEIGHT

        pyxel.rect(x, y, w, h, pyxel.COLOR_YELLOW)
        pyxel.rectb(x, y, w, h, pyxel.COLOR_WHITE)
        text_renderer.draw_text_centered(x, y + 8, w, "Next >", pyxel.COLOR_BLACK)
