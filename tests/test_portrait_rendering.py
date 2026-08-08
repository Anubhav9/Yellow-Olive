"""Tests for the terminal portrait renderer in utils.general_utils."""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

import global_constants
from utils import general_utils


PORTRAITS = sorted(Path(global_constants.IMAGE_MEDIA_PATH).glob("*.png"))


def _rows(rendered) -> list[str]:
    return [line for line in rendered.plain.split("\n") if line]


@pytest.mark.parametrize("portrait", PORTRAITS, ids=lambda p: p.stem)
def test_portrait_renders_at_target_size(portrait: Path) -> None:
    rows = _rows(general_utils.convert_to_ascii(str(portrait)))

    assert len(rows) == global_constants.PORTRAIT_TARGET_ROWS
    assert len({len(row) for row in rows}) == 1


def test_portrait_fits_the_narrowest_supported_terminal() -> None:
    """The game area is 70% of the terminal, less a border and 4 cells of padding."""
    rows = _rows(general_utils.convert_to_ascii(str(PORTRAITS[0])))
    narrowest_game_area = int(80 * 0.7) - 2 - 4

    assert len(rows[0]) <= narrowest_game_area


def test_portrait_uses_a_flat_palette() -> None:
    rendered = general_utils.convert_to_ascii(str(PORTRAITS[0]))
    half_blocks = {span.style for span in rendered.spans}

    assert len(half_blocks) <= global_constants.PORTRAIT_COLOR_COUNT**2


def test_target_rows_is_configurable(tmp_path: Path) -> None:
    source = tmp_path / "square.png"
    Image.new("RGB", (64, 64), (200, 40, 40)).save(source)

    assert len(_rows(general_utils.convert_to_ascii(str(source), target_rows=10))) == 10
