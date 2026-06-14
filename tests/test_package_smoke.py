"""Smoke tests against an installed yellow-olive wheel (CI installs dist/*.whl first)."""

from __future__ import annotations

import pytest

from app import ProjectOlive


@pytest.mark.asyncio
async def test_main_menu_mounts() -> None:
    app = ProjectOlive()
    async with app.run_test(size=(80, 24)) as pilot:
        await pilot.pause()
        assert pilot.app.query_one("#start-game")
        assert pilot.app.query_one("#help")
        assert pilot.app.query_one("#default-text")
        assert "Professor Bald" in pilot.app.title
