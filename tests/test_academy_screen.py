"""Academy menu entry opens the hosted Pyxel lesson."""

from __future__ import annotations

import importlib
import subprocess
import sys

import pytest

import global_constants
from app import ProjectOlive
from screens.common import academy_screen
from screens.common.academy_screen import AcademyScreen


@pytest.mark.asyncio
async def test_academy_button_mounts_screen_and_opens_browser(monkeypatch) -> None:
    opened: list[str] = []
    monkeypatch.setattr(
        "screens.common.academy_screen.webbrowser.open",
        lambda url: bool(opened.append(url)) or True,
    )

    app = ProjectOlive()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.click("#academy")
        await pilot.pause()
        academy = pilot.app.query_one(AcademyScreen)
        await academy.workers.wait_for_complete()

    assert opened == [global_constants.ACADEMY_URL]


@pytest.mark.asyncio
async def test_psyquack_back_removes_academy_screen(monkeypatch) -> None:
    monkeypatch.setattr("screens.common.academy_screen.webbrowser.open", lambda url: True)

    app = ProjectOlive()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.click("#academy")
        await pilot.pause()
        pilot.app.query_one("#academy-input").value = "psyquack back"
        await pilot.press("enter")
        await pilot.pause()
        assert not pilot.app.query(AcademyScreen)


def test_open_url_falls_back_to_platform_opener(monkeypatch) -> None:
    monkeypatch.setattr("screens.common.academy_screen.webbrowser.open", lambda url: False)
    monkeypatch.setattr("screens.common.academy_screen.shutil.which", lambda name: f"/usr/bin/{name}")
    calls: list[list[str]] = []

    def fake_run(command, **kwargs):
        calls.append(command)
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr("screens.common.academy_screen.subprocess.run", fake_run)

    assert academy_screen.open_url("http://localhost:8000/") is True
    assert calls == [["open" if sys.platform == "darwin" else "xdg-open", "http://localhost:8000/"]]


def test_academy_url_can_be_overridden_by_env(monkeypatch) -> None:
    monkeypatch.setenv("YELLOW_OLIVE_ACADEMY_URL", "http://localhost:8000/")
    try:
        reloaded = importlib.reload(global_constants)
        assert reloaded.ACADEMY_URL == "http://localhost:8000/"
    finally:
        monkeypatch.delenv("YELLOW_OLIVE_ACADEMY_URL")
        importlib.reload(global_constants)

    assert global_constants.ACADEMY_URL == global_constants.ACADEMY_DEFAULT_URL
