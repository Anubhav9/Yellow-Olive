import pyxel

import game_state
import global_constants
import text_renderer
from screens.intro import constants, maps, sounds, tiles
from screens.intro.village_screen import draw_skip_hint

NEXT_PAGE = "home_screen"

FADE_IN = "fade_in"
PLAYER_WALK = "player_walk"
PROFESSOR_WALK = "professor_walk"
INTRO = "intro"
NAME_ENTRY = "name_entry"
OUTRO = "outro"
FADE_OUT = "fade_out"

NAME_KEYS = (
    [(key, chr(key)) for key in range(pyxel.KEY_A, pyxel.KEY_Z + 1)]
    + [(key, chr(key)) for key in range(pyxel.KEY_0, pyxel.KEY_9 + 1)]
    + [(pyxel.KEY_SPACE, " "), (pyxel.KEY_MINUS, "-")]
)


def _advance_pressed():
    return (
        pyxel.btnp(pyxel.KEY_RETURN)
        or pyxel.btnp(pyxel.KEY_SPACE)
        or pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)
        or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A)
    )


class AcademyHallScreen:
    def __init__(self):
        tiles.init_sheets()
        sounds.init_sounds()
        self.room_image = tiles.bake_map(tiles.DUNGEON, maps.hall_floor(), maps.hall_objects())
        self.player_y = constants.HALL_PLAYER_START_Y
        self.professor_y = constants.HALL_PROFESSOR_START_Y
        self.state = FADE_IN
        self.state_frame = 0
        self.script = constants.PROFESSOR_INTRO
        self.line_index = 0
        self.chars_shown = 0
        self.player_name = ""

    def update(self):
        if pyxel.btnp(pyxel.KEY_TAB):
            return NEXT_PAGE
        self.state_frame += 1

        if self.state == FADE_IN:
            self.player_y -= constants.WALK_SPEED
            if self.state_frame >= constants.FADE_FRAMES:
                self._set_state(PLAYER_WALK)
        elif self.state == PLAYER_WALK:
            self.player_y = max(constants.HALL_PLAYER_STOP_Y, self.player_y - constants.WALK_SPEED)
            if self.player_y == constants.HALL_PLAYER_STOP_Y:
                self._set_state(PROFESSOR_WALK)
        elif self.state == PROFESSOR_WALK:
            self.professor_y = min(
                constants.HALL_PROFESSOR_STOP_Y,
                self.professor_y + constants.PROFESSOR_WALK_SPEED,
            )
            if self.professor_y == constants.HALL_PROFESSOR_STOP_Y:
                self._start_script(constants.PROFESSOR_INTRO, INTRO)
        elif self.state in (INTRO, OUTRO):
            self._update_dialogue()
        elif self.state == NAME_ENTRY:
            self._update_name_entry()
        elif self.state == FADE_OUT and self.state_frame >= constants.FADE_FRAMES:
            return NEXT_PAGE
        return None

    def _set_state(self, state):
        self.state = state
        self.state_frame = 0

    def _start_script(self, script, state):
        self.script = script
        self._set_state(state)
        self._start_line(0)

    def _start_line(self, index):
        self.line_index = index
        self.chars_shown = 0
        if self.script[index].get("jingle"):
            sounds.play(sounds.TADA)

    def _current_lines(self):
        return [line.format(name=self.player_name) for line in self.script[self.line_index]["lines"]]

    def _update_dialogue(self):
        total_chars = sum(len(line) for line in self._current_lines())
        if self.chars_shown < total_chars:
            self.chars_shown += constants.TYPEWRITER_CHARS_PER_FRAME
            if self.chars_shown % constants.BLIP_EVERY_CHARS == 0 and not self.script[self.line_index].get("jingle"):
                sounds.play(sounds.TEXT_BLIP)
            if _advance_pressed():
                self.chars_shown = total_chars
            return

        if not _advance_pressed():
            return
        if self.line_index + 1 < len(self.script):
            self._start_line(self.line_index + 1)
        elif self.state == INTRO:
            self._set_state(NAME_ENTRY)
        else:
            game_state.player_name = self.player_name
            self._set_state(FADE_OUT)

    def _update_name_entry(self):
        shift = pyxel.btn(pyxel.KEY_SHIFT)
        for key, char in NAME_KEYS:
            if pyxel.btnp(key) and len(self.player_name) < constants.NAME_MAX_LENGTH:
                if char == " " and not self.player_name:
                    continue
                if shift or not self.player_name:
                    char = char.upper()
                self.player_name += char
        if pyxel.btnp(pyxel.KEY_BACKSPACE, 10, 2):
            self.player_name = self.player_name[:-1]

        if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self.player_name = self.player_name.strip() or constants.DEFAULT_PLAYER_NAME
            self._start_script(constants.PROFESSOR_OUTRO, OUTRO)

    def draw(self):
        pyxel.cls(0)
        pyxel.blt(0, 0, self.room_image, 0, 0, global_constants.WINDOW_WIDTH, global_constants.WINDOW_HEIGHT)

        professor_bob = 1 if self.state == PROFESSOR_WALK and (pyxel.frame_count // constants.BOB_FRAMES) % 2 else 0
        tiles.draw_tile(tiles.DUNGEON, constants.PROFESSOR_TILE, constants.HALL_CHARACTER_X, self.professor_y - professor_bob)
        player_bob = 1 if self.state in (FADE_IN, PLAYER_WALK) and (pyxel.frame_count // constants.BOB_FRAMES) % 2 else 0
        tiles.draw_tile(tiles.DUNGEON, constants.PLAYER_TILE, constants.HALL_CHARACTER_X, self.player_y - player_bob)

        if self.state in (INTRO, OUTRO):
            self._draw_dialogue_box(self._typed_lines(), self._line_finished())
        elif self.state == NAME_ENTRY:
            cursor = "_" if (pyxel.frame_count // 8) % 2 else " "
            lines = [line.format(name=self.player_name, cursor=cursor) for line in constants.NAME_PROMPT_LINES]
            self._draw_dialogue_box(lines, False)
        elif self.state == FADE_OUT:
            self._draw_dialogue_box(self._current_lines(), False)

        draw_skip_hint()
        if self.state == FADE_IN:
            tiles.draw_fade(1 - self.state_frame / constants.FADE_FRAMES)
        elif self.state == FADE_OUT:
            tiles.draw_fade(self.state_frame / constants.FADE_FRAMES)

    def _typed_lines(self):
        remaining = self.chars_shown
        typed = []
        for line in self._current_lines():
            typed.append(line[:max(0, remaining)])
            remaining -= len(line)
        return typed

    def _line_finished(self):
        return self.chars_shown >= sum(len(line) for line in self._current_lines())

    def _draw_dialogue_box(self, lines, show_arrow):
        x, y = constants.DIALOGUE_BOX_X, constants.DIALOGUE_BOX_Y
        w, h = constants.DIALOGUE_BOX_WIDTH, constants.DIALOGUE_BOX_HEIGHT

        pyxel.rect(
            constants.NAME_TAG_X, constants.NAME_TAG_Y,
            constants.NAME_TAG_WIDTH, constants.NAME_TAG_HEIGHT, pyxel.COLOR_YELLOW,
        )
        text_renderer.draw_text_centered(
            constants.NAME_TAG_X, constants.NAME_TAG_Y,
            constants.NAME_TAG_WIDTH, constants.NAME_TAG, pyxel.COLOR_BLACK,
        )

        pyxel.rect(x, y, w, h, pyxel.COLOR_YELLOW)
        pyxel.rect(x + 2, y + 2, w - 4, h - 4, pyxel.COLOR_WHITE)

        pyxel.rect(constants.PORTRAIT_X - 1, constants.PORTRAIT_Y - 1, 34, 34, pyxel.COLOR_NAVY)
        tiles.draw_tile(tiles.DUNGEON, constants.PROFESSOR_TILE, constants.PORTRAIT_X, constants.PORTRAIT_Y, scale=2)

        for index, line in enumerate(lines):
            text_renderer.draw_text(
                constants.DIALOGUE_TEXT_X,
                constants.DIALOGUE_TEXT_Y + index * constants.DIALOGUE_LINE_SPACING,
                line, pyxel.COLOR_NAVY,
            )

        if show_arrow and (pyxel.frame_count // 8) % 2:
            pyxel.tri(x + w - 14, y + h - 12, x + w - 6, y + h - 12, x + w - 10, y + h - 7, pyxel.COLOR_NAVY)
