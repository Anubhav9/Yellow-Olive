# Lab Workspace

The lab workspace is the directory where Yellow Olive mirrors editable Kubernetes manifests and stores save-game progress. It keeps player edits separate from the game source shipped in the repo or PyPI package.

## Location

```
<your current working directory>/yellow-olive-lab/
```

The path is always relative to where you run `yellow-olive start` or `python app.py`. If you move terminals or change directories between sessions, you may see a fresh lab folder. Pick one working directory and stick with it.

## What gets created

```
yellow-olive-lab/
├── progress.json
├── challenge_files/          # legacy mirror (harmless, may be empty)
└── scenarios/
    └── <scenario>/
        └── challenge_<N>/
            └── k8s_resources/
                ├── pod-q<N>.yaml
                └── svc-q<N>.yaml
```

### progress.json

Tracks player name, active challenge, music preference, and Signal Town intro state. Created on first save. Deleting the lab folder resets the campaign (`reset_progress()` also removes it).

### Scenario manifests

On first run, `ensure_lab_workspace()` copies any missing YAML from:

```
<package or repo>/scenarios/<scenario>/challenge_<N>/k8s_resources/*
```

into the matching path under `yellow-olive-lab/scenarios/`.

**Copy rules:**

- Copy only when the target file **does not exist**
- Never overwrite an existing lab file - player edits are preserved across sessions
- New challenge YAML added in a game update will appear in the lab on next run if the target was missing

### What is NOT mirrored

Prologue infrastructure (namespaces) is **not** copied to the lab. Those files stay under `scenarios/<scenario>/prologue/k8s_resources/` and are applied directly by the game.

## What the game applies

When a challenge mounts, `resource_manager.apply_manifest()` reads from the **lab** path:

```
yellow-olive-lab/scenarios/<scenario>/challenge_<N>/k8s_resources/
```

Every `.yaml` / `.yml` file in that folder is applied with `kubectl apply -f`.

This means:

- Edit lab copies, not repo source, during normal gameplay
- After fixing a manifest, use `kubectl delete` / `kubectl apply -f` (or equivalent) from the Command Chamber
- Re-applying from the game on challenge remount will use your edited lab files

## Helper paths in code

`utils/general_utils.py` exposes:

| Function | Returns |
|----------|---------|
| `get_lab_root()` | `Path.cwd() / "yellow-olive-lab"` |
| `get_lab_challenge_file(scenario, id)` | Path to `pod-q<id>.yaml` in lab |
| `get_lab_service_file(scenario, id)` | Path to `svc-q<id>.yaml` in lab |
| `get_progress_file()` | `yellow-olive-lab/progress.json` |

Challenge 1 displays the pod manifest path to the player using `get_lab_challenge_file`.

## PyPI vs source installs

| Install type | Source manifests copied from |
|--------------|------------------------------|
| PyPI | Files inside the installed `yellow-olive` package |
| Source | Your local clone under `scenarios/` |

In both cases, gameplay edits land in `yellow-olive-lab/` only.

## Legacy challenge_files mirror

`ensure_lab_workspace()` still mirrors `challenge_files/*.yaml` into `yellow-olive-lab/challenge_files/` for backward compatibility. New development should use the `scenarios/` layout. This legacy path may be removed in a future cleanup.

## Tips for contributors testing locally

1. Run the game from the repo root so lab paths are predictable.
2. To test pristine manifests, delete `yellow-olive-lab/scenarios/<scenario>/challenge_<N>/` and restart - files will be re-copied from source.
3. To fully reset save state, delete the entire `yellow-olive-lab/` folder or use in-game reset if available.

## Related pages

- [Getting Started](getting-started.md) - two-terminal workflow
- [Contributing: Adding a Challenge](contributing/adding-a-challenge.md) - where to place new YAML
- [Validation](validation.md) - validators inspect live cluster state, not lab files directly
