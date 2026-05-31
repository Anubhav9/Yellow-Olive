# What is Project Yellow Olive?

**Pokémon Yellow, but you tame Kubernetes clusters instead of Pokémon.**

Project Yellow Olive is a terminal-native retro adventure built with [Textual](https://textual.textualize.io/). It turns Kubernetes practice into a story-driven game: broken pods, miswired Services, and missing routes show up as in-world problems you fix with real `kubectl` commands.

## The idea

Kubernetes is powerful and everywhere, but learning it can feel dry. Yellow Olive uses nostalgia and narrative to lower the barrier - you meet characters like Professor Bald, Electromon, and PsyQuack while working through hands-on cluster scenarios.

This is not a replacement for CKA/CKAD prep or platforms like Killer.sh. It is a practice ground to build confidence, stay engaged, and rehearse debugging in a low-stakes world that still uses a real local cluster.

## How it works

1. You run the game in one terminal (`yellow-olive start` or `python app.py`).
2. You keep a second terminal open as your **Command Chamber** for `kubectl`.
3. The game starts a local Minikube profile and applies deliberately broken manifests.
4. You read YAML in `yellow-olive-lab/`, fix the cluster, then type `psyquack validate`.
5. PsyQuack checks live cluster state - effort is not enough, the fix must be correct.

## What you learn

Each challenge maps game vocabulary to real Kubernetes concepts:

| Yellow Olive | Kubernetes |
|--------------|------------|
| Posemon | Container |
| Pokepod | Pod |
| Region / Town | Namespace |

Oakwood Meadows (challenges 1-7) focuses on Pods. Signal Town (challenges 8-13) focuses on Services, DNS, NodePort, Endpoints, and Ingress.

## Who this is for

- Developers who want a gentler on-ramp to Kubernetes
- Learners who benefit from story and structure alongside docs
- Contributors who want to add educational scenarios to an open-source game

## Where to go next

- [Getting Started](getting-started.md) - install and first run
- [Architecture](architecture.md) - how the codebase is organised
- [Contributing](contributing/index.md) - add challenges or new scenarios
- [GitHub README](https://github.com/Anubhav9/Yellow-Olive) - characters, motivation, and quick start
