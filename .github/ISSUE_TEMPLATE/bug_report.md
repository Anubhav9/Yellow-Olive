---
name: Bug report
about: Create a report to help us improve
title: ''
labels: ''
assignees: ''

---

name: Bug report
description: Report something broken in the game, docs, or install flow
title: "[Bug]: "
labels:
  - bug
body:
  - type: markdown
    attributes:
      value: |
        Thanks for taking the time to report a bug.

        **Security issues:** Do not use this form. See [SECURITY.md](https://github.com/Anubhav9/Yellow-Olive/blob/main/SECURITY.md) and report via a [private security advisory](https://github.com/Anubhav9/Yellow-Olive/security/advisories/new).

        **Docs site:** https://anubhav9.github.io/Yellow-Olive/

  - type: checkboxes
    id: checks
    attributes:
      label: Before you submit
      options:
        - label: I searched [existing issues](https://github.com/Anubhav9/Yellow-Olive/issues) and did not find a duplicate
          required: true
        - label: This is not a security vulnerability (see SECURITY.md if it is)
          required: true

  - type: textarea
    id: description
    attributes:
      label: What happened?
      description: A clear description of the bug
      placeholder: PsyQuack validation fails even though the pod is Ready in kubectl...
    validations:
      required: true

  - type: textarea
    id: expected
    attributes:
      label: What did you expect to happen?
    validations:
      required: true

  - type: textarea
    id: reproduction
    attributes:
      label: Steps to reproduce
      description: Numbered steps help us replay the issue
      placeholder: |
        1. Run `yellow-olive start`
        2. Start a new game and reach Challenge 3
        3. Fix the pod in the Command Chamber
        4. Type `psyquack validate`
        5. See error message: ...
      value: |
        1.
        2.
        3.
    validations:
      required: true

  - type: dropdown
    id: area
    attributes:
      label: Where did this happen?
      options:
        - Game startup / main menu
        - Prologue / story screens
        - Challenge gameplay
        - PsyQuack validation
        - Minikube / cluster bootstrap
        - Lab workspace (`yellow-olive-lab/`)
        - Save / resume progress
        - PyPI install
        - Source install / development
        - Documentation / GitHub Pages
        - Other
    validations:
      required: true

  - type: input
    id: challenge
    attributes:
      label: Challenge ID (if applicable)
      description: Leave blank if not challenge-related
      placeholder: "e.g. 3, or Oakwood Meadows / Signal Town"

  - type: dropdown
    id: install_method
    attributes:
      label: How did you install Yellow Olive?
      options:
        - PyPI (`pip install yellow-olive`)
        - Source (`git clone` + `python app.py`)
        - Not sure
    validations:
      required: true

  - type: input
    id: version
    attributes:
      label: Yellow Olive version
      description: PyPI version or git commit/branch if running from source
      placeholder: "e.g. 0.4.0 or main @ abc1234"
    validations:
      required: true

  - type: dropdown
    id: os
    attributes:
      label: Operating system
      options:
        - macOS
        - Linux
        - Windows (WSL)
        - Windows (native)
        - Other
    validations:
      required: true

  - type: input
    id: python
    attributes:
      label: Python version
      placeholder: "e.g. 3.12.2"
    validations:
      required: true

  - type: textarea
    id: environment
    attributes:
      label: Environment details (optional)
      description: Output of version commands helps for cluster-related bugs
      placeholder: |
        docker --version
        minikube version
        kubectl version --client
      render: shell

  - type: textarea
    id: logs
    attributes:
      label: Error output / logs (optional)
      description: Terminal output, in-game message, or kubectl describe snippets
      render: shell

  - type: textarea
    id: extra
    attributes:
      label: Anything else?
      description: Screenshots, screen recordings, or other context

  - type: checkboxes
    id: contribution
    attributes:
      label: Contribution
      options:
        - label: I am willing to open a pull request if given guidance
          required: false
