from dataclasses import replace
from pathlib import Path

from PIL import Image

from rubin_cues.bank import generate_bank
from rubin_cues.combinations import combination_specs
from rubin_cues.config import load_config

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_combination_space_has_30_non_conflicting_conditions() -> None:
    specs = combination_specs()

    assert len(specs) == 30
    assert len({spec.compact_id for spec in specs}) == 30
    assert all(not (spec.face_cues and spec.vase_cues) for spec in specs)


def test_generator_writes_120_openable_images(tmp_path: Path) -> None:
    config = load_config(PROJECT_ROOT / "config.toml")
    small_config = replace(config, canvas_size=64)

    result = generate_bank(small_config, tmp_path / "images")
    images = sorted((tmp_path / "images").glob("*.png"))

    assert result["source_count"] == 4
    assert result["image_count"] == 120
    assert len(images) == 120
    for path in images:
        with Image.open(path) as image:
            image.load()
            assert image.mode == "L"
            assert image.size == (64, 64)
