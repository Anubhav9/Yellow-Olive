import pyxel

TEXT_BLIP = 60
TADA = 61
DOOR = 62
EFFECTS_CHANNEL = 3

_ready = False


def init_sounds():
    global _ready
    if _ready:
        return
    pyxel.sounds[TEXT_BLIP].set("a3", "p", "2", "f", 2)
    pyxel.sounds[TADA].set("c3e3g3c4rc4", "s", "5", "nnnnnf", 8)
    pyxel.sounds[DOOR].set("g2c3", "t", "4", "nf", 6)
    _ready = True


def play(sound):
    pyxel.play(EFFECTS_CHANNEL, sound)
