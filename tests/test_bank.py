from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import numpy as np
from PIL import Image

from rubin_cues.bank import generate_bank, load_manifest
from rubin_cues.montage import create_montages
from rubin_cues.source_geometry import source_bases
from rubin_cues.validate import validate_manifest


def test_small_bank_is_complete_valid_and_reproducible(small_config, tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    first_report = generate_bank(small_config, first)
    second_report = generate_bank(small_config, second)
    assert first_report["bank_kind"] == second_report["bank_kind"] == "factorial"
    assert first_report["stimulus_count"] == second_report["stimulus_count"] == 192
    assert first_report["mask_count"] == second_report["mask_count"] == 2
    assert first_report["tag_counts"] == {
        "face": 48,
        "ambiguous": 12,
        "vase": 60,
        "conflict": 72,
    }

    first_rows = load_manifest(first / "manifest.jsonl")
    second_rows = load_manifest(second / "manifest.jsonl")
    assert [row["file_sha256"] for row in first_rows] == [row["file_sha256"] for row in second_rows]
    assert [row["svg_sha256"] for row in first_rows] == [row["svg_sha256"] for row in second_rows]
    assert validate_manifest(first / "manifest.csv")["ok"]

    masks = json.loads((first / "masks.json").read_text(encoding="utf-8"))
    with Image.open(first / masks[0]["mask_path"]) as image:
        assert image.mode == "L"
        assert image.size == (small_config.canvas_size, small_config.canvas_size)


def test_v2_bank_has_versioned_schema_without_content_or_conflict(
    small_v2_config, tmp_path: Path
) -> None:
    output = tmp_path / "v2"
    report = generate_bank(small_v2_config, output)
    assert report["schema_version"] == 8
    assert report["design_profile"] == "v2"
    assert report["stimulus_count"] == 60
    assert report["tag_counts"] == {"face": 24, "ambiguous": 12, "vase": 24}
    assert report["palette_values"] == {"black": 43, "gray": 154, "white": 201}
    assert report["material_value_ranges"] == {
        "black": [20, 58],
        "gray": [103, 186],
        "white": [132, 244],
    }
    assert report["material_shape_rendering"] == "crispEdges"

    rows = load_manifest(output / "manifest.jsonl")
    assert rows
    assert all("content" not in row for row in rows)
    assert all("is_conflict" not in row for row in rows)
    assert all("content_face_accent_side" not in row for row in rows)
    assert all(row["design_tag"] != "conflict" for row in rows)
    assert any(row["shading"] == "figure" for row in rows)
    assert validate_manifest(output / "manifest.csv")["ok"]
    montage_report = create_montages(output / "manifest.jsonl", cell_size=32)
    assert Path(montage_report["baseline_overview"]).exists()
    assert len(montage_report["base_montages"]) == 2


def test_frozen_v2_flat_and_material_means_are_luminance_matched() -> None:
    project_root = Path(__file__).parents[1]
    bank_root = project_root / "stimuli" / "v2"
    rows = load_manifest(bank_root / "manifest.jsonl")
    bases = {
        base.source.source_id: base
        for base in source_bases(project_root)
        if base.polarity == "dark-outer" and base.source.bank_enabled
    }
    totals = {
        kind: defaultdict(lambda: [0.0, 0]) for kind in ("texture", "flat")
    }

    for texture_row in rows:
        if not (
            texture_row["outline"] == "ambiguous"
            and texture_row["shading"] == "none"
            and texture_row["material"] == "vase"
        ):
            continue
        flat_row = next(
            row
            for row in rows
            if row["base_id"] == texture_row["base_id"]
            and row["outline"] == "ambiguous"
            and row["shading"] == "none"
            and row["material"] == "ambiguous"
            and row["polarity"] == texture_row["polarity"]
        )
        base = bases[str(texture_row["base_id"])]
        for kind, row in (("texture", texture_row), ("flat", flat_row)):
            with Image.open(bank_root / str(row["png_path"])) as image:
                pixels = np.asarray(image.convert("L"), dtype=np.float64)
            height, width = pixels.shape
            y = (np.arange(height) + 0.5) / height
            x = (np.arange(width) + 0.5) / width
            half_width = np.interp(y, base.y, base.widths, left=-1.0, right=-1.0)
            vase_mask = (half_width[:, None] >= 0.0) & (
                np.abs(x[None, :] - 0.5) <= half_width[:, None]
            )
            values = pixels[vase_mask]
            color = str(texture_row["figure_color"])
            totals[kind][color][0] += float(values.sum())
            totals[kind][color][1] += int(values.size)

    for color in ("black", "gray", "white"):
        texture_sum, texture_count = totals["texture"][color]
        flat_sum, flat_count = totals["flat"][color]
        texture_mean = texture_sum / texture_count
        flat_mean = flat_sum / flat_count
        assert abs(flat_mean - texture_mean) <= 0.5
