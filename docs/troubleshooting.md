# Troubleshooting

Common issues when running Yellow Olive locally and how to fix them.

## Minikube fails to start

**Symptoms:** Game shows "Lab cluster failed" after you type `yes`. Terminal may show Docker or driver errors.

**Checks:**

1. Docker Desktop (or Docker Engine) is running
2. `minikube start -p project-yellow-olive` works manually
3. Enough disk and memory for a single-node cluster

**Fix:**

```bash
minikube delete -p project-yellow-olive --purge
minikube start --nodes 1 -p project-yellow-olive
```

Then restart the game.

## Cluster not ready within 5 minutes

**Symptoms:** Bootstrap message stays visible, then failure notification.

**Cause:** Slow first pull of Kubernetes images, Docker under load, or stuck profile.

**Fix:**

- Wait for manual `minikube start` to finish once, then retry in the game
- Increase Docker resources (CPU / memory) in Docker Desktop settings
- Delete and recreate the profile (see above)

## kubectl context wrong

**Symptoms:** `kubectl get pods` shows resources from a different cluster, or connection refused.

**Fix:**

```bash
kubectl config use-context project-yellow-olive
kubectl get nodes
```

Run kubectl from the same machine as the game. The game switches context during bootstrap but other tools may change it back.

## Namespace not found

**Symptoms:** Pods or services fail to create. Validator says resources not found in `oakwood-meadows` or `signal-town`.

**Fix:**

Apply the namespace manually from the repo:

```bash
kubectl apply -f scenarios/oakwood_meadows/prologue/k8s_resources/namespace.yaml
kubectl apply -f scenarios/signal_town/prologue/k8s_resources/namespace.yaml
```

Or replay the prologue flow that applies them automatically.

## Challenge pod not updating after manifest edit

**Symptoms:** You fixed YAML but the pod still shows the old spec.

**Cause:** `kubectl apply` alone may not recreate pods when certain fields change. The game applies lab files on challenge mount, but your Command Chamber commands must actually replace the workload.

**Fix:**

```bash
kubectl delete pod <name> -n <namespace>
kubectl apply -f yellow-olive-lab/scenarios/<scenario>/challenge_<N>/k8s_resources/pod-q<N>.yaml
```

Or delete and re-apply as the challenge text instructs.

## psyquack validate says not ready - pod looks fine

**Checks:**

1. Correct namespace: `kubectl get pod -n oakwood-meadows` vs `signal-town`
2. Pod name matches what the validator expects (see `challenge_constants.py`)
3. Container **Ready** column is `True`: `kubectl get pod -n <ns> -o wide`
4. For Services: `kubectl get endpoints -n <ns>` shows addresses

## Lab workspace in the wrong place

**Symptoms:** Empty progress, manifests not where you edited them.

**Cause:** `yellow-olive-lab/` is created relative to **current working directory**, not the repo root.

**Fix:**

Always start the game from the same directory, or use absolute paths when editing manifests.

## Stale lab files after git pull

**Symptoms:** New challenge YAML from an update does not appear, or old broken config persists.

**Cause:** Lab mirror never overwrites existing files.

**Fix:**

Delete specific stale files or the whole lab scenarios subtree, then restart the game to re-copy from source:

```bash
rm -rf yellow-olive-lab/scenarios/oakwood_meadows/challenge_3
```

Progress in `progress.json` is kept if you only delete scenario subfolders.

## Game imports fail from source

**Symptoms:** `ImportError` for moved modules after pulling latest main.

**Fix:**

```bash
pip install -r requirements.txt
python -c "import app"
```

Report persistent import errors as a GitHub issue - the scenario refactor moved many paths.

## PyPI package out of date

**Symptoms:** Missing challenges, old folder layout, missing Signal Town content.

**Fix:**

```bash
pip install -U yellow-olive
```

For bleeding-edge changes, install from source instead.

## Still stuck?

1. Capture output from `minikube status -p project-yellow-olive` and `kubectl get all -A`
2. Note challenge ID and what you changed in the lab manifest
3. [Open an issue](https://github.com/Anubhav9/Yellow-Olive/issues) with logs and steps

## Related pages

- [Cluster Lifecycle](cluster-lifecycle.md) - intended startup and teardown behaviour
- [Lab Workspace](lab-workspace.md) - copy semantics and paths
- [Getting Started](getting-started.md) - prerequisite versions
