# Adding a Scenario

A **scenario** is a story arc with its own prologue, namespace, and challenge sequence. Oakwood Meadows and Signal Town are the two scenarios today. Use this guide when adding a third region (for example a Deployment-focused town).

## Overview

```
scenarios/<new_scenario>/
├── prologue/
│   ├── screens/
│   ├── dialogues/
│   └── k8s_resources/
│       └── namespace.yaml
└── challenge_<N>/
    └── ... (same layout as existing challenges)
```

You will also wire the scenario into progress, story intros, and `CHALLENGE_SCENARIO_MAP`.

## 1. Plan the arc

Decide:

- Scenario folder name (snake_case, for example `iron_peak`)
- Kubernetes namespace string (for example `iron-peak`)
- Challenge ID range (must not overlap unless you replace an arc)
- Prologue characters and screens
- Which concepts the arc teaches

Open an issue before large additions.

## 2. Create prologue infrastructure

### namespace.yaml

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: iron-peak
```

Place under `scenarios/<new_scenario>/prologue/k8s_resources/`.

### Bootstrap hook

Prologue namespaces are applied by `resource_manager.apply_prologue_resources(scenario_name)`.

Choose when to call it:

- **Option A:** On a dedicated intro screen's `on_mount` (Signal Town pattern)
- **Option B:** During game initialisation when entering the arc (Oakwood pattern)

Example (intro screen):

```python
async def _bootstrap_iron_peak_infra(self) -> None:
    await asyncio.to_thread(
        resource_manager.apply_prologue_resources, "iron_peak"
    )
```

Ensure the cluster is running before apply.

## 3. Prologue screens and dialogues

Add under:

```
scenarios/<new_scenario>/prologue/screens/
scenarios/<new_scenario>/prologue/dialogues/
```

Follow existing intro screens for structure:

- `scenarios/oakwood_meadows/prologue/screens/professor_bald_intro.py`
- `scenarios/signal_town/prologue/screens/signal_town_intro_screen.py`

Wire navigation from the previous arc's success path or a new `story_intro_act` value in `global_constants.py` and `general_utils.load_story_intro_screen()`.

## 4. Add challenges

For each challenge in the arc, follow [Adding a Challenge](adding-a-challenge.md).

Use the new namespace in all manifests and validators. Add a constant:

```python
NAMESPACE_IRON_PEAK = "iron-peak"
```

in `challenge_files/challenge_constants.py` (or a future scenario-local constants module).

## 5. Register challenge IDs

Update `CHALLENGE_SCENARIO_MAP` in `utils/general_utils.py`:

```python
"14": "iron_peak",
"15": "iron_peak",
```

Update `TOTAL_CHALLENGES` in `global_constants.py`.

## 6. Lab workspace

No extra code needed - `ensure_lab_workspace()` glob-copies all `scenarios/*/challenge_*/k8s_resources/*` into `yellow-olive-lab/`.

Verify a fresh lab picks up your new manifests.

## 7. Package discovery

Ensure `pyproject.toml` still includes the `scenarios*` package (it does today via setuptools find).

Run:

```bash
pip install -e .
python -c "import scenarios.iron_peak.challenge_14.screen"
```

## 8. Story and progress integration

Depending on how the arc enters the campaign, you may need to update:

| File | Change |
|------|--------|
| `global_constants.py` | New `STORY_ACT_*` values if multi-screen prologue |
| `utils/general_utils.py` | `load_story_intro_screen()`, `CHALLENGE_SCENARIO_MAP` |
| `screens/common/base_challenge_screen.py` | Transition from previous arc's last challenge |
| `screens/common/psy_quack_success_screen.py` | Load next challenge or intro screen |

Keep transitions consistent with how challenge 7 hands off to Signal Town.

## 9. Shared UI

Cross-scenario screens stay in `screens/common/`. Only put content in `scenarios/<name>/` if it is specific to that arc.

## 10. Documentation

Update:

- [Scenarios](../scenarios.md) - add row to scenario map and challenge table
- [Roadmap](../roadmap.md) - if this arc was planned work

## Testing checklist

- [ ] Namespace applies on prologue entry
- [ ] Each challenge applies lab manifests in the new namespace
- [ ] Validators use the new namespace constant
- [ ] Resume mid-arc loads correct screen
- [ ] PyPI / editable install includes new package paths

## Related pages

- [Adding a Challenge](adding-a-challenge.md)
- [Architecture](../architecture.md)
- [Cluster Lifecycle](../cluster-lifecycle.md)
