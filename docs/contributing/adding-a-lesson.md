# Adding an Academy lesson

Yellow Olive Academy is the Pyxel (WebAssembly) course published at
[`/academy/`](../academy/index.html). It is deliberately split in two:

| File | Role |
|------|------|
| `docs/academy/engine.py` | All machinery: palette, pop-in animation, beat state machine, sound cues, header, narration panel, prompt |
| `docs/academy/lessons/lesson_XX_*.py` | Pure content: the narration for each beat and the boxes that appear with it |
| `docs/academy/lessons/__init__.py` | Ordered registry of lessons |
| `docs/academy/academy.py` | Entry point: hands the registry to the engine |

A lesson never draws anything itself. It declares data.

## 1. Write the lesson module

Create `docs/academy/lessons/lesson_02_services.py`:

```python
from engine import COLOR_POD, Beat, Box, Lesson

BEATS = (
    Beat((
        "A SERVICE GIVES PODS A STABLE ADDRESS.",
        "PODS COME AND GO. THE SERVICE NAME DOES NOT.",
    )),
)

LESSON = Lesson(
    number=2,
    title="SERVICES AND DISCOVERY",
    subtitle="HOW PODS FIND EACH OTHER",
    beats=BEATS,
    boxes=(Box(0, 20, 48, 64, 40, COLOR_POD, "POD web"),),
)
```

- `Beat.lines` is the narration shown while that beat is on screen. The screen
  is 256px wide with a 4px font, so keep lines under ~60 characters.
- `Box.beat` is the beat index at which the box pops in. It stays on screen for
  the rest of the lesson.
- `Box.note` is drawn under the box only while its own beat is current - use it
  for a one-word callout such as `SIDECAR`.
- Colors come from `engine`: `COLOR_NODE`, `COLOR_NAMESPACE`, `COLOR_POD`,
  `COLOR_CONTAINER`, `COLOR_ACCENT`.

## 2. Register it

```python
# docs/academy/lessons/__init__.py
from lessons.lesson_01_intro_and_pods import LESSON as LESSON_01
from lessons.lesson_02_services import LESSON as LESSON_02

LESSONS = (LESSON_01, LESSON_02)
```

Lessons play in registry order and wrap back to the first one at the end.

Sound is engine-owned: a blip plays on every reveal and a chord when a lesson
ends, and `M` mutes. Lessons do not declare audio.

## 3. Run it locally

The Pyxel WASM loader fetches lesson modules over HTTP, so the files must be
served rather than opened from disk:

```sh
python -m http.server -d docs/academy 8000
# then open http://localhost:8000/
```

Changing the lesson number, title or subtitle is enough to confirm the right
module is loading - the title card reads them directly.
