# Scenarios

Story content is organised by **scenario** (a town / arc). Each scenario has a prologue and a set of numbered challenges. Challenges 1-7 belong to Oakwood Meadows. Challenges 8-13 belong to Signal Town.

## Scenario map

| Challenge IDs | Scenario folder | Kubernetes namespace | Primary topics |
|---------------|-----------------|----------------------|----------------|
| 1-7 | `scenarios/oakwood_meadows/` | `oakwood-meadows` | Pods, containers, probes, resources |
| 8-13 | `scenarios/signal_town/` | `signal-town` | Services, DNS, NodePort, Endpoints, Ingress |

## Folder layout

Every challenge follows the same shape:

```
scenarios/<scenario_name>/
├── prologue/
│   ├── screens/              # Intro UI for this arc
│   ├── dialogues/            # Intro copy
│   └── k8s_resources/        # Namespace and other infra (game-managed)
└── challenge_<N>/
    ├── screen.py             # Textual screen class (subclasses BaseChallengeScreen)
    ├── challenge_text.py     # Story text shown in the RichLog panel
    ├── validator.py          # validate() -> (bool, message)
    └── k8s_resources/        # Broken manifests the player fixes
        ├── pod-q<N>.yaml
        └── svc-q<N>.yaml     # when the challenge needs a Service
```

### Prologue

Prologue resources are applied automatically:

- **Oakwood Meadows** - namespace applied when the player types `yes` on the game initialisation screen (after Minikube is ready)
- **Signal Town** - namespace applied when the Signal Town intro screen mounts (cluster already running)

Prologue YAML is read from the **installed repo / package**, not from `yellow-olive-lab/`.

## Oakwood Meadows (challenges 1-7)

Professor Bald's laboratory arc. Electromon (your companion) is deployed as pods with deliberate misconfigurations. Players learn to read manifests, use `kubectl describe`, and recreate workloads.

| Challenge | Focus (high level) |
|-----------|-------------------|
| 1 | Pod not ready - fix container image or command |
| 2 | Pod scheduling / resource issues |
| 3 | Environment and configuration |
| 4 | Labels and selectors |
| 5 | Probes and readiness |
| 6 | Multi-container pod |
| 7 | Capstone pod scenario before leaving for Signal Town |

After challenge 7, progress advances to challenge 8 and sets `story_intro_act` so the Signal Town prologue plays before challenge 8 loads.

## Signal Town (challenges 8-13)

Cool Turtle needs help restoring connectivity. Team Evil broke the paths between workloads. Challenges move from ClusterIP Services through DNS, cross-namespace access, NodePort, endpoint scaling, and Ingress.

| Challenge | Focus (high level) |
|-----------|-------------------|
| 8 | ClusterIP Service wiring to a pod |
| 9 | In-cluster DNS resolution |
| 10 | Cross-namespace Service DNS |
| 11 | NodePort exposure |
| 12 | Multiple backend pods and endpoints |
| 13 | Ingress routing |

Signal Town prologue is a three-act intro (Signal Town, Cool Turtle, Team Evil) tracked via `story_intro_act` in progress.

## Screen class conventions

Each `screen.py` exports `Challenge<N>`:

```python
class Challenge8(BaseChallengeScreen):
    challenge_id = "8"
    challenge_scenario = "signal_town"
    challenge_text = challenge_text.CHALLENGE_8_TEXT

    def create_resources_for_challenge(self):
        resource_manager.apply_manifest(self.challenge_scenario, self.challenge_id)
```

Some Oakwood screens customise `challenge_text` in `__init__` to include the lab manifest path (see challenge 1).

## Registering a new challenge in an existing scenario

1. Add the folder `scenarios/<scenario>/challenge_<N>/` with all four files.
2. Add `"<N>": "<scenario>"` to `CHALLENGE_SCENARIO_MAP` in `utils/general_utils.py`.
3. Bump `TOTAL_CHALLENGES` in `global_constants.py` if this extends the campaign end.
4. Wire the previous challenge's success screen to load challenge N (handled automatically via `get_next_challenge_id` unless you need a special story transition).

See [Adding a Challenge](contributing/adding-a-challenge.md) for the full checklist.

## Adding a whole new scenario

See [Adding a Scenario](contributing/adding-a-scenario.md).

## Related pages

- [Lab Workspace](lab-workspace.md) - where manifests are copied for player edits
- [Validation](validation.md) - writing `validator.py`
- [Architecture](architecture.md) - how screens and services connect
