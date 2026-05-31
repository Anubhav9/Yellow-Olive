# Roadmap

High-level plan for Project Yellow Olive. Status reflects the scenario-based refactor branch as of May 2026.

## Shipped

| Feature | Notes |
|---------|-------|
| Save / load progress | `yellow-olive-lab/progress.json`, resume from main menu |
| PyPI packaging | `pip install yellow-olive`, `yellow-olive start` |
| Oakwood Meadows arc | Challenges 1-7, `oakwood-meadows` namespace |
| Signal Town arc (in progress) | Challenges 8-13, Services and networking topics |
| Scenario-based codebase | `scenarios/<name>/challenge_<N>/` layout, per-challenge validators |
| Lab workspace mirror | Editable manifests under `yellow-olive-lab/scenarios/` |
| Cluster lifecycle | Minikube profile with 60s health wait, teardown on quit |
| Technical documentation | This site |

## In active development

| Feature | Target | Notes |
|---------|--------|-------|
| Signal Town polish | May 2026 | Intro sequence, music, challenge copy |
| `psyquack hint` command | TBD | Listed in README, not wired in game yet |
| Resume + namespace bootstrap | TBD | Ensure namespace exists when skipping prologue |
| Move `challenge_constants.py` | TBD | Closer to scenarios or shared `_shared/constants.py` |
| Remove legacy `challenge_files/` mirror | TBD | Lab workspace cleanup |

## Planned

| Feature | Why it matters |
|---------|----------------|
| More scenarios / regions | Teach Deployments, ConfigMaps, RBAC, etc. |
| GitHub Pages CI for docs | Auto-deploy on push to main |
| Hint system | Professor Bald nudges without full spoilers |
| Challenge difficulty tags | Help players pick practice topics |
| Contributor templates | Issue and PR templates for new challenges |

## Phase history (original roadmap)

| Stage | Feature | Status |
|-------|---------|--------|
| Phase 1 | Save/load and jump to challenges | Released (April 2026) |
| Phase 2 | Service-focused challenges (Signal Town) | In progress |
| Phase 3 | PyPI publish | Released (April 2026) |

## How to influence the roadmap

- Star and watch the [repository](https://github.com/Anubhav9/Yellow-Olive) for updates
- [Open an issue](https://github.com/Anubhav9/Yellow-Olive/issues) with challenge ideas and learning objectives
- Submit a PR following [Adding a Challenge](contributing/adding-a-challenge.md)

## Related pages

- [Contributing](contributing/adding-a-challenge.md)
- [Scenarios](scenarios.md) - current challenge list
