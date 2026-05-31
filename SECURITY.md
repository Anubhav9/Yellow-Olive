# Security Policy

## Overview

Project Yellow Olive is a **local terminal application**. It is not a hosted online service. It runs on your machine, starts a local Minikube cluster, and calls `kubectl` to apply Kubernetes manifests from your `yellow-olive-lab/` workspace.

Most security risk is therefore **local**: what the game can run on your computer and what it can change in your lab cluster.

## Supported versions

Security fixes are applied to:

| Version | Supported |
|---------|-----------|
| Latest release on [PyPI](https://pypi.org/project/yellow-olive/) | Yes |
| `main` branch | Yes |
| Older releases | No |

Install updates with:

```bash
pip install -U yellow-olive
```

## Reporting a vulnerability

**Please do not open public GitHub issues for security vulnerabilities.**

Instead, use one of these channels:

1. **Preferred:** [GitHub private security advisory](https://github.com/Anubhav9/Yellow-Olive/security/advisories/new) for this repository.
2. **Alternative:** Open a draft advisory via **Security → Advisories → Report a vulnerability** on the GitHub repo page.

Include as much detail as you can:

- Description of the issue and potential impact
- Steps to reproduce
- Affected version(s)
- Proof of concept if available
- Suggested fix (optional)

We aim to acknowledge reports within **7 days** and share a fix or mitigation plan as soon as practical.

## In scope

We treat the following as in scope for this project:

- Command injection or unsafe shell invocation in Yellow Olive code (for example via `subprocess`, `kubectl`, or bundled scripts)
- Path traversal or arbitrary file read/write outside the intended lab workspace
- Issues where untrusted input in the game or lab manifests leads to unintended local code execution
- Vulnerabilities in dependencies shipped with the official `yellow-olive` PyPI package
- Supply-chain concerns specific to the official GitHub repository or PyPI package name `yellow-olive`

## Out of scope

The following are generally **out of scope**:

- Bugs in **Minikube**, **Docker**, **kubectl**, or **Kubernetes** themselves - report those to the upstream projects
- Misconfiguration of your local Docker, Minikube, or cluster permissions
- Gameplay exploits that only skip or bypass challenge validation without security impact
- Issues that require running a **modified or unofficial** copy of the game from an untrusted source
- Denial of service against your local machine caused by normal Minikube resource usage during gameplay
- Social engineering or phishing using the project name

## Local runtime expectations

Yellow Olive intentionally:

- Runs `minikube` and `kubectl` as the user who started the game
- Applies YAML from `yellow-olive-lab/scenarios/.../k8s_resources/`
- Deletes the Minikube profile `project-yellow-olive` when you quit from the main menu

Only install Yellow Olive from trusted sources (official PyPI package or this repository). Treat lab manifest files like any local Kubernetes config - do not paste untrusted YAML into your lab workspace.

## Safe usage recommendations

- Run the game with a normal user account, not as root
- Use the dedicated Minikube profile (`project-yellow-olive`) rather than pointing the game at production clusters
- Keep Docker, Minikube, kubectl, and `yellow-olive` updated
- Do not commit secrets into challenge manifests or your lab workspace

## Disclosure

We prefer coordinated disclosure. After a fix is available, we will publish a security advisory and credit reporters who wish to be named.

## Questions

For non-security questions, use [GitHub Issues](https://github.com/Anubhav9/Yellow-Olive/issues). For security concerns, use the private advisory flow above.
