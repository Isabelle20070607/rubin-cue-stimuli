from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

COLOR_NAMES = ("black", "gray", "white")


@dataclass(frozen=True)
class Config:
    path: Path
    seed: int
    canvas_size: int
    shadow_min_abs_component: float
    shadow_max_radius: float
    palette_values: dict[str, int]
    material_value_ranges: dict[str, tuple[int, int]]


def load_config(path: str | Path) -> Config:
    config_path = Path(path).expanduser().resolve()
    with config_path.open("rb") as stream:
        data = tomllib.load(stream)
    project = data["project"]
    render = data["render"]
    palette = render["palette"]
    ranges = render["material_value_ranges"]
    config = Config(
        path=config_path,
        seed=int(project["seed"]),
        canvas_size=int(project["canvas_size"]),
        shadow_min_abs_component=float(render["shadow_min_abs_component"]),
        shadow_max_radius=float(render["shadow_max_radius"]),
        palette_values={color: int(palette[color]) for color in COLOR_NAMES},
        material_value_ranges={
            color: (int(ranges[color][0]), int(ranges[color][1]))
            for color in COLOR_NAMES
        },
    )
    if config.canvas_size < 64:
        raise ValueError("project.canvas_size must be at least 64")
    if not 0.0 < config.shadow_min_abs_component < 0.5:
        raise ValueError("render.shadow_min_abs_component must be between 0 and 0.5")
    if config.shadow_max_radius <= (2.0**0.5) * config.shadow_min_abs_component:
        raise ValueError(
            "render.shadow_max_radius must exceed the minimum two-component radius"
        )
    if any(not 0 <= value <= 255 for value in config.palette_values.values()):
        raise ValueError("render.palette values must be between 0 and 255")
    if not (
        config.palette_values["black"]
        < config.palette_values["gray"]
        < config.palette_values["white"]
    ):
        raise ValueError("render.palette values must increase from black to gray to white")
    for color, (low, high) in config.material_value_ranges.items():
        if not 0 <= low < high <= 255:
            raise ValueError(
                f"render.material_value_ranges.{color} must increase within 0-255"
            )
    return config
