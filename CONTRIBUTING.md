# Contributing to Project Yellow Olive

Thanks for your interest in contributing. Yellow Olive is a terminal Kubernetes learning game - contributions that add challenges, fix bugs, or improve docs are especially welcome.

## Full documentation

Detailed guides live on GitHub Pages:

- [Contributing overview](https://anubhav9.github.io/Yellow-Olive/contributing/)
- [Adding a challenge](https://anubhav9.github.io/Yellow-Olive/contributing/adding-a-challenge/)
- [Adding a scenario](https://anubhav9.github.io/Yellow-Olive/contributing/adding-a-scenario/)
- [Architecture](https://anubhav9.github.io/Yellow-Olive/architecture/)
- [Validation](https://anubhav9.github.io/Yellow-Olive/validation/)

## How to contribute

1. **Open an issue** - Describe the learning objective, Kubernetes concept, or bug. For new challenges, mention which scenario (Oakwood Meadows or Signal Town) it belongs to.
2. **Fork and clone** - Install from source and verify the game runs (`python app.py`).
3. **Make your change** - Follow the guides linked above for new challenges or scenarios.
4. **Test locally** - Walk through the challenge flow: manifest apply, fix in a second terminal with `kubectl`, `psyquack validate`, success and failure paths.
5. **Open a pull request** - Link the issue, describe what changed, and include a short demo or screenshot if it is a new challenge.

## Development setup

```bash
git clone https://github.com/Anubhav9/Yellow-Olive.git
cd Yellow-Olive
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Prerequisites: Python 3.10+, Docker, Minikube, and kubectl. See [Getting Started](https://anubhav9.github.io/Yellow-Olive/getting-started/) for details.

## Adding a challenge (quick reference)

Create a folder under the scenario:

```
scenarios/<scenario>/challenge_<N>/
├── screen.py
├── challenge_text.py
├── validator.py
└── k8s_resources/
```

Then:

- Register the challenge in `CHALLENGE_SCENARIO_MAP` in `utils/general_utils.py`
- Add shared names to `challenge_files/challenge_constants.py` if needed
- Bump `TOTAL_CHALLENGES` in `global_constants.py` if this extends the campaign

Validators must use `services/resource_inspector.py` (read-only kubectl helpers), not direct shell calls.

## Adding a scenario

A new scenario needs a prologue (screens, dialogues, namespace YAML), a challenge sequence, and wiring in `CHALLENGE_SCENARIO_MAP` and story progress. See the [adding a scenario guide](https://anubhav9.github.io/Yellow-Olive/contributing/adding-a-scenario/).

## Pull request guidelines

- Keep PRs focused - one challenge or one logical change per PR when possible
- Match existing code style and naming in the scenario you are editing
- Do not commit `yellow-olive-lab/` or other local generated files
- Update documentation if you add challenges, change architecture, or move files

## Questions

Open a [GitHub issue](https://github.com/Anubhav9/Yellow-Olive/issues) or start a discussion if you are unsure about scope before coding.

## License

By contributing, you agree that your contributions will be licensed under the same [MIT License](LICENSE) as the project.
