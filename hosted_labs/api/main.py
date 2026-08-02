import asyncio
import secrets
import sys
from contextlib import suppress
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

HOSTED_LABS_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = HOSTED_LABS_ROOT.parent
load_dotenv(HOSTED_LABS_ROOT / ".env")

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from hosted_labs.core import audit  # noqa: E402
from hosted_labs.core.auth_config import get_session_secret  # noqa: E402
from hosted_labs.core.challenge_config import load_challenge_session_config  # noqa: E402
from hosted_labs.core import completions  # noqa: E402
from hosted_labs.core.cleanup import teardown_lab_session  # noqa: E402
from hosted_labs.core.github_oauth import configure_github_oauth, new_oauth_state, oauth  # noqa: E402
from hosted_labs.core.lab_slots import lab_slot_manager  # noqa: E402
from hosted_labs.core.session import (  # noqa: E402
    bootstrap_challenge_session,
    get_challenge_dir,
    list_challenge_slugs,
    load_challenge_text,
    validate_challenge_session,
)
from hosted_labs.core.session_runtime import (  # noqa: E402
    session_runtime_manager,
    session_timeout_sweep_loop,
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
_timeout_sweep_task: asyncio.Task | None = None


@app.on_event("startup")
async def startup() -> None:
    global _timeout_sweep_task
    configure_github_oauth()
    _timeout_sweep_task = asyncio.create_task(session_timeout_sweep_loop())


@app.on_event("shutdown")
async def shutdown() -> None:
    global _timeout_sweep_task
    if _timeout_sweep_task is not None:
        _timeout_sweep_task.cancel()
        with suppress(asyncio.CancelledError):
            await _timeout_sweep_task
        _timeout_sweep_task = None


def _get_lab_user(request: Request) -> dict | None:
    lab_user = request.session.get("lab_user")
    if not lab_user or not lab_user.get("lab_granted"):
        return None
    if session_runtime_manager.is_terminated(lab_user["lab_session_id"]):
        request.session.clear()
        return None
    return lab_user


def _finalize_lab_session(lab_user: dict, *, reason: str, challenge_failed: bool | None = None) -> None:
    teardown_lab_session(
        lab_user,
        reason=reason,
        challenge_failed=challenge_failed,
    )
    session_runtime_manager.clear_runtime(lab_user["lab_session_id"])
    session_runtime_manager.mark_terminated(lab_user["lab_session_id"])


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
    finish_message: str | None = None,
):
    session_status = session_runtime_manager.build_status(lab_user["lab_session_id"])
    challenge_config = load_challenge_session_config(challenge_slug)
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
        "finish_message": finish_message,
        "session_status": session_status,
        "challenge_config": challenge_config,
    }


def _record_session_activity(
    lab_user: dict,
    *,
    level: str,
    category: str,
    event: str,
    **fields,
) -> None:
    audit.record_activity(
        lab_session_id=lab_user["lab_session_id"],
        session_started_at=lab_user["session_started_at"],
        level=level,
        category=category,
        event=event,
        **fields,
    )


