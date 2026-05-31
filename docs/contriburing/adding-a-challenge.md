# Adding a Challenge

This guide replaces the old README contributing steps. Follow it when adding a new challenge to an **existing** scenario (Oakwood Meadows or Signal Town).

## Before you start

1. Open a [GitHub issue](https://github.com/Anubhav9/Yellow-Olive/issues) describing the learning objective and Kubernetes concept.
2. Pick the scenario folder and next challenge number.
3. Run the game from source so you can test the full flow.

## Checklist

- [ ] Create challenge folder with four files + manifests
- [ ] Add constants to `challenge_files/challenge_constants.py` if needed
- [ ] Register in `CHALLENGE_SCENARIO_MAP` and bump `TOTAL_CHALLENGES` if extending the campaign
- [ ] Test: apply, fix in Command Chamber, `psyquack validate`, success screen, next challenge
- [ ] Update docs or scenario table if the challenge list changes materially

## 1. Create the folder

```
scenarios/<scenario>/challenge_<N>/
├── screen.py
├── challenge_text.py
├── validator.py
└── k8s_resources/
    ├── pod-q<N>.yaml
    └── svc-q<N>.yaml    # optional, for Service challenges
```

Use existing challenges as templates:

- Pod-focused: copy from `scenarios/oakwood_meadows/challenge_1/`
- Service-focused: copy from `scenarios/signal_town/challenge_8/`

## 2. challenge_text.py

Export a string constant with the story setup:

```python
CHALLENGE_14_TEXT = """
Your narrative setup here.
Explain what broke in Yellow Olive terms.
"""
```

Keep tone consistent with nearby challenges in the same scenario.

## 3. screen.py

Minimum implementation:

```python
from scenarios.<scenario>.challenge_<N> import challenge_text
from screens.common.base_challenge_screen import BaseChallengeScreen
from services import resource_manager


class Challenge<N>(BaseChallengeScreen):
    challenge_id = "<N>"
    challenge_scenario = "<scenario>"
    challenge_text = challenge_text.CHALLENGE_<N>_TEXT

    def create_resources_for_challenge(self):
        resource_manager.apply_manifest(self.challenge_scenario, self.challenge_id)
```

Optional: customise `__init__` to append the lab manifest path (see challenge 1).

## 4. k8s_resources/

Write deliberately broken YAML that teaches the target concept. Use the correct namespace in metadata:

- Oakwood Meadows: `namespace: oakwood-meadows`
- Signal Town: `namespace: signal-town`

File naming convention:

- `pod-q<N>.yaml`
- `svc-q<N>.yaml`

Players receive copies under `yellow-olive-lab/scenarios/<scenario>/challenge_<N>/k8s_resources/`.

## 5. validator.py

Implement `validate()` returning `(bool, str)`. Use `resource_inspector` only.

Pattern:

```python
from challenge_files import challenge_constants
from services import resource_inspector


def validate():
    # 1. Resource exists
    # 2. Spec fields
    # 3. Runtime state (ready, endpoints, etc.)
    return True, "In-character success message"
```

See [Validation](../validation.md) for API details and examples.

## 6. Constants

Add shared names to `challenge_files/challenge_constants.py`:

```python
CHALLENGE_14_POD_NAME = "my-pod"
CHALLENGE_14_SERVICE_NAME = "my-service"
```

Use existing namespace constants (`NAMESPACE_OAKWOOD_MEADOWS`, `NAMESPACE_SIGNAL_TOWN`) where possible.

## 7. Register the challenge

In `utils/general_utils.py`:

```python
CHALLENGE_SCENARIO_MAP = {
    ...
    "<N>": "<scenario>",
}
```

If `<N>` is the new final challenge, update `TOTAL_CHALLENGES` in `global_constants.py`.

## 8. Story transitions (optional)

Most challenges advance automatically via `get_next_challenge_id`. Special cases need edits in `BaseChallengeScreen.handle_validation()` - for example challenge 7 sets `story_intro_act` before Signal Town.

Only touch that code if your challenge ends an arc or starts a new prologue.

## 9. Test locally

```bash
# From repo root
python -c "from utils.general_utils import load_challenge; load_challenge('<N>')"

# Manual validator test (cluster must be running, challenge applied)
python -c "from scenarios.<scenario>.challenge_<N>.validator import validate; print(validate())"

# Full game
python app.py
```

Walk through:

1. Challenge loads and applies manifests
2. Broken state is reproducible
3. Your fix passes validation
4. Wrong states fail with helpful messages
5. Success screen and next challenge (or story transition) work

## 10. Pull request

Include in the PR description:

- Learning objective (what Kubernetes skill this teaches)
- Scenario and challenge number
- Short screen recording or terminal capture of pass and fail paths
- Any new constants or namespace assumptions

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Validator checks `default` namespace | Use scenario namespace constants |
| Forgot `challenge_scenario` on screen | Set attribute on the screen class |
| Manifest only in repo, not lab | Game copies on first run - delete lab copy to refresh |
| Validator shells out to kubectl | Use `resource_inspector` |
| Success possible without intended fix | Tighten checks (endpoints, not just Service exists) |

## Related pages

- [Adding a Scenario](adding-a-scenario.md) - new town / arc
- [Validation](../validation.md) - inspector API
- [Lab Workspace](../lab-workspace.md) - where players edit YAML
