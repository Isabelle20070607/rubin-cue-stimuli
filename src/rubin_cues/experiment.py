from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any


def milliseconds_to_frames(milliseconds: float, refresh_hz: float) -> int:
    if milliseconds < 0:
        raise ValueError("milliseconds cannot be negative")
    if refresh_hz <= 0:
        raise ValueError("refresh_hz must be positive")
    return max(1 if milliseconds > 0 else 0, round(milliseconds * refresh_hz / 1000.0))


def load_display_config(path: str | Path, production: bool = False) -> dict[str, Any]:
    config_path = Path(path).expanduser().resolve()
    with config_path.open("rb") as stream:
        data = tomllib.load(stream)["display"]
    required = (
        "monitor_name",
        "width_cm",
        "distance_cm",
        "resolution_width_px",
        "resolution_height_px",
        "refresh_hz",
    )
    if production:
        invalid = bool(data.get("placeholder", True)) or any(
            not data.get(name) for name in required
        )
        if invalid:
            raise ValueError(
                "production display config still contains placeholders or zero-valued geometry"
            )
    return data
