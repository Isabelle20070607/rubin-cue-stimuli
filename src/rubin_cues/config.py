from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

COLOR_NAMES = ("black", "gray", "white")
DEFAULT_PALETTE_VALUES = {"black": 24, "gray": 133, "white": 232}
DEFAULT_MATERIAL_VALUE_RANGES = {
    "black": (18, 92),
    "gray": (52, 220),
    "white": (132, 244),
}


@dataclass(frozen=True)
class Config:
    path: Path
    project: dict[str, Any]
    geometry: dict[str, Any]
    render: dict[str, Any]
    quality: dict[str, Any]
    experiment: dict[str, Any]
    selection: dict[str, Any]

    @property
    def version(self) -> str:
        return str(self.project["version"])

    @property
    def design_profile(self) -> str:
        return str(self.project.get("design_profile", "v1"))

    @property
    def seed(self) -> int:
        return int(self.project["seed"])

    @property
    def base_count(self) -> int:
        return int(self.project["base_count"])

    @property
    def canvas_size(self) -> int:
        return int(self.project["canvas_size"])

    @property
    def supersample(self) -> int:
        return int(self.project["supersample"])

    @property
    def shadow_min_abs_component(self) -> float:
        return float(self.render["shadow_min_abs_component"])

    @property
    def shadow_max_radius(self) -> float:
        return float(self.render["shadow_max_radius"])

    @property
    def palette_values(self) -> dict[str, int]:
        values = self.render.get("palette", DEFAULT_PALETTE_VALUES)
        return {color: int(values[color]) for color in COLOR_NAMES}

    @property
    def material_value_ranges(self) -> dict[str, tuple[int, int]]:
        ranges = self.render.get("material_value_ranges", DEFAULT_MATERIAL_VALUE_RANGES)
        return {
            color: (int(ranges[color][0]), int(ranges[color][1]))
            for color in COLOR_NAMES
        }

    @property
    def material_shape_rendering(self) -> str:
        return str(self.render.get("material_shape_rendering", "auto"))


def load_config(path: str | Path) -> Config:
    config_path = Path(path).expanduser().resolve()
    with config_path.open("rb") as stream:
        data = tomllib.load(stream)
    required = ("project", "geometry", "render", "quality", "experiment", "selection")
    missing = [section for section in required if section not in data]
    if missing:
        raise ValueError(f"Missing config sections: {', '.join(missing)}")
    config = Config(path=config_path, **{name: data[name] for name in required})
    if config.base_count < 1:
        raise ValueError("project.base_count must be positive")
    if config.canvas_size < 64:
        raise ValueError("project.canvas_size must be at least 64")
    if config.supersample < 1:
        raise ValueError("project.supersample must be positive")
    if config.design_profile not in ("v1", "v2"):
        raise ValueError("project.design_profile must be 'v1' or 'v2'")
    if not 0.0 < config.shadow_min_abs_component < 0.5:
        raise ValueError("render.shadow_min_abs_component must be between 0 and 0.5")
    if config.shadow_max_radius <= (2.0**0.5) * config.shadow_min_abs_component:
        raise ValueError(
            "render.shadow_max_radius must exceed the minimum two-component radius"
        )
    if set(config.palette_values) != set(COLOR_NAMES):
        raise ValueError("render.palette must define black, gray, and white")
    if any(not 0 <= value <= 255 for value in config.palette_values.values()):
        raise ValueError("render.palette values must be between 0 and 255")
    if not (
        config.palette_values["black"]
        < config.palette_values["gray"]
        < config.palette_values["white"]
    ):
        raise ValueError("render.palette values must increase from black to gray to white")
    if set(config.material_value_ranges) != set(COLOR_NAMES):
        raise ValueError(
            "render.material_value_ranges must define black, gray, and white"
        )
    for color, (low, high) in config.material_value_ranges.items():
        if not 0 <= low < high <= 255:
            raise ValueError(
                f"render.material_value_ranges.{color} must increase within 0-255"
            )
    if config.material_shape_rendering not in ("auto", "crispEdges"):
        raise ValueError(
            "render.material_shape_rendering must be 'auto' or 'crispEdges'"
        )
    return config
