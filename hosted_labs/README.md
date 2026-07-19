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

## Session audit logs

Each lab visit writes **one JSON file** with `meta` (who/when) and `activity` (what they did — auth, bootstrap, kubectl, policy violations).

Default path (gitignored in dev):

```
hosted_labs/logs/audit/YYYY-MM-DD/yo-sess-<id>.json
```

Override on homelab:

```bash
export HOSTED_LABS_AUDIT_DIR=/var/log/yellow-olive/audit
mkdir -p /var/log/yellow-olive/audit
```

Example:

```bash
jq '.activity[] | select(.category=="policy_violation")' \
  /var/log/yellow-olive/audit/2026-07-19/yo-sess-a1b2c3d4.json
```

One-off incidents (login failure, labs full, unauthenticated terminal) are stored as single files in the same date folder (`incident-*.json`).

## Session lifecycle

Each visit follows these rules after **Start session** (bootstrap succeeds):

| Rule | Default (challenge 1) | Result |
|------|----------------------|--------|
| Idle timeout | 4 minutes | Kicked out — **not** marked as challenge failed |
| Challenge time limit | 15 minutes | Session ends — **challenge failed** |

Per-challenge limits live in `challenges/<slug>/challenge_config.yaml`.

On end (logout, idle kick, timeout, or **Finish session** after pass):

- Lab seat is released
- Audit file is closed with a `reason` (`logout`, `idle_timeout`, `challenge_timeout`, `challenge_completed`)
- Kubernetes namespaces and `hosted_labs/sessions/<namespace>/` files are **left in place** for later review

## Challenge completions

Successful validations are appended to a single JSON array file (separate from audit logs):

```
hosted_labs/logs/completions.json
```

Example:

```json
[
  {
    "github_login": "anubhav9",
    "github_user_id": 12345,
    "challenge_slug": "challenge_1",
    "lab_session_id": "yo-sess-a1b2c3d4",
    "completed_at": "2026-07-19T04:12:00+00:00",
    "duration_seconds": 523,
    "duration_display": "8m 43s"
  }
]
```

Override on homelab:

```bash
export HOSTED_LABS_COMPLETIONS_FILE=/var/log/yellow-olive/completions.json
```

`duration_seconds` is measured from **Start session** (bootstrap succeeded) to validation pass.

## CLI bootstrap

```bash
python hosted_labs/core/render_policy.py --challenge challenge_1
python hosted_labs/core/render_policy.py --challenge challenge_1 --validate
```

