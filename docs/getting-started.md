# Getting Started

This page covers full setup for local development and playing from source. If you only want to try the game, the README quick start is enough:

```bash
pip install yellow-olive
yellow-olive start
```

## Prerequisites

| Tool | Version | Why you need it |
|------|---------|-----------------|
| Python | 3.10+ | Runs the Textual game |
| Docker | Latest stable | Minikube driver |
| Minikube | Latest stable | Local Kubernetes cluster |
| kubectl | Latest stable | Apply and inspect cluster resources |

Verify your tooling:

```bash
python --version
docker --version
minikube version
kubectl version --client
```

Make sure Docker is running before you start the game.

### Install Minikube and kubectl

Follow the official guides if you do not have them yet:

- [Install Minikube](https://minikube.sigs.k8s.io/docs/start/)
- [Install kubectl](https://kubernetes.io/docs/tasks/tools/)

## Install from PyPI

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install yellow-olive
yellow-olive start
```

On first mission start, the game creates a Minikube cluster. This can take up to 60 seconds.

## Install from source

```bash
git clone https://github.com/Anubhav9/Yellow-Olive.git
cd Yellow-Olive
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

From source you get the latest scenario refactor and can edit validators or manifests directly in the repo.

## Two-terminal workflow

Yellow Olive is designed around two terminals:

1. **Game terminal** - run `yellow-olive start` or `python app.py`
2. **Command Chamber** - run `kubectl` commands to inspect and fix cluster resources

The game applies broken manifests for you. You diagnose and repair them in the Command Chamber, then type `psyquack validate` in the game when you think the fix is correct.

## Lab workspace

When the game starts, it materialises `yellow-olive-lab/` in your **current working directory**. Challenge manifests are copied there so players edit lab copies, not the installed package or repo source.

See [Lab Workspace](lab-workspace.md) for paths and copy semantics.

## In-game commands

| Command | Status | Description |
|---------|--------|-------------|
| `psyquack validate` | Implemented | PsyQuack checks your cluster fix for the current challenge |
| `psyquack back` | Implemented | Return to the previous screen |
| `psyquack hint` | Planned | Nudge from Professor Bald without spoiling the answer |

During prologue and init screens, follow the on-screen prompts (for example `yes` to begin your mission).

## First run flow

1. Start the game from the main menu.
2. Complete the Oakwood Meadows prologue (name input, Professor Bald intro).
3. Type `yes` on the game initialisation screen - this starts Minikube and applies the `oakwood-meadows` namespace.
4. Choose whether to play challenge music.
5. Challenge 1 loads - broken pod manifest is applied from your lab workspace.
6. Fix the pod in your Command Chamber, then `psyquack validate` in the game.

## Cluster profile

The game uses a dedicated Minikube profile so it does not touch your other clusters:

- **Profile name:** `project-yellow-olive`
- **Context:** switched automatically by `scripts/script.sh`
- **Teardown:** profile is deleted when you quit the game from the main menu

Details: [Cluster Lifecycle](cluster-lifecycle.md).

## Next steps

- [Architecture](architecture.md) - module map and request flow
- [Contributing: Adding a Challenge](contributing/adding-a-challenge.md) - extend the game
- [Troubleshooting](troubleshooting.md) - when Minikube or kubectl misbehaves
