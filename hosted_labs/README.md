# Hosted Labs

Public Kubernetes challenges run on a shared cluster. This folder is **not** part of the
`yellow-olive` PyPI package and is not imported by the local terminal game.

## Layout

```
hosted_labs/
├── api/                  # FastAPI + Jinja templates (POC frontend)
├── core/                 # session bootstrap, render, kubectl apply
├── policies/             # absolute platform guardrails (every session)
└── challenges/
    └── challenge_1/
        ├── challenge_text.py
        ├── validator.py
        ├── delicate/       # platform-only (RBAC config — never player-facing)
        └── resources/      # starter manifests seeded into the player namespace
```

## Session flow

1. `core` receives `formatted_github_user_id`, `session_id`, and `challenge_slug`
2. Apply absolute policies (namespace, quota, network)
3. Read `delicate/rbac.yaml` and apply challenge Role, ServiceAccount, and RoleBinding
4. Render and apply starter manifests from `resources/` into the player's namespace
5. Mint a ServiceAccount token and write a limited player kubeconfig under `sessions/<namespace>/kubeconfig`
6. Player fixes YAML in-cluster via the browser terminal (limited kubeconfig only)
7. Validate against `resources/validation.yaml`

## Web UI (POC)

1. Copy `hosted_labs/.env.example` to `hosted_labs/.env` and fill in your GitHub OAuth credentials.
2. Register the callback URL in your GitHub OAuth App, e.g. `http://127.0.0.1:8000/auth/github/callback`.
3. Install and run:

```bash
pip install -r hosted_labs/requirements.txt
uvicorn hosted_labs.api.main:app --reload
```

Open [http://127.0.0.1:8000/login](http://127.0.0.1:8000/login)

Challenge text and the kubectl terminal are only available **after GitHub login** and when a lab seat is free (default max: 7).

The API process needs **admin** cluster access for bootstrap and validation. On k3s, copy `/etc/rancher/k3s/k3s.yaml` to `~/.kube/config` for the user running uvicorn, or set `KUBECONFIG` to that file.

## CLI bootstrap

```bash
python hosted_labs/core/render_policy.py --challenge challenge_1
python hosted_labs/core/render_policy.py --challenge challenge_1 --validate
```

