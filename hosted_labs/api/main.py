import secrets
import sys
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Form, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

HOSTED_LABS_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = HOSTED_LABS_ROOT.parent
load_dotenv(HOSTED_LABS_ROOT / ".env")

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from hosted_labs.core.auth_config import get_session_secret  # noqa: E402
from hosted_labs.core.github_oauth import configure_github_oauth, new_oauth_state, oauth  # noqa: E402
from hosted_labs.core.lab_slots import lab_slot_manager  # noqa: E402
from hosted_labs.core.session import (  # noqa: E402
    bootstrap_challenge_session,
    get_challenge_dir,
    list_challenge_slugs,
    load_challenge_text,
    validate_challenge_session,
)
from hosted_labs.core.terminal import execute_terminal_line, welcome_message  # noqa: E402

API_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(API_DIR / "templates"))

app = FastAPI(
    title="Yellow Olive Hosted Labs",
    description="Public Kubernetes challenges (POC — not part of the PyPI game package).",
)

app.add_middleware(SessionMiddleware, secret_key=get_session_secret(), https_only=False)
app.mount("/static", StaticFiles(directory=str(API_DIR / "static")), name="static")


@app.on_event("startup")
async def startup() -> None:
    configure_github_oauth()


def _get_lab_user(request: Request) -> dict | None:
    lab_user = request.session.get("lab_user")
    if not lab_user or not lab_user.get("lab_granted"):
        return None
    return lab_user


def _require_lab_user(request: Request) -> dict | RedirectResponse:
    lab_user = _get_lab_user(request)
    if lab_user is None:
        return RedirectResponse(url="/login", status_code=302)
    return lab_user


def _challenge_context(
    request: Request,
    challenge_slug: str,
    lab_user: dict,
    *,
    bootstrap_message: str | None = None,
    validation_message: str | None = None,
    validation_passed: bool | None = None,
):
    return {
        "request": request,
        "challenge_slug": challenge_slug,
        "challenge_title": challenge_slug.replace("_", " ").title(),
        "challenge_text": load_challenge_text(challenge_slug),
        "namespace": lab_user["namespace"],
        "lab_session_id": lab_user["lab_session_id"],
        "github_login": lab_user["github_login"],
        "bootstrap_message": bootstrap_message,
        "validation_message": validation_message,
        "validation_passed": validation_passed,
    }


@app.get("/")
def index(request: Request):
    if _get_lab_user(request) is None:
        return RedirectResponse(url="/login", status_code=302)

    challenges = list_challenge_slugs()
    if not challenges:
        raise HTTPException(status_code=404, detail="No challenges found")
    return RedirectResponse(url=f"/challenges/{challenges[0]}", status_code=302)


@app.get("/login")
def login_page(request: Request):
    if _get_lab_user(request) is not None:
        return RedirectResponse(url="/", status_code=302)

    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/labs-full")
def labs_full_page(request: Request):
    return templates.TemplateResponse(
        "labs_full.html",
        {
            "request": request,
            "seats_used": lab_slot_manager.active_count(),
            "seats_max": lab_slot_manager.max_slots(),
        },
    )


@app.get("/auth/github")
async def auth_github(request: Request):
    redirect_uri = request.url_for("auth_github_callback")
    state = new_oauth_state()
    request.session["oauth_state"] = state
    return await oauth.github.authorize_redirect(request, redirect_uri, state=state)


@app.get("/auth/github/callback", name="auth_github_callback")
async def auth_github_callback(request: Request):
    try:
        token = await oauth.github.authorize_access_token(request)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"GitHub OAuth failed: {exc}") from exc

    user_response = await oauth.github.get("user", token=token)
    profile = user_response.json()
    github_user_id = int(profile["id"])
    github_login = profile["login"]
    lab_session_id = f"yo-sess-{secrets.token_hex(4)}"

    granted, seat = lab_slot_manager.claim(github_user_id, github_login, lab_session_id)
    if not granted or seat is None:
        return RedirectResponse(url="/labs-full", status_code=302)

    request.session["lab_user"] = {
        "github_user_id": github_user_id,
        "github_login": github_login,
        "namespace": seat.namespace,
        "lab_session_id": seat.lab_session_id,
        "lab_granted": True,
    }

    challenges = list_challenge_slugs()
    if not challenges:
        raise HTTPException(status_code=404, detail="No challenges found")
    return RedirectResponse(url=f"/challenges/{challenges[0]}", status_code=302)


