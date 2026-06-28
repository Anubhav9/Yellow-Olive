import os
import re
import secrets


def get_github_client_id() -> str:
    client_id = os.getenv("GITHUB_CLIENT_ID", "").strip()
    if not client_id:
        raise RuntimeError("GITHUB_CLIENT_ID is not set")
    return client_id


def get_github_client_secret() -> str:
    client_secret = os.getenv("GITHUB_CLIENT_SECRET", "").strip()
    if not client_secret:
        raise RuntimeError("GITHUB_CLIENT_SECRET is not set")
    return client_secret


def get_session_secret() -> str:
    return os.getenv("SESSION_SECRET", "").strip() or secrets.token_urlsafe(32)


def get_max_lab_slots() -> int:
    raw_value = os.getenv("HOSTED_LABS_MAX_SLOTS", "7").strip()
    return max(1, int(raw_value))


def format_github_namespace(github_login: str, github_user_id: int) -> str:
    """Build a DNS-safe namespace from GitHub username + numeric user id."""
    login = github_login.lower()
    login = re.sub(r"[^a-z0-9-]", "-", login)
    login = re.sub(r"-+", "-", login).strip("-") or "user"
    namespace = f"{login}-{github_user_id}"
    return namespace[:63].rstrip("-")
