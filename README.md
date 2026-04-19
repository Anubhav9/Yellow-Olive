# Project Yellow Olive 

**Pokémon Yellow, but you tame Kubernetes clusters instead of Pokémon.**

A terminal-native retro adventure designed to make infrastructure learning feel fun, nostalgic, and a little less overwhelming.

[![GitHub stars](https://img.shields.io/github/stars/Anubhav9/Yellow-Olive?style=social)](https://github.com/Anubhav9/Yellow-Olive)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Made with ❤️ in Bengaluru 🇮🇳](https://img.shields.io/badge/Made%20with%20❤️%20in-Bengaluru%20🇮🇳-%23D4AF37?style=flat)](https://github.com/Anubhav9/Yellow-Olive)

<img src="https://github.com/user-attachments/assets/f752fbca-da89-4227-bf44-b4659bf63969" width="80%" alt="Opening screen with Professor Bald">

---
## Index

- [The Motivation](#the-motivation)
- [An Honest Take](#an-honest-take)
- [Setup and Run (Local)](#setup-and-run-local)
- [Meet the Characters](#meet-the-characters)
- [From Yellow Olive to Kubernetes](#from-yellow-olive-to-kubernetes)
- [Gameplay Commands](#gameplay-commands)
- [Project Yellow Olive in Action](#project-yellow-olive-in-action)
- [Contributing](#contributing)
- [What's next in the roadmap?](#whats-next-in-the-roadmap)

---

## The Motivation

```Kubernetes is powerful...  
Kubernetes is everywhere...  
Kubernetes runs the modern world...  
And yet, for many of us, learning it feels confusing, overwhelming, and sometimes just plain boring :(
```

Project Yellow Olive is my personal, experimental attempt at changing that.

I grew up on a GameBoy, lost in the world of Pokémon. Even today, a single chiptune note takes me straight back to those golden childhood days. I know I’m not alone in that feeling.

Nostalgia has a strange power - it lowers resistance, sparks curiosity, and makes difficult things feel lighter.

Yellow Olive is built on that belief: combine nostalgia with motivation, and even something as complex as Kubernetes can become approachable.

---

## An Honest Take

I’ve attempted the CKAD and CKA certifications - and I didn’t clear them.

Not because I didn’t understand the concepts, but because I didn’t practice enough. Platforms like Killer.sh demand consistency and repetition - and like many of us, I underestimated that discipline.

This project isn’t a replacement for serious exam prep.

It’s a practice ground - a way to build confidence, stay engaged, and keep the adrenaline slightly elevated while solving real problems.

Not every day is productive. Not every day is high-energy.

This is just my attempt to make the hard days a little easier to push through.

---

## Setup and Run

### Prerequisites

- Python 3.10+
- Docker Desktop or Docker Engine (required)
- `minikube` (required)
- `kubectl` (required)

Project Yellow Olive uses Minikube to create and manage the local Kubernetes cluster used during gameplay, so Docker and Minikube must be installed before starting the game.

### Install Minikube and Kubernetes Tooling

1. Install Docker and make sure it is running.
2. Install Minikube by following the official guide: [Install Minikube](https://minikube.sigs.k8s.io/docs/start/)
3. Install `kubectl` by following the official guide: [Install kubectl](https://kubernetes.io/docs/tasks/tools/)

You can verify the setup with:

```bash
docker --version
minikube version
kubectl version --client
```

### Install from PyPI

```bash
python -m venv .venv
source .venv/bin/activate
pip install yellow-olive
```

### Start the Game from PyPI

```bash
yellow-olive start
```

When the game starts, Project Yellow Olive creates a `yellow-olive-lab/` folder in your current working directory and places the editable challenge manifests there.

### Install from Source

```bash
git clone https://github.com/Anubhav9/Yellow-Olive.git
cd Yellow-Olive
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Start the Game from Source

```bash
python app.py
```

When you start the game and proceed through initialization, Yellow Olive will start a Minikube profile and switch kubectl context automatically.

### Helpful Tip for Gameplay

Keep two terminal tabs open:

1. **Game terminal** -> run `yellow-olive start` or `python app.py`
2. **Command Chamber terminal** -> run your `kubectl` commands for challenge fixes

---

## Meet the Characters

### Professor Bald Uncle
<p align="center">
  <img width="120" src="https://github.com/user-attachments/assets/0b975f11-f319-45fe-96f1-6d73b557f17a" alt="Professor Bald Uncle" />
</p>

```
The classic mentor archetype. Calm, experienced, slightly intimidating at first glance.

He steps in when you’re stuck, nudges you in the right direction, and reminds you that debugging is part of the journey.

Strict on the outside, generous at heart.
```

### Electromon
<p align="center">
  <img width="120" src="https://github.com/user-attachments/assets/dad3be2b-216f-44ec-9a12-c79c763dfd32" alt="Electromon" />
</p>

```
Your closest companion. Quiet by nature, but restless at heart — he doesn’t like being confined for long.
 
When something feels off in the cluster, he’s usually at the center of it. Shy, but loyal through every broken deployment.
```

### PsyQuack
<p align="center">
  <img width="120" src="https://github.com/user-attachments/assets/bfc93cfc-f4c5-4b58-ac6a-4c430eb8b879" alt="PsyQuack" />
</p>

```
He doesn’t talk much. He watches.  
You think you fixed the Deployment? He checks.  
You’re confident the Service works? He verifies.  
If something’s still off, PsyQuack will let you know - in his own slightly unhinged way.  
He doesn’t reward effort. He rewards correctness.
```
---
## From Yellow Olive to Kubernetes

Every character, keyword, and challenge maps directly to a real Kubernetes concept.

| Yellow Olive Concept | Kubernetes Equivalent | What It Means in Practice                          |
|----------------------|-----------------------|----------------------------------------------------|
| Posemon              | Container             | A single runnable unit inside a workload           |
| Pokepod              | Pod                   | The smallest deployable unit - houses Posemons     |

(And many more coming — every mechanic is built to teach something real.)

---
## Gameplay Commands

Quick in-game commands you’ll use often:

- `psyquack validate` → Invokes PsyQuack to evaluate your solution for the current challenge.
- `psyquack hint` → PsyQuack calls Professor Bald Uncle for a nudge (without spoiling the answer).
- `psyquack back` → Returns to the previous challenge screen.

---

## Project Yellow Olive in Action

***Full gameplay walkthrough (2 min):
[Watch on YouTube](https://youtu.be/vAu4aaM1oOw)***

---

## Music Credits

All music files used in Project Yellow Olive are sourced from OpenGameArt, shared under the `CC0` license, and the relevant creators are credited below.

| Music File | Music Name | Author Name | License | Source |
|------------|------------|-------------|---------|--------|
| `screen_1_opening_song.mp3` | JRPG Piano | [Joth](https://opengameart.org/users/joth) | CC0 | OpenGameArt |
| `screen_2_music.mp3` | Town Theme RPG | [CynicMusic](https://opengameart.org/users/joth) | CC0 | OpenGameArt |
| `battle_music.ogg` | 8 bit RPG Battle Encounter Theme | [Ted Kerr](https://opengameart.org/users/wolfgang) | CC0 | OpenGameArt |
| `battle_music_2.mp3` | 8 bit Chiptune Encounter Theme | [Shiru8Bit](https://opengameart.org/users/shiru8bit) | CC0 | OpenGameArt |
| `win_music.ogg` | Win Jingle | [Fupi](https://opengameart.org/users/fupi) | CC0 | OpenGameArt |
| `loose_music.ogg` | Lost Game Short Music Clip | [Robin Lamb](https://opengameart.org/users/robin-lamb) | CC0 | OpenGameArt |

---

## Contributing

Contributions are welcome, especially for adding new challenges.

If you'd like to contribute:

1. Open an issue with the challenge idea and learning objective.
2. Add/update challenge text in `challenge_files/`.
3. Add/update corresponding manifest files in `challenge_files/{type}-q*.yaml`.
4. Add/update challenge validation rules in `core_logic/challenge_validation.py`.
5. Submit a pull request with a short demo of the challenge flow.

---

## What's next in the roadmap?

This is currently a work in progress. Planned milestones:

| Roadmap Stage | Planned Feature | Why It Matters |
|---------------|------------------|----------------|
| Phase 1 | Save/load game progress and jump directly to a specific challenge | Lets players resume quickly and practice targeted scenarios |
| Phase 2 | Add more challenges focused on Kubernetes Services | Expands learning beyond Pods into core networking concepts |
| Phase 3 | Package and publish Project Yellow Olive on PyPI | Makes installation easier for the community |

