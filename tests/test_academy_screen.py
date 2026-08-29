"""Academy menu entry opens the hosted Pyxel lesson."""

from __future__ import annotations

import importlib

import pytest

import global_constants
from app import ProjectOlive
from screens.common.academy_screen import AcademyScreen


@pytest.mark.asyncio
async def test_academy_button_mounts_screen_and_opens_browser(monkeypatch) -> None:
    opened: list[str] = []
    monkeypatch.setattr(
        "screens.common.academy_screen.webbrowser.open", lambda url: opened.append(url)
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
    monkeypatch.setattr("screens.common.academy_screen.webbrowser.open", lambda url: None)

    app = ProjectOlive()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.click("#academy")
        await pilot.pause()
        pilot.app.query_one("#academy-input").value = "psyquack back"
        await pilot.press("enter")
        await pilot.pause()
        assert not pilot.app.query(AcademyScreen)


def test_academy_url_can_be_overridden_by_env(monkeypatch) -> None:
    monkeypatch.setenv("YELLOW_OLIVE_ACADEMY_URL", "http://localhost:8000/")
    try:
        reloaded = importlib.reload(global_constants)
        assert reloaded.ACADEMY_URL == "http://localhost:8000/"
    finally:
        monkeypatch.delenv("YELLOW_OLIVE_ACADEMY_URL")
        importlib.reload(global_constants)

    assert global_constants.ACADEMY_URL == global_constants.ACADEMY_DEFAULT_URL
