# Cluster Lifecycle

Yellow Olive manages a dedicated Minikube cluster for the lab. The game starts the cluster when the player commits to the mission, applies scenario namespaces at prologue boundaries, and tears the cluster down on quit.

## Minikube profile

| Setting | Value |
|---------|-------|
| Profile | `project-yellow-olive` |
| Nodes | 1 |
| Driver | Default Minikube driver (Docker on most setups) |

The profile is isolated from other Minikube profiles you may use for work or study.

## Startup sequence

### 1. scripts/script.sh

Called by `general_utils.start_core_infra(wait=True)` from the game initialisation screen.

Steps:

1. Verify `minikube` is on PATH
2. `minikube start --nodes 1 -p project-yellow-olive`
3. Poll `minikube status -p project-yellow-olive` every 2 seconds until healthy
4. **Timeout:** 60 seconds - exits non-zero if cluster never becomes ready
5. `kubectl config use-context project-yellow-olive`

When `wait=False`, the script is fired in the background (legacy path - prologue bootstrap uses `wait=True`).

### 2. Oakwood Meadows namespace

After the cluster is ready, `GameInitialisationScreen._bootstrap_oakwood_meadows_infra()` applies:

```
scenarios/oakwood_meadows/prologue/k8s_resources/namespace.yaml
```

This creates the `oakwood-meadows` namespace before challenge 1.

### 3. Per-challenge manifests

Each challenge screen's `create_resources_for_challenge()` applies lab manifests for that challenge only.

### 4. Signal Town namespace

When the player completes challenge 7 and finishes the Signal Town story intro, `SignalTownIntroScreen._bootstrap_signal_town_infra()` applies:

```
scenarios/signal_town/prologue/k8s_resources/namespace.yaml
```

The cluster is already running at this point - only the namespace is applied.

## Resume behaviour

If the player resumes mid-campaign:

- **Cluster:** started again when they continue from the resume screen (same 60s bootstrap message)
- **Oakwood namespace:** applied during init if they go through a fresh start path
- **Signal Town namespace:** applied when the Signal Town intro screen mounts if they are in that arc

!!! note "Known gap"
    Resuming directly into an Oakwood challenge without replaying prologue may skip namespace re-apply if the cluster was torn down. If pods fail with namespace not found, apply the namespace manually or restart from the game initialisation flow. This is tracked for a future fix.

## Teardown

When the player quits from the main menu, `app.on_exit()` runs:

```python
minikube delete -p project-yellow-olive --purge
```

This removes the profile and its Docker resources. The lab workspace on disk (`yellow-olive-lab/`) is **not** deleted - progress persists for the next session.

## UI messaging

The game initialisation screen shows `CLUSTER_BOOTSTRAP_MESSAGE` while waiting - it mentions the cluster can take up to 60 seconds.

If startup fails, the player sees a notification with `CLUSTER_STARTUP_FAILURE_MESSAGE` and can retry by typing `yes` again.

## Manual cluster commands

Useful when debugging outside the game:

```bash
# Check profile status
minikube status -p project-yellow-olive

# Point kubectl at the lab context
kubectl config use-context project-yellow-olive

# Nuclear reset (same as quitting the game)
minikube delete -p project-yellow-olive --purge
```

## Namespace reference

| Namespace | Created by | Used by |
|-----------|------------|---------|
| `oakwood-meadows` | Oakwood prologue bootstrap | Challenges 1-7 |
| `signal-town` | Signal Town intro bootstrap | Challenges 8-13 |
| `default` | Kubernetes default | Some cross-namespace challenges (for example relay pods) |

## Related pages

- [Getting Started](getting-started.md) - first run expectations
- [Troubleshooting](troubleshooting.md) - when startup hangs or fails
- [Scenarios](scenarios.md) - prologue resource locations
