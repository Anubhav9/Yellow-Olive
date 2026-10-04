"""Browser entry point for Yellow Olive Academy (Pyxel WASM)."""

import pyxel

import global_constants
import text_renderer
from manager import screen_manager
from screens.home_screen import constants as home_constants


class YellowOliveAcademy:

    def __init__(self):
        pyxel.init(
            global_constants.WINDOW_WIDTH,
            global_constants.WINDOW_HEIGHT,
            global_constants.WINDOW_TITLE,
        )
        pyxel.screen_mode(0)
        text_renderer.init_fonts()
        pyxel.mouse(True)

        self.current_page_name = "home_screen"
        self.current_screen = (
            screen_manager.screen_to_class_mapping_map(
                self.current_page_name
            )()
        )

        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()

        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            if self.current_page_name == "home_screen":
                self.handle_home_click()
            elif self.current_page_name == "lessons_screen":
                self.handle_lessons_click()
            elif self._inside(
                global_constants.NEXT_BUTTON_X_CORDINATE,
                global_constants.NEXT_BUTTON_Y_CORDINATE,
                global_constants.NEXT_BUTTON_WIDTH,
                global_constants.NEXT_BUTTON_HEIGHT,
            ):
                self.navigate_to_next_page()

    def handle_home_click(self):
        if self._inside(
            home_constants.BUTTON_X,
            home_constants.START_BUTTON_Y,
            home_constants.BUTTON_WIDTH,
            home_constants.BUTTON_HEIGHT,
        ):
            self.open_page("screen_1_pods_introduction")
        elif self._inside(
            home_constants.BUTTON_X,
            home_constants.LESSONS_BUTTON_Y,
            home_constants.BUTTON_WIDTH,
            home_constants.BUTTON_HEIGHT,
        ):
            self.open_page("lessons_screen")
        elif self._inside(
            home_constants.BUTTON_X,
            home_constants.EXIT_BUTTON_Y,
            home_constants.BUTTON_WIDTH,
            home_constants.BUTTON_HEIGHT,
        ):
            pyxel.quit()

    def handle_lessons_click(self):
        if self._inside(
            home_constants.BACK_BUTTON_X,
            home_constants.BACK_BUTTON_Y,
            home_constants.BACK_BUTTON_WIDTH,
            home_constants.BACK_BUTTON_HEIGHT,
        ):
            self.open_page("home_screen")
            return

        for index, (page_name, _label) in enumerate(home_constants.LESSON_PAGES):
            row_y = (
                home_constants.LESSON_ROW_Y
                + index * (
                    home_constants.LESSON_ROW_HEIGHT
                    + home_constants.LESSON_ROW_GAP
                )
            )
            if self._inside(
                home_constants.LESSON_ROW_X,
                row_y,
                home_constants.LESSON_ROW_WIDTH,
                home_constants.LESSON_ROW_HEIGHT,
            ):
                self.open_page(page_name)
                return

    def navigate_to_next_page(self):
        next_page_name = screen_manager.screen_management_map()[
            self.current_page_name
        ]
        self.open_page(next_page_name)

    def open_page(self, page_name):
        self.current_page_name = page_name
        screen_class = screen_manager.screen_to_class_mapping_map(page_name)
        self.current_screen = screen_class()

    def draw(self):
        self.current_screen.draw()

    def _inside(self, x, y, width, height):
        return (
            x <= pyxel.mouse_x <= x + width
            and y <= pyxel.mouse_y <= y + height
        )


YellowOliveAcademy()
