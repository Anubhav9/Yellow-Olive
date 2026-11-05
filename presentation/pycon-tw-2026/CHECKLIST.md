# Pre-talk checklist

## Make it yours
- [ ] Slide 2 (About me): check the bio details and the LinkedIn QR.
- [ ] Slide 11: retell the CKA/CKAD story in your own words.
- [ ] Slide 15: add a line on Hana, the Mayor and Cool Turtle. The deck only names them.
- [ ] Slide 27: confirm the "why kubectl" reasons are your real reasons.
- [ ] Slide 35: make at least two of the lessons personal.

## Proposal and code: what changed
- The proposal says **Kubernetes Python client**. The code uses `kubectl ... -o json` through `subprocess`. Slide 27 says this openly.
- The proposal mentions **hints**. There's no `psyquack hint` command yet (the roadmap says "not wired in game yet"). The deck only claims the hints that exist: objective text, mentor dialogue and validator messages.
- **Probes**: only Challenge 2 covers them, and it checks a `livenessProbe` config (`/`, port 80). The deck doesn't claim readiness probes or probe behaviour.
- **Pygame**: the game uses `pygame-ce`, for audio only.

## Evidence used
- Every screenshot in `public/img/demo/` and the demo video come from one real run of Challenge 1 on minikube (`project-yellow-olive`, Kubernetes v1.37).
- Code on slides 21–25 is copied from the repo. Slides 21 and 25 are trimmed, and both say so.
- The deck has no metrics, user numbers or feedback quotes. Add some only if you have real data.

## Missing / optional
- [ ] No screenshots yet from Challenges 2, 6, 8, 19 or 23. Those slides show code and YAML only.
- [ ] Optional: replace the video with a recording that has your voice-over.

## Day of the talk
- [ ] Docker is running. Start the game once before the talk so minikube is up and `nginx` is already pulled.
- [ ] Docker Hub can rate-limit pulls on conference Wi-Fi. If the Pod shows `ImagePullBackOff`, use the video.
- [ ] Open two terminals side by side: the game and the Command Chamber. Use a large font.
- [ ] Have `dist/pods-probes-and-play.pdf` on a USB stick as a backup.
- [ ] Test the video plays on the venue projector (slide 34).
- [ ] Check that both QR codes scan from the back of the room.

## Gamification section (slides 2–6)

- Sources to be comfortable quoting: Deterding, Dixon, Khaled & Nacke (2011), "From game design elements to gamefulness: defining gamification"; Csikszentmihalyi (1990), *Flow*.
- The example sites on slide 7 were all checked as live on 2026-10-15: learngitbranching.js.org, flexboxfroggy.com, vim-adventures.com, overthewire.org/wargames/bandit, sadservers.com, killercoda.com.
- Consider swapping in an example you have personally used, so the slide sounds like you.

## About me and bonus slides (slides 2, 32–33)

- Slide 2 uses the speaker bio from your PyCon TW proposal. PyCon JP was added from earlier notes, so confirm it, and confirm whether each talk was given or only accepted.
- Every slide from 3 onwards has a small Yellow Olive repo QR in the bottom-right corner (`slide-bottom.vue`).
- Home Lab slide: add your hardware/cluster details. The slide only says "my home lab cluster".
