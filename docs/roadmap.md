# Roadmap

High-level plan for Project Yellow Olive. Status reflects the campaign and diagnostics work as of September 2026.

## Latest updates

**September 2026 (0.8.0) — Migration from PyGame to pygame-ce complete.** The game now
depends on [pygame-ce](https://pyga.me/) instead of `pygame` for audio. Because pygame-ce
ships wheels for current Python releases, Yellow Olive now officially supports **Python 3.14
and 3.15** in addition to 3.10–3.13, and both are part of the PyPI install smoke-test matrix.

!!! note "Upgrading an existing install"
    `pygame` and `pygame-ce` install into the same `pygame` package. If you previously had
    `pygame` installed, run `pip uninstall pygame` before upgrading `yellow-olive`.

## Shipped

| Feature | Notes |
|---------|-------|
| Save / load progress | `yellow-olive-lab/progress.json`, resume from main menu |
| PyPI packaging | `pip install yellow-olive`, `yellow-olive start` (0.6.x) |
| Oakwood Meadows arc | Challenges 1–7, `oakwood-meadows` namespace |
| Signal Town arc | Challenges 8–13, Services and networking |
| Gold Rush City arc | Challenges 14–19, RBAC |
| Sakura Harbour arc | Challenges 20–24, Deployments, rollouts, canary |
| Scenario-based codebase | `scenarios/<name>/challenge_<N>/` layout, per-challenge validators |
| Lab workspace mirror | Editable manifests under `yellow-olive-lab/scenarios/` |
| Cluster lifecycle | Minikube profile with startup budget, teardown on quit |
| Opt-in diagnostics | Consent screen, Sentry Logs for gameplay, Issues for errors |
| pygame-ce migration | Audio via `pygame-ce`; Python 3.10–3.15 supported (0.8.0) |
| Technical documentation | This site |

## In active development

| Feature | Notes |
|---------|--------|
| `psyquack hint` command | Listed in README, not wired in game yet |
| Help screen privacy controls | Revoke or change diagnostics consent from Help |
| Docs CI polish | Keep scenario and architecture pages in sync with new arcs |

## Planned

| Feature | Why it matters |
|---------|----------------|
| More scenarios / regions | Teach additional workload patterns |
| Hint system | Professor Bald nudges without full spoilers |
| Challenge difficulty tags | Help players pick practice topics |
| Contributor templates | Issue and PR templates for new challenges |
| Hosted lab mode | Browser-based challenges (separate from PyPI game) |

## Phase history

| Stage | Feature | Status |
|-------|---------|--------|
| Phase 1 | Save/load and jump to challenges | Released (April 2026) |
| Phase 2 | Service-focused challenges (Signal Town) | Released |
| Phase 3 | PyPI publish | Released (April 2026) |
| Phase 4 | Gold Rush City + Sakura Harbour | Released (2026) |
| Phase 5 | Opt-in diagnostics | Released on `feature/sentry-logging` |
| Phase 6 | pygame-ce migration, Python 3.14 / 3.15 support | Released (September 2026, 0.8.0) |

## How to influence the roadmap

- Star and watch the [repository](https://github.com/Anubhav9/Yellow-Olive) for updates
- [Open an issue](https://github.com/Anubhav9/Yellow-Olive/issues) with challenge ideas and learning objectives
- Submit a PR following [Adding a Challenge](contributing/adding-a-challenge.md)

## Related pages

- [Scenarios](scenario.md) — current challenge list by arc
- [Privacy and Diagnostics](privacy.md) — what telemetry collects
- [Contributing](contributing/adding-a-challenge.md)
