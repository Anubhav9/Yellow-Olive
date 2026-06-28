import sys
from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from hosted_labs.core.session import (  # noqa: E402
    POC_GITHUB_ID,
    POC_SESSION_ID,
    bootstrap_challenge_session,
    get_challenge_dir,
    list_challenge_slugs,
    load_challenge_text,
    validate_challenge_session,
)
from hosted_labs.core.terminal import (  # noqa: E402
    execute_terminal_line,
    welcome_message,
)

API_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(API_DIR / "templates"))

app = FastAPI(
    title="Yellow Olive Hosted Labs",
    description="Public Kubernetes challenges (POC — not part of the PyPI game package).",
)


def _challenge_context(
    request: Request,
    challenge_slug: str,
    *,
    bootstrap_message: str | None = None,
    validation_message: str | None = None,
    validation_passed: bool | None = None,
):
    challenge_text = load_challenge_text(challenge_slug)
    return {
        "request": request,
        "challenge_slug": challenge_slug,
        "challenge_title": challenge_slug.replace("_", " ").title(),
        "challenge_text": challenge_text,
        "poc_github_id": POC_GITHUB_ID,
        "poc_session_id": POC_SESSION_ID,
        "bootstrap_message": bootstrap_message,
        "validation_message": validation_message,
        "validation_passed": validation_passed,
    }


@app.get("/")
def index():
    challenges = list_challenge_slugs()
    if not challenges:
        raise HTTPException(status_code=404, detail="No challenges found")
    return RedirectResponse(url=f"/challenges/{challenges[0]}", status_code=302)


@app.get("/challenges")
def challenge_list(request: Request):
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
        },
    )


@app.get("/challenges/{challenge_slug}")
def challenge_page(request: Request, challenge_slug: str):
    try:
        get_challenge_dir(challenge_slug)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return templates.TemplateResponse(
        "challenge.html",
        _challenge_context(request, challenge_slug),
    )


@app.post("/challenges/{challenge_slug}/bootstrap")
def bootstrap_challenge(
    request: Request,
    challenge_slug: str,
    github_id: str = Form(default=POC_GITHUB_ID),
    session_id: str = Form(default=POC_SESSION_ID),
):
    try:
        result = bootstrap_challenge_session(
            challenge_slug=challenge_slug,
            formatted_github_user_id=github_id,
            session_id=session_id,
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
            bootstrap_message=bootstrap_message or "Session bootstrap completed.",
        ),
    )


@app.post("/challenges/{challenge_slug}/validate")
def validate_challenge(
    request: Request,
    challenge_slug: str,
    github_id: str = Form(default=POC_GITHUB_ID),
):
    try:
        result = validate_challenge_session(
            challenge_slug=challenge_slug,
            formatted_github_user_id=github_id,
        )
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return templates.TemplateResponse(
        "challenge.html",
        _challenge_context(
            request,
            challenge_slug,
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

    await websocket.accept()
    namespace = POC_GITHUB_ID
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
