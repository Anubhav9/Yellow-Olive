import pyxel

import global_constants
from screens.intro import art, constants, maps, sounds
from screens.intro.character import UP, Walker
from screens.intro.character import HEIGHT as SPRITE_HEIGHT
from screens.intro.character import WIDTH as SPRITE_WIDTH

SKIP_PAGE = "home_screen"
NEXT_PAGE = "academy_hall_screen"


def draw_skip_hint():
    art.draw_box(
        constants.SKIP_HINT_X, constants.SKIP_HINT_Y,
        constants.SKIP_HINT_WIDTH, constants.SKIP_HINT_HEIGHT, accent="text",
    )
    art.draw_text_centered(
        constants.SKIP_HINT_X, constants.SKIP_HINT_Y + 3,
        constants.SKIP_HINT_WIDTH, constants.SKIP_HINT,
    )


def _overlaps(a, b):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah


def _grow(rect, margin):
    x, y, width, height = rect
    return (x - margin, y - margin, width + 2 * margin, height + 2 * margin)


class VillageScreen:
    def __init__(self):
        art.init_sheets()
        sounds.init_sounds()
        self.background = maps.bake_village()
        self.player = Walker(
            art.PLAYER, constants.VILLAGE_PLAYER_START_X, constants.VILLAGE_PLAYER_START_Y, UP,
        )
        self.blockers = maps.HEDGE_BLOCKERS + (maps.SIGN_RECT,) + maps.MAILBOX_RECTS
        self.notes = ((maps.SIGN_RECT, constants.SIGN_MESSAGE),) + tuple(
            (rect, constants.MAILBOX_MESSAGE) for rect in maps.MAILBOX_RECTS
        )
        self.house_doors = (
            (maps.GREEN_HOUSE_DOOR, constants.GREEN_HOUSE_MESSAGE),
            (maps.GREY_HOUSE_DOOR, constants.GREY_HOUSE_MESSAGE),
        )
        self.message = constants.WELCOME_MESSAGE
        self.message_timer = constants.WELCOME_MESSAGE_FRAMES
        self.fade_frame = None
        self.frame = 0

    def update(self):
        self.frame += 1
        if pyxel.btnp(pyxel.KEY_TAB):
            return SKIP_PAGE

        if self.fade_frame is not None:
            self.fade_frame += 1
            if self.fade_frame >= constants.FADE_FRAMES:
                return NEXT_PAGE
            return None

        dx, dy = self._read_direction()
        if dx and dy:
            dx = 0
        self.player.face(dx, dy)
        self.player.set_moving(bool(dx or dy))
        self._move(dx * constants.WALK_SPEED, dy * constants.WALK_SPEED)

        if self.message_timer > 0:
            self.message_timer -= 1
        self._check_triggers(dy)
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
            centre_x = self.player.x + SPRITE_WIDTH // 2
            centre_y = self.player.y + constants.HITBOX_TOP
            if abs(pyxel.mouse_x - centre_x) > constants.WALK_SPEED:
                dx = 1 if pyxel.mouse_x > centre_x else -1
            elif abs(pyxel.mouse_y - centre_y) > constants.WALK_SPEED:
                dy = 1 if pyxel.mouse_y > centre_y else -1
        return dx, dy

    def _feet(self, x, y):
        return (
            x + constants.HITBOX_LEFT, y + constants.HITBOX_TOP,
            constants.HITBOX_WIDTH, constants.HITBOX_HEIGHT,
        )

    def _blocked(self, x, y):
        feet = self._feet(x, y)
        if feet[1] < maps.WALK_TOP:
            return True
        return any(_overlaps(feet, rect) for rect in self.blockers)

    def _move(self, dx, dy):
        if not (dx or dy):
            return
        new_x = max(0, min(self.player.x + dx, global_constants.WINDOW_WIDTH - SPRITE_WIDTH))
        new_y = min(self.player.y + dy, global_constants.WINDOW_HEIGHT - SPRITE_HEIGHT)
        if not self._blocked(new_x, new_y):
            self.player.x = new_x
            self.player.y = new_y

    def _check_triggers(self, dy):
        feet = self._feet(self.player.x, self.player.y)
        centre_x = feet[0] + feet[2] // 2
        at_doorstep = dy < 0 and feet[1] <= maps.WALK_TOP + constants.TOUCH_MARGIN

        if at_doorstep and maps.ACADEMY_DOOR[0] <= centre_x <= maps.ACADEMY_DOOR[1]:
            self.fade_frame = 0
            sounds.play(sounds.DOOR)
            return
        if at_doorstep:
            for (left, right), message in self.house_doors:
                if left <= centre_x <= right:
                    self._show(message)

        touching = _grow(feet, constants.TOUCH_MARGIN)
        for rect, message in self.notes:
            if _overlaps(touching, rect):
                self._show(message)

    def _show(self, message):
        self.message = message
        self.message_timer = constants.MESSAGE_FRAMES

    def draw(self):
        pyxel.cls(0)
        pyxel.blt(0, 0, self.background, 0, 0, global_constants.WINDOW_WIDTH, global_constants.WINDOW_HEIGHT)
        self.player.draw()

        art.draw_box(
            constants.ACADEMY_LABEL_X, constants.ACADEMY_LABEL_Y,
            constants.ACADEMY_LABEL_WIDTH, constants.ACADEMY_LABEL_HEIGHT, accent="gold",
        )
        art.draw_text_centered(
            constants.ACADEMY_LABEL_X, constants.ACADEMY_LABEL_Y + 3,
            constants.ACADEMY_LABEL_WIDTH, constants.ACADEMY_LABEL, color_name="brown",
        )
        self._draw_location_popup()
        if self.message_timer > 0:
            art.draw_box(
                constants.MESSAGE_BOX_X, constants.MESSAGE_BOX_Y,
                constants.MESSAGE_BOX_WIDTH, constants.MESSAGE_BOX_HEIGHT,
            )
            art.draw_text_centered(
                constants.MESSAGE_BOX_X, constants.MESSAGE_BOX_Y + 7,
                constants.MESSAGE_BOX_WIDTH, self.message,
            )
        draw_skip_hint()
        if self.fade_frame is not None:
            art.draw_fade(self.fade_frame / constants.FADE_FRAMES)

    def _draw_location_popup(self):
        frame = self.frame
        slide = constants.LOCATION_SLIDE_FRAMES
        if frame >= constants.LOCATION_SHOW_FRAMES + slide:
            return
        hidden_y = -constants.LOCATION_BOX_HEIGHT
        if frame < slide:
            progress = frame / slide
        elif frame >= constants.LOCATION_SHOW_FRAMES:
            progress = 1 - (frame - constants.LOCATION_SHOW_FRAMES) / slide
        else:
            progress = 1
        y = int(hidden_y + (constants.LOCATION_BOX_Y - hidden_y) * progress)
        art.draw_box(constants.LOCATION_BOX_X, y, constants.LOCATION_BOX_WIDTH, constants.LOCATION_BOX_HEIGHT)
        art.draw_text_centered(constants.LOCATION_BOX_X, y + 3, constants.LOCATION_BOX_WIDTH, constants.LOCATION_NAME)