def _record_terminal_activity(lab_user: dict, challenge_slug: str, result) -> None:
    for violation in result.policy_violations:
        _record_session_activity(
            lab_user,
            level="WARN",
            category="policy_violation",
            event=str(violation.get("type", "policy_violation")),
            challenge_slug=challenge_slug,
            command_raw=result.command_raw,
            violation=violation,
        )

    if not result.command_raw.strip():
        return

    if result.blocked and not result.command_executed:
        _record_session_activity(
            lab_user,
            level="WARN",
            category="terminal",
            event="kubectl_blocked",
            challenge_slug=challenge_slug,
            command_raw=result.command_raw,
            block_reason=result.block_reason,
        )
        return

    _record_session_activity(
        lab_user,
        level="INFO",
        category="terminal",
        event="kubectl_executed",
        challenge_slug=challenge_slug,
        command_raw=result.command_raw,
        command_executed=result.command_executed,
        exit_code=result.exit_code,
        policy_violation=bool(result.policy_violations),
    )


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
    client_ip = audit.client_ip_from_request(request)
    user_agent = request.headers.get("user-agent")

    try:
        token = await oauth.github.authorize_access_token(request)
    except Exception as exc:
        audit.record_incident(
            incident_id=f"incident-login-failed-{secrets.token_hex(4)}",
            meta={"client_ip": client_ip, "user_agent": user_agent},
            level="WARN",
            category="auth",
            event="login_failed",
            detail=str(exc),
        )
        raise HTTPException(status_code=400, detail=f"GitHub OAuth failed: {exc}") from exc

    user_response = await oauth.github.get("user", token=token)
    profile = user_response.json()
    github_user_id = int(profile["id"])
    github_login = profile["login"]
    lab_session_id = f"yo-sess-{secrets.token_hex(4)}"

    granted, seat = lab_slot_manager.claim(github_user_id, github_login, lab_session_id)
    if not granted or seat is None:
        audit.record_incident(
            incident_id=f"incident-labs-full-{secrets.token_hex(4)}",
            meta={
                "client_ip": client_ip,
                "user_agent": user_agent,
                "github_login": github_login,
                "github_user_id": github_user_id,
            },
            level="WARN",
            category="auth",
            event="seat_denied_labs_full",
            seats_used=lab_slot_manager.active_count(),
            seats_max=lab_slot_manager.max_slots(),
        )
        return RedirectResponse(url="/labs-full", status_code=302)

    is_new_session = seat.lab_session_id == lab_session_id
    if is_new_session:
        audit.start_session(
            lab_session_id=seat.lab_session_id,
            github_login=github_login,
            github_user_id=github_user_id,
            namespace=seat.namespace,
            client_ip=client_ip,
            user_agent=user_agent,
            started_at=seat.claimed_at,
        )
        _record_session_activity(
            {
                "lab_session_id": seat.lab_session_id,
                "session_started_at": seat.claimed_at,
            },
            level="INFO",
            category="auth",
            event="login_succeeded",
            client_ip=client_ip,
        )
    else:
        _record_session_activity(
            {
                "lab_session_id": seat.lab_session_id,
                "session_started_at": seat.claimed_at,
            },
            level="INFO",
            category="auth",
            event="login_resumed_existing_seat",
            client_ip=client_ip,
        )

    request.session["lab_user"] = {
        "github_user_id": github_user_id,
        "github_login": github_login,
        "namespace": seat.namespace,
        "lab_session_id": seat.lab_session_id,
        "session_started_at": seat.claimed_at,
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
        _finalize_lab_session(lab_user, reason="logout")
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

    _record_session_activity(
        lab_user,
        level="INFO",
        category="session",
        event="bootstrap_called",
        challenge_slug=challenge_slug,
    )
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
        _record_session_activity(
            lab_user,
            level="INFO",
            category="session",
            event="bootstrap_succeeded",
            challenge_slug=challenge_slug,
            apply_messages=result["apply_messages"],
        )
        challenge_config = load_challenge_session_config(challenge_slug)
        session_runtime_manager.start_challenge(lab_user, challenge_slug, challenge_config)
        _record_session_activity(
            lab_user,
            level="INFO",
            category="session",
            event="challenge_timer_started",
            challenge_slug=challenge_slug,
            time_limit_minutes=challenge_config.time_limit_minutes,
            idle_timeout_minutes=challenge_config.idle_timeout_minutes,
        )
    except (FileNotFoundError, AttributeError, RuntimeError) as exc:
        _record_session_activity(
            lab_user,
            level="ERROR",
            category="session",
            event="bootstrap_failed",
            challenge_slug=challenge_slug,
            detail=str(exc),
        )
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

    _record_session_activity(
        lab_user,
        level="INFO",
        category="session",
        event="validation_attempted",
        challenge_slug=challenge_slug,
    )
    session_runtime_manager.bump_activity(lab_user["lab_session_id"])
    try:
        result = validate_challenge_session(
            challenge_slug=challenge_slug,
            formatted_github_user_id=lab_user["namespace"],
        )
    except (FileNotFoundError, ValueError) as exc:
        _record_session_activity(
            lab_user,
            level="WARN",
            category="session",
            event="validation_error",
            challenge_slug=challenge_slug,
            detail=str(exc),
        )
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    _record_session_activity(
        lab_user,
        level="INFO" if result["passed"] else "WARN",
        category="session",
        event="validation_passed" if result["passed"] else "validation_failed",
        challenge_slug=challenge_slug,
        message=result["message"],
    )
    if result["passed"]:
        session_runtime_manager.mark_challenge_passed(lab_user["lab_session_id"])
        runtime = session_runtime_manager.get_runtime(lab_user["lab_session_id"])
        if runtime is not None:
            completions.record_completion(
                github_login=lab_user["github_login"],
                github_user_id=int(lab_user["github_user_id"]),
                challenge_slug=challenge_slug,
                lab_session_id=lab_user["lab_session_id"],
                challenge_started_at=runtime.challenge_started_at,
            )

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


@app.post("/challenges/{challenge_slug}/finish")
def finish_challenge(request: Request, challenge_slug: str):
    lab_user = _require_lab_user(request)
    if isinstance(lab_user, RedirectResponse):
        return lab_user

    runtime = session_runtime_manager.get_runtime(lab_user["lab_session_id"])
    if runtime is None or runtime.challenge_slug != challenge_slug:
        raise HTTPException(status_code=400, detail="Start the challenge session before finishing.")
    if not runtime.challenge_passed:
        raise HTTPException(status_code=400, detail="Complete the challenge before finishing the session.")

    _finalize_lab_session(lab_user, reason="challenge_completed")
    request.session.clear()
    return RedirectResponse(url="/login?ended=challenge_completed", status_code=302)


@app.get("/challenges/{challenge_slug}/session-status")
def challenge_session_status(request: Request, challenge_slug: str):
    lab_user = _require_lab_user(request)
    if isinstance(lab_user, RedirectResponse):
        return lab_user

    status = session_runtime_manager.build_status(lab_user["lab_session_id"])
    if status is None or status["challenge_slug"] != challenge_slug:
        return JSONResponse(
            {
                "challenge_started": False,
                "challenge_slug": challenge_slug,
            }
        )
    return JSONResponse(status)


@app.websocket("/challenges/{challenge_slug}/terminal/ws")
async def challenge_terminal(websocket: WebSocket, challenge_slug: str):
    try:
        get_challenge_dir(challenge_slug)
    except FileNotFoundError:
        audit.record_incident(
            incident_id=f"incident-terminal-404-{secrets.token_hex(4)}",
            meta={"challenge_slug": challenge_slug},
            level="WARN",
            category="terminal",
            event="terminal_rejected_unknown_challenge",
            challenge_slug=challenge_slug,
        )
        await websocket.close(code=4404)
        return

    session = websocket.scope.get("session")
    lab_user = session.get("lab_user") if session else None
    if not lab_user or not lab_user.get("lab_granted"):
        audit.record_incident(
            incident_id=f"incident-terminal-401-{secrets.token_hex(4)}",
            meta={"challenge_slug": challenge_slug},
            level="WARN",
            category="terminal",
            event="terminal_rejected_unauthenticated",
            challenge_slug=challenge_slug,
        )
        await websocket.close(code=4401)
        return

    await websocket.accept()
    namespace = lab_user["namespace"]
    prompt = f"{namespace}> "
    lab_session_id = lab_user["lab_session_id"]

    session_runtime_manager.register_websocket(lab_session_id, websocket)

    _record_session_activity(
        lab_user,
        level="INFO",
        category="terminal",
        event="terminal_connected",
        challenge_slug=challenge_slug,
    )

    await websocket.send_json(
        {
            "type": "welcome",
            "text": welcome_message(namespace),
            "prompt": prompt,
        }
    )
    status = session_runtime_manager.build_status(lab_session_id)
    if status is not None:
        await websocket.send_json({"type": "status", **status})

    try:
        while True:
            message = await websocket.receive_json()
            message_type = message.get("type")

            if message_type == "ping":
                session_runtime_manager.bump_activity(lab_session_id)
                status = session_runtime_manager.build_status(lab_session_id)
                if status is not None:
                    await websocket.send_json({"type": "status", **status})
                continue

            if message_type != "command":
                continue

            if session_runtime_manager.is_terminated(lab_session_id):
                break

            command_line = message.get("text", "")
            await websocket.send_json({"type": "prompt", "text": f"{prompt}{command_line}\r\n"})

            session_runtime_manager.bump_activity(lab_session_id)
            result = execute_terminal_line(command_line, namespace, namespace)
            _record_terminal_activity(lab_user, challenge_slug, result)
            if result.output:
                await websocket.send_json({"type": "output", "text": result.output})

            await websocket.send_json({"type": "prompt", "text": prompt})
            status = session_runtime_manager.build_status(lab_session_id)
            if status is not None:
                await websocket.send_json({"type": "status", **status})
    except WebSocketDisconnect:
        _record_session_activity(
            lab_user,
            level="INFO",
            category="terminal",
            event="terminal_disconnected",
            challenge_slug=challenge_slug,
        )
    finally:
        session_runtime_manager.unregister_websocket(lab_session_id)
        return
