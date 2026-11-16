import pyxel

FONT_PATH = "assets/fonts/Tamzen6x12r.bdf"

_font = None

CHAR_WIDTH = 6
LINE_HEIGHT = 13


def init_fonts():
    global _font
    if _font is None:
        _font = pyxel.Font(FONT_PATH)


def text_width(text):
    init_fonts()
    return _font.text_width(text)


def draw_text(x, y, text, color):
    init_fonts()
    pyxel.text(x, y, text, color, _font)


def draw_text_centered(x, y, width, text, color):
    init_fonts()
    text_x = x + max(0, (width - _font.text_width(text)) // 2)
    pyxel.text(text_x, y, text, color, _font)
