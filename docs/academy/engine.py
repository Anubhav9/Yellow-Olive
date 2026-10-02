"""Yellow Olive Academy engine.

Holds every piece of machinery a lesson needs: the palette, the pop-in
animation, the beat state machine and the chrome (header, narration panel,
prompt). Lessons themselves are pure data - see `lessons/`.
"""

from dataclasses import dataclass, field
from typing import Tuple

import pyxel

SCREEN_WIDTH = 256
SCREEN_HEIGHT = 240
FRAME_RATE = 30

COLOR_BACKGROUND = 7
COLOR_INK = 1
COLOR_NODE = 6
COLOR_NAMESPACE = 15
COLOR_POD = 11
COLOR_CONTAINER = 3
COLOR_ACCENT = 8

FONT_WIDTH = 4
LINE_HEIGHT = 10
HEADER_HEIGHT = 12
NARRATION_TOP = 180
POP_FRAMES = 10

SOUND_REVEAL = 0
SOUND_LESSON_DONE = 1
SOUND_CHANNEL = 0


@dataclass(frozen=True)
class Box:
    """One rectangle of a lesson diagram, revealed at `beat`."""

    beat: int
    x: int
    y: int
    width: int
    height: int
    color: int
    label: str = ""
    note: str = ""


@dataclass(frozen=True)
class Beat:
    """One press of Space: the narration shown while it is on screen."""

    lines: Tuple[str, ...]


@dataclass(frozen=True)
class Lesson:
    number: int
    title: str
    subtitle: str
    beats: Tuple[Beat, ...]
    boxes: Tuple[Box, ...] = field(default_factory=tuple)


def centered_text(y: int, text: str, color: int) -> None:
    pyxel.text((SCREEN_WIDTH - len(text) * FONT_WIDTH) // 2, y, text, color)


def _eased(progress: float) -> float:
    """Ease-out so a box decelerates as it reaches full size."""
    return 1.0 - (1.0 - progress) ** 3


class Academy:
    """Runs a sequence of lessons, one beat at a time."""

    def __init__(self, lessons):
        if not lessons:
            raise ValueError("The academy needs at least one lesson")
        self.lessons = tuple(lessons)
        self.lesson_index = 0
        self.beat_index = -1
        self.beat_frame = 0
        self.muted = False

    def run(self) -> None:
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="Yellow Olive Academy", fps=FRAME_RATE)
        pyxel.mouse(True)
        self._define_sounds()
        pyxel.run(self.update, self.draw)

    def _define_sounds(self) -> None:
        """Two synth cues: a blip when something is revealed, a chord per lesson."""
        pyxel.sounds[SOUND_REVEAL].set("c3e3", "p", "64", "n", 18)
        pyxel.sounds[SOUND_LESSON_DONE].set("c3e3g3c4", "t", "6543", "f", 14)

    def _play(self, sound: int) -> None:
        if not self.muted:
            pyxel.play(SOUND_CHANNEL, sound)

    @property
    def lesson(self) -> Lesson:
        return self.lessons[self.lesson_index]

    @property
    def on_title(self) -> bool:
        return self.beat_index < 0

    def update(self) -> None:
        self.beat_frame += 1
        if pyxel.btnp(pyxel.KEY_M):
            self.muted = not self.muted
            pyxel.stop()
        if not self._advance_pressed():
            return
        self.beat_index += 1
        self.beat_frame = 0
        if self.beat_index < len(self.lesson.beats):
            self._play(SOUND_REVEAL)
            return
        self._play(SOUND_LESSON_DONE)
        self.lesson_index = (self.lesson_index + 1) % len(self.lessons)
        self.beat_index = -1

    def _advance_pressed(self) -> bool:
        return (
            pyxel.btnp(pyxel.KEY_SPACE)
            or pyxel.btnp(pyxel.KEY_RETURN)
            or pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)
            or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A)
        )

    def draw(self) -> None:
        pyxel.cls(COLOR_BACKGROUND)
        if self.on_title:
            self._draw_title()
        else:
            self._draw_header()
            self._draw_diagram()
            self._draw_narration()
        self._draw_prompt()

    def _draw_title(self) -> None:
        lesson = self.lesson
        pyxel.rectb(16, 76, SCREEN_WIDTH - 32, 60, COLOR_INK)
        pyxel.rect(16, 76, SCREEN_WIDTH - 32, 10, COLOR_NAMESPACE)
        centered_text(78, "* YELLOW OLIVE ACADEMY *", COLOR_INK)
        centered_text(96, f"LESSON {lesson.number:02d}: {lesson.title}", COLOR_INK)
        centered_text(112, lesson.subtitle, COLOR_CONTAINER)
        centered_text(146, "M MUTES THE SOUND" if not self.muted else "SOUND MUTED - M", COLOR_INK)

    def _draw_header(self) -> None:
        lesson = self.lesson
        pyxel.rect(0, 0, SCREEN_WIDTH, HEADER_HEIGHT, COLOR_NAMESPACE)
        pyxel.text(6, 3, f"{lesson.number:02d} {lesson.title}"[:52], COLOR_INK)
        progress = f"{self.beat_index + 1}/{len(lesson.beats)}"
        pyxel.text(SCREEN_WIDTH - 6 - len(progress) * FONT_WIDTH, 3, progress, COLOR_INK)

    def _draw_diagram(self) -> None:
        for box in self.lesson.boxes:
            if box.beat > self.beat_index:
                continue
            self._draw_box(box, self._pop(box.beat))

    def _pop(self, beat: int) -> float:
        """0.0 -> 1.0 growth factor for elements revealed at `beat`."""
        if self.beat_index > beat:
            return 1.0
        return _eased(min(self.beat_frame, POP_FRAMES) / POP_FRAMES)

    def _draw_box(self, box: Box, pop: float) -> None:
        drawn_width = max(2, int(box.width * pop))
        drawn_height = max(2, int(box.height * pop))
        drawn_x = box.x + (box.width - drawn_width) // 2
        drawn_y = box.y + (box.height - drawn_height) // 2
        pyxel.rect(drawn_x, drawn_y, drawn_width, drawn_height, box.color)
        pyxel.rectb(drawn_x, drawn_y, drawn_width, drawn_height, COLOR_INK)
        if pop < 1.0:
            return
        if box.label:
            pyxel.text(box.x + 3, box.y + 3, box.label[: (box.width - 4) // FONT_WIDTH], COLOR_INK)
        if box.note and box.beat == self.beat_index:
            note_x = box.x + box.width // 2 - len(box.note) * FONT_WIDTH // 2
            pyxel.text(note_x, box.y + box.height + 2, box.note, COLOR_ACCENT)

    def _draw_narration(self) -> None:
        pyxel.rect(0, NARRATION_TOP, SCREEN_WIDTH, SCREEN_HEIGHT - NARRATION_TOP, COLOR_INK)
        for line_index, line in enumerate(self.lesson.beats[self.beat_index].lines):
            pyxel.text(8, NARRATION_TOP + 10 + line_index * LINE_HEIGHT, line, COLOR_BACKGROUND)

    def _draw_prompt(self) -> None:
        if pyxel.frame_count % 30 >= 20:
            return
        centered_text(
            SCREEN_HEIGHT - 12,
            "PRESS SPACE TO CONTINUE",
            COLOR_INK if self.on_title else COLOR_NAMESPACE,
        )
