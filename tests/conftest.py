from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from rubin_cues.config import Config, load_config


@pytest.fixture
def config() -> Config:
    return load_config(Path(__file__).parents[1] / "configs" / "v1.toml")


@pytest.fixture
def small_config(config: Config) -> Config:
    return replace(
        config,
        project={
            **config.project,
            "version": "test",
            "base_count": 2,
            "canvas_size": 192,
            "supersample": 1,
        },
    )
