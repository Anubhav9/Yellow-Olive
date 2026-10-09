import pyxel

import global_constants
import text_renderer
from screens.intro import constants, maps, sounds, tiles

SKIP_PAGE = "home_screen"
NEXT_PAGE = "academy_hall_screen"


def draw_skip_hint():
    pyxel.rect(
        constants.SKIP_HINT_X, constants.SKIP_HINT_Y,
        constants.SKIP_HINT_WIDTH, constants.SKIP_HINT_HEIGHT, pyxel.COLOR_BLACK,
    )
    text_renderer.draw_text_centered(
        constants.SKIP_HINT_X, constants.SKIP_HINT_Y + 1,
        constants.SKIP_HINT_WIDTH, constants.SKIP_HINT, pyxel.COLOR_WHITE,
    )


class VillageScreen:
    def __init__(self):
        tiles.init_sheets()
        sounds.init_sounds()
        self.objects = maps.village_objects()
        self.map_image = tiles.bake_map(tiles.TOWN, maps.village_ground(), self.objects)
        self.triggers = {
            maps.BLUE_HOUSE_DOOR_CELL: constants.BLUE_HOUSE_MESSAGE,
            maps.RED_HOUSE_DOOR_CELL: constants.RED_HOUSE_MESSAGE,
            maps.SIGNPOST_CELL: constants.SIGNPOST_MESSAGE,
        }
        self.player_x = constants.VILLAGE_PLAYER_START_X
        self.player_y = constants.VILLAGE_PLAYER_START_Y
        self.facing_left = False
        self.moving = False
        self.message = constants.WELCOME_MESSAGE
        self.message_timer = constants.WELCOME_MESSAGE_FRAMES
        self.fade_frame = None

    def update(self):
        if pyxel.btnp(pyxel.KEY_TAB):
            return SKIP_PAGE

        if self.fade_frame is not None:
            self.fade_frame += 1
            if self.fade_frame >= constants.FADE_FRAMES:
                return NEXT_PAGE
            return None

        dx, dy = self._read_direction()
        self.moving = bool(dx or dy)
        if dx:
            self.facing_left = dx < 0
        self._move(dx * constants.WALK_SPEED, 0)
        self._move(0, dy * constants.WALK_SPEED)

        if self.message_timer > 0:
            self.message_timer -= 1
        self._check_triggers()
        return None

    def _read_direction(self):
        dx = dy = 0
        if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.KEY_A) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT):
            dx -= 1
        if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.KEY_D) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT):
            dx += 1
        if pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.KEY_W) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_UP):
            dy -= 1
        if pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.KEY_S) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN):
            dy += 1

        if not (dx or dy) and pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
            centre_x = self.player_x + tiles.TILE_SIZE // 2
            centre_y = self.player_y + tiles.TILE_SIZE // 2
            if abs(pyxel.mouse_x - centre_x) > constants.WALK_SPEED:
                dx = 1 if pyxel.mouse_x > centre_x else -1
            if abs(pyxel.mouse_y - centre_y) > constants.WALK_SPEED:
                dy = 1 if pyxel.mouse_y > centre_y else -1
        return dx, dy

    def _move(self, dx, dy):
        if not (dx or dy):
            return
        new_x = max(0, min(self.player_x + dx, global_constants.WINDOW_WIDTH - tiles.TILE_SIZE))
        new_y = max(0, min(self.player_y + dy, global_constants.WINDOW_HEIGHT - tiles.TILE_SIZE))
        if not self._blocked(new_x, new_y):
            self.player_x = new_x
            self.player_y = new_y

    def _hitbox_cells(self, x, y, margin=0):
        left = x + constants.HITBOX_LEFT - margin
        right = x + constants.HITBOX_RIGHT + margin
        top = y + constants.HITBOX_TOP - margin
        bottom = y + constants.HITBOX_BOTTOM + margin
        cells = set()
        for px in (left, right):
            for py in (top, bottom):
                column = int(px) // tiles.TILE_SIZE
                row = int(py) // tiles.TILE_SIZE
                if 0 <= column < maps.COLUMNS and 0 <= row < maps.ROWS:
                    cells.add((column, row))
        return cells

    def _blocked(self, x, y):
        for column, row in self._hitbox_cells(x, y):
            if (column, row) in maps.ACADEMY_DOOR_CELLS:
                continue
            if self.objects[row][column] is not None:
                return True
        return False

    def _check_triggers(self):
        touching = self._hitbox_cells(self.player_x, self.player_y, constants.TOUCH_MARGIN)
        if touching & set(maps.ACADEMY_DOOR_CELLS):
            self.fade_frame = 0
            sounds.play(sounds.DOOR)
            return

        for cell, message in self.triggers.items():
            if cell in touching:
                self.message = message
                self.message_timer = constants.MESSAGE_FRAMES

    def draw(self):
        pyxel.cls(0)
        pyxel.blt(0, 0, self.map_image, 0, 0, global_constants.WINDOW_WIDTH, global_constants.WINDOW_HEIGHT)
        self._draw_academy_label()

        bob = 1 if self.moving and (pyxel.frame_count // constants.BOB_FRAMES) % 2 else 0
        tiles.draw_tile(
            tiles.DUNGEON, constants.PLAYER_TILE,
            self.player_x, self.player_y - bob, flip=self.facing_left,
        )

        if self.message_timer > 0:
            self._draw_message()
        draw_skip_hint()
        if self.fade_frame is not None:
            tiles.draw_fade(self.fade_frame / constants.FADE_FRAMES)

    def _draw_academy_label(self):
        x, y = constants.ACADEMY_LABEL_X, constants.ACADEMY_LABEL_Y
        w, h = constants.ACADEMY_LABEL_WIDTH, constants.ACADEMY_LABEL_HEIGHT
        pyxel.rect(x, y, w, h, pyxel.COLOR_BLACK)
        pyxel.rectb(x, y, w, h, pyxel.COLOR_YELLOW)
        text_renderer.draw_text_centered(x, y + 1, w, constants.ACADEMY_LABEL, pyxel.COLOR_YELLOW)

    def _draw_message(self):
        x, y = constants.MESSAGE_BOX_X, constants.MESSAGE_BOX_Y
        w, h = constants.MESSAGE_BOX_WIDTH, constants.MESSAGE_BOX_HEIGHT
        pyxel.rect(x, y, w, h, pyxel.COLOR_WHITE)
        pyxel.rectb(x, y, w, h, pyxel.COLOR_NAVY)
        text_renderer.draw_text_centered(x, y + 2, w, self.message, pyxel.COLOR_NAVY)
