# Yellow Olive Technical Documentation

Project Yellow Olive is a terminal-native game built with [Textual](https://textual.textualize.io/). Players fix real Kubernetes problems in a local Minikube cluster while progressing through a Pokémon-inspired story.

This site is for contributors, maintainers, and anyone who wants to understand how the game works under the hood. For the player-facing pitch, characters, and quick start, see the [GitHub README](https://github.com/Anubhav9/Yellow-Olive).

## What you will find here

| Page | Purpose |
|------|---------|
| [Getting Started](getting-started.md) | Full install, PyPI vs source, two-terminal workflow |
| [Architecture](architecture.md) | How the app boots, loads challenges, and talks to kubectl |
| [Scenarios](scenarios.md) | Oakwood Meadows and Signal Town arcs, folder layout |
| [Lab Workspace](lab-workspace.md) | The `yellow-olive-lab/` mirror and what players edit |
| [Validation](validation.md) | `resource_inspector` helpers and per-challenge validators |
| [Cluster Lifecycle](cluster-lifecycle.md) | Minikube bootstrap, namespaces, teardown on quit |
| [Contributing](contributing/adding-a-challenge.md) | How to add challenges and new scenarios |
| [Troubleshooting](troubleshooting.md) | Common Minikube and kubectl failures |
| [Roadmap](roadmap.md) | Planned features and release status |

## Repository layout (high level)

```
Yellow-Olive/
├── app.py                    # Textual app entry point + `yellow-olive` CLI
├── scenarios/                # Story arcs, challenges, prologues, k8s manifests
├── screens/common/           # Shared UI (base challenge screen, init, resume, help)
├── services/                 # kubectl apply (write) and inspect (read)
├── utils/general_utils.py    # Progress, lab workspace, challenge loading
├── scripts/script.sh         # Minikube start + health wait
└── challenge_files/          # Shared constants used by validators
```

## Tech stack

- **UI:** Textual + Rich
- **Cluster:** Minikube profile `project-yellow-olive`, single node
- **Manifests:** Plain YAML applied with `kubectl apply -f`
- **Validation:** Python validators call `kubectl get` / `kubectl exec` via `services/resource_inspector.py`
- **Progress:** JSON file at `yellow-olive-lab/progress.json`

## Quick links

- [Repository](https://github.com/Anubhav9/Yellow-Olive)
- [PyPI package](https://pypi.org/project/yellow-olive/)
- [Report an issue](https://github.com/Anubhav9/Yellow-Olive/issues)
