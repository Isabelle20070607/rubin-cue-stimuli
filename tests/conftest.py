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


@pytest.fixture
def v2_config() -> Config:
    return load_config(Path(__file__).parents[1] / "configs" / "v2.toml")


@pytest.fixture
def small_v2_config(v2_config: Config) -> Config:
    return replace(
        v2_config,
        project={
            **v2_config.project,
            "version": "test-v2",
            "base_count": 2,
            "canvas_size": 192,
            "supersample": 1,
        },
    )
