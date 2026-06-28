import secrets

from authlib.integrations.starlette_client import OAuth

from hosted_labs.core.auth_config import get_github_client_id, get_github_client_secret

oauth = OAuth()
_oauth_configured = False


def configure_github_oauth() -> None:
    global _oauth_configured
    if _oauth_configured:
        return

    oauth.register(
        name="github",
        client_id=get_github_client_id(),
        client_secret=get_github_client_secret(),
        access_token_url="https://github.com/login/oauth/access_token",
        authorize_url="https://github.com/login/oauth/authorize",
        api_base_url="https://api.github.com/",
        client_kwargs={"scope": "read:user user:email"},
    )
    _oauth_configured = True


def new_oauth_state() -> str:
    return secrets.token_urlsafe(24)
