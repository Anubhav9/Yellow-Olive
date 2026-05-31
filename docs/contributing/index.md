# Contributing

Contributions are welcome - especially new challenges, scenarios, and documentation improvements.

## Before you open a PR

1. [Open an issue](https://github.com/Anubhav9/Yellow-Olive/issues) with the learning objective and Kubernetes concept you want to teach.
2. Install from source and run the game locally.
3. Follow the guide that matches your change:

| Guide | Use when |
|-------|----------|
| [Adding a Challenge](adding-a-challenge.md) | New challenge in an existing scenario (Oakwood Meadows or Signal Town) |
| [Adding a Scenario](adding-a-scenario.md) | Entirely new story arc with its own namespace and prologue |

## Quick reference

New challenge folder layout:

```
scenarios/<scenario>/challenge_<N>/
├── screen.py
├── challenge_text.py
├── validator.py
└── k8s_resources/
```

Register the challenge in `utils/general_utils.py` (`CHALLENGE_SCENARIO_MAP`) and add constants to `challenge_files/challenge_constants.py` when needed.

See [Validation](../validation.md) for how PsyQuack checks cluster state.

## Code of conduct

Be respectful in issues and PRs. The project is a learning experiment - clarity and kindness help everyone.
