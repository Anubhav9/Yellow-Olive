# Privacy and Diagnostics

Yellow Olive runs locally on your machine. The game does **not** read your cluster contents, secrets, or kubectl output for diagnostics.

Optional, anonymous telemetry helps improve the game when you opt in on first **Start Game**.

## Consent

On the first run (when `consent` is `unknown` in settings), the game shows a short welcome screen with two choices:

- **Yes, opt in** — anonymous gameplay and error reports may be sent
- **No thanks, skip** — no ongoing reports; the game works the same

Your choice is stored in `yellow-olive-lab/settings.json` and is not asked again unless you reset it.

## What we may send (opt-in only)

Every event shares the same envelope:

| Field | Purpose |
|-------|---------|
| `event` | What happened (for example `challenge_completed`) |
| `app_version` | Yellow Olive version |
| `python_version` | Python runtime |
| `platform` | OS family (`darwin`, `linux`, `windows`) |
| `installation_id` | Random UUID for this install (not your name) |
| `session_id` | Random UUID for this game run |
| `timestamp` | UTC ISO timestamp |
| `data` | Event-specific fields (challenge id, scenario, reason codes, etc.) |

### Gameplay events

| Event | When |
|-------|------|
| `game_started` | Player starts from the main menu |
| `game_quit` | Player chooses Quit |
| `consent_granted` | Player opts in |
| `challenge_started` | Challenge screen mounts |
| `challenge_completed` | `psyquack validate` succeeds |
| `challenge_failed` | Validation fails |
| `section_completed` | Story intro or arc epilogue finished |
| `music_preference_set` | Player chooses challenge music on/off |
| `infra_setup_started` | Minikube bootstrap begins |
| `infra_setup_succeeded` | Cluster is ready |
| `infra_setup_failed` | Bootstrap failed (`reason` enum only — no stderr) |

### Errors

When opted in, caught exceptions can be sent via `track_exception()` with stack traces. These appear in Sentry **Issues**, not Logs.

## What we never send

- Pod specs, secrets, ConfigMaps, or other cluster objects
- `kubectl` command output or stderr
- Player name or `progress.json` contents
- Commands typed in the terminal

## Opt-out behaviour

If you decline:

- No Sentry session is created
- No gameplay events are sent
- A single anonymous `consent_declined` ping is recorded in Sentry Logs (no `installation_id`) so maintainers can measure opt-in rates — no gameplay data is sent after you decline

## Where data goes

Opt-in events are sent to [Sentry](https://sentry.io/) using the public DSN shipped in the package. Gameplay events use **Sentry Logs**; real errors use **Issues**.

Maintainers can override the DSN with:

```bash
export YELLOW_OLIVE_SENTRY_DSN="https://..."
```

## Settings file

`yellow-olive-lab/settings.json`:

```json
{
  "version": 1,
  "diagnostics": {
    "consent": "unknown",
    "installation_id": null,
    "consent_prompted_at": null,
    "consent_updated_at": null
  }
}
```

`consent` is one of `unknown`, `granted`, or `declined`. Delete this file or set `consent` back to `unknown` to see the prompt again.

## For contributors

Game code should call only:

```python
from services.diagnostics import track, track_exception

track("challenge_completed", challenge_id="20", scenario="sakura_harbour")
```

Implementation lives in `services/diagnostics/`. Do not import `sentry_sdk` elsewhere.

## Related pages

- [Lab Workspace](lab-workspace.md) — `settings.json` location
- [Architecture](architecture.md) — where hooks are wired
- [SECURITY.md](https://github.com/Anubhav9/Yellow-Olive/blob/main/SECURITY.md) — reporting security issues
