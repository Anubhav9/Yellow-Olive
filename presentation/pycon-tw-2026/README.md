# Pods, Probes, and Play: PyCon Taiwan 2026

Slides for the PyCon Taiwan 2026 talk on Yellow Olive (Day 2, Sun 18 Oct, 10:50, R2).

## Run

```bash
cd presentation/pycon-tw-2026
npm install
npm run dev          # opens on http://localhost:3030
```

Press `p` for presenter mode, which shows the speaker notes and a timer.

## Edit

- All slides and speaker notes are in `slides.md`. The notes are the `<!-- -->` block at the end of each slide.
- Colours and fonts are in `styles/index.css`.
- Images are in `public/img/`. Real game screenshots are in `public/img/demo/`.
- The demo video is `public/demo/challenge1-demo.mp4`.

## Build and export

```bash
npm run build          # static site in dist/
npm run export         # PDF: dist/pods-probes-and-play.pdf
npm run export-notes   # speaker notes PDF: dist/speaker-notes.pdf
```

The first export downloads Chromium: `npx playwright install chromium`.

## Timing (about 37 min + Q&A)

| Section | Slides | Time |
|---|---:|---:|
| Title + About me | 1–2 | 2 min |
| Level 01: Gamification | 3–7 | 5 min |
| Level 02: The Problem | 8–11 | 3 min |
| Level 03: Enter Yellow Olive | 12–17 | 4 min |
| Level 04: The Game Loop | 18–23 | 6 min |
| Level 05: Under the Hood | 24–29 | 6 min |
| More Battles | 30–31 | 3 min |
| Bonus Level: Pyxel Academy + Home Lab | 32–33 | 3 min |
| Final Boss: Demo | 34 | 4 min |
| Save Point | 35–36 | 2 min |

Before the talk, go through [CHECKLIST.md](CHECKLIST.md).
