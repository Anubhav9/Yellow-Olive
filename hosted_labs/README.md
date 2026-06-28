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
3. Read `delicate/rbac.yaml` and apply challenge Role + RoleBinding
4. Render and apply starter manifests from `resources/` into the player's namespace
5. Player fixes YAML in-cluster
6. Validate against `resources/validation.yaml`

## Web UI (POC)

```bash
pip install -r hosted_labs/requirements.txt
uvicorn hosted_labs.api.main:app --reload
```

Open [http://127.0.0.1:8000/challenges/challenge_1](http://127.0.0.1:8000/challenges/challenge_1)

The challenge page shows briefing text and a **kubectl terminal**. Commands are sent over a
FastAPI WebSocket to `core/terminal.py`, which runs `kubectl` on the server (namespace is forced;
per-user kubeconfig is used when present under `hosted_labs/sessions/<github_id>/kubeconfig`).

## CLI bootstrap

```bash
python hosted_labs/core/render_policy.py --challenge challenge_1
python hosted_labs/core/render_policy.py --challenge challenge_1 --validate
```

