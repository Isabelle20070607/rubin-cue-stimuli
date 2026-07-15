from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any


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
    if not 0.0 < config.shadow_min_abs_component < 0.5:
        raise ValueError("render.shadow_min_abs_component must be between 0 and 0.5")
    if config.shadow_max_radius <= (2.0**0.5) * config.shadow_min_abs_component:
        raise ValueError(
            "render.shadow_max_radius must exceed the minimum two-component radius"
        )
    return config
