"""Entry point for Yellow Olive Academy.

Runs in the browser through the Pyxel WASM custom element (see index.html).
Space, click or gamepad A advances one beat at a time.
"""

import engine
from lessons import LESSONS

engine.Academy(LESSONS).run()
