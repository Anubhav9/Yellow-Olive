import pyxel

import game_state
import global_constants
from screens.intro import art, constants, maps, sounds
from screens.intro.character import DOWN, UP, Walker
from screens.intro.village_screen import draw_skip_hint

NEXT_PAGE = "home_screen"

FADE_IN = "fade_in"
PLAYER_WALK = "player_walk"
NOTICE = "notice"
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
        art.init_sheets()
        sounds.init_sounds()
        self.background = maps.bake_hall()
        self.player = Walker(art.PLAYER, constants.HALL_CHARACTER_X, constants.HALL_PLAYER_START_Y, UP)
        self.professor = Walker(art.PROFESSOR, constants.HALL_CHARACTER_X, constants.HALL_PROFESSOR_Y, DOWN)
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

        if self.state in (FADE_IN, PLAYER_WALK):
            self.player.y = max(constants.HALL_PLAYER_STOP_Y, self.player.y - constants.WALK_SPEED)
            arrived = self.player.y == constants.HALL_PLAYER_STOP_Y
            self.player.set_moving(not arrived)
            if self.state == FADE_IN and self.state_frame >= constants.FADE_FRAMES:
                self._set_state(PLAYER_WALK)
            elif self.state == PLAYER_WALK and arrived:
                self._set_state(NOTICE)
                sounds.play(sounds.TEXT_BLIP)
        elif self.state == NOTICE and self.state_frame >= constants.NOTICE_FRAMES:
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
        pyxel.blt(0, 0, self.background, 0, 0, global_constants.WINDOW_WIDTH, global_constants.WINDOW_HEIGHT)
        self.professor.draw()
        self.player.draw()

        if self.state == NOTICE:
            self._draw_notice_bubble()
        elif self.state in (INTRO, OUTRO):
            self._draw_dialogue_box(self._typed_lines(), self._line_finished())
        elif self.state == NAME_ENTRY:
            cursor = "_" if (pyxel.frame_count // 8) % 2 else " "
            lines = [line.format(name=self.player_name, cursor=cursor) for line in constants.NAME_PROMPT_LINES]
            self._draw_dialogue_box(lines, False)
        elif self.state == FADE_OUT:
            self._draw_dialogue_box(self._current_lines(), False)

        draw_skip_hint()
        if self.state == FADE_IN:
            art.draw_fade(1 - self.state_frame / constants.FADE_FRAMES)
        elif self.state == FADE_OUT:
            art.draw_fade(self.state_frame / constants.FADE_FRAMES)

    def _typed_lines(self):
        remaining = self.chars_shown
        typed = []
        for line in self._current_lines():
            typed.append(line[:max(0, remaining)])
            remaining -= len(line)
        return typed

    def _line_finished(self):
        return self.chars_shown >= sum(len(line) for line in self._current_lines())

    def _draw_notice_bubble(self):
        art.draw_box(
            constants.NOTICE_BUBBLE_X, constants.NOTICE_BUBBLE_Y,
            constants.NOTICE_BUBBLE_WIDTH, constants.NOTICE_BUBBLE_HEIGHT, accent="red",
        )
        art.draw_text_centered(
            constants.NOTICE_BUBBLE_X, constants.NOTICE_BUBBLE_Y + 3,
            constants.NOTICE_BUBBLE_WIDTH, "!", color_name="red", shadow_name="red_shadow",
        )

    def _draw_dialogue_box(self, lines, show_arrow):
        x, y = constants.DIALOGUE_BOX_X, constants.DIALOGUE_BOX_Y
        w, h = constants.DIALOGUE_BOX_WIDTH, constants.DIALOGUE_BOX_HEIGHT
        art.draw_box(x, y, w, h, accent="red")
        art.draw_box(
            constants.PORTRAIT_FRAME_X, constants.PORTRAIT_FRAME_Y,
            constants.PORTRAIT_FRAME_WIDTH, constants.PORTRAIT_FRAME_HEIGHT,
            accent="brown", fill="parchment",
        )
        pyxel.clip(
            constants.PORTRAIT_FRAME_X + 3, constants.PORTRAIT_FRAME_Y + 3,
            constants.PORTRAIT_FRAME_WIDTH - 6, constants.PORTRAIT_FRAME_HEIGHT - 6,
        )
        art.blt(
            None, art.PORTRAIT, 0, 0, constants.PORTRAIT_WIDTH, constants.PORTRAIT_HEIGHT,
            constants.PORTRAIT_X, constants.PORTRAIT_Y,
        )
        pyxel.clip()

        art.draw_text(
            constants.DIALOGUE_TEXT_X, constants.NAME_TAG_Y, constants.NAME_TAG,
            color_name="red", shadow_name="red_shadow",
        )
        for index, line in enumerate(lines):
            art.draw_text(
                constants.DIALOGUE_TEXT_X,
                constants.DIALOGUE_TEXT_Y + index * constants.DIALOGUE_LINE_SPACING,
                line,
            )

        if show_arrow and (pyxel.frame_count // 8) % 2:
            pyxel.tri(
                x + w - 16, y + h - 14, x + w - 8, y + h - 14, x + w - 12, y + h - 9, art.color("red"),
            )
