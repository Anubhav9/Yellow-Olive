"""Diagnostics context helpers."""

from __future__ import annotations

from services.diagnostics import context


def test_get_app_version_resolves_from_project_metadata() -> None:
    assert context.get_app_version() not in {"", "unknown"}
