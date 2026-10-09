from screens.intro import art

# Sheet rows of the Tuxemon overworld sprites (3 frames of 16x32 per row).
DOWN = 0
LEFT = 1
RIGHT = 2
UP = 3

WIDTH = 16
HEIGHT = 32
STANDING_FRAME = 1
WALK_CYCLE = (0, 1, 2, 1)
FRAMES_PER_STEP = 6


class Walker:
    def __init__(self, sheet, x, y, facing=DOWN):
        self.sheet = sheet
        self.x = x
        self.y = y
        self.facing = facing
        self.moving = False
        self.walk_frame = 0

    def face(self, dx, dy):
        if dy < 0:
            self.facing = UP
        elif dy > 0:
            self.facing = DOWN
        elif dx < 0:
            self.facing = LEFT
        elif dx > 0:
            self.facing = RIGHT

    def set_moving(self, moving):
        self.moving = moving
        self.walk_frame = self.walk_frame + 1 if moving else 0

    def draw(self):
        if self.moving:
            frame = WALK_CYCLE[(self.walk_frame // FRAMES_PER_STEP) % len(WALK_CYCLE)]
        else:
            frame = STANDING_FRAME
        art.draw_shadow(self.x + WIDTH // 2, self.y + HEIGHT - 1)
        art.blt(None, self.sheet, frame * WIDTH, self.facing * HEIGHT, WIDTH, HEIGHT, self.x, self.y)
