from __future__ import annotations

import csv
import os
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from rubin_cues.experiment import load_display_config, milliseconds_to_frames


def read_schedule(path: str | Path) -> list[dict[str, str]]:
    with Path(path).expanduser().resolve().open(
        "r", encoding="utf-8-sig", newline=""
    ) as stream:
        return list(csv.DictReader(stream))


def prepare_display(path: str | Path, production: bool) -> dict[str, Any]:
    display = load_display_config(path, production=production)
    if production and not bool(display.get("fullscreen", True)):
        raise ValueError("production runs require fullscreen = true")
    return display


def frames(milliseconds: str | int | float, refresh_hz: float) -> int:
    return milliseconds_to_frames(float(milliseconds), refresh_hz)


def append_row(path: str | Path, row: dict[str, Any], fields: Iterable[str]) -> None:
    output = Path(path).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    field_list = list(fields)
    is_new = not output.exists() or output.stat().st_size == 0
    with output.open("a", encoding="utf-8-sig" if is_new else "utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=field_list, extrasaction="ignore")
        if is_new:
            writer.writeheader()
        writer.writerow(row)
        stream.flush()
        os.fsync(stream.fileno())


def response_for_key(row: dict[str, str], key: str) -> str | None:
    for percept in ("face", "vase", "unsure"):
        if key == row[f"{percept}_key"]:
            return percept
    return None
