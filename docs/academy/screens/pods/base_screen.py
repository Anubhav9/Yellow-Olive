import pyxel
from screens.pods import constants
import global_constants
import text_renderer
from manager import screen_manager


class BaseScreen:
    def __init__(self):
        self.current_page_name="screen_1_pods_introduction"
        # Set this to hand control over to the next page.
        self.next_screen = None
        # The map is 320 wide, more than an image bank (256), so it gets its own image.
        self.classroom_map = pyxel.Image(global_constants.WINDOW_WIDTH, global_constants.WINDOW_HEIGHT)
        self.classroom_map.load(0, 0, constants.CLASSROOM_MAP_ASSET_PATH)
        pyxel.images[global_constants.PLAYER_IMAGE_BANK].load(0, 0, constants.PLAYER_ASSET_PATH)
        pyxel.images[global_constants.PROFESSOR_IMAGE_BANK].load(0, 0, constants.PROFESSOR_ASSET_PATH)

    def update(self):
        # Z moves on to the next lesson, in the order from manager/screen_manager.py.
        next_page = screen_manager.screen_management_map().get(self.page_name)
        if pyxel.btnp(pyxel.KEY_Z) and next_page and next_page != "home_screen":
            self.next_screen = screen_manager.screen_to_class_mapping_map(next_page)()

    def draw(self, lesson_number, lesson_name, lesson_badge, lesson_header,
             lesson_explain_text_a, lesson_explanation_text_b, lesson_explanation_text_c,
             dialogue_text_a, dialogue_text_b, dialogue_text_c):
        self.draw_background()
        self.draw_header(lesson_number, lesson_name)
        self.draw_lesson_panel(
            lesson_badge, lesson_header,
            lesson_explain_text_a, lesson_explanation_text_b, lesson_explanation_text_c
        )
        self.draw_characters()
        self.draw_dialogue_box(dialogue_text_a, dialogue_text_b, dialogue_text_c)

    def draw_background(self):
        pyxel.cls(0)
        pyxel.blt(
            0, 0, self.classroom_map,
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
        # The chalkboard: lesson text on the left, each screen draws its diagram on the right.
        x, y = constants.CHALKBOARD_X, constants.CHALKBOARD_Y
        w, h = constants.CHALKBOARD_WIDTH, constants.CHALKBOARD_HEIGHT
        frame = constants.CHALKBOARD_FRAME
        pyxel.rect(x - frame, y - frame, w + frame * 2, h + frame * 2, pyxel.COLOR_BROWN)
        pyxel.rect(x, y, w, h, global_constants.PALETTE.index(constants.CHALKBOARD_COLOR_RGB))

        text_x = constants.LESSON_TEXT_X
        pyxel.rect(text_x, constants.LESSON_BADGE_Y,
                   constants.LESSON_BADGE_WIDTH, constants.LESSON_BADGE_HEIGHT, pyxel.COLOR_YELLOW)
        text_renderer.draw_text_centered(text_x, constants.LESSON_BADGE_Y + 1,
                                         constants.LESSON_BADGE_WIDTH, lesson_badge, pyxel.COLOR_BLACK)
        text_renderer.draw_text(text_x, constants.LESSON_TITLE_Y, lesson_text, pyxel.COLOR_YELLOW)
        lines = (lesson_explain_text_a, lesson_explanation_text_b, lesson_explanation_text_c)
        for row, line in enumerate(lines):
            text_renderer.draw_text(
                text_x, constants.LESSON_EXPLAIN_Y + row * text_renderer.LINE_HEIGHT,
                line, pyxel.COLOR_WHITE,
            )

    def draw_characters(self):
        self.draw_character(global_constants.PROFESSOR_IMAGE_BANK, constants.PROFESSOR_X, global_constants.RIGHT)
        self.draw_character(global_constants.PLAYER_IMAGE_BANK, constants.PLAYER_X, global_constants.LEFT)

    def draw_character(self, bank, x, facing):
        pyxel.blt(
            x, constants.CHARACTERS_Y, bank,
            global_constants.STANDING_FRAME * global_constants.FRAME_WIDTH,
            facing * global_constants.FRAME_HEIGHT,
            global_constants.FRAME_WIDTH, global_constants.FRAME_HEIGHT,
            global_constants.KEY,
        )

    def draw_dialogue_box(self, dialogue_text_a, dialogue_text_b, dialogue_text_c):
        x, y = constants.DIALOGUE_BOX_X, constants.DIALOGUE_BOX_Y
        w, h = constants.DIALOGUE_BOX_WIDTH, constants.DIALOGUE_BOX_HEIGHT
        pyxel.rect(x, y, w, h, pyxel.COLOR_BLACK)
        pyxel.rectb(x, y, w, h, pyxel.COLOR_YELLOW)
        text_renderer.draw_text(x + 6, y + 2, constants.PROFESSOR_NAME, pyxel.COLOR_YELLOW)
        for row, line in enumerate((dialogue_text_a, dialogue_text_b, dialogue_text_c)):
            text_renderer.draw_text(x + 6, y + 2 + (row + 1) * text_renderer.LINE_HEIGHT, line, pyxel.COLOR_WHITE)

        pyxel.tri(
            x + w - 12, y + h - 9,
            x + w - 5, y + h - 9,
            x + w - 8, y + h - 5,
            pyxel.COLOR_YELLOW,
        )
