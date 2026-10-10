"""Browser entry point for Yellow Olive Academy (Pyxel WASM)."""

import pyxel

import global_constants
from screens.intro_screen import constants as town


CHARACTER_ASSET_PATH = "assets/tilesets/Characters/character_1.png"


class YellowOliveAcademy:
    def __init__(self):
        pyxel.init(
            global_constants.WINDOW_WIDTH,
            global_constants.WINDOW_HEIGHT,
            title=global_constants.WINDOW_TITLE,
            fps=30,
            quit_key=pyxel.KEY_Q,
        )

        # Set the full palette before loading, so images keep their exact colours.
        pyxel.colors[:] = global_constants.PALETTE
        pyxel.images[global_constants.PLAYER_IMAGE_BANK].load(0, 0, CHARACTER_ASSET_PATH)

        self.music=pyxel.sounds[0].pcm(town.TOWN_MAP_MUSIC_PATH)
        # Set background music volume
        pyxel.channels[0].gain = 0.5

        # Play continuously
        pyxel.play(0, 0, loop=True)

        # Pages load their images when created, so create the first one after the palette is set.
        from screens.classroom_screen.classroom_screen import ClassroomScreen
        from screens.intro_screen.intro_screen import IntroScreen
        self.intro_screen = IntroScreen()
        self.classroom_screen = ClassroomScreen()
        self.current_screen = self.intro_screen

        pyxel.run(self.update, self.draw)

    def update(self):
        self.current_screen.update()
        if self.current_screen is self.intro_screen and self.intro_screen.reached_door:
            self.current_screen = self.classroom_screen

    def draw(self):
        self.current_screen.draw()


YellowOliveAcademy()