@app.get("/logout")
def logout(request: Request):
    lab_user = request.session.get("lab_user")
    if lab_user:
        lab_slot_manager.release(int(lab_user["github_user_id"]))
    request.session.clear()
    return RedirectResponse(url="/login", status_code=302)


@app.get("/challenges")
def challenge_list(request: Request):
    lab_user = _require_lab_user(request)
    if isinstance(lab_user, RedirectResponse):
        return lab_user
    challenges = [
        {
            "slug": slug,
            "title": slug.replace("_", " ").title(),
        }
        for slug in list_challenge_slugs()
    ]
    return templates.TemplateResponse(
        "challenge_list.html",
        {
            "request": request,
            "challenges": challenges,
            "github_login": lab_user["github_login"],
        },
    )


@app.get("/challenges/{challenge_slug}")
def challenge_page(request: Request, challenge_slug: str):
    lab_user = _require_lab_user(request)
    if isinstance(lab_user, RedirectResponse):
        return lab_user
    try:
        get_challenge_dir(challenge_slug)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return templates.TemplateResponse(
        "challenge.html",
        _challenge_context(request, challenge_slug, lab_user),
    )


@app.post("/challenges/{challenge_slug}/bootstrap")
def bootstrap_challenge(request: Request, challenge_slug: str):
    lab_user = _require_lab_user(request)
    if isinstance(lab_user, RedirectResponse):
        return lab_user
    try:
        result = bootstrap_challenge_session(
            challenge_slug=challenge_slug,
            formatted_github_user_id=lab_user["namespace"],
            session_id=lab_user["lab_session_id"],
        )
        bootstrap_message = "; ".join(
            f"{message['name']}: {message['message']}"
            for message in result["apply_messages"]
        )
    except (FileNotFoundError, AttributeError, RuntimeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return templates.TemplateResponse(
        "challenge.html",
        _challenge_context(
            request,
            challenge_slug,
            lab_user,
            bootstrap_message=bootstrap_message or "Session bootstrap completed.",
        ),
    )


@app.post("/challenges/{challenge_slug}/validate")
def validate_challenge(request: Request, challenge_slug: str):
    lab_user = _require_lab_user(request)
    if isinstance(lab_user, RedirectResponse):
        return lab_user
    try:
        result = validate_challenge_session(
            challenge_slug=challenge_slug,
            formatted_github_user_id=lab_user["namespace"],
        )
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return templates.TemplateResponse(
        "challenge.html",
        _challenge_context(
            request,
            challenge_slug,
            lab_user,
            validation_message=result["message"],
            validation_passed=result["passed"],
        ),
    )


@app.websocket("/challenges/{challenge_slug}/terminal/ws")
async def challenge_terminal(websocket: WebSocket, challenge_slug: str):
    try:
        get_challenge_dir(challenge_slug)
    except FileNotFoundError:
        await websocket.close(code=4404)
        return

    session = websocket.scope.get("session")
    lab_user = session.get("lab_user") if session else None
    if not lab_user or not lab_user.get("lab_granted"):
        await websocket.close(code=4401)
        return

    await websocket.accept()
    namespace = lab_user["namespace"]
    prompt = f"{namespace}> "

    await websocket.send_json(
        {
            "type": "welcome",
            "text": welcome_message(namespace),
            "prompt": prompt,
        }
    )

    try:
        while True:
            message = await websocket.receive_json()
            if message.get("type") != "command":
                continue

            command_line = message.get("text", "")
            await websocket.send_json({"type": "prompt", "text": f"{prompt}{command_line}\r\n"})

            output = execute_terminal_line(command_line, namespace, namespace)
            if output:
                await websocket.send_json({"type": "output", "text": output})

            await websocket.send_json({"type": "prompt", "text": prompt})
    except WebSocketDisconnect:
        return
