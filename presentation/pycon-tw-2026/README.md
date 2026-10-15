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
|---|---|---|
| Press Start | 1 | 1 min |
| Level 01: The Problem | 2–5 | 5 min |
| Level 02: Enter Yellow Olive | 6–11 | 5 min |
| Level 03: The Game Loop | 12–17 | 7 min |
| Level 04: Under the Hood | 18–23 | 10 min |
| More Battles | 24–25 | 4 min |
| Final Boss: Demo | 26 | 5 min |
| Save Point | 27–28 | 3 min |

Before the talk, go through [CHECKLIST.md](CHECKLIST.md).
