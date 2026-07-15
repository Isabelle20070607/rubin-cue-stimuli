from __future__ import annotations

from pathlib import Path

import pytest

from rubin_cues.experiment import load_display_config, milliseconds_to_frames


def test_milliseconds_to_frames() -> None:
    assert milliseconds_to_frames(150, 60) == 9
    assert milliseconds_to_frames(200, 120) == 24
    assert milliseconds_to_frames(0, 60) == 0
    with pytest.raises(ValueError):
        milliseconds_to_frames(150, 0)


def test_placeholder_display_blocks_production() -> None:
    display = Path(__file__).parents[1] / "configs" / "display.example.toml"
    assert load_display_config(display, production=False)["placeholder"]
    with pytest.raises(ValueError, match="placeholder"):
        load_display_config(display, production=True)
